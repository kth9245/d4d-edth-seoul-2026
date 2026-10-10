---
id: drone-detection-range-sources
title: 드론·센서 탐지 거리 공개 수치(4~8 km 주장은 미확인)
summary: DSIAC 원문 기준 소형 드론의 레이더 탐지는 1~3 km(모델 최대 2 km), RF·EO/IR은 거리 수치 없음이라 드론 탐지 4~8 km는 근거를 못 찾았다
tags: [sensor, range, evidence, drone]
modules: [sensing, sim]
confidence: 추정
sources: [https://dsiac.dtic.mil/articles/detection-and-classification-of-small-uas-for-threat-neutralization, https://www.navalnews.com/event-news/euronaval-2024/2024/11/exavision-unveils-seamos-lr-10k-naval-optronic-solution/, https://www.canada.ca/en/department-national-defence/maple-leaf/rcn/2019/02/advanced-unmanned-aircraft-to-provide-eye-in-the-sky-for-kingston-class-ships.html]
author: 최동호
---
## 결론
"드론의 일반적인 탐지 범위가 4~8 km"라는 말을 뒷받침하는 자료는 검색에서 찾지 못했다. 위협도의 3배 근접(6 km)은 센서 범위가 아니라 **접근 경계라는 설계 선택**으로 설명해야 한다. DSIAC는 원문을 직접 읽었고 Exavision·PUMA는 검색 요약만 읽었다.

## 근거
- 소형 UAS 탐지(DSIAC 원문): 주된 방식은 레이더이고 "1~3 km에서 탐지할 수 있다"(RF 출력과 RCS에 의존). 모델은 Ka대역 AESA 3D 레이더 10 W로 DJI Phantom 4(RCS 약 0.02 m²)를 최대 2 km로 예측한다. RF 탐지는 "가까운 거리 목적"의 별도 소규모 부류이고 거리 수치는 없다. EO/IR은 "분류에 가장 능숙"하다고만 쓰고 거리 수치는 없다. 이론 연구에 많이 의존한다.
- 선박급 표적의 해상 광학: 냉각형 MWIR로 소형 표적 식별 10 km, 비냉각 LWIR로 5 km라는 제조사 공개값이 있다. 다만 이는 함정·지상 설치형 광학 장비(Exavision)이고 소형 드론 탑재체가 아니며, 식별은 탐지보다 어렵다.
- 캐나다 PUMA의 20 km는 운용 반경이지 탐지 거리가 아니다.
- 한계: 소형 UAS 탑재체의 선박 탐지 거리 공개값은 드물다. 정확한 값은 제조사 데이터시트가 필요하다.

## 코드에 적용하는 법
시나리오 값은 가상이다: 드론 시각 센서 800 m, RF 2000 m, 수상정 500 m, 지상 로봇 300 m, 기준점 반경 2000 m, 근접 단계 3배(6 km). 발표에서 "일반 탐지 범위"를 근거로 말하지 않는다.

## 관련 카드
[[threat-evaluation-parameters]]
