---
id: cumulative-alarm-cusum-m-of-n
title: 점수를 시간에 쌓아 문턱에서 경보하는 방식(CUSUM, M-of-N 트랙 확정)
summary: 점수×시간 누적으로 카드를 올리는 규칙은 CUSUM·점수 기반 트랙 확정과 같은 발상이고, 우리는 내려가면 즉시 0으로 리셋하는 단순형이다
tags: [threat, accumulation, cusum, track-confirmation, evidence]
modules: [sensing, runtime]
confidence: 추정
sources: [https://en.wikipedia.org/wiki/CUSUM, https://www.mathworks.com/help/fusion/ug/introduction-to-track-logic.html, https://www.mathworks.com/help/radar/ug/assessing-performance-with-the-tracker-operating-characteristic.html]
author: 최동호
---
## 결론
"위협 점수 0.40 이상인 동안 점수×시간을 쌓아 4.5가 되면 카드를 올린다"(`CARD_ACCUM`)는 지속시간으로 오경보를 거르는 표준적 발상이다. 검색 요약 기준이며 원문은 읽지 않았다.

## 근거
- CUSUM: E. S. Page가 1954년 Biometrika에 소개했다. 표본을 가중해 합하다가 합이 문턱을 넘으면 경보를 내고, Wald의 SPRT를 반복 적용한 것과 같다(Lorden 1971이 점근 최적성을 보였다).
- M-of-N 트랙 확정: 연속 N번 중 M번 검출돼야 트랙을 확정한다. M/N이 낮으면 거짓 트랙이 확정될 수 있고, M·N은 확정 속도와 거짓 트랙률의 균형이다. 점수가 문턱을 넘을 때 확정하는 점수 기반 논리도 있다(MathWorks 문서).
- 한계: 경보 문턱을 정하는 공식(ARL 등)은 검색에서 못 찾았다.

## 코드에 적용하는 법
우리 규칙은 CUSUM과 달리 문턱 미만이면 누적을 즉시 0으로 리셋한다(스친 표적을 거르는 단순형). 이 선택의 오경보·미탐 성능은 따로 평가하지 않았고, 4.5(점수 1.0으로 4.5초)와 0.40은 임의 값이다.

## 관련 카드
[[threat-evaluation-parameters]]
