import unittest

from workflow_contract_gate.validator import validate


CONTRACT = {
    "type": "object",
    "required": ["id", "state"],
    "allow_unknown": False,
    "properties": {
        "id": {"type": "integer"},
        "state": {"type": "string", "enum": ["ready", "done"]},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
}


class ValidatorTests(unittest.TestCase):
    def test_valid_payload(self):
        self.assertEqual(validate({"id": 1, "state": "ready", "tags": ["a"]}, CONTRACT), [])

    def test_reports_paths_without_values(self):
        issues = validate({"id": "secret-value", "state": "bad", "extra": "secret"}, CONTRACT)
        as_dict = [x.as_dict() for x in issues]
        self.assertIn({"path": "$.id", "code": "type_mismatch", "message": "expected integer"}, as_dict)
        self.assertIn({"path": "$.state", "code": "enum_violation", "message": "value is not in the allowed set"}, as_dict)
        self.assertIn({"path": "$.extra", "code": "unknown_field", "message": "field is not allowed by the contract"}, as_dict)
        self.assertNotIn("secret-value", repr(as_dict))

    def test_missing_required(self):
        issues = validate({"id": 1, "state": "ready"}, {**CONTRACT, "required": ["id", "state", "tags"]})
        self.assertEqual(issues[0].code, "missing_required")
        self.assertEqual(issues[0].path, "$.tags")

    def test_array_item_path(self):
        issues = validate({"id": 1, "state": "ready", "tags": ["ok", 2]}, CONTRACT)
        self.assertEqual(issues[0].path, "$.tags[1]")

    def test_boolean_is_not_integer(self):
        issues = validate({"id": True, "state": "ready"}, CONTRACT)
        self.assertEqual(issues[0].code, "type_mismatch")


if __name__ == "__main__":
    unittest.main()
