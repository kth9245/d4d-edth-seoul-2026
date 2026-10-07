# contracts — 모듈 간 데이터 형식

`models.py`(pydantic)가 유일한 정본이다. `contracts/schema/*.json`과
`modules/cop-ui/src/contracts.gen.ts`는 `scripts/gen_contracts.py`가 만든 자동 생성 파일이다(직접 수정 금지).

## 데이터 흐름
sim → (Detection) → sensing → (Detection) → tracking → (Track) → assess → (Assessment)
→ respond → (Response) → gateway → (Frame, WebSocket `/ws`) → cop-ui

| 모델 | 만드는 곳 | 쓰는 곳 |
|---|---|---|
| Detection | sim | sensing, tracking |
| Track | tracking | assess, respond, gateway |
| Assessment | assess | respond, gateway |
| Response | respond | gateway |
| Frame | gateway | cop-ui |

## 단위 (decisions/POLICY.md)
- 좌표: WGS84 위경도(도), 고도: m, 시간: UTC epoch 밀리초(`t_ms`).

## 수정 방법
- `contracts/<주제>` 브랜치에서만 수정한다(리드 담당).
- `contracts/models.py`를 고치면 커밋 시 `scripts/gen_contracts.py`가 자동 실행된다. 수동: `uv run python scripts/gen_contracts.py`.
- 예시 데이터는 `contracts/examples/*.json`. 모델과 함께 갱신한다.
