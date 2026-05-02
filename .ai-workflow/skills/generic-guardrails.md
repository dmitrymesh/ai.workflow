# Generic Guardrails

Forbidden unless explicitly allowed:

- Secrets or credentials
- `.env` changes
- Broad formatting-only diffs mixed with logic changes
- Dependency upgrades unrelated to the task
- Public API changes without tests or migration notes

Prefer:

- Small diffs
- Existing project style
- Tests for changed logic
- Clear validation results
- Explicit assumptions
