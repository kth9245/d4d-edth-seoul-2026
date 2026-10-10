---
id: 0027
title: AI 초안 LLM은 Anthropic API로 통일
status: 폐기
decided_by: 황승주
date: 2026-10-10
modules: [play, infra]
supersedes: null
---
## 결정
> 폐기: 결정 0028으로 대체(AI 해석 오류. 원래 발언은 팀원 작업 세션이 Claude라는 뜻이었다).

2026-10-10 오전, PLY-09 draft_play와 Part1-5(AI 초안 프롬프트·캐시)의 선행 관계를 설명받던 중 사람이 말한 것을 그대로 적는다.

사람(황승주): "팀원 모두 Anthropic로 통일"
AI가 저장소 결정으로 기록할지 물음 → 사람: "이름은 황승주로 하고 기록을 부탁해"

(AI 해석)
1. 저장소에서 LLM을 부르는 곳(지금은 play `draft_play` 하나, 결정 0001·09 문서 3.2)은 Anthropic API만 쓴다. 키는 `.env`의 `ANTHROPIC_API_KEY`.
2. Part1-5의 AI 초안 캐시 2개도 Anthropic 모델의 응답으로 만든다. 캐시 키(sha256(prompt))는 그대로.
3. `.env.example`의 `OPENAI_API_KEY` 칸은 쓰지 않는다(지울지는 리드가 정한다).
4. 모델 이름·SDK(anthropic 패키지 또는 httpx 직접 호출)는 이 결정에 포함하지 않는다. 구현하는 사람이 고르고 `task.py decide`로 남긴다.

## 이유
- 팀원이 쓰는 키·과금을 한 곳으로 모아 시연 전에 키 준비를 한 번만 한다.
- 제공자가 하나면 프롬프트·캐시·재요청 처리를 한 가지 응답 형식에 맞추면 된다.

## 버린 대안
- OpenAI 사용: `.env.example`에 칸은 있으나 팀이 통일하지 않기로 함.
- 두 제공자 모두 지원: happy path 원칙(결정 0024)에 비해 코드와 테스트가 늘어난다.

## 영향
- play `draft_play`(PLY-09, 황승주): Anthropic API 1회 호출·스키마 밖이면 1회 재요청·실패 시 템플릿.
- Part1-5(리드): 캐시 2개를 Anthropic 응답으로 생성.
- infra: 의존성 추가가 필요하면 `uv add`로(리드 확인).
