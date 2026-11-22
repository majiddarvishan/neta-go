"""Strict JSON decoding for qualification evidence.

Reject duplicate object keys and non-standard NaN/Infinity constants instead
of accepting Python json's permissive last-key-wins/default-constant behavior.
"""
from __future__ import annotations

import json


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key: " + key)
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("Non-standard JSON numeric constant: " + value)


def loads(payload):
    if type(payload) is not str:
        raise TypeError("JSON payload must be text")
    return json.loads(
        payload,
        object_pairs_hook=_unique_object,
        parse_constant=_reject_constant,
    )
