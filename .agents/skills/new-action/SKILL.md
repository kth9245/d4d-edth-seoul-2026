---
name: new-action
description: Start a new action in a module. Use whenever you are about to add new behavior to modules/<m>/ — creates the SPEC.md row, the action file skeleton and a failing test in one step.
---

1. Pick a `verb_noun` name and a one-line Korean description.
2. Run: `uv run python scripts/new_action.py <module> <verb_noun> "<설명>" --inputs "<타입>" --outputs "<타입>" --done "<완료 기준>"`
3. Replace the generated failing test with a real test of the behavior (inputs from `contracts/examples/*.json` when possible).
4. Implement the action until `uv run pytest modules/<module>/tests/test_<verb_noun>.py` passes. Keep the file <= 80 lines; if it grows, split into another action.
5. Wire it into `modules/<module>/pipeline.py` and export from `__init__.py` only if other modules need it.
6. Set the SPEC.md row status to `완료`.
