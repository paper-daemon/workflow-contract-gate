from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .validator import validate


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: line {exc.lineno}, column {exc.colno}") from exc


def _check(contract_path: Path, fixture_path: Path) -> dict[str, Any]:
    contract = _load(contract_path)
    fixture = _load(fixture_path)
    if not isinstance(contract, dict):
        raise ValueError("contract root must be an object")
    violations = validate(fixture, contract)
    return {
        "fixture": str(fixture_path),
        "ok": not violations,
        "violations": [v.as_dict() for v in violations],
    }


def _emit(results: list[dict[str, Any]], as_json: bool) -> None:
    if as_json:
        print(json.dumps({"ok": all(r["ok"] for r in results), "results": results}, indent=2))
        return
    for result in results:
        print(f"{'PASS' if result['ok'] else 'FAIL'} {result['fixture']}")
        for violation in result["violations"]:
            print(f"  {violation['path']} [{violation['code']}] {violation['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="workflow-contract-gate")
    sub = parser.add_subparsers(dest="command", required=True)

    one = sub.add_parser("check", help="Validate one JSON fixture")
    one.add_argument("--contract", required=True, type=Path)
    one.add_argument("fixture", type=Path)
    one.add_argument("--json", action="store_true", dest="as_json")

    many = sub.add_parser("check-dir", help="Validate all *.json fixtures in a directory")
    many.add_argument("--contract", required=True, type=Path)
    many.add_argument("directory", type=Path)
    many.add_argument("--json", action="store_true", dest="as_json")

    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            results = [_check(args.contract, args.fixture)]
        else:
            fixtures = sorted(args.directory.glob("*.json"))
            if not fixtures:
                raise ValueError(f"no JSON fixtures found in {args.directory}")
            results = [_check(args.contract, p) for p in fixtures]
        _emit(results, args.as_json)
        return 0 if all(r["ok"] for r in results) else 1
    except (OSError, ValueError) as exc:
        print(f"ERROR {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
