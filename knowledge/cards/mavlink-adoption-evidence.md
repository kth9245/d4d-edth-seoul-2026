---
id: mavlink-adoption-evidence
title: MAVLink가 소형·오픈소스 기체의 공통 명령 체계라는 근거
summary: ArduPilot 100만 대+, PX4·MAVLink를 Dronecode가 관리, 미 국방부 sUAS 표준 RAS-A가 MAVLink 기반, 우크라이나 Spider Web이 ArduPilot 사용
tags: [mavlink, protocol, evidence, presentation]
modules: [play, demo]
confidence: 확인됨
sources: [https://ardupilot.org/, https://ardupilot.org/rover/docs/boat-configuration.html, https://arxiv.org/abs/1906.10641, https://dronecode.org/the-2024-year-in-review/, https://www.404media.co/ukraines-massive-drone-attack-was-powered-by-open-source-software/, https://pages.skydio.com/rs/784-TUF-591/images/X10D_Data-Sheet.pdf, https://support.skydio.com/hc/article_attachments/28759364986907, https://www.modalai.com/pages/blue-uas-framework]
author: 리드
---
## 결론
결정 0011의 "변환 대상을 MAVLink 하나로 잡은 이유"는 출처로 받칠 수 있다. 말할 수 있는 범위는 "오픈소스 오토파일럿(ArduPilot·PX4)을 쓰는 소형 공중·지상·해상 기체와 미 국방부 소형 무인기 표준(RAS-A)이 MAVLink를 쓴다"까지다. "대부분의 무인기가 MAVLink"는 출처가 없으므로 말하지 않는다.

## 근거
- ArduPilot: 공식 첫 화면 "Installed in over 1,000,000 vehicles world-wide". Copter·Plane·Rover·Sub 펌웨어. 보트는 Rover 펌웨어에서 FRAME_CLASS=2 → 공중·지상·해상이 같은 MAVLink 임무 명령.
- MAVLink: IEEE Access 2019 설문 "used in major autopilot systems, mainly ArduPilot and PX4". Dronecode Foundation(Linux Foundation)이 PX4·MAVLink·QGC를 관리, 2024년 기여자 13,300+.
- 군용 소형: 미 DoD sUAS Joint Reference Architecture의 RAS-A MAVLink Control Link IOP(Release 1.2, 2023-05)가 "built on top of the MAVLink industry standard". Skydio X10D(미 육군 SRR)가 "open MAVLINK protocol"로 정부 소프트웨어 연동. Blue UAS Framework의 VOXL 2는 PX4 또는 ArduPilot.
- 실전: 2025-06 우크라이나 Operation Spider Web이 ArduPilot 사용(404 Media).
- 한계: MAVLink 점유율·대수 통계는 없다. 미군 지상 로봇 표준 RAS-G는 JAUS 기반이라 지상은 MAVLink가 유일하지 않다. DJI 등 폐쇄형은 별도.

## 코드에 적용하는 법
발표·BUILT_HERE에 위 문장과 출처 3개(ardupilot.org, RAS-A IOP, Skydio 데이터시트)를 적는다. `compile_mavlink`(play, Part3-15)의 대응표는 ArduPilot Rover 보트 문서대로 해상도 Rover 명령을 쓴다.

## 관련 카드
