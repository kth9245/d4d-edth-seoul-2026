# MAVLink·ArduPilot·PX4 보급 근거 조사 원문 (2026-10-09, 결정 0011 발표 문장용)

질문: "MAVLink를 변환 대상으로 고른 이유 = 오픈소스·소형 기체에서 많이 쓰인다"에 댈 출처.

## 확인된 원문 발췌
- ardupilot.org 첫 화면: "Installed in over 1,000,000 vehicles world-wide", "multi-copters, traditional helicopters, fixed wing aircraft" + Rover·Sub·AntennaTracker 펌웨어, "used for testing and development by large institutions and corporations such as NASA, Intel and Insitu/Boeing". https://ardupilot.org/
- ArduPilot Rover 보트 문서: "Boats can also be controlled with the standard Rover firmware." FRAME_CLASS=2(Boat). Loiter로 위치 유지. https://ardupilot.org/rover/docs/boat-configuration.html
- Koubâa et al., "Micro Air Vehicle Link (MAVLink) in a Nutshell: A Survey", IEEE Access 2019: "This protocol is used in major autopilot systems, mainly ArduPilot and PX4". https://arxiv.org/abs/1906.10641
- Dronecode Foundation 2024 Year in Review: "over 13,300 unique contributors and 1,900 new contributors in 2024 alone", 20 members, 5 projects(PX4·Pixhawk·MAVLink·MAVSDK·QGC), "59.72 million lines of code and an estimated $1 billion in project value". 기체 대수 통계는 없음. https://dronecode.org/the-2024-year-in-review/
- 404 Media 2025-06-03: 우크라이나 SBU "Operation Spider Web"이 "a nearly 20-year-old piece of open source drone autopilot software called ArduPilot"을 썼다. MAVLink 언급 없음. https://www.404media.co/ukraines-massive-drone-attack-was-powered-by-open-source-software/
- Skydio X10D 데이터시트·보도자료: "RAS-A compliance and open MAVLINK protocol enable the use of third-party and government-owned flight application software". 2024-12 Control and Telemetry ICD는 "MAVLink-based Robotics and Autonomous Systems – Air (RAS-A) protocol". https://pages.skydio.com/rs/784-TUF-591/images/X10D_Data-Sheet.pdf , https://skydio.com/blog/unlocking-skydio-x10d-control-and-telemetry-for-developers
- RAS-A MAVLink Control Link IOP Release 1.2 (2023-05-19, Distribution A): "for development of the Department of Defense (DOD) small unmanned aircraft systems (sUAS) Joint Reference Architecture", "built on top of the MAVLink industry standard", Joint Program Office 관리. 사본은 Skydio 지원 사이트 첨부. https://support.skydio.com/hc/article_attachments/28759364986907
- ModalAI Blue UAS Framework 페이지: VOXL 2 "PX4 or ArduPilot on the sensors DSP. Founding autopilot of Framework 2.0"(2022). 2025년 DCMA가 DIU에서 인계. https://www.modalai.com/pages/blue-uas-framework
- RAS-G(지상)은 SAE AS-4 JAUS 기반(검색 스니펫). 즉 미군 소형 공중은 MAVLink 계열, 지상은 JAUS 계열.

## 못 찾은 것
- MAVLink 자체의 시장 점유율·기체 대수. "de facto standard"라는 표현의 1차 출처 없음. 2019 설문 논문은 "major autopilot systems"까지만.
- PX4의 상용 채택 대수(Dronecode 지표는 기여자 수).
- DJI 등 폐쇄형은 MAVLink를 쓰지 않는다는 1차 출처(일반 상식, 확인 안 함).
