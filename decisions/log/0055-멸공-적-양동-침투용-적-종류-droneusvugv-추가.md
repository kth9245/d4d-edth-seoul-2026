---
id: 0055
title: 멸공 적 양동 침투용 적 종류 drone·usv·ugv 추가
status: 확정
decided_by: 황승주
date: 2026-10-10
modules: [contracts, sim, runtime]
supersedes: null
---
## 결정

TargetKind에 drone(자폭 드론), usv(적 수상정), ugv(적 지상로봇) 세 값을 더한다. 기존 값(boat, fast_boat, person, unknown)과 의미는 그대로. 멸공 작전 적 양동 침투(설계 docs/superpowers/specs/2026-10-10-24h-enemies-design.md)에 쓴다. 화면 라벨은 자폭 드론·적 수상정·적 지상로봇.

## 이유

사용자 10/10 지시: 멸공 적은 자폭 드론 1, UGV 2대를 실은 USV 1, 그 UGV 2로 4기. 아군 드론이 적이 공중·지상·해상 중 어디인지 판단해 USV는 해상, UGV는 지상 적만 추적하게 하려면 종류 구분이 필요하다.

## 버린 대안

모두 unknown으로 두고 시나리오 쪽 별도 표시로 구분: 계약은 그대로지만 화면·선택지 로직이 종류를 알 수 없어 어색하다.

## 영향
