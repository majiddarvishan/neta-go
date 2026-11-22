package neta

import (
	"context"
	"fmt"
	"io"
	"net"
	"sync/atomic"
	"testing"
	"time"

	"github.com/majiddarvishan/neta-go/internal/wire"
)

func readQCOR02Frame(conn net.Conn) (wire.Frame, error) {
	header := make([]byte, wire.HeaderSize)
	if _, err := io.ReadFull(conn, header); err != nil {
		return wire.Frame{}, err
	}
	parsed, err := wire.ParseHeader(header)
	if err != nil {
		return wire.Frame{}, err
	}
	frame := make([]byte, int(parsed.Length))
	copy(frame, header)
	if _, err := io.ReadFull(conn, frame[wire.HeaderSize:]); err != nil {
		return wire.Frame{}, err
	}
	return wire.DecodeFrame(frame)
}

func writeQCOR02Frame(conn net.Conn, frame []byte) error {
	for len(frame) > 0 {
		n, err := conn.Write(frame)
		if err != nil {
			return err
		}
		if n == 0 {
			return io.ErrShortWrite
		}
		frame = frame[n:]
	}
	return nil
}

func TestQCOR02ExplicitReconnectRequiresOwnerAction(t *testing.T) {
	const generations = 3

	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer listener.Close()

	releaseClose := make(chan int, generations-1)
	boundGenerations := make(chan int, generations)
	peerDone := make(chan error, 1)
	var accepted atomic.Int32

	go func() {
		for generation := 1; generation <= generations; generation++ {
			conn, acceptErr := listener.Accept()
			if acceptErr != nil {
				peerDone <- acceptErr
				return
			}
			accepted.Add(1)
			_ = conn.SetDeadline(time.Now().Add(5 * time.Second))

			bindFrame, readErr := readQCOR02Frame(conn)
			if readErr != nil {
				_ = conn.Close()
				peerDone <- fmt.Errorf("generation %d read Bind: %w", generation, readErr)
				return
			}
			if bindFrame.Header.Command != wire.CommandBindRequest {
				_ = conn.Close()
				peerDone <- fmt.Errorf("generation %d command 0x%x, want Bind Request",
					generation, bindFrame.Header.Command)
				return
			}
			bind, decodeErr := wire.DecodeBindRequestV2(bindFrame)
			if decodeErr != nil {
				_ = conn.Close()
				peerDone <- fmt.Errorf("generation %d decode Bind: %w", generation, decodeErr)
				return
			}
			if bind.SystemID != "qcor02-client" {
				_ = conn.Close()
				peerDone <- fmt.Errorf("generation %d SystemID = %q", generation, bind.SystemID)
				return
			}
			bindResponse, encodeErr := wire.EncodeBindResponseV2(
				bindFrame.Header.Sequence,
				wire.StatusOK,
				wire.Bind{Type: bind.Type, SystemID: "qcor02-peer"},
			)
			if encodeErr == nil {
				encodeErr = writeQCOR02Frame(conn, bindResponse)
			}
			if encodeErr != nil {
				_ = conn.Close()
				peerDone <- fmt.Errorf("generation %d write Bind Response: %w", generation, encodeErr)
				return
			}
			boundGenerations <- generation

			if generation < generations {
				released := <-releaseClose
				if released != generation {
					_ = conn.Close()
					peerDone <- fmt.Errorf("release generation = %d, want %d", released, generation)
					return
				}
				if tcp, ok := conn.(*net.TCPConn); ok {
					_ = tcp.SetLinger(0)
				}
				_ = conn.Close()
				continue
			}

			requestFrame, requestErr := readQCOR02Frame(conn)
			if requestErr != nil {
				_ = conn.Close()
				peerDone <- fmt.Errorf("final generation read Stream Request: %w", requestErr)
				return
			}
			if requestFrame.Header.Command != wire.CommandStreamRequest {
				_ = conn.Close()
				peerDone <- fmt.Errorf("final generation command 0x%x, want Stream Request",
					requestFrame.Header.Command)
				return
			}
			payload, decodeErr := wire.DecodeStreamRequest(requestFrame)
			if decodeErr != nil || string(payload) != "final-generation" {
				_ = conn.Close()
				peerDone <- fmt.Errorf("final generation payload = %q, decode error = %v", payload, decodeErr)
				return
			}
			response, responseErr := wire.EncodeStreamResponse(
				requestFrame.Header.Sequence,
				wire.StatusOK,
				[]byte("ack:final-generation"),
			)
			if responseErr == nil {
				responseErr = writeQCOR02Frame(conn, response)
			}
			if responseErr != nil {
				_ = conn.Close()
				peerDone <- fmt.Errorf("final generation write Stream Response: %w", responseErr)
				return
			}

			unbindFrame, unbindErr := readQCOR02Frame(conn)
			if unbindErr != nil {
				_ = conn.Close()
				peerDone <- fmt.Errorf("final generation read Unbind: %w", unbindErr)
				return
			}
			if unbindFrame.Header.Command != wire.CommandUnbindRequest {
				_ = conn.Close()
				peerDone <- fmt.Errorf("final generation command 0x%x, want Unbind Request",
					unbindFrame.Header.Command)
				return
			}
			unbindResponse, unbindEncodeErr := wire.EncodeUnbindResponse(unbindFrame.Header.Sequence)
			if unbindEncodeErr == nil {
				unbindEncodeErr = writeQCOR02Frame(conn, unbindResponse)
			}
			_ = conn.Close()
			peerDone <- unbindEncodeErr
			return
		}
		peerDone <- fmt.Errorf("peer exhausted generations without final exchange")
	}()

	type closeEvent struct {
		session *Session
		cause   error
	}
	closed := make(chan closeEvent, generations)
	client, err := NewClient(
		WithClientAddress(listener.Addr().String()),
		WithClientSystemID("qcor02-client"),
		WithAutoReconnect(false),
		WithClientOnCloseHandler(func(session *Session, cause error) {
			closed <- closeEvent{session: session, cause: cause}
		}),
	)
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}
	defer func() {
		stopCtx, cancel := context.WithTimeout(context.Background(), time.Second)
		defer cancel()
		_ = client.Stop(stopCtx)
	}()

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	var previous *Session
	for generation := 1; generation <= generations; generation++ {
		if err := client.Connect(ctx); err != nil {
			select {
			case peerErr := <-peerDone:
				t.Fatalf("generation %d Connect: %v (peer: %v)", generation, err, peerErr)
			case <-time.After(100 * time.Millisecond):
				t.Fatalf("generation %d Connect: %v", generation, err)
			}
		}
		session, ok := client.CurrentSession()
		if !ok {
			t.Fatalf("generation %d did not publish a Bound Session", generation)
		}
		if previous != nil && session == previous {
			t.Fatalf("generation %d reused the previous Session pointer", generation)
		}
		previous = session

		select {
		case got := <-boundGenerations:
			if got != generation {
				t.Fatalf("peer bound generation %d, want %d", got, generation)
			}
		case <-ctx.Done():
			t.Fatalf("generation %d peer did not observe Bind: %v", generation, ctx.Err())
		}

		if generation < generations {
			releaseClose <- generation
			select {
			case event := <-closed:
				if event.session != session {
					t.Fatalf("OnClose Session = %p, want generation %d Session %p",
						event.session, generation, session)
				}
				if event.cause == nil {
					t.Fatalf("generation %d abrupt close reported nil cause", generation)
				}
			case <-ctx.Done():
				t.Fatalf("generation %d OnClose not delivered: %v", generation, ctx.Err())
			}

			deadline := time.Now().Add(time.Second)
			for {
				if _, ok := client.CurrentSession(); !ok {
					break
				}
				if time.Now().After(deadline) {
					t.Fatalf("generation %d remained published after Done", generation)
				}
				time.Sleep(time.Millisecond)
			}
			time.Sleep(50 * time.Millisecond)
			if got := accepted.Load(); got != int32(generation) {
				t.Fatalf("implicit reconnect accepted %d connections after generation %d; want no retry",
					got, generation)
			}
			continue
		}

		completed := make(chan struct {
			response Response
			err      error
		}, 1)
		sequence, err := session.SendRequest([]byte("final-generation"),
			func(response Response, err error) {
				completed <- struct {
					response Response
					err      error
				}{response: response, err: err}
			})
		if err != nil {
			t.Fatalf("final generation SendRequest: %v", err)
		}
		select {
		case result := <-completed:
			if result.err != nil {
				t.Fatalf("final generation Completion: %v", result.err)
			}
			if result.response.Sequence != sequence ||
				result.response.Status != 0 ||
				string(result.response.Payload) != "ack:final-generation" {
				t.Fatalf("final generation response = %+v, want sequence %d status 0 ack payload",
					result.response, sequence)
			}
		case <-ctx.Done():
			t.Fatalf("final generation Completion timed out: %v", ctx.Err())
		}
		if err := client.Stop(ctx); err != nil {
			t.Fatalf("final generation graceful Stop: %v", err)
		}
	}

	select {
	case err := <-peerDone:
		if err != nil {
			t.Fatalf("Q-COR-02 peer: %v", err)
		}
	case <-ctx.Done():
		t.Fatalf("Q-COR-02 peer did not finish: %v", ctx.Err())
	}
	if got := accepted.Load(); got != generations {
		t.Fatalf("accepted connections = %d, want exactly %d", got, generations)
	}
}
