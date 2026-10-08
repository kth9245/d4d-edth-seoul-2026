# 상용·산업용 노코드/로우코드 로봇·드론 행동(임무) 저작 도구 조사 — "이종 편대용 시각적 행동 저작 + 검증 + 역할 인계" 컨셉과 비교

> 조사일, 모든 URL 접근일: **2026-10-08**. 아래 "접근 2026-10-08" 표기도 같은 뜻이다.
> 평가 대상 컨셉(KDTH 2026 팀 아이디어): 임무 전에 계획자가 노코드 시각 편집기로 차량 행동을 만든다. 편집기는 스텝 카드를 엣지로 잇는 방식이고, 스텝마다 액션을 담는다(구역 수색, 순찰 경로, 표적 관측, 표적 접근, 통신 중계, 신호 송수신, IF 조건, 정지 조건이 있는 반복, 운용자 승인 게이트). 저장한 행동은 정적 검증과 서명을 거친다. 배정 시점에 도메인(드론/보트/지상로봇)별로 확장되고, 지상 인터프리터가 실행한다. 실행 중에는 도메인 간 역할 인계, 임무 중 계획 주입, 수동 개입, 모든 명령에 대한 런타임 안전 가드가 붙는다.
> 표기 규칙
> - 출처 등급: [1차]는 제조사 공식 문서·매뉴얼·보도자료, [언론]은 업계지·일반 언론, [2차]는 집계·리셀러·블로그·디렉터리, [마케팅]은 독립 검증이 없는 회사 자체 주장, [미검증]은 단일 2차 출처라 교차확인을 못한 것.
> - 따옴표 안 문장은 원문 발췌다. "(검색 스니펫)"은 검색엔진이 원문에서 뽑아 보여준 문장이라 페이지 전체를 열어 확인하지는 못했다는 뜻이다. "(페이지 확인)"은 페이지를 직접 열어 읽은 것이다.
> - 2024년 이전 정보에는 연도를 붙였다.
> - 국방용 C2(Anduril Lattice, Shield AI Hivemind 등)는 `2026-10-08-multi-uxv-research/products-market.md`에서 이미 다뤘다. 여기서는 상용·산업용 위주로 보고, 국방 제품은 대조용으로만 짧게 언급한다.

## 1. 이동로봇(AMR·사족보행) 플릿 임무 편집기: MiR, OTTO/Rockwell, Locus, Fetch, Boston Dynamics Orbit·Autowalk, ANYbotics (+대조: UR PolyScope, ABB Wizard, Techman TMflow)

### Takeaway
"스텝 리스트 + 컨테이너형 제어 블록(Loop/If/Try-Catch) + 운용자 질의(Prompt user)"를 브라우저에서 드래그로 조립하는 방식은 **MiR 미션 편집기**에 이미 성숙해 있다. 컨셉의 "IF 조건 / 반복 / 운용자 승인 게이트"와 구조가 가장 가깝다. 다만 MiR은 실내 AMR 단일 도메인이고, 저장된 미션의 정적 검증은 액션 파라미터 검증("Validate and close") 수준이다. OTTO·Locus는 "행동 저작"보다 작업(job) 자동 배정·교통 규칙에 무게를 둔다. Boston Dynamics는 Autowalk(경로 녹화 + 액션 평면 리스트)에서 Orbit의 원격 저작(Site View, 2025-2026)으로 옮겨 가는 중이다. 2026-10 Spot 5.2에서는 외부 센서·PLC가 Spot 점검을 트리거하는 API와 MCP 계층 "기반"을 발표했다.

