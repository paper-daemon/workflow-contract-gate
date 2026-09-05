import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from workflow_contract_gate.cli import main


class CliTests(unittest.TestCase):
    def test_exit_codes_and_json_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract = root / "contract.json"
            fixture = root / "fixture.json"
            contract.write_text(json.dumps({"type": "object", "required": ["id"], "properties": {"id": {"type": "integer"}}}))
            fixture.write_text(json.dumps({"id": "x"}))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["check", "--contract", str(contract), str(fixture), "--json"])
            self.assertEqual(code, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])

    def test_config_error_is_exit_2(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract = root / "contract.json"
            fixture = root / "fixture.json"
            contract.write_text('{"type":"wat"}')
            fixture.write_text('{}')
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["check", "--contract", str(contract), str(fixture)]), 2)


if __name__ == "__main__":
    unittest.main()
