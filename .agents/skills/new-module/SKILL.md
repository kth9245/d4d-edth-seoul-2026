---
name: new-module
description: Create a brand-new pipeline module (e.g. edge, identify, planning) that does not exist yet. Use before adding any code under a module directory that is missing.
---

1. Pick a lowercase module name and a 2-5 letter uppercase SPEC prefix (e.g. `edge` / `EDG`).
2. Run: `uv run python scripts/new_module.py <name> <PREFIX>`
3. Fill in `modules/<name>/AGENTS.md` (role, input, output, public API).
4. Work on a branch named `<name>/<topic>` (`scripts/setup.sh <name>` creates it).
5. Add the first action with `/new-action`.
