from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Violation:
    path: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code, "message": self.message}


_TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "null": type(None),
}


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    py_type = _TYPE_MAP.get(expected)
    if py_type is None:
        raise ValueError(f"unsupported contract type: {expected}")
    return isinstance(value, py_type)


def validate(value: Any, contract: dict[str, Any], path: str = "$") -> list[Violation]:
    out: list[Violation] = []
    expected = contract.get("type")
    if expected is not None:
        if not isinstance(expected, str):
            raise ValueError(f"{path}: contract type must be a string")
        if not _type_ok(value, expected):
            return [Violation(path, "type_mismatch", f"expected {expected}")]

    if "enum" in contract and value not in contract["enum"]:
        out.append(Violation(path, "enum_violation", "value is not in the allowed set"))

    if isinstance(value, dict):
        props = contract.get("properties", {})
        if not isinstance(props, dict):
            raise ValueError(f"{path}: properties must be an object")
        required = contract.get("required", [])
        if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
            raise ValueError(f"{path}: required must be a list of strings")
        for key in required:
            if key not in value:
                out.append(Violation(f"{path}.{key}", "missing_required", "required field is missing"))
        for key, child in props.items():
            if key in value:
                if not isinstance(child, dict):
                    raise ValueError(f"{path}.{key}: property contract must be an object")
                out.extend(validate(value[key], child, f"{path}.{key}"))
        if contract.get("allow_unknown", True) is False:
            for key in value.keys() - props.keys():
                out.append(Violation(f"{path}.{key}", "unknown_field", "field is not allowed by the contract"))

    if isinstance(value, list) and "items" in contract:
        item_contract = contract["items"]
        if not isinstance(item_contract, dict):
            raise ValueError(f"{path}: items must be an object")
        for idx, item in enumerate(value):
            out.extend(validate(item, item_contract, f"{path}[{idx}]"))

    return out
