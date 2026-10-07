# d4d-edth-seoul-2026

Korean Defense Tech Hackathon 2026 (D4D × EDTH SEOUL) 팀 저장소.

## 시작하기 (팀원 1회)
1. Claude Code를 최신으로 업데이트하고 한 번 실행해 둔다 (v2.1.281 이상). Codex 사용자는 `/hooks`에서 저장소 hook을 신뢰 승인한다.
2. `git clone https://github.com/kth9245/d4d-edth-seoul-2026 && cd d4d-edth-seoul-2026`
3. `scripts/setup.sh <내 모듈>` — 의존성 설치, git hook 연결, `<모듈>/work` 브랜치 생성
4. AI 도구 실행: Claude Code는 저장소 루트에서, Codex는 `cd modules/<내 모듈> && codex`

## 매일 쓰는 명령
| 명령 | 하는 일 |
|---|---|
| `/new-action` | 액션 시작 (SPEC 행 + 파일 + 실패 테스트) |
| `git commit` | 2초 검사 후 커밋 |
| `scripts/ship.sh` | main 반영 + 테스트 + smoke test + push |
| `scripts/dev.sh` | 개발 실행 (http://localhost:5173) |
| `scripts/demo.sh` | 시연 실행 (http://localhost:8000, 오프라인) |

규칙 전체: `AGENTS.md`. 설계: `docs/superpowers/specs/`.
