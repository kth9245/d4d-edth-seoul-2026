---
name: task
description: Record work on the numbered plan (docs/research/09 §6, Part<n>-<k>). Use when starting, finishing, blocking or splitting a plan item, helping on someone else's item, or making a small decision mid-work.
---

All commands: `uv run python scripts/task.py ...`. Each write is pushed to main at once (decision 0013).

1. Before work: `task.py show` (one item with notes: `task.py show <번호>`; whole board: `--all`).
2. Start: `task.py start <번호>` (an action: `new_action.py` starts its linked item). Someone else's item in progress: `task.py add <번호> "<제목>"`, then start the new sub-item. Take over only after telling them in chat: `--take`.
3. After `scripts/ship.sh` succeeds: `task.py done <번호>`. Open sub-items block done.
4. Stuck for 5 minutes: `task.py block <번호> "<증상>"` and post the number in chat.
5. A decision that stays inside my item: `task.py decide <번호> "<결정>"`. Contracts, another person's module or policy: `/decide`, then `task.py decide <번호> "결정 NNNN 참조"`.
6. Note for whoever continues: `task.py note <번호> "<메모>"`. Item cut (09 §7): `task.py drop <번호> "<이유>"`.
7. Never edit `tasks/log.jsonl` or `tasks/NOW.md` by hand. "기록 못 올림" = network; retry later. "거부" = read the reason; do not work around it.
