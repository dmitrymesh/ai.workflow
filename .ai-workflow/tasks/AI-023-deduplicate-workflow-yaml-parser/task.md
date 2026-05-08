# AI-023: Deduplicate workflow YAML parser

## Goal

Remove duplicate simple-YAML parsing logic between `_core.py` and `_discovery.py`.

## Context

AI-018 found that `_discovery.py::_parse_yaml_string` duplicates
`_core.py::parse_simple_yaml`. This increases maintenance cost and risks parser
behavior drifting between local task files and branch metadata.

## Scope

Allowed changes:

- Add a string-input parsing helper to `_core.py`, or generalize the existing parser.
- Update `_discovery.py` to use the shared helper.
- Add focused tests or smoke checks for metadata parsing through `list-branches`.

Forbidden changes:

- Do not introduce PyYAML or other dependencies.
- Do not change metadata file format.
- Do not change discovery output except where required by bug fixes.

## Requirements

- There must be one shared implementation for simple metadata parsing.
- Existing task metadata files must continue to parse correctly.
- `list-branches` and `show-branch` output must remain behaviorally unchanged.

## Acceptance criteria

- `_discovery.py` no longer has a duplicate YAML parser.
- Existing cascade and show tests still pass.
- `list-branches` and `show-branch AI-018` still work.
- `validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Existing Python tests
- `python .ai-workflow/scripts/ai_task.py list-branches`
- `python .ai-workflow/scripts/ai_task.py show-branch AI-018`

## Notes

Created from AI-018 finding: "LOW - _discovery.py duplicates the YAML parser".
