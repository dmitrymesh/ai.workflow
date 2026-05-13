# Unity Profile

Unity-specific profile.

Use `.ai-workflow/skills/unity-guardrails.md`.

Primary risks:

- scene YAML changes
- prefab references
- `.meta` files
- serialized field renames
- package changes
- save/load migrations
- lifecycle ordering

## Required validation

After implementation, trigger Unity recompilation through Unity MCP or
equivalent editor automation and inspect compiler diagnostics before submitting.
See the "Validation for Unity-profile tasks" section in `unity-guardrails.md`
for the exact steps and what to record in `validation.md`.
