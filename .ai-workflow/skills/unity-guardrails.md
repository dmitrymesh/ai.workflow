# Unity Guardrails

Forbidden unless explicitly allowed in `task.md`:

- `.unity` scene changes
- `.prefab` changes
- `.asset` changes
- `.meta` changes
- `Packages/manifest.json` changes
- `Packages/packages-lock.json` changes
- `ProjectSettings/*` changes
- Serialized field renames without migration notes
- Save/load format changes without backward compatibility notes

Prefer:

- Pure C# services for business logic
- EditMode tests for pure logic
- PlayMode tests only for scene/lifecycle behavior
- Small diffs
- Dependency injection over `FindObjectOfType`
- Explicit timeout helpers instead of arbitrary waits
- Clear cleanup in test teardown

Avoid:

- New singletons without explicit approval
- Hidden changes in `Awake`, `Start`, `OnEnable`, `Update`
- Broad refactors mixed with feature work
- Package changes as part of unrelated tasks
