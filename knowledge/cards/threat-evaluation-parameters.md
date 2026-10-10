---
id: threat-evaluation-parameters
title: 위협 평가 문헌의 지표 구성(TEWA·해상 이상행동·충돌위험 가중합)
summary: 위협 평가는 종류·속도·거리·도달 시간 같은 지표의 가중합에 문턱을 두는 구조가 흔하고, 우리 점수는 이 구조를 따르되 가중치는 도출한 값이 아니다
tags: [threat, scoring, evidence, tewa, maritime]
modules: [sensing, gateway]
confidence: 추정
sources: [https://www.comsys.rwth-aachen.de/fileadmin/papers/2022/2022-wolsing-aistracks.pdf, https://cambridgepixel.com/site/assets/files/7473/threat-evaluation-and-weapon-assignment-tewa-datasheet-cp-16-444-01.pdf, https://arxiv.org/pdf/0907.0067, https://www.comsys.rwth-aachen.de/publication/2022/2022_wolsing_anomaly-detection-in-maritime/, https://arxiv.org/pdf/2505.07374, https://arxiv.org/pdf/1606.00981, https://www.iaeng.org/IJCS/issues_v52/issue_9/IJCS_52_9_38.pdf]
author: 최동호
---
## 결론
우리 위협 점수(종류+기준점 거리+RF+속도, 문턱 0.40)는 공개 문헌의 **구조**와 같다. **값**의 근거는 문헌이 아니라 시연 실측이다. 원문을 직접 읽은 것은 Wolsing 외(2022), arXiv 2505.07374의 해당 문단이고 나머지는 검색 요약이다.

## 근거
- TEWA(위협 평가·무기 할당): 상용 위협 처리기는 사용자 위협 수준, 자동 분류, 트랙 속도, 출처, 최근 기동성으로 기본 점수를 만들고 자산별 거리·도달 시간을 쓴다. 시작 조건(문턱)과 정렬 입력을 나눠 부르는 분류도 있다(Cambridge Pixel, arXiv 0907.0067).
- 해상 이상행동(원문 확인): Wolsing 외 2022는 44편을 Lane 외(2010)의 5종류로 분류한다: 경로 이탈(37편), 비정상 AIS 활동(7편), 도착지 이상(3편), 근접 접근(약 4편, 선박 사이), 구역 진입(3편, 일정 시간 머무는 것). 구역 진입은 위치만으로 판정하면 너무 단순하다고 여겨져 소홀히 다뤄졌고, 곧 진입할지를 예측하는 더 정교한 방법을 상상할 수 있다고 쓴다(의역). 이 논문은 문턱 방식을 논의하지 않는다.
- 문턱 방식(원문 확인): arXiv 2505.07374는 Transformer 기반 행동 탐지 "8편 중 절반"이 문턱을 쓴다고 한다. 규모가 작고 범위가 한정돼 "일반적"이라고 하기엔 약하다.
- 충돌위험: DCPA·TCPA의 가중합에 문턱을 두는 단순 지수가 흔하고, 가중치를 퍼지 AHP로 구하는 연구가 있다(arXiv 1606.00981, IJCS).
- 한계: 검색에서 CPA를 TEWA 입력으로 명시한 자료는 못 찾았다. 거리·속도·방출을 한 모델에 합친 해상 위협 순위 논문도 못 찾았다.

## 코드에 적용하는 법
`sensing/score_target`의 가산치(0.15~0.40)·기준치 0.40은 "임의 값, 시연에서 조정"이라고 설명한다. 문헌과 맞는 것은 지표 종류와 가중합+문턱 구조다. CPA·TCPA(접근 방향·도달 시간)는 쓰지 않았고 결정 0041에서 보류했다.

## 관련 카드
[[cumulative-alarm-cusum-m-of-n]], [[rf-emission-indicator]], [[drone-detection-range-sources]]
