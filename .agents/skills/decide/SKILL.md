---
name: decide
description: Record a human decision or policy. Use when a person states a choice ("앞으로 ~로 하자", "~는 쓰지 말자") or when your work needs a decision a person must make.
---

1. Check `decisions/INDEX.md` for an existing decision on the topic.
2. Run: `uv run python scripts/decide.py new "<제목>" --modules <m1,m2>` and fill `## 결정`, `## 이유`, `## 버린 대안`, `## 영향`.
3. Leave `status: 제안`. Never write `확정` into a decision file yourself (the guard blocks it).
4. Confirm only when the person explicitly says to confirm that specific decision.
   Run exactly `uv run python scripts/decide.py accept NNNN --by <이름>` as its own command (no `&&`, `;`, pipes).
   - Claude Code: the guard hook shows the person an approval prompt; it runs only if they approve.
   - Codex: `.codex/rules/decide.rules` (decision="prompt") makes Codex ask the person first. Needs the project trusted in Codex.
   - If it is blocked anyway, tell the person "확정하려면 `! uv run python scripts/decide.py accept NNNN --by <이름>`을 직접 실행해 주세요."
5. Standing rules (always apply) belong in `decisions/POLICY.md`, which only humans edit — propose the wording in chat.
