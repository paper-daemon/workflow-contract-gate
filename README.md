# Workflow Contract Gate

A small, dependency-light contract gate for API, webhook, and automation fixtures. It catches integration-breaking payload changes before they reach n8n, Make, Python workers, or downstream APIs.


## Want this adapted to your API or webhook?

The CLI and examples below are **free MIT-licensed software**. The optional **$89 USD fixed-scope setup service** is for adapting this pattern to one agreed API or webhook contract boundary, adding representative fixtures and checking the result. This requires customer-specific work and is **not an instant download**.

- [Read the scope and verify the case study](https://paper-daemon.github.io/work.html#services)
- [Stripe checkout for the $89 USD contract-gate setup](https://book.stripe.com/bJefZggNM1kq9IJbOHgEg2a)
- [See the implementation case study](https://paper-daemon.github.io/portfolio/workflow-contract-gate.html)

You can use this repository freely without purchasing the setup service.
## Why it exists

Automation failures often start with a tiny contract change: a required field disappears, an integer becomes a string, an enum gains an unexpected value, or a webhook adds structure your downstream step does not accept. Workflow Contract Gate makes those assumptions explicit and testable in CI.

## Features

- Explicit JSON contract file
- Required and optional object fields
- Nested objects and arrays
- Primitive type checks
- Enum constraints
- Strict or permissive unknown-field policy
- Secret-safe diagnostics: paths and rule failures, not payload values
- Human-readable and JSON output
- Stable exit codes for CI and automation
- Python 3.10, 3.12, and 3.13 CI coverage

## Install

```bash
python -m pip install -e .
```

## Quick start

```bash
workflow-contract-gate check \
  --contract examples/contract.json \
  examples/fixtures/good.json
```

A valid fixture exits `0`. Contract violations exit `1`. Invalid configuration or unreadable JSON exits `2`.

Check a fixture directory:

```bash
workflow-contract-gate check-dir --contract examples/contract.json examples/fixtures
```

Machine-readable result:

```bash
workflow-contract-gate check --json --contract contract.json payload.json
```

## Contract format

```json
{
  "type": "object",
  "required": ["event", "payload"],
  "allow_unknown": false,
  "properties": {
    "event": {"type": "string", "enum": ["lead.created", "lead.updated"]},
    "payload": {
      "type": "object",
      "required": ["id"],
      "properties": {"id": {"type": "integer"}}
    }
  }
}
```

Supported types: `object`, `array`, `string`, `number`, `integer`, `boolean`, and `null`.

## CI example

```yaml
- run: python -m pip install -e .
- run: workflow-contract-gate check-dir --contract contracts/webhook.json fixtures/webhook
```

Use it before deploying a workflow or after saving representative payload fixtures from a staging system. It works especially well next to n8n/Make export tests, webhook handlers, API adapters, and scheduled data pipelines.

## Design boundaries

This is intentionally not a full JSON Schema implementation. The goal is a compact, reviewable contract format for workflow edges where teams want deterministic checks without pulling a large validation stack into every automation repository.

Diagnostics do not print input values by default. A failed check reports only the JSON path, violation code, and rule message.

## License

MIT
