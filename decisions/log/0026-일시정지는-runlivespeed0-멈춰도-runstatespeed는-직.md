---
id: 0026
title: 일시정지는 /run/live?speed=0, 멈춰도 RunState.speed는 직전 배속 유지
status: 확정
decided_by: kth9245
date: 2026-10-10
modules: [contracts, gateway, cop-ui]
supersedes: null
---
## 결정
2026-10-10 10시, Part1-7(gateway REST·WS) 설계 중. 계약에 일시정지 엔드포인트가 없어 AI가 "`/run/live?speed=0`을 일시정지로 해석하고 API.md에 한 줄 추가"를 추천했고, 사람이 "일시 정지 speed 0은 ui 상에서 조절 가능한가"라고 물은 뒤(답: Part1-13 배속 패널의 버튼), AI가 "멈춰도 `run.speed`에 직전 배속을 남긴다"를 덧붙인 설계로 시작할지 묻자 사람이 "직접 구현 + subagent 리뷰 (추천)"(설명: 앞의 설계(일시정지 speed=0, 직전 배속 유지)로 바로 시작)을 골랐다.

(AI 해석)
1. `POST /run/live?speed=0`은 틱을 멈춘다. `Frame.run.status = paused`.
2. 이때 `Frame.run.speed`는 0이 아니라 멈추기 전 배속을 그대로 둔다. 화면의 "다시 재생"은 `run.speed`를 다시 보내면 된다.
3. `speed > 0`이면 `status = running`, `speed`는 그 값.
4. 같은 자리에서 "다음 사건으로"(`/run/jump`)는 계약 그대로 `offset_ms` 필수로 두었다(사람 "계약 그대로", task.py Part1-7 기록).

## 이유
- 발표자가 카드를 설명하는 동안 화면을 멈춰야 한다. 새 엔드포인트 없이 배속 값 하나로 된다.
- 직전 배속을 남기지 않으면 화면이 따로 기억해야 하고 새로고침하면 잃는다.

## 버린 대안
- `/run/pause` 엔드포인트 추가: 엔드포인트가 하나 늘고 하는 일은 같다.
- 일시정지 없음: 30배속에서 발표자가 카드를 설명할 시간이 없다.

## 영향
- `contracts/API.md` 5절 `/run/live` 줄, `modules/gateway/app.py`·`live.py`(Part1-7), 화면 배속 패널(Part1-13).
