---
id: drone-detection-range-sources
title: 드론·센서 탐지 거리 공개 수치(4~8 km 주장은 미확인)
summary: 소형 드론을 레이더로 잡는 거리는 약 1~3 km이고 선박급 표적의 해상 광학 식별은 5~10 km(함정·지상 설치형)라서, 드론 탐지 4~8 km는 근거를 못 찾았다
tags: [sensor, range, evidence, drone]
modules: [sensing, sim]
confidence: 추정
sources: [https://dsiac.dtic.mil/articles/detection-and-classification-of-small-uas-for-threat-neutralization, https://www.navalnews.com/event-news/euronaval-2024/2024/11/exavision-unveils-seamos-lr-10k-naval-optronic-solution/, https://www.canada.ca/en/department-national-defence/maple-leaf/rcn/2019/02/advanced-unmanned-aircraft-to-provide-eye-in-the-sky-for-kingston-class-ships.html]
author: 최동호
---
## 결론
"드론의 일반적인 탐지 범위가 4~8 km"라는 말을 뒷받침하는 자료는 검색에서 찾지 못했다. 위협도의 3배 근접(6 km)은 센서 범위가 아니라 **접근 경계라는 설계 선택**으로 설명해야 한다. 검색 요약 기준이며 원문은 읽지 않았다.

## 근거
- 소형 UAS를 레이더로 탐지하는 거리: 컴팩트 AESA·3D 레이더로 약 1~3 km, 표적 RCS에 따라 다르다. RF 탐지와 카메라는 더 가까운 거리용이다(DSIAC).
- 선박급 표적의 해상 광학: 냉각형 MWIR로 소형 표적 식별 10 km, 비냉각 LWIR로 5 km라는 제조사 공개값이 있다. 다만 이는 함정·지상 설치형 광학 장비(Exavision)이고 소형 드론 탑재체가 아니며, 식별은 탐지보다 어렵다.
- 캐나다 PUMA의 20 km는 운용 반경이지 탐지 거리가 아니다.
- 한계: 소형 UAS 탑재체의 선박 탐지 거리 공개값은 드물다. 정확한 값은 제조사 데이터시트가 필요하다.

## 코드에 적용하는 법
시나리오 값은 가상이다: 드론 시각 센서 800 m, RF 2000 m, 수상정 500 m, 지상 로봇 300 m, 기준점 반경 2000 m, 근접 단계 3배(6 km). 발표에서 "일반 탐지 범위"를 근거로 말하지 않는다.

## 관련 카드
[[threat-evaluation-parameters]]
