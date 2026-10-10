---
id: 0028
title: AI 초안 LLM은 Grok(xAI)으로 바꿈
status: 확정
decided_by: kth9245
date: 2026-10-10
modules: [play, infra]
supersedes: 0027
---
## 결정
2026-10-10 10:50경, Part1-5(AI 초안 프롬프트·캐시)와 Part3-9(`draft_play`)의 순서를 묻자 리드가 답한 것을 그대로 적는다.

리드(kth9245): "2번을 하고 genlab-module 폴더의 change_cot 프롬프트 처럼 구조화되고 논리적으로 명확하며 json으로 출력하게 하는 프롬프트로 만들어줘. 그리고 그록 모델로 하고 env에 GROK_KEY 넣어둠"

질문의 2번 선택지: "Part1-5의 앞부분(프롬프트 틀과 문장 2개)을 리드가 지금 만들어 넘기고, 캐시는 나중에 만든다."

(AI 해석)
1. 저장소에서 LLM을 부르는 곳(play `draft_play` 하나)은 xAI Grok API만 쓴다. 키는 `.env`의 `GROK_KEY`. 결정 0027(Anthropic 통일)을 대체한다.
2. 프롬프트 틀은 리드가 지금 만든다. 형식은 change_cot처럼 번호 붙은 절(목적·기본 규칙·표기 규약·출력 항목별 작성 규칙·입력 자료·출력 양식)로 나누고, 응답은 JSON 객체 하나로 받는다.
3. 캐시 2개(`demo/plays/cache/<sha256(prompt)>.json`)는 `draft_play`가 생긴 뒤 Grok 응답으로 만든다. 캐시 키 규칙은 그대로.
4. 모델 이름은 이 결정에 넣지 않는다. 10/10 기준 키로 쓸 수 있는 텍스트 모델 중 최신은 `grok-4.7`(GET /v1/models로 확인).

## 이유
- 리드가 Grok 키를 준비해 두었다.
- 프롬프트를 한 사람이 한 곳에서 만들어야 `sha256(prompt)` 캐시 키가 어긋나지 않는다. 지금까지는 09 문서상 Part1-5(통합 2 뒤)와 Part3-9(Part1-5 뒤)가 서로를 기다리는 상태였다.

## 버린 대안
- Anthropic 유지(결정 0027): 리드가 Grok으로 바꾸기로 함.
- 프롬프트도 `draft_play` 안에서 황승주가 작성: 리드가 시연 장면(보고 지점 없는 초안 → 검사 실패)에 맞춰 프롬프트를 직접 쓰기로 함.
- 계획대로 18:00 뒤 Part1-5 전체: 그때까지 `draft_play`가 시작하지 못함.

## 영향
- play `draft_play`(PLY-09, 황승주): Anthropic 대신 xAI API(`https://api.x.ai/v1/chat/completions`, OpenAI 호환) 호출. 프롬프트는 리드가 만든 함수로 받는다.
- Part1-5(리드): 프롬프트 틀과 시연 문장 2개를 먼저, 캐시 2개는 Part3-9 뒤.
- infra: `.env.example`의 `ANTHROPIC_API_KEY`·`OPENAI_API_KEY`를 `GROK_KEY`로 바꾼다.
- 황승주에게 결정 0027이 바뀌었음을 채팅으로 알린다.
