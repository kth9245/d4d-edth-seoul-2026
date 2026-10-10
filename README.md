# d4d-edth-seoul-2026

Korean Defense Tech Hackathon 2026 (D4D × EDTH SEOUL) 팀 저장소.

## 실행하기

준비물 (인터넷은 설치할 때만 필요하고, 실행은 오프라인으로 된다)
- git
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python 3.11 이상이 없으면 uv가 받아 온다
- [Node.js](https://nodejs.org/) 22.12 이상 (또는 20.19 이상)
- Linux 또는 macOS. Windows는 WSL2 안에서 실행한다.

```bash
git clone https://github.com/kth9245/d4d-edth-seoul-2026.git
cd d4d-edth-seoul-2026
uv sync                          # Python 의존성 (.venv)
(cd modules/cop-ui && npm ci)    # 화면 의존성
scripts/demo.sh                  # 화면을 빌드하고 서버를 띄운다
```

브라우저에서 http://localhost:8000 을 연다. 끌 때는 터미널에서 Ctrl+C.

- zip으로 받으면 실행되지 않는다. 스크립트가 git 저장소 안에서만 돈다.
- 지도 타일은 저장소에 들어 있다. 따로 받을 필요 없다.
- API 키 없이 돈다. AI 초안은 저장소에 있는 캐시 응답을 쓴다. 캐시에 없는 문장으로 초안을 만들 때만 `.env.example`을 `.env`로 복사하고 `GROK_KEY`를 채운다.
- 8000 포트를 다른 프로그램이 쓰고 있으면 서버가 뜨지 않는다. 그 프로그램을 끄고 다시 실행한다.

### 시연 작전 돌려 보기
1. 위쪽 **편집기** 탭 → 왼쪽 **작전** 목록에서 "해안 거점·무인장비 무력화"를 고른다.
2. 작전 이름 옆 **▶ 시뮬레이션** → 시뮬레이션 탭이 멈춘 채로 열린다.
3. 배속 **×30** → **▶ 재생**. 30초쯤이면 끝까지 간다.

장면별 설명과 직접 조종·표적 타격 조작은 `demo/assault_script.md`.

### 개발할 때
| 명령 | 하는 일 |
|---|---|
| `scripts/dev.sh` | 개발 실행. 코드를 고치면 바로 반영 (http://localhost:5173) |
| `uv run pytest` | Python 테스트 |
| `(cd modules/cop-ui && npm test)` | 화면 테스트 |

## 팀원

처음 한 번
1. Claude Code를 최신으로 업데이트하고 한 번 실행해 둔다 (v2.1.281 이상). Codex 사용자는 `/hooks`에서 저장소 hook을 신뢰 승인한다.
2. clone한 뒤 `scripts/setup.sh <내 모듈>` — git hook 연결, 의존성 설치. 끝나면 `<모듈>/work` 브랜치에 있으니 `git switch main`으로 돌아온다.
3. 작업은 메인 폴더가 아니라 자기 worktree에서 한다 (`AGENTS.md`의 "반영" 절).

| 명령 | 하는 일 |
|---|---|
| `/new-action` | 액션 시작 (SPEC 행 + 파일 + 실패 테스트) |
| `git commit` | 2초 검사 후 커밋 |
| `scripts/ship.sh` | main 반영 + 테스트 + smoke test + push |

규칙 전체: `AGENTS.md`. 설계: `docs/superpowers/specs/`.
