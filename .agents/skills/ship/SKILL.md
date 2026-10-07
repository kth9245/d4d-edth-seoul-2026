---
name: ship
description: Push finished work to main. Use when one or more actions are done and committed.
---

1. Make sure everything is committed (`git status` clean).
2. Run `scripts/ship.sh`. It rebases on origin/main, runs tests of changed modules and the demo smoke test, then pushes to main.
3. On failure, read the short failure output, fix it, commit, and run `scripts/ship.sh` again.
4. On rebase conflict in a file you do not own, stop and ask the owner.
