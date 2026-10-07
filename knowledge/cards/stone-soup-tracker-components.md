---
id: stone-soup-tracker-components
title: 다중표적 추적기의 부품 분리 (Stone Soup)
summary: 추적기는 예측·연관·갱신·생성·삭제 부품으로 나누면 각각 독립 구현·교체할 수 있다
tags: [tracking, architecture]
modules: [tracking]
confidence: 확인됨
sources: [https://stonesoup.readthedocs.io/en/v1.9.1/stonesoup.tracker.html]
author: 리드
---
## 결론
tracking 모듈 액션을 predict_tracks, associate_detections, update_tracks, initiate_tracks, delete_stale_tracks로 나눈다.

## 근거
Stone Soup의 MultiTargetTracker는 data_associator로 예측과 탐지를 짝짓고, 짝이 있으면 updater, 없으면 예측값으로 갱신한 뒤 deleter로 삭제하고 남은 탐지는 initiator로 새 표적을 만든다.

## 코드에 적용하는 법
각 부품을 액션 파일 하나로 두고 pipeline.py에서 위 순서로 호출한다. 알고리즘 교체(최근접 → JPDA 등)는 해당 액션만 바꾼다.

## 관련 카드
