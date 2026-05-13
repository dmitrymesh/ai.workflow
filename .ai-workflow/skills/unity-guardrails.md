# Unity Guardrails

Forbidden by default (direct hand edits are never allowed):

- `.unity` scene changes
- `.prefab` changes
- `.asset` changes
- `.meta` changes
- `Packages/manifest.json` changes
- `Packages/packages-lock.json` changes
- `ProjectSettings/*` changes
- Serialized field renames without migration notes
- Save/load format changes without backward compatibility notes

**Unity MCP / editor-backed changes — exception when explicitly authorized:**

Changes to `.unity`, `.prefab`, `.asset`, and `.meta` files are allowed
**only** when `task.md` explicitly authorizes them by meeting all three
conditions:

1. **Scope named**: the specific scenes, prefabs, or asset files that may
   change are identified as precisely as practical.
2. **Tooling stated**: the task states that Unity MCP or Unity Editor tooling
   will be used (e.g., `refresh_unity`, `create_script`, a Unity MCP command).
3. **Validation included**: the task's Validation section specifies how the
   change will be verified (e.g., Unity compiles without errors, a PlayMode
   test passes).

Direct manual edits to Unity serialized YAML remain forbidden even when
Unity MCP/editor-backed changes are authorized. If Unity MCP or Editor
tooling is not accessible, stop and document the reason in `report.md`.

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
