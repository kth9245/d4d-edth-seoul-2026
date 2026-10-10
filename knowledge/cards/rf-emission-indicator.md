---
id: rf-emission-indicator
title: RF 방출 여부를 위협 단서로 쓰는 근거와 한계(EMCON)
summary: 방출 여부와 방출의 부재를 단서로 보는 것은 상용 분석에서 쓰이지만 권위 있는 표준은 못 찾았다
tags: [threat, rf, emcon, evidence]
modules: [sensing, sim]
confidence: 추정
sources: [https://www.usni.org/magazines/proceedings/2022/august/digital-age-make-ships-go-dark, https://windward.ai/glossary/what-is-emcon/]
author: 최동호
---
## 결론
"RF는 출력이 크냐가 아니라 **표적이 방출을 하는가**를 단서로 쓴다"는 방침은 상용 분석 자료와 방향이 같다. 다만 출처는 해설 기사와 상업 자료이고 정식 기준이 아니다. 검색 요약 기준이며 원문은 읽지 않았다.

## 근거
- EMCON은 함정·항공기가 전자 방출을 일부러 줄이거나 끄는 운용이며 단계가 있다(전면 송신에서 완전 무선 침묵까지).
- 상업 해상 분석은 EMCON 상태 선박의 탐지에 공을 들이고, 기대되는 신호의 부재 자체를 분석적으로 가치 있게 본다. RF 탐지는 AIS를 끈 선박의 활동도 잡고 단독 수단이 아니라 보조 층이다.
- USNI 해설: 방출의 탐지 가능 거리는 유용 거리의 약 두 배라는 경험칙이 소개된다.
- 한계: 방출 부재를 이상행동으로 형식화하는 권위 있는 기준은 못 찾았다.

## 코드에 적용하는 법
RF 수신 범위(2000 m)를 드론 시각 센서 범위(800 m)보다 크게 둔 것은 방향이 같지만, 이 수치를 경험칙에서 도출한 것은 아니다. 화면에는 우리가 잡은 것(`rf_detected`)만 보이고 정답(`emitting`)은 쓰지 않는다. 방출을 적대의 증거로 설명하지 않는다.

## 관련 카드
[[threat-evaluation-parameters]]
