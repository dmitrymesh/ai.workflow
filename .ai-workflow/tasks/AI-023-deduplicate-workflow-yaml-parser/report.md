# Execution Report: AI-023

## Summary

Removed the duplicate YAML parser in `_discovery.py`. There is now one shared implementation — `parse_simple_yaml_str(text: str)` in `_core.py`. The existing file-path wrapper `parse_simple_yaml(path: Path)` delegates to it. All callers of the removed `_parse_yaml_string` in `_discovery.py` and `_approve.py` now use the shared function from `_core`.

## Changed files

- `.ai-workflow/scripts/_core.py` — extracted `parse_simple_yaml_str(text: str)` from `parse_simple_yaml`; `parse_simple_yaml` now reads the file and delegates to it. Added boolean handling that the duplicate lacked.
- `.ai-workflow/scripts/_discovery.py` — removed `_parse_yaml_string`; import `parse_simple_yaml_str` from `_core`; replaced callsite.
- `.ai-workflow/scripts/_approve.py` — removed `_parse_yaml_string` from `_discovery` import; import `parse_simple_yaml_str` from `_core`; replaced callsite.

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python -m unittest test_cascade test_show` — 11 tests passed
- `python .ai-workflow/scripts/ai_task.py list-branches` — output unchanged
- `python .ai-workflow/scripts/ai_task.py show-branch AI-018` — output unchanged

## Assumptions

- The duplicate `_parse_yaml_string` lacked boolean parsing (`true`/`false`). Adding it to the shared implementation is safe; no metadata files use boolean values, so behavior is unchanged.
- `_parse_workflow_config` in `_discovery.py` is a separate, purpose-built indent-aware parser for the nested `workflow:` config block and is not part of this deduplication.

## Known risks

- Low. Pure refactor — no behavior change to any command output or metadata format.
