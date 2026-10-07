---
name: kb-save
description: Turn research findings into knowledge cards. Use after researching anything (web search, docs, experiments) or when knowledge/inbox/ has unprocessed material.
---

1. Read `knowledge/INDEX.md` and the files in `knowledge/inbox/`.
2. For each distinct conclusion, update the existing card if one covers it; otherwise create `knowledge/cards/<kebab-id>.md`:
   frontmatter `id, title, summary (one line), tags [..], modules [..], confidence (확인됨|추정), sources [urls], author`,
   then sections `## 결론`, `## 근거`, `## 코드에 적용하는 법`, `## 관련 카드` (`[[id]]`). Max 40 lines.
3. No source URL → `confidence: 추정`. Never invent sources.
4. Move processed inbox files to `knowledge/inbox/done/`.
5. Run `python scripts/sync_docs.py` to refresh the index.