### Cited Findings
**MiR (Mobile Industrial Robots, Teradyne 계열) — 미션 편집기**
- [1차] (2023-04, MiR100 User Guide v4.2) 기본 사용 방식: "The main way to use MiR100 is through missions that you create." (페이지 확인, PDF 텍스트 추출, 접근 2026-10-08) — [MiR100 User Guide 4.2 PDF](https://supportportal.mobile-industrial-robots.com/support-files/manuals/html/en/mir100_user_guide_4.2/content/_Resources/pdf/MiR100%20User%20Guide%204.2_en.pdf)
- [1차] 같은 문서의 **운용자 승인 게이트에 해당하는 액션**: "Prompt user actions are used for prompting the user with a question on how the robot should proceed." 파라미터는 Question, User group, Timeout(예시 10분)이다. 절차는 "In the Prompt user action, drag a Move to action under the Yes box and a Move to action under the No box."처럼 Yes/No 분기 박스에 다른 액션을 끌어 넣는다. 액션은 "In the Logic menu, select Prompt user."처럼 카테고리 메뉴에서 고르고, 파라미터를 설정한 뒤 "select Validate and close"로 닫는다. (페이지 확인) — [MiR100 User Guide 4.2 PDF §11.3](https://supportportal.mobile-industrial-robots.com/support-files/manuals/html/en/mir100_user_guide_4.2/content/_Resources/pdf/MiR100%20User%20Guide%204.2_en.pdf)
- [1차] 같은 문서의 **오류 처리 블록**: "Try/Catch actions are used to handle mission errors. When you use a Try/Catch action, you can define what the robot should do if, at any point, it fails to execute its main mission." 예시는 Try 박스에 미션 전체(Prompt user 미션)를 끌어 넣고 Catch 박스에 Play sound를 두는 구조로, 미션 중첩을 보여준다. (페이지 확인) — 같은 PDF §11.4
- [1차] 같은 문서의 **미션 변수(재사용 파라미터)**: 변수를 쓰면 미션을 쓸 때마다 값을 고르게 되고 "This allows you to reuse the same mission"이 된다. 예시는 Set footprint 액션의 Footprint를 변수로 만드는 것이다. (페이지 확인) — 같은 PDF §11.5
- [1차] Loop/If/Break/Continue 동작: "The robot can repeat a mission either a specified number of times or endlessly (until stopped by an operator). Drag actions or predefined missions into the loop action"; "If actions make it possible to check battery level, number of pending missions, PLC registers or input from I/O modules and then define which actions or missions should be performed if the conditions return either true or false."; "A Break action is used to interrupt a loop action."; "A Return action is used to abort a mission." (검색 스니펫. 출처는 아래 두 문서 중 하나로 보이며, 정확한 페이지 매핑은 확인 못함) — [MiR robot Reference guide rev1.9, 2019-03](https://cdn.kyklo.co/assets/W1siZiIsIjIwMTkvMTAvMTYvMTgvNTgvNTYvMGNkOTJiZGQtZGYzMS00OTVmLThlMGEtMWUwODhiNzQ1ODgwL01pUiUyMC0lMjBNaVIlMjByb2JvdCUyMHJlZmVyZW5jZSUyMGd1aWRlLnBkZiJdXQ?sha=9b51843b3f3b3c7f) / [MiR250 User Manual p.155 (manualslib)](https://www.manualslib.com/manual/1941073/Mir-Mir250.html?page=155)
- [1차] MiR Academy "Mission programming" 과정 목차의 액션 그룹은 "Battery, Error Handling, PLC, I/O module, Move, Logic, Sound/Light, and E-mail"이고, 주제는 "Try/Catch action, Nested missions, Mission troubleshooting, Resumable missions, Robustify a mission"이다. (검색 스니펫, 로그인 필요) — [MiR Academy](https://academy.mobile-industrial-robots.com/pathways/mission-programming) / [test-mir-academy](https://test-mir-academy.universal-robots.com/free-skill-paths/mission-programming/)
- [1차/오픈소스] InOrbit의 MiR 커넥터 PR은 MiR 미션 구조를 이렇게 설명한다: "Scope-bearing actions (loop, if, try_catch, ...) are containers rather than steps". MiR 미션이 평면 리스트가 아니라 **중첩 컨테이너 트리**라는 외부 증거다. (검색 스니펫) — [GitHub inorbit-robot-connectors PR #126](https://github.com/inorbit-ai/inorbit-robot-connectors/pull/126)
- [2차] (2024-11-25, MiR SW v3 기준) 통합사 블로그 예시: "start with a Move command followed by a Place Shelf command". 대시보드에는 "mission queue"와 미션 버튼을 배치한다. (페이지 확인) — [Neff Automation](https://neffautomation.com/blog/mir-amrs-positions-and-missions)
- [1차] MiR Fleet 레퍼런스 가이드가 따로 있다(SW 2.5.0, 2019-01 / rev 1.2, 2020-03). 내용은 이번 조사에서 열어보지 못했다. — [MiRFleet Reference guide 2019](https://iptech1.com/wp-content/uploads/2019/01/mirfleet_reference_guide_sw250_rev10.pdf) / [MiR Fleet reference guide 2020](https://www.hmi-mbs.fr/wp-content/uploads/2020/07/notice-mir_fleet_reference_guide_12_en.pdf)
- [1차] MiR와 UR 협동로봇을 동기화하는 URCap이 UR+에 있다(AMR과 로봇팔이라는 이종 장비 간 협조 사례). 상세는 미확인. — [UR+ MiR/UR synchronisation URCap](https://www.universal-robots.com/plus/products/universal-robots/mir-ur-synchronisation-urcap/)

**OTTO Motors / Clearpath (Rockwell Automation)**
- [1차] Rockwell은 2023-10-02에 Clearpath Robotics와 산업 부문 OTTO Motors 인수를 완료했다. — [BusinessWire 2023-10-02](https://www.businesswire.com/news/home/20231002758377/en/Rockwell-Automation-completes-acquisition-of-autonomous-robotics-leader-Clearpath-Robotics-and-its-industrial-offering-OTTO-Motors/)
- [1차·마케팅] OTTO Fleet Manager 브로셔: 작업(픽업·드롭·충전)을 실시간으로 최적 로봇에 배정하고, 기준은 "battery levels, minimized idle time, and maximized utilization"이다. 교통 규칙은 "speed limits and heavy pedestrian areas" 등이다. 연동은 "MES, ERP, and WMS through open APIs", "HTTPS REST and WebSocket, OPC-UA, and Ignition"이다. (검색 스니펫) — [OTTO Fleet Manager brochure (Rockwell)](https://www.rockwellautomation.com/content/dam/rockwell-automation/documents/pdf/events/automate/otto-fleet-manager-brochure.pdf)
- [1차] 소개 영상은 매핑, POI 태깅, "rules of the road"(일방통행·속도제한 구역), 자재 이동을 시작하는 workflow 정의 순으로 진행된다. (검색 스니펫) — [Intro to OTTO Fleet Manager](https://ottomotors.com/resources/videos/intro-to-otto-fleet-manager/)
- 이번 조사로는 OTTO의 "job template"이나 노코드 분기·루프 편집기를 확인하지 못했다(아래 Gaps).

**Locus Robotics / Fetch (Zebra)**
- [1차·마케팅] LocusONE(2023-03 발표): "seamless operation and management of large quantities of multiple AMR form factors as a single, coordinated fleet". Origin, Vector, Max AMR을 지원하고, "a thousand or more robots" 규모를 내세운다. (검색 스니펫) — [Locus Robotics news](https://locusrobotics.com/news/introducing-locus-one-warehouse-orchestration-platform) / [The Robot Report](https://www.therobotreport.com/locus-robotics-introduces-locusone-multi-bot-warehouse-management/)
- [언론] Zebra는 2021년에 Fetch Robotics를 2억 9천만 달러에 인수했다. 이후 로보틱스 자동화 사업을 "dispose or exit"하겠다고 공시했다. 보도에 따르면 FY2025 4분기 최대 8천만 달러의 일회성 비용이 예상된다. (검색 스니펫. 공시 시점을 2025-12로 본 요약이 있으나 1차 공시는 직접 확인 못함) — [Robotics 24/7](https://www.robotics247.com/article/zebra_technologies_announces_plan_to_dispose_or_exit_robotics_automation_business_unit) / [Automated Warehouse](https://www.automatedwarehouseonline.com/zebra-winds-down-mobile-robot-group-acquired-fetch/)

**Boston Dynamics — Autowalk(Spot)와 Orbit**
- [1차] Autowalk 편집 SDK 예제: "allowing you to drag and drop actions"; 실행 방식은 "the Autowalk mission can run once, periodically, or continuously"; 도킹 액션은 마지막이어야 한다("docking must be last"). Autowalk는 하위 behavior tree보다 편집하기 쉬운 평면 구조인 대신 "a flexibility loss compared to missions"가 있다. (검색 스니펫) — [Spot SDK: Edit Autowalk](https://dev.bostondynamics.com/python/examples/edit_autowalk/readme) / [Autowalk Service](https://dev.bostondynamics.com/docs/concepts/autonomy/autowalk_service) / [Record Autowalk](https://dev.bostondynamics.com/python/examples/record_autowalk/readme)
- [1차·마케팅] Orbit 제품 페이지 기능 목록: "Mission editing and scheduling", "Remote inspection authoring and editing", Site View로 "author new inspections—without ever stepping on site", "Automated in-product and email alerts", "Multi-site view", "APIs", "Webhooks", "Low-code work order generation (beta)". 지원 로봇은 "Spot, Stretch, and eventually Atlas"이다. 가격은 공개하지 않는다. (페이지 확인) — [Boston Dynamics Orbit](https://bostondynamics.com/products/orbit/)
- [언론] Orbit 스케줄링: "loop within a launch window, specific days and times or other designated timeframes"(주말 등 제외 가능). (검색 스니펫, 연도 미상) — [Robotics 24/7](https://robotics247.com/article/boston_dynamics_announces_orbit_robot_fleet_management_software_spot_enhancements)
- [언론] Orbit 5.0(2025-05)에서 Site View 원격 저작이 도입됐다. Orbit 5.1(2026-01-21)에서는 Spot Cam 사용자가 "author new inspection actions for PTZ, thermal, and gauge readings directly from the Site View window in Orbit"할 수 있게 됐고, "Staffers no longer need to walk around their facilities with Spot to record new inspection points." (검색 스니펫) — [The Robot Report: Orbit 5.0](https://www.therobotreport.com/orbit-5-0-adds-features-boston-dynamics-spot-quadruped-robot/) / [The Robot Report: Spot & Orbit 5.1](https://www.therobotreport.com/boston-dynamics-releases-spot-and-orbit-5-1-with-new-spot-cam/)
- [언론] (2026-10-01) Spot 5.2에서 Orbit API를 넓혀 PLC, 고정 센서, 보안 카메라 입력을 받는다. 이것이 AI 에이전트가 사전 정의된 업무 조건에서 Spot을 출동시키는 "the foundation for a new Model Context Protocol (MCP) layer"라고 설명한다. 예시는 고정 센서 알림이 오면 Spot이 해당 설비로 이동하는 것이다. MCP 계층이 이미 출시됐는지는 기사에 없다. 미션 저작 방식 변경과 다중 로봇 협조는 기사에 언급이 없다. (페이지 확인) — [Robotics & Automation News 2026-10-01](https://roboticsandautomationnews.com/2026/10/01/boston-dynamics-updates-spot-to-connect-autonomous-robot-inspections-with-enterprise-ai-systems/105384/)

**ANYbotics (ANYmal)**
- [1차] 사양서: "Inspection missions can be set up using the Mission Editor in the Operator GUI."; 배치 단계에서 내비게이션 웨이포인트가 생성되고, 점검점은 "a special navigation goal"로 정의된다. "Rule-based logic can be implemented to have the …"라는 문장은 스니펫에서 잘려 내용을 확인하지 못했다. (검색 스니펫) — [ANYmal technical specifications PDF](https://www.anybotics.com/anymal-technical-specifications.pdf)
- [언론] Data Navigator(2025-02-27 발표)는 점검 데이터 자산관리 플랫폼으로, "on-premise (local and air-gapped, no internet required) and cloud" 배치를 지원한다. 미션 편집 기능이라는 증거는 없다. (검색 스니펫) — [World Pipelines 2025-02-27](https://www.worldpipelines.com/equipment-and-safety/27022025/anybotics-launches-a-new-asset-management-platform-for-inspection-data/amp/) / [The Robot Report](https://www.therobotreport.com/anybotics-launches-data-navigator-unlock-value-inspection-data/)

**대조: 로봇팔 노코드 프로그래밍**
- [1차·마케팅] ABB Wizard Easy Programming(2020 출시, 2023-11에 OmniCore 6축 산업로봇으로 확대): "intuitive, block-based no-code programming for cobots and full range of six-axis industrial robots". 통합사용 커스텀 블록 도구 "Skill Creator"가 있다. Blockly 기반 여부는 확인하지 못했다. (검색 스니펫) — [ABB 보도자료](https://new.abb.com/news/de/detail/109841/prsrl-abb-extends-no-code-wizard-easy-programming-to-industrial-robots) / [Design World 2023-11](https://www.designworldonline.com/abb-extends-no-code-wizard-easy-programming-to-industrial-robots/)
- [1차] UR PolyScope X: Program Tree 기반 시각 프로그래밍이고, 10.12에서 "Logic Program (BETA only)"가 추가됐다. URCaps가 program node와 installation node를 확장한다. (검색 스니펫) — [UR PolyScope X](https://universal-robots.com/products/polyscope-x) / [PolyScope X URCap](https://www.universal-robots.com/developer/ur-cap/polyscope-x-urcap)
- [1차] Techman TMflow는 **노드를 선으로 잇는 플로차트형**이다: "Its graphical interface, powered by a series of function nodes … easy to master flow-based programming without any robotic experience." 설계 단계에서 노드 설정이 "translated into a bunch of scripts"(TMscript)로 프로젝트 파일에 기록되고 실행 단계에서 실행된다. 즉 시각 그래프를 스크립트로 컴파일한 뒤 실행하는 구조다. TMflow Simulator와 커스텀 노드(TMcraft, C#/WPF)를 제공한다. (검색 스니펫) — [Techman TMflow](https://www2.tm-robot.com/en/tmflow/) / [TM path planning tutorial](https://www.tm-robot.com/en/support/technical-document/start-using-path-planning-function-in-tmflow) / [Omron TMFlow 1.84 deck (2021)](https://assets.omron.com/m/3405a95b793db00/original/Omron-TMFlow-1-84-Presentation.pdf)

### Inferences
- 컨셉의 "스텝 카드 + IF + 반복(정지 조건) + 운용자 승인 게이트"는 MiR의 Logic(Prompt user, If, Loop/Break/Continue), Error handling(Try/Catch), 변수, 중첩 미션과 거의 대응한다. 심사위원이 "이건 산업용 AMR에 이미 있다"고 지적할 수 있으므로, 차별점은 편집기 문법이 아니라 **도메인 확장, 정적 검증·서명, 도메인 간 인계, 런타임 가드**에 둬야 한다.
- TMflow의 "시각 그래프 → 스크립트 컴파일 → 실행" 구조는 컨셉의 "저장 → 검증 → 도메인별 확장 → 인터프리터 실행" 파이프라인과 아키텍처가 비슷하다. 그래프를 중간 표현으로 컴파일한다는 설계를 설명할 때 선례로 쓸 수 있다.
- Boston Dynamics는 "현장 녹화(Autowalk)"에서 "원격 저작(Site View)"과 "외부 이벤트 트리거(5.2 API/MCP)"로 옮겨 가고 있다. 행동 저작이 사전 정의 그래프에서 이벤트 구동, 에이전트 구동으로 넘어가는 업계 흐름의 신호로 읽힌다(추정).
- 이번 조사 범위의 AMR 도구 가운데 저장된 미션 전체에 대한 정적 검증(도달성, 자원 제약, 금지구역)을 별도 기능으로 내세우는 사례는 찾지 못했다. MiR은 액션 단위 "Validate and close", Autowalk는 "docking must be last" 같은 개별 규칙 수준이다.

### Gaps
- MiR Fleet에서 미션을 여러 로봇에 배정하는 규칙(미션 그룹, 우선순위, 로봇 그룹)은 레퍼런스 가이드를 열지 못해 확인하지 못했다. 최신 MiR SW 3.x 편집기 UI도 확인하지 못했다.
- OTTO Fleet Manager의 workflow 정의 UI(분기, 조건 지원 여부)는 1차 문서를 확인하지 못했다.
- Fanuc의 노코드/아이콘 프로그래밍(Tablet TP 등)은 이번 조사에서 다루지 못했다.
- Orbit의 미션 편집이 분기·조건을 지원하는지, 다중 Spot 간 작업 분배가 있는지는 공개 자료로 확인하지 못했다.
- Orbit과 MiR 모두 라이선스 가격이 공개돼 있지 않다.

## 2. 로봇 플릿 운영 플랫폼의 워크플로·자동화: Formant, InOrbit, Freedom Robotics, Viam, Foxglove(대조), AWS RoboMaker

### Takeaway
이 범주는 **운영 이벤트(텔레메트리 이상, 인시던트)에 대한 트리거-액션 자동화**가 중심이고, 임무 행동 그래프를 저작하는 도구는 아니다. Formant는 텔레메트리 트리거, 사람 개입(human-in-the-loop), 외부 알림(Slack/PagerDuty/Jira) 워크플로를 내세운다. InOrbit은 인시던트 상태 정의와 대응(자동 또는 사람 입력 대기), 커스텀 액션을 제공한다. AWS RoboMaker는 2025-09-10에 서비스가 종료됐다. 컨셉과 겹치는 지점은 "승인 게이트형 대응"과 "멀티벤더 단일 뷰" 정도다.

### Cited Findings
**Formant**
- [1차·마케팅] (구 페이지, 연도 미상) "Workflows automate the repeatable processes needed to operate those fleets." 예시로 "human-in-the-loop responses to anomalies", "teleoperation queues for fleet operators", "automated monthly fleet summary emails"를 든다. 트리거는 "Trigger events based on telemetry data to power workflows", 외부 연동은 "Connect Formant to 3rd party applications such as Slack, PagerDuty, Jira"이다. (검색 스니펫) — [Formant Automation Workflows](https://formant.io/?p=75)
- [1차] 같은 URL은 현재 formant.ai로 리다이렉트된다. 현재 페이지(2026-10-07 게시)에는 워크플로 빌더 설명이 없어, 위 기능이 지금도 그대로인지는 확인하지 못했다. (페이지 확인) — [formant.ai/?p=75](https://formant.ai/?p=75)
- [언론] (2022-01) 예시 워크플로: "An automaker could create a workflow that deactivates a robotic arm if a potential hardware issue is detected." — [SiliconANGLE 2022-01-05](https://siliconangle.com/2022/01/05/robot-fleet-management-startup-formant-nabs-18m-investment/)
- [1차] Formant CLI README: "query telemetry, trigger AI-powered investigations, delegate tasks to AI personas, send remote commands … and automate workflows." (검색 스니펫) — [@formant/formant-cli README](https://cdn.jsdelivr.net/npm/@formant/formant-cli@1.1.17/README.md)
- [2차·미검증] 공개 가격은 없다. 디렉터리 추정치는 "$50 and $150/vehicle/month"이다. — [Software Finder](https://softwarefinder.com/fleet-management-software/formant)

**InOrbit**
- [1차·마케팅] 인시던트 기능: 로봇 상태 정의를 스크립트로 만들고, 상태마다 사전 정의된 대응을 연결한다. 대응은 자동으로 실행되거나 사람 입력을 기다린다. 원클릭 가이드 조치를 나중에 완전 자동 대응으로 바꿀 수 있다고 한다. (검색 요약이라 원문 문장은 확보하지 못함) — [InOrbit Advanced Incidents](https://inorbit.ai/advance-incidents) / [InOrbit Operations](https://www.inorbit.ai/operations)
- [1차·마케팅] 단일 뷰가 여러 벤더와 여러 사이트에 걸친 플릿을 덮고, 반복 작업, 즉석 디스패치, 일회성 요청을 한 플랫폼에서 돌린다고 한다. (검색 요약) — [InOrbit Product](https://www.inorbit.ai/product)
- [1차] Edge SDK: "Execute scripts (or any program) in response to Custom Action execution."(v1.16.2). 커스텀 액션은 InOrbit UI에서 정의한 `cmd` 문자열로 로봇 쪽 콜백을 호출한다. (검색 스니펫) — [PyPI inorbit-edge 1.16.2](https://pypi.org/project/inorbit-edge/1.16.2)
- [1차] 가격: 2021-09에 Free Edition을 출시했다("unlimited number of robots for free forever", 2021 기준). 현재 plans 페이지에서 teleoperation과 missions는 상위 유료 티어에만 있고, Standard는 로봇당 종량제다. (검색 스니펫) — [InOrbit plans](https://inorbit.ai/plans) / [InOrbit press 2021](https://inorbit.ai/press/free-edition-2021)
- [1차] Developer Portal에 Mission Tracking 튜토리얼이 있다(미션 진행 추적 기능). — [InOrbit Developer Portal](https://developer.inorbit.ai/tutorials)

**Freedom Robotics / Viam / AWS**
- [언론] Freedom Robotics: 2019-07 시드 660만 달러. 인수 보도는 찾지 못했고, 집계 사이트는 "alive"로 표시한다(최신성 불명). — [The Robot Report 2019](https://www.therobotreport.com/freedom-robotics-raises-seed-funding-robotic-fleet-controls/) / [CB Insights](https://www.cbinsights.com/company/freedom-robotics)
- [1차] Viam: 2025년 블로그에 "fragments"(대규모 배치용 재사용 설정)와 2025-09-15 "Build a custom dashboard for your fleet operators"가 있다. 트리거 기반 노코드 행동 저작 기능은 찾지 못했다. (검색 스니펫) — [Viam blog](https://www.viam.com/blog/all)
- [1차] AWS RoboMaker: "End of support notice: On September 10, 2025, AWS will discontinue support for AWS RoboMaker." 시뮬레이션과 WorldForge도 함께 종료됐고, AWS는 AWS Batch로 이전을 권고했다. (검색 스니펫) — [AWS RoboMaker docs](https://docs.aws.amazon.com/robomaker/latest/dg/using-service-linked-roles.html)

### Inferences
- 플릿 운영 플랫폼의 "워크플로"는 **운영 사건 처리용 트리거-액션**이다. 컨셉의 "임무 행동 그래프"와는 층위가 다르다. 컨셉 데모에서는 "우리는 임무 자체의 행동을 저작한다"로 구분해 설명할 수 있다.
- InOrbit의 "자동 대응 ↔ 사람 입력 대기" 이중 모드와 Formant의 "human-in-the-loop responses"는 컨셉의 운용자 승인 게이트와 UX상 선례다.
- AWS RoboMaker 종료(2025-09)는 클라우드 의존 로봇 플랫폼의 지속성 리스크를 보여준다. 오프라인 시연 정책(POLICY 1)을 정당화하는 보조 근거로 쓸 수 있다(추정).

### Gaps
- Foxglove는 이번 조사에서 1차 출처를 확보하지 못했다. 관측·시각화(로그·MCAP) 도구로 알려져 있으나 미확인이다(confidence: 추정).
- AWS IoT(Greengrass, FleetWise 등)의 로봇 플릿 워크플로 현황은 다루지 못했다.
- Formant 현행(2026) 워크플로 빌더가 시각적·노코드인지 확인하지 못했다.
- InOrbit "Actions" 정의 화면과 승인(confirmation) 옵션의 1차 문서를 확보하지 못했다.

## 3. 드론 자동화·드론인어박스(DiaB): FlytBase, DJI FlightHub 2·Dock, Skydio, Percepto, Nokia, Ondas, Asylon, Sunflower Labs, DroneDeploy, UgCS, Auterion, QGC/Mission Planner(대조), Hammer Missions, Dronelink

### Takeaway
드론 쪽에서 컨셉과 가장 가까운 상용 도구는 **FlytBase Aeroflo**다. 트리거 + 액션 체인을 캔버스에서 조립하고, 이벤트/게이트웨이/액션 노드를 쓰며, 실행 전 **노드 단위 드라이런 시뮬레이션**과 실행 로그를 제공한다. 같은 회사의 Flows는 알람 대응을 Manual(운용자 선택)과 Automated로 고르게 한다. 컨셉의 운용자 승인 게이트와 대응된다. **역할 인계**에 가장 가까운 상용 기능은 DJI FlightHub 2의 Dock 3 "자동 교대(swap)·릴레이 관측"이다(2025). 다만 같은 기종 드론 2대 사이의 인계일 뿐 도메인 간 인계는 아니다. 다기체 동시 운용(UgCS Commander, Skydio Remote Ops)과 비행 전 안전 점검(Auterion MC의 지오펜스·지형 충돌, UgCS의 비행금지구역 우회)은 있다. 하지만 **이종 도메인을 아우르는 행동 그래프 저작과 정적 검증·서명**은 이 범주에서 찾지 못했다.

### Cited Findings
**FlytBase (Flinks / Flows / Aeroflo)**
- [1차] Flows 문서: 대응 유형은 "Go to alarm location"과 "Perform mission: Carries out a specific pre-existing mission at the alarm's location."이다. 대응 모드는 "Manual: The Dashboard prompts you to select an action in response to the alarm when it is triggered. Automated: The drone automatically executes the selected action without operator intervention."이다. 범위 규칙은 "You can link multiple Alarm sources to a single Flow … while each Alarm source can only be linked to one Flow."이고, 사이트 선택으로 응답할 장비를 거른다. 로그 탭은 "records the trigger time and status of each flow." (검색 스니펫) — [FlytBase docs: Flows](https://docs.flytbase.com/en/flinks-and-flows/flows) / [Flows alarms](https://docs.flytbase.com/en/flinks-and-flows/flows/flows-alarms)
- [1차] Automations 문서의 제약: "Since only alarms can currently have automated workflows, select Alarms as the Category." Flinks 문서에는 "Currently, only Alarm Custom Flink is available on the FlytBase dashboard."라고 돼 있다. 문서마다 시점이 달라 현행 여부는 불명확하다. (검색 스니펫) — [FlytBase Automations](https://docs.flytbase.com/flinks-and-automation/automations) / [Flinks](https://docs.flytbase.com/flinks-and-automation/flinks)
- [1차] 외부 알람은 alarm source별 "Trigger URL (and an authorization token)"으로 JSON을 POST해 들어온다. (검색 스니펫) — [Flows alarms](https://docs.flytbase.com/flinks-and-flows/flows/flows-alarms)
- [1차·마케팅] Aeroflo 제품 페이지(페이지 확인, 접근 시 한국어 로캘로 표시됨): 트리거는 cron, 일출·일몰 스케줄, 비행 이벤트(mission start, waypoint reached, battery drop, RTH, abort), 도크 센서(rainfall, wind, temperature), alarm sources, inbound webhooks, manual button이다. 액션은 카메라 페이로드(wide/zoom/thermal), 짐벌, 스포트라이트, 보고서 생성, 게스트 공유 링크, HTTP·웹훅·"custom JavaScript"이다. 캔버스 이미지 alt 텍스트는 "이벤트, 게이트웨이 및 액션 노드"이고, 실행 이력은 "모든 실행 과정은 추적됩니다", 지속성은 "서버 재시작 후에도 유지됩니다", 템플릿은 "한 번의 클릭으로 복제할 수 있습니다"이다. 승인 단계는 페이지에 언급이 없다. — [FlytBase Aeroflo](https://flytbase.com/flex/aero-flow-control)
- [1차·마케팅] Aeroflo 시뮬레이션 영문 원문: "Before a flow goes live, the simulation engine walks every node, validates inputs, and produces realistic outputs without sending a single drone command." (검색 스니펫) — [FlytBase Aeroflo](https://flytbase.com/flex/aero-flow-control)
- [1차] Aeroflo는 Flex Factory 구성요소이고, 쓰려면 FlytBase 계정과 Flex Factory 구독, 호환 드론이 필요하다. 출시일은 찾지 못했다. (검색 스니펫) — [FlytBase docs: Aeroflo](https://docs.flytbase.com/flex-factory/aeroflo)
- [언론·리셀러] 가격: Pro는 2025-04 출시, "$99/month … with no limit on the number of docks or users in an organization"이다. Zero는 $0 종량제다. Enterprise는 "billed per dock on yearly basis"이고 리셀러가 올린 DJI Dock 3 Enterprise 1년 가격은 $4,499이다. — [sUAS News 2025-04](https://www.suasnews.com/2025/04/flytbase-launches-pro-plan-to-scale-remotedrone-operations-for-99-month/) / [FlytBase pricing](https://flytbase.com/pricing) / [Dronefly 리셀러](https://www.dronefly.com/products/flytbase-enterprise-base-package-for-dji-dock-3-m4d-m4td-1-year)

**DJI FlightHub 2 + Dock 2/3**
- [1차] (블로그 2025-05-07, FlightHub 2 V13.1) 자동 교대: "Automatic Swap Task"(Dock 3 전용). 릴레이: "automated scheduling" 덕분에 Dock 3 드론 2대가 "seamlessly perform uninterrupted relay observation" of designated targets한다. 가상 조종석은 "view tasks from the route library"에서 비행 중인 기체에 웨이포인트·영역 경로를 보낸다(Dock 3, Dock 2, Matrice 4). Grid Deployment는 여러 도크가 표적 근처에 있으면 "flexibly dispatch the most suitable device"한다. 영역 경로에는 "custom restricted zones bypass function"이 있다. 알람·AI 트리거 임무는 이 글에 없다. (페이지 확인) — [DJI Enterprise Insights](https://enterprise-insights.dji.com/blog/new-update-flighthub2-april)
- [2차·리셀러] Task Area Management는 비행 구역, 제한 구역, 장애물 데이터를 정의하고, 도크 기체가 FlyTo와 귀환 경로를 스스로 고르게 한다. FlightHub Sync는 "Launch on-demand flight missions from external systems"하고, Dock 2와 함께 "dispatch tasks across multiple docks simultaneously"한다. 온프레미스 버전은 중국 본토 한정이라는 언급이 있다(날짜 미상). (검색 스니펫) — [Heliguy 2025-04-15](https://www.heliguy.com/blogs/posts/dji-flighthub2-update-15-4-25/) / [Advexure](https://advexure.com/products/dji-flighthub-2) / [Drone Parts Center](https://drone-parts-center.com/en/product/dji-flighthub-2-on-premises/)

**Skydio (Dock, Remote Ops)**
- [1차·마케팅] "Drones deploy on a schedule or from alarm triggers"; 알람에서 이륙까지 "airborne in under 20 seconds"; 여러 도크를 "Dock Hive"로 네트워크화; "Organizations already running Genetec or Milestone VMS can stream drone video directly into their existing interface." VMS 이벤트가 출동을 트리거하는지는 명시돼 있지 않다. (검색 스니펫) — [Skydio site security FAQ](https://www.skydio.com/solutions/site-security/faq)
- [1차·마케팅] Remote Ops: "pilot multiple drones from one Remote Ops command center"; "Hand activated or Dock launched. One drone or many at once."; "Seamlessly pass off control between pilots"(운용자 간 통제권 인계). 데이터시트는 국방용 X10D 기준이다. (검색 스니펫, 2025 저작권 표기) — [Remote Ops for Defense datasheet](https://www.skydio.com/resources/datasheets/remote-ops-for-defense)

**Percepto, Nokia, Ondas, Asylon, Sunflower Labs (DiaB·보안)**
- [2차·마케팅] Percepto AIM은 "orchestrates drones, robots, and visual sensors"이고, 데이터 요청이 오면 "deploy the most suitable robot to retrieve and stream that data—without involving a human"한다. 2020년부터 Boston Dynamics Spot을 통합했다. Series C 5천만 달러(2023-06), 누적 1억 2,250만 달러라는 집계가 있다. (검색 스니펫) — [SoftwareOne listing](https://platform.softwareone.com/product/percepto-aim/PCP-7685-4992) / [Inside Unmanned Systems](https://insideunmannedsystems.com/percepto-launches-aim-platform-for-autonomous-industrial-inspections/) / [Commercial UAV News 2022](https://commercialuavnews.com/surveying/percepto-s-aim-2022-update-brings-a-new-drone-and-advanced-ai-powered-analytics-to-the-table)
- [1차] Nokia Drone Networks(2023-05)는 CE 인증 5G DiaB로, "programmed to manage autonomous scheduled flights"하고 "Open API framework"를 갖췄다. 다중 도크 협조는 확인하지 못했다. — [Nokia newsroom 2023-05-02](https://www.nokia.com/newsroom/nokia-unveils-first-ce-certified-5g-automated-drone-in-a-box-solution-for-secure-reliable-public-sector-and-industrial-operations/)
- [1차·마케팅] Ondas Optimus: "11 onboard batteries and up to nine mission payloads … real-time mission switching". UAE 주문(2025-04, 320만 달러)은 기지당 드론 1대 구성이다. Kestrel DAA를 통합했고 DCMA Blue List에 올랐다. — [Ondas IR (UAE 주문)](https://ir.ondas.com/press-releases/detail/200/ondas-secures-3-2-million-order-to-expand-the-optimus) / [Inside Unmanned Systems: Blue List](https://insideunmannedsystems.com/ondas-optimus-drone-gains-dcma-blue-list-status/)
- [1차·마케팅] Asylon Guardian(2024-09)은 DroneIQ 소프트웨어로 "seamless integration with ground solutions like DroneDog and existing VMS and alarm systems"를 제공한다. 공중 + 지상(로봇견)을 결합한 보안 상품이다. RaaS로 판매하고, 이전 세대 DroneCore는 "more than 45,000 missions"를 수행했다. — [sUAS News 2024-09](https://www.suasnews.com/2024/09/asylon-unveils-guardian-a-revolutionary-automated-aerial-security-drone-solution/) / [Asylon](https://asylonrobotics.com/guardian-security-drone-release/)
- [1차·언론] Sunflower Labs(2025-11): FAA BVLOS 승인 범위가 미국 약 99%로 넓어졌고, Sequoia 주도로 1,600만 달러를 유치했다. 지상 센서 조명이 사람·동물·차량을 분류하고, 의미 있는 사건에만 출동한다. — [Sunflower Labs press 2025-11-04](https://sunflower-labs.com/post/press-release-2025-11-04) / [Pulse 2.0](https://pulse2.com/sunflower-labs-16-million-series-b-raised-to-advance-autonomous-security-drones)

**DroneDeploy (Rocos 인수 → 공중 + 지상 통합)**
- [언론] (2021-08) Rocos 인수로 "deploy and orchestrate both aerial and ground robots on their job sites"를 내세웠다. 예시 시나리오: "program a drone to fly over a solar power plant, identify thermal hotspots, and automatically activate ground robots to walk under the hotspot … no human intervention needed." 이는 **공중 → 지상 크로스도메인 트리거**의 상용 비전이다(2021, 구현 여부는 미확인). — [DroneDJ 2021-08-10](https://dronedj.com/2021/08/10/dronedeploy-acquires-robotics-software-company-rocos/) / [The Drone Girl 2021-08-11](https://www.thedronegirl.com/2021/08/11/rocos-dronedeploy/)
- [1차·마케팅] 현행 DroneDeploy Robotics: "docked drones and ground robots, including Boston Dynamics Spot and Unitree Go2-W"; "Missions can be daily, weekly or triggered on demand"; "almost any ROS or Mavlink-based models"; Dock Automation은 엔터프라이즈 애드온이다. (검색 스니펫) — [DroneDeploy Robotics](https://www.dronedeploy.com/product/robotics) / [Dock Automation help](https://help.dronedeploy.com/hc/en-us/articles/30951051530135)

**다기체 계획·비행 전 안전 점검: UgCS, Auterion, QGC/ArduPilot**
- [1차·마케팅] UgCS Commander: "manage multiple UAVs on automated missions simultaneously"; "Assign missions per drone, launch in sequence or parallel, and watch real-time telemetry for all vehicles from a single screen"; "Receive alerts if drones come too close to each other"; DJI와 PX4/ArduPilot을 한 세션에서 혼합 운용한다. 자동 과업 할당·최적화는 언급이 없다. (검색 스니펫) — [SPH Engineering UgCS Commander](https://www.sphengineering.com/flight-planning/ugcs-commander) / [One operator multiple drones](https://www.sphengineering.com/news/one-operator-multiple-drones-multi-uav-ops-with-ugcs-commander)
- [1차] UgCS 비행금지구역: "UgCS will automatically calculate flight path around these areas and make sure that the drone does not enter NFZ while on an automated flight." OPEN 라이선스는 첫 웨이포인트에서 500 m, 120 m AGL로 제한된다. (검색 스니펫, 매뉴얼 v4.17) — [UgCS manual FAQ](https://manuals-ugcs.sphengineering.com/docs/faq)
- [1차·마케팅] Auterion Mission Control의 안전 기능: "Geofence", 안전 착륙용 "Rally points", "Automatic pre-flight checks", "Terrain collision checks", "VTOL flight path prediction". 임무 유형은 survey, corridor, structure scan, waypoint다. 다기체 동시 계획은 현 페이지에 명시돼 있지 않다(2020 자료에는 "multiple drones, using one app"). (페이지 확인) — [Auterion Mission Control](https://auterion.com/product/mission-control/) / [UST 2020-09](https://www.unmannedsystemstechnology.com/2020/09/auterion-enables-large-scale-operations-for-enterprise-drone-fleets/)
- [언론·대조(국방)] Auterion Nemyx(2025-09 출시)는 다제조사 스웜 엔진이다. 2026-01 실사격 시험에서 운용자 1명이 표적 3개를 동시 지정했다. "If one drone is lost, another automatically reassumes its target" — 국방 타격용이며, 컨셉의 역할 인계와 개념상 유사하다. — [Auterion Nemyx](https://auterion.com/auterion-launches-nemyx-enabling-fully-coordinated-drone-swarms/) / [Interesting Engineering](https://interestingengineering.com/military/pentagon-operator-three-targets-drone-swarm)
- [1차] QGroundControl Plan view 패턴(Survey, Corridor Scan, Structure Scan)은 "The available pattern tools depend on the vehicle". QGC는 여러 기체를 동시에 연결해 감시할 수 있지만, 다기체 공동 계획 기능은 확인하지 못했다. — [QGC Plan view patterns](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/plan_view/pattern.html) / [QGC README](https://cdn.jsdelivr.net/gh/mavlink/qgroundcontrol@master/README.md)
- [1차] ArduPilot/Mission Planner 미션 명령(대조): DO_JUMP는 "WP # is the mission command to jump to. Repeat is the maximum number of times"(-1이면 무조건 반복)이다. 조건 명령은 "Conditional commands control the execution of _DO_ commands"이고, 조건을 다음 웨이포인트까지 충족하지 못하면 "any unexecuted _DO_ commands … will be skipped." 즉 평면 명령 리스트 + 점프·게이트 수준의 제어흐름이다. — [ArduPilot Mission Commands](https://ardupilot.org/copter/docs/common-mavlink-mission-command-messages-mav_cmd.html)

**단일 드론 미션 저작 앱: Hammer Missions, Dronelink**
- [2차·마케팅] Hammer Missions(DJI 전용): "link 2 or more types of missions together", 다중 배터리 재개, "run the 3D flight simulator to validate the mission", "connectionless mode". 다기체 기능은 없다. — [Apple App Store](https://apps.apple.com/gb/app/hammer-missions/id1458728185) / [SourceForge](https://sourceforge.net/software/product/Hammer-Missions/) / [Hammer Notion docs](https://hammer-missions.notion.site/Mission-Planning-Additional-Tools-2693245c164580a6adfef4a714bee51e)
- [1차] Dronelink: 컴포넌트(waypoints, orbits, maps, 360s)를 순서 리스트로 결합하고, "the run order moves from the top and move down the list". "Mission Preview tool"로 사전 확인하고, Marker로 지점별 추가 명령을 단다. — [Dronelink support: multi component](https://support.dronelink.com/hc/en-us/articles/1500006098222-Breaking-Down-a-Multi-Component-Waypoint-Mission) / [Link missions](https://support.dronelink.com/hc/en-us/articles/16872550077075)
- [1차] Dronelink 스크립팅: "Dronelink's function architecture brings drone programming to the modern web with javascript syntax". 코드 변경을 미션 프리뷰어로 확인한다. 커널은 npm `dronelink-kernel`로 배포된다. 계획 하나를 여러 기종에 재사용할 수 있지만 기종에 따라 일부 명령이 동작하지 않는다(커뮤니티 답변). 여러 기체 동시 비행은 확인하지 못했다. (검색 스니펫) — [Dronelink business](https://www.dronelink.com/business) / [npm dronelink-kernel](https://www.npmjs.org/package/dronelink-kernel) / [DJI ecosystem](https://enterprise.dji.com/ecosystem/dronelink)

### Inferences
- FlytBase Aeroflo의 "이벤트·게이트웨이·액션 노드 캔버스 + 드라이런 시뮬레이션 + 실행 로그 + JavaScript 탈출구"는 컨셉의 편집기 UX와 검증 단계에 가장 가까운 드론 상용 선례다. 다만 (a) 드론(DJI Dock 중심) 단일 도메인이고, (b) 공개 자료상 **분기·반복·승인 노드**가 확인되지 않으며(게이트웨이 기능 설명 없음), (c) 시뮬레이션은 입력 검증과 출력 모사이지 공간·자원 제약의 정적 검증으로 보이지 않는다(추정).
- DJI Dock 3 swap/relay는 "같은 임무 역할을 다른 기체가 이어받는" 상용 구현이다. 컨셉의 역할 인계를 "드론 → 보트 → 지상"의 **이종 간**으로 넓히면 차별점이 분명해진다.
- DroneDeploy가 2021년에 내건 "드론 열점 탐지 → 지상로봇 자동 출동" 시나리오는 컨셉의 크로스도메인 트리거와 같은 방향이다. 하지만 현행 제품 페이지는 스케줄·온디맨드 수준만 보여준다. 시장 비전은 있었으나 사용자가 저작 가능한 형태로는 노출되지 않은 것으로 보인다(추정).
- 비행 전 안전 점검(지오펜스, 지형 충돌, NFZ 우회, 제한구역 우회)은 계획 단계 검증으로 업계 표준이다. 컨셉의 "모든 명령에 대한 런타임 가드"는 이를 실행 중 명령 단위로 옮긴 것이므로, 데모에서 "계획 시점 검사 vs 실행 시점 가드"를 구분해 보여주는 것이 설득력이 있다.

### Gaps
- Aeroflo의 게이트웨이 노드 의미(조건 분기·병렬·대기·승인 여부)와 출시일은 문서 페이지가 HTTP 429로 막혀 확인하지 못했다.
- DJI FlightHub 2의 알람·외부 이벤트 트리거 임무(FlightHub Sync 상세)와 가격은 1차 출처로 확인하지 못했다.
- Skydio Remote Ops에서 VMS/알람 이벤트가 도크 출동을 자동 트리거하는 통합 방식(API, 웹훅)은 공개 자료가 없다.
- Percepto AIM의 2025-2026 현행 기능, 다중 드론 협조 방식은 확인하지 못했다.
- 어떤 드론 도구도 저작한 임무·플로의 **암호학적 서명**을 언급하지 않았다(검색 범위 내 부재이지, 없다는 증명은 아님).

## 4. 블록·시각 프로그래밍(교육·범용·산업): DroneBlocks, DJI Tello EDU·RoboMaster, Robolink CoDrone, Parrot, LEGO/VEX(대조), Node-RED(MAVLink/ROS), Blockly 계열 산업 UI, Groot2

### Takeaway
드론 블록 코딩은 교육 시장(DroneBlocks, CoDrone EDU, RoboMaster TT)에 집중돼 있다. 대부분 Blockly/Scratch 계열이고 단일 기체 비행 시퀀스용이다. DJI는 2024년 STEAM 교육 사업을 축소했다. 범용 플로 도구인 Node-RED에는 MAVLink 노드(미션 업로드, 파라미터, "formation control")가 커뮤니티 패키지로 있다. 산업용 로봇팔 쪽은 ABB Wizard(블록), Techman TMflow(노드 플로)가 노코드를 상용화했다. 로봇 행동을 behavior tree로 저작·디버깅하는 **Groot2 PRO**(유료, €590/년)는 브레이크포인트·폴트 인젝션·런타임 노드 치환까지 제공한다. "검증 가능한 행동 그래프" 관점에서 기술적으로 가장 성숙한 상용 편집기다.

### Cited Findings
- [1차·마케팅] DroneBlocks: Block Coding App은 Tello, Tello EDU, RoboMaster TT용 드래그앤드롭이다. 상위 단계 DroneBlocks Code는 JavaScript를 쓰고, 시뮬레이터에서 먼저 시험한다. 수업 수는 "250 cloud-based lessons" 이상이고, 기관 라이선스는 학생 수 무제한이다. 2015년 DJI SDK + 블록 프로그래밍 PoC에서 출발했다. (검색 스니펫) — [DroneBlocks apps](https://droneblocks.io/apps) / [DroneBlocks Learn](https://learn.droneblocks.io/)
- [1차] (2024-01) DroneBlocks 공지에 따르면 DJI가 STEAM 교육 부문에서 손을 떼고 Tello 판매를 중단했다. 커리큘럼 페이지는 Tello 계열을 단종으로 표시한다. (검색 스니펫) — [DroneBlocks Tello curriculum](https://droneblocks.io/?p=180) / [DroneBlocks](https://droneblocks.io/?p=1533)
- [1차] DJI Tello EDU에서는 "Scratch, Python and Swift"를 학습한다. RoboMaster TT는 다기체 제어를 지원한다고 DJI가 밝혔다. RoboMaster EP(지상 로버)와 TT(드론) 모두 Scratch 계열 블록을 쓴다. (검색 스니펫) — [DJI STEAM Education](https://www.dji.com/no/products/steam) / [Digital Camera World](https://www.digitalcameraworld.com/au/news/dji-launches-powerful-robomaster-tello-talent-drone-for-classroom-coders)
- [1차·리셀러] Robolink CoDrone EDU는 Blockly와 Python을 지원하고, 단일 키트 가격은 $249(Stemfinity)다. 구 레슨 아카이브는 2026-06까지만 유지한다고 공지했다. (검색 스니펫) — [Robolink CoDrone EDU](https://robolink.com/products/codrone-edu-set-of-10-kits) / [Stemfinity](https://stemfinity.com/collections/in-school-learning/products/codrone-edu) / [Robolink archive](https://archive.learn.robolink.com/product/codrone-edu/)
- [2차] Parrot: AR.Drone 2.0과 미니드론의 Scratch 계열 프로그래밍 자료는 2017년 이전 것만 찾았다. 현행 Parrot 교육용 블록 코딩 제품은 확인하지 못했다. — [Uni Potsdam ScratchDrone flyer](https://www.uni-potsdam.de/fileadmin01/projects/multimedia/docs/scratchdrohne/ScratchDrone-Flyer_v3.pdf) / [INSHEA 2017](https://bepep.inshea.fr/mod/resource/view.php?id=654)
- [1차·커뮤니티] Node-RED `@cmc0619/node-red-contrib-mavlink` 0.5.0은 GCS와 컴패니언 컴퓨터 역할 노드, UDP/TCP/serial, 미션 업로드·다운로드, 파라미터 읽기·쓰기, formation control을 제공하고 Node-RED 4.0 이상이 필요하다. 예제 플로 23개와 SITL용 41개가 있다. `node-red-contrib-ros`(rosbridge)는 약 3년 전이 마지막 배포다. (검색 스니펫) — [flows.nodered.org: mavlink](https://flows.nodered.org/node/@cmc0619/node-red-contrib-mavlink) / [node-red-contrib-mf-mavlink](https://flows.nodered.org/node/node-red-contrib-mf-mavlink)
- [1차] Groot2(BehaviorTree.CPP 4.x용) Free는 €0이고 편집기 전체를 제공하지만 Monitor·Log Visualizer는 "20 nodes"로 제한된다. PRO는 "€590/year, floating license"이고 "Interactive Breakpoints", "Fault Injection", "Substitute any Nodes with dummy ones, at run-time", "Blackboard Visualization"을 추가한다. (페이지 확인) — [behaviortree.dev/groot](https://www.behaviortree.dev/groot/) / [Nav2 Groot2 tutorial](https://docs.nav2.org/tutorials/docs/groot2.html)
- [1차·마케팅] 산업용: ABB Wizard(블록 기반, Skill Creator)와 Techman TMflow(노드 플로 → TMscript)는 §1 Cited Findings를 참조한다.

### Inferences
- 교육용 블록 코딩은 "단일 기체 + 순차 명령 + 간단한 반복"에 머문다. 이종 편대, 승인 게이트, 검증 개념이 없어 컨셉의 경쟁자라기보다 "누구나 쓸 수 있다"는 UX 설득 근거로 쓰는 편이 맞다.
- Groot2 PRO의 폴트 인젝션과 런타임 노드 치환은 컨셉의 "런타임 안전 가드·수동 개입·계획 주입"을 개발자용으로 구현한 선례다. 컨셉이 behavior tree 대신 스텝 카드 그래프를 쓰는 이유(계획자 대상 노코드)를 설명할 때 대비 대상으로 쓸 수 있다.
- Node-RED + MAVLink 노드로는 "시각 플로 → 드론 명령"을 빠르게 만들 수 있다. 하지만 정적 검증, 도메인 확장, 서명 개념은 없다. 해커톤 대안 구현 경로로 참고할 만하다(추정. 단 POLICY상 오프라인 동작이 필요하므로 Node-RED 로컬 실행 가능 여부는 별도 확인이 필요하다).

### Gaps
- LEGO(SPIKE)와 VEX(VEXcode) 블록 코딩은 이번 조사에서 출처를 확보하지 못했다(대조용, 우선순위 낮음).
- 산업 현장 로봇 UI 중 Blockly를 직접 쓰는 사례(ABB Wizard의 Blockly 기반 여부 포함)는 확인하지 못했다.
- Groot2의 기업 도입 규모와 사용자 수는 공개 자료가 없다.

## 5. 민간 분야 다중 도메인·이종 플릿 오케스트레이션: 해양 USV(Sea Machines, Saildrone, XOCEAN, SeeByte Neptune), 광산·농업, 산업 점검(Korial/구 Energy Robotics, Yokogawa, Cognite, Percepto, DroneDeploy), Unmanned Life, "1인 다수 로봇" 주장

### Takeaway
민간 이종 오케스트레이션의 최선두 사례는 **SeeByte Neptune**(해양)이다. 기체 능력에 따라 "goal-based" 계획을 배정하고, 행동 어휘가 "surveying an area, investigating a target, or loitering"이며, 고장 시 **자동 과업 인계**, 통신 두절 시 분산 자율, 미션 리허설과 시뮬레이터를 갖췄다. 컨셉의 행동 어휘(구역 수색, 표적 관측, 체공·순찰)와 인계 개념이 거의 그대로 겹친다. 다만 지원 기체는 UUV/USV 중심이고, 저작 방식은 SeeTrack 플러그인 기반 계획 UI다. 노코드 스텝 그래프 편집기라는 증거는 찾지 못했다. 육상 산업 점검(Korial, Yokogawa, Percepto, DroneDeploy)은 "로봇 + 드론 혼합 플릿 하나의 플랫폼"을 판매한다. 하지만 공개 자료상 저작은 점검 경로·스케줄 중심이고, 크로스도메인 역할 인계는 없다. "1인 다수" 주장은 광산(도저 1:4), 농업(Sabanto), 해양(Sea Machines)에 있다. XOCEAN은 2021 기준 USV 1척당 조종사 1명이다.

### Cited Findings
**SeeByte Neptune (해양 이종 자율)**
- [1차·마케팅] "Neptune assigns goal-based mission plans built on common behaviours such as surveying an area, investigating a target, or loitering." / "assigns goal-based plans and objectives based on the assets capabilities". (검색 스니펫) — [SeeByte Neptune PDF](https://www.seebyte.com/images/section/uploads/Neptune.pdf) / [UST company page](https://www.unmannedsystemstechnology.com/company/seebyte/neptune-maritime-autonomy-software/)
- [1차·마케팅] "The system's unique decentralised autonomy architecture allows multiple tasks to be run in parallel, with automatic malfunction management and task handover in response to failure or changes in the environment."; "the decentralised autonomy ensures vehicles operate even in comms-denied environments." 정량 근거 없이 "faster mission planning with fewer errors"라고 주장한다. (검색 스니펫 + 페이지 확인) — [SeeByte Neptune](https://seebyte.com/products/neptune/) / [Neptune 2023 brochure](https://seebyte.com/images/section/uploads/neptune-2023-1.pdf)
- [1차] 제품 페이지(페이지 확인): 운용 중 "swap tasks, add new tasks, or manage malfunctions"이 가능하다. 한 자산이 고장 나면 나머지가 누락 목표를 대신 맡도록 설정할 수 있다. 미션 리허설은 미션 전에 기체별 예상 경로를 요약해 보여준다. 미션 시험용 "Neptune Simulator"가 있고, topside UI는 "installed as a plug-in to SeeTrack"이다. 지원 플랫폼은 HII REMUS, ATLAS SEACAT, MARTAC MANTAS(USV)이고, SDK로 제3자 기체·센서·행동을 붙인다. — [SeeByte Neptune](https://seebyte.com/products/neptune/)
- [언론] 미국, 영국, 캐나다, 네덜란드 해군이 EOD/MCM용으로 선정했고, 네덜란드 해군은 신형 REMUS 100에 통합했다. (검색 스니펫) — [Seapower Magazine](https://seapowermagazine.org/royal-netherlands-navy-successfully-integrates-seebytes-neptune-into-remus-100/?print=pdf)
- [학술] (2021-07 Charles River 시험) Neptune(상위 계획: 자산 능력, 배제구역)과 MIT MOOS-IvP(하위 반응형 경로, 충돌 회피)를 공유 인터페이스로 결합한 사례가 있다. "Neptune's high-level mission planning based on asset capabilities and exclusion zones to provide objectives to MOOS-IvP". (검색 스니펫) — [Univ. Pisa repository PDF](https://arpi.unipi.it/retrieve/14955b06-d9ee-4f19-854a-6386d3ebc188/Coordinating%20multiple%20autonomies_AAM.pdf)

**해양 USV 운영**
- [1차·마케팅] (약 2020) Sea Machines SM300: "remotely monitor and command multiple autonomous vessels from a shipboard or shore-based center". 2척 이상이 "perform autonomous missions collaboratively"하고, ECDIS 기반으로 계획한다. 용도는 "patrol and surveillance and mothership-daughter vessel collaborations"이다. (검색 스니펫) — [Sea Machines SM300 release](https://sea-machines.com/sea-machines-announces-release-of-the-sea-machines-300-autonomy-system/) / [Marine Log](https://www.marinelog.com/technology/sea-machines-autonomy-selected-for-unmanned-wadden-sea-surveys)
- [1차] Saildrone: 보트는 원격 조종이 아니라 사전 웨이포인트를 따르고 바람·조류를 보정해 회랑 안에 머문다. 웹 기반 Mission Portal에서 임무 중 경로를 바꾸고 API로 외부와 연동한다. 2023년 Operation Windward Stack에 Voyager 10척을 배치했다. (검색 스니펫) — [Saildrone Mission Management](https://saildrone.com/news/saildrone-mission-management) / [U.S. Navy](https://www.navy.mil/Press-Office/News-Stories/Article/3525423/saildrones-set-sail-in-support-of-us-4th-fleets-operation-windward-stack/)
- [1차] XOCEAN(2021 NOAA 발표): 인력 계획이 USV 1척당 조종사 1명, 서베이어 1명당 USV 3척이다. 2024 IMO 발표 기준 "level 3" 자율(원격 운용, 조종사가 저장된 경로 명령의 실행을 감시), 누적 1,085 임무, 13만 운용시간이다. Baird Maritime은 "the USV has no autonomous collision avoidance system"이라고 썼다. — [NOAA HSRP 2021 PDF](https://www.nauticalcharts.noaa.gov/hsrp/meetings/fall-2021/02%20presentations%20Sept%20HSRP%202021/03%20Shallow%20Water%20Surveys/03%20Mallace%20D.%20Tech%20_%20Shallow%20Surveys%20HSRP%202Sept2021.pdf) / [IMO 2024 symposium PDF](https://wwwcdn.imo.org/localresources/en/About/Events/Documents/2024%20IMO-ROK%20MASS%20Symposium%20presentations/2-4.%20Remotely%20operated%20survey%20fleet%20Experience%20from%20the%20first%201,000%20missions%20-%20Shepard%20Smith(XOCEAN).pdf) / [Baird Maritime](https://www.bairdmaritime.com/work-boat-world/specialised-fields/unmanned-craft-non-naval/vessel-review-electric-powered-long-range-unmanned-catamarans-for-irish-subsea-data-company)

**광산·농업 "1인 다수"**
- [1차·마케팅] Caterpillar MineStar Command: 반자율 도징에서 "one operator can handle up to four machines from a remote location"이다. 드릴은 원격 운용석 하나에서 여러 대를 맡는다. 운반 트럭은 무인 탑승으로 셔블 호출, 덤프, 정비 입고를 수행한다. 트럭당 감독 비율은 공개되지 않았다. (검색 스니펫) — [Cat MineStar Command](https://www.cat.com/en_US/by-industry/mining/surface-mining/surface-technology/command.html) / [Westrac Command for Hauling](https://westrac.com.au/technology/minestar/minestar-command/minestar-command-for-hauling)
- [1차·마케팅] Sabanto Steward는 휴대폰·태블릿의 "Vehicle Mission Control app"으로 임무를 생성·감시한다. 인용: "With Steward, a single operator can deploy multiple tractors to achieve more with less." 2023-03에 미 우주군 Patrick 기지에 2대를 공급했다. (검색 스니펫) — [Compact Equipment](https://compactequip.com/tractors/sabanto-is-bringing-autonomy-to-existing-tractors-with-help-of-your-phone-or-tablet/) / [The Defense Post 2023-03](https://thedefensepost.com/2023/03/01/us-autonomous-tractor-sabanto/amp/)

**산업 점검: 로봇 + 드론 혼합 플릿 플랫폼**
- [1차·마케팅] Korial(구 Energy Robotics, 리브랜딩 시점 미상): "from powering individual robots and drones to orchestrating autonomy as an enterprise-scale AI platform"; 하드웨어 무관; "agentic workflows"; Shell Rheinland 사례는 "a mixed fleet of autonomous inspection robots and a drone"이다. 미션 저작 UI(노코드 여부)는 페이지에 없다. (페이지 확인) — [Korial](https://www.korial.com/)
- [언론] Energy Robotics는 2025-10에 Series A 1,350만 달러를 유치했고, 2023 IEEE RAS 제품혁신상을 받았다. 집계 사이트는 "200,000+ mission hours … 80 deployed robots"라고 쓴다[미검증]. — [Pulse 2.0](https://pulse2.com/energy-robotics-13-5-million-series-a-closed-for-scaling-fleet-orchestration-software-platform/amp/) / [Robotics.press profile](https://www.robotics.press/news/energy-robotics-company-profile/) / [computer-automation.de](https://www.computer-automation.de/robotics-en/ieee-award-2023-presented.htm)
- [1차] ANYbotics와 Energy Robotics의 전략 제휴(ACHEMA 2024-06): "manage their robot fleet directly from existing asset management or digital twin software". — [ANYbotics news](https://www.anybotics.com/news/anybotics-energy-robotics-partnership-achema-2024/)
- [1차] Yokogawa OpreX Robot Management Core(2024-03-21): "registration, management, and operation of multiple types of robots in a unified manner"; Spot과 MHI EX ROVR을 지원한다. "In the future, support will be added … as well as drones"; 제어시스템 작업절차와 연동된 로봇 지시도 계획에 있다. — [Yokogawa press 2024-03-21](https://www.yokogawa.com/us/news/press-releases/2024/2024-03-21/)
- [1차] Cognite InRobot: 내비게이션 웨이포인트를 3D 모델에 정렬해 자율 미션을 계획하고, Spot, ANYmal D, ANYmal X를 지원한다. (검색 스니펫) — [Cognite docs InRobot](https://docs.cognite.com/cdf/inrobot)
- [2차·마케팅] Unmanned Life는 이종 드론·지상로봇 SaaS를 표방한다: "We act as one central intelligent brain powering different robotics use cases". 5G와 엣지를 강조한다. 한 독립 프로필은 "no publicly verified production-scale deployments"라고 평가한다. 회사 기본 정보(설립연도·위치)가 출처마다 다르다. — [The Innovator](https://theinnovator.news/startup-of-the-week-unmanned-life/) / [Robotics.press](https://robotics.press/companies/unmanned-life/)
- Percepto AIM(드론 + Spot)과 DroneDeploy Robotics(도크 드론 + Spot/Go2-W)는 §3 Cited Findings를 참조한다.

### Inferences
- **SeeByte Neptune은 컨셉의 "의미 기반 행동 어휘 + 능력 기반 배정 + 고장 시 인계 + 시뮬레이터"를 상용으로 구현한 가장 가까운 사례다.** 컨셉이 Neptune 대비 새로 내세울 수 있는 것은 (1) 공중·수상·지상을 한 그래프로 묶는 도메인 확장, (2) 계획자용 노코드 스텝 카드 UI, (3) 저장 시 정적 검증과 서명, (4) 명령 단위 런타임 가드다. 다만 Neptune 내부에도 검증 단계가 있을 수 있으므로 "업계 최초" 주장은 피해야 한다(추정).
- 육상 산업 점검 플랫폼(Korial, Yokogawa, Percepto, DroneDeploy)은 이종 하드웨어를 "등록·스케줄·데이터 수집"으로 통합한다. 행동 로직은 벤더별 미션(예: Spot Autowalk)에 위임하는 구조로 보인다(추정). 컨셉의 "도메인 무관 행동 → 배정 시 도메인별 확장"은 이 위임 계층을 표준화하는 제안으로 설명할 수 있다.
- XOCEAN(1:1)과 Sea Machines(1:N 주장)의 대비는 실제 해양 운용에서 1인 다수 감독이 아직 일반적이지 않다는 신호다. 컨셉의 운용자 부하 경감 주장의 동기 근거로 쓸 수 있다(XOCEAN 비율은 2021 자료).

### Gaps
- Neptune 계획 UI의 실제 형태(맵 기반 목표 배치인지, 리스트·그래프 편집인지)와 정적 검증 기능 유무는 1차 매뉴얼이 없어 확인하지 못했다. 2025-2026 업데이트도 찾지 못했다.
- Saildrone 조종사 1인당 감독 척수는 공개 자료가 없다.
- Komatsu FrontRunner 등 다른 광산 자율운반 시스템의 감독 비율과 임무 저작 방식은 다루지 못했다.
- Korial의 "agentic workflows"가 사용자 저작 워크플로인지, 지원 하드웨어 목록과 드론 기종이 무엇인지는 확인하지 못했다.
- 상용 민간 제품 가운데 공중·수상·지상 3도메인을 한 플랫폼에서 동시에 운용하는 사례는 찾지 못했다. 해양(Neptune: 수중·수상)과 육상(Korial 등: 지상·공중) 조합만 확인됐다.

## 6. 결론: "이종 편대용 시각적 행동 저작 + 검증 + 인계"에 가장 가까운 상용 도구와 남는 공백

### Takeaway
단일 제품으로 컨셉 전체에 가장 가까운 것은 **SeeByte Neptune**(해양 이종, 목표 기반 행동, 자동 인계, 시뮬레이터)이다. 편집기 UX는 **MiR 미션 편집기**(Prompt user 승인 게이트, If/Loop/Try-Catch, 변수, 중첩)와 **FlytBase Aeroflo**(트리거·게이트웨이·액션 캔버스, 노드 단위 드라이런)가 가장 가깝다. 역할 인계는 **DJI Dock 3 swap/relay**(같은 기종)와 Neptune 과업 인계(같은 해양 도메인)가 가장 가깝다. 이번 조사 범위에서 컨셉의 네 요소, 즉 **(1) 도메인 무관 행동 그래프의 배정 시점 도메인별 확장, (2) 저장 시 정적 검증 + 서명, (3) 공중↔수상↔지상 도메인 간 역할 인계, (4) 모든 명령에 대한 런타임 안전 가드**를 함께 갖춘 상용 제품은 찾지 못했다.

### Cited Findings
- 편집기 구조(승인 게이트·분기·반복·예외)의 선례: MiR Prompt user(Yes/No, User group, Timeout), Try/Catch, 변수, Loop, If — [MiR100 User Guide 4.2](https://supportportal.mobile-industrial-robots.com/support-files/manuals/html/en/mir100_user_guide_4.2/content/_Resources/pdf/MiR100%20User%20Guide%204.2_en.pdf) / [MiR Reference guide 2019](https://cdn.kyklo.co/assets/W1siZiIsIjIwMTkvMTAvMTYvMTgvNTgvNTYvMGNkOTJiZGQtZGYzMS00OTVmLThlMGEtMWUwODhiNzQ1ODgwL01pUiUyMC0lMjBNaVIlMjByb2JvdCUyMHJlZmVyZW5jZSUyMGd1aWRlLnBkZiJdXQ?sha=9b51843b3f3b3c7f)
- 트리거-액션 캔버스와 사전 시뮬레이션의 선례: FlytBase Aeroflo "walks every node, validates inputs … without sending a single drone command"; Flows의 Manual/Automated 대응 모드 — [FlytBase Aeroflo](https://flytbase.com/flex/aero-flow-control) / [FlytBase Flows](https://docs.flytbase.com/en/flinks-and-flows/flows)
- 행동 어휘와 인계의 선례: Neptune "surveying an area, investigating a target, or loitering", "automatic malfunction management and task handover" — [SeeByte Neptune](https://seebyte.com/products/neptune/) / [Neptune PDF](https://www.seebyte.com/images/section/uploads/Neptune.pdf)
- 같은 기종 간 역할 인계의 선례: DJI Dock 3 "Automatic Swap Task", "uninterrupted relay observation" — [DJI Enterprise Insights 2025-05-07](https://enterprise-insights.dji.com/blog/new-update-flighthub2-april)
- 크로스도메인 트리거 비전(2021): DroneDeploy 드론 열점 → 지상로봇 출동 — [DroneDJ 2021-08-10](https://dronedj.com/2021/08/10/dronedeploy-acquires-robotics-software-company-rocos/)
- 계획 시점 안전 점검의 선례: Auterion MC "Geofence", "Terrain collision checks", "Automatic pre-flight checks"; UgCS NFZ 자동 우회; DJI 제한구역 우회 — [Auterion MC](https://auterion.com/product/mission-control/) / [UgCS FAQ](https://manuals-ugcs.sphengineering.com/docs/faq) / [DJI Enterprise Insights](https://enterprise-insights.dji.com/blog/new-update-flighthub2-april)
- 개발자용 행동 그래프 디버깅·폴트 인젝션의 선례: Groot2 PRO "Interactive Breakpoints", "Fault Injection", 런타임 노드 치환 — [behaviortree.dev/groot](https://www.behaviortree.dev/groot/)
- 시각 그래프를 스크립트로 컴파일하는 구조의 선례: Techman TMflow(노드 → TMscript) — [TM path planning doc](https://www.tm-robot.com/en/support/technical-document/start-using-path-planning-function-in-tmflow)
- 외부 이벤트가 로봇 점검을 트리거하는 최신 동향: Spot 5.2(2026-10) PLC·센서·CCTV 입력, MCP 계층 기반 — [Robotics & Automation News 2026-10-01](https://roboticsandautomationnews.com/2026/10/01/boston-dynamics-updates-spot-to-connect-autonomous-robot-inspections-with-enterprise-ai-systems/105384/)

### Inferences
**요소별 최근접 상용 사례 매트릭스** (O = 공개 자료로 확인, △ = 부분·같은 도메인 한정, X = 공개 자료에서 찾지 못함)

| 컨셉 요소 | MiR 편집기 | FlytBase Aeroflo/Flows | DJI FH2 + Dock 3 | SeeByte Neptune | BD Orbit/Autowalk | Korial/Percepto/DroneDeploy | UgCS / Auterion MC | Groot2 PRO |
|---|---|---|---|---|---|---|---|---|
| 노코드 시각 저작(스텝·노드) | O(리스트+컨테이너) | O(캔버스) | △(경로·작업) | △(목표 계획 UI, 형태 미확인) | △(녹화+액션 리스트) | X(공개 UI 미확인) | △(경로 계획) | O(BT, 개발자용) |
| IF/반복/예외 | O | △(게이트웨이, 의미 미확인) | X | X(미확인) | X(평면 리스트) | X | △(DO_JUMP 수준은 ArduPilot) | O |
| 운용자 승인 게이트 | O(Prompt user) | O(Manual 모드) | X | X(미확인) | X | X | X | X |
| 다기체·이종 배정 | X(MiR Fleet 미확인) | △(다도크·드론 한정) | △(Grid 배정, 드론 한정) | O(능력 기반, 해양) | △(Spot/Stretch) | O(로봇+드론 등록) | △(다드론, 수동 배정) | X |
| 정적 검증 | △(액션 파라미터 Validate) | △(드라이런 시뮬레이션) | △(제한구역 우회) | △(리허설·시뮬레이터) | △(개별 규칙) | X | △(지오펜스·지형·NFZ) | X |
| 저작물 서명 | X | X | X | X | X | X | X | X |
| 역할 인계 | X | X | △(같은 기종 swap/relay) | O(과업 인계, 해양) | X | X | X | X |
| 임무 중 계획 주입 | X(미확인) | X | O(비행 중 경로 배포) | O(swap/add tasks) | X | X | X | △(런타임 노드 치환) |
| 런타임 명령 가드 | X(안전 PLC는 별도) | X | X | X(미확인) | X | X | △(지오펜스 실행 시 작동) | △(폴트 인젝션은 시험용) |

- 위 표의 X는 "이번 조사의 공개 자료에서 찾지 못함"을 뜻한다. 제품에 기능이 없다는 증명은 아니다.
- **해커톤 포지셔닝 제안(추정)**:
  - "편집기 자체"는 새롭지 않다. MiR와 FlytBase가 산업에서 이미 검증한 UX이고, 이를 오히려 "익숙한 UX"의 근거로 쓴다.
  - 새로운 점은 **이종 도메인 확장 + 저장 시 정적 검증·서명 + 크로스도메인 인계 + 명령 단위 런타임 가드의 결합**이다. 특히 "서명"과 "명령 단위 가드"는 상용 사례를 찾지 못한 영역이다.
  - 데모 시나리오에서 Neptune형 행동 어휘(sweep/observe/loiter)를 쓰면 해군 MCM 실무와 연결된다. DJI relay 같은 인계를 "드론 → 보트"로 넓혀 보여주면 차별점이 바로 보인다.
- 시장 신호: DiaB와 보안 드론 쪽은 2025년에 BVLOS 승인과 투자가 늘었다(Sunflower 2025-11 1,600만 달러, Ondas UAE 주문 2025-04, FlytBase Pro $99/월 2025-04). 산업 점검 이종 플랫폼(Energy Robotics/Korial Series A 2025-10)도 성장 중이다. 반면 AMR 쪽에는 Zebra/Fetch 철수(2025) 같은 구조조정 신호가 있다. 범용 로봇 클라우드 플랫폼에는 AWS RoboMaker 종료(2025-09) 같은 지속성 리스크가 있다.

### Gaps
- 저작한 임무·행동을 **암호학적으로 서명**하고 실행 전에 검증하는 상용 로봇·드론 도구는 검색 범위에서 한 건도 찾지 못했다. 국방 C2(Lattice 등)에 유사 기능이 있는지는 `products-market.md`에서 따로 확인해야 한다.
- 상용 제품 가운데 정적 검증(도달성, 배터리·통신 범위, 금지구역, 승인 게이트 누락 등)을 저작물 전체에 대해 수행한다고 명시한 사례도 찾지 못했다. Neptune 리허설과 FlytBase 드라이런이 가장 가깝지만 상세 검증 항목은 비공개다.
- Neptune의 실제 저작 UI, MiR Fleet의 다로봇 배정 규칙, Aeroflo 게이트웨이 노드의 의미는 1차 문서 접근 제한(로그인, HTTP 429)으로 확인하지 못했다. 시연 전에 인용하려면 영상이나 데모 자료로 보강해야 한다.
- 가격 공개 사례는 FlytBase, InOrbit, Groot2뿐이다. Orbit, Neptune, Korial, Percepto, Formant는 견적제다.
