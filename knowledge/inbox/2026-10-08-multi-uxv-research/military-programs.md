# 단일·소수 운용자의 다중 무인체계(Multi-UxV) 통제 — 미국·NATO/동맹·한국의 프로그램, 교리, 요구사항

> 작성 2026-10-08. 모든 URL 접속일 = 2026-10-08.
> 표기: **[원문 확인]** = 해당 URL을 직접 열어 문장을 확인함. **[검색 요약]** = 검색엔진 요약/스니펫으로만 확인, 원문 미열람(인용 전 재확인 권장). 직접 인용(영문)은 원문 언어 그대로 둔다.
> 용도: T1-1 "Multi-UxV Control"(1인 운용자가 3+ 이기종 무인체계를 임무 할당·감시·통제, 인지부하 최소화) 피치의 "military applicability"(30%) 근거.

## Q1. DARPA OFFSET · DARPA CODE · AFRL IMPACT(및 ACT3/OpenUxAS) — 실제로 달성된 운용자 대 기체 비율은?

### Takeaway
공개 기록상 "1인 대 다수"의 최고 실증치는 DARPA OFFSET 최종 야외실험(FX-6, 2021.11, Fort Campbell)에서 **스웜 지휘관 1명이 100대 이상(최대 UAV 139·UGV 44 + 가상 최대 100)** 이기종 로봇을 VR 인터페이스로 운용하고 과부하 상태는 전체 추정치의 3.2%였던 것이다. 다만 "1인"은 실제로는 *스웜 지휘관 + 보조 운용자* 팀으로 운영됐고, 핵심 수단은 개별 조종이 아닌 **사전 정의된 전술 라이브러리(play/tactic) 호출**이었다. CODE(2019)는 1:6 실기 + 가상 14대, AFRL IMPACT(2017)는 시뮬레이션 12대를 "play" 명령으로 관리했다.

### Cited Findings

**DARPA OFFSET (OFFensive Swarm-Enabled Tactics, 2017~2021, 종료)**
- 프로그램 목표: 소부대 보병이 최대 250대 소형 무인기/지상로봇 스웜을 쓰는 미래상. 원문: "envisions future small-unit infantry forces using swarms comprising upwards of 250 small unmanned aircraft systems" / 인터페이스 목표: "monitor and direct potentially hundreds of unmanned platforms simultaneously in real time" / 프로그램 상태: "This program is now complete" — [DARPA OFFSET 프로그램 페이지](https://www.darpa.mil/research/programs/offensive-swarm-enabled-tactics) [원문 확인]
- 250은 **목표(vision)**이며 실증 수치가 아님. 프로그램 구조: ① human-swarm 지휘 인터페이스 ② 네트워크 가상 시험환경 ③ 커뮤니티 전술 교환(tactics exchange). 원문: tactics designed "by composing collective behaviors, swarm algorithms" — 같은 출처 [원문 확인]
- 최종 야외실험: "Fort Campbell hosted the final field experiment for DARPA's OFFensive Swarm-Enabled Tactics, or OFFSET, program on Nov. 16" … "they used them to deploy over 100 robots across Cassidy Range Complex" / 인터페이스: "tablet-based and virtual reality interfaces to control drone swarms" / 전술: "teams of drones and rovers to perform dozens of maneuvers using a digital library" — [army.mil, 2021](https://www.army.mil/article/252556) [원문 확인]
- PM(Timothy Chung) 발언: "We would rather be able to orchestrate how these swarms of robots go out with a single operator" / "Trying to take what you've learned from controlling one robot or controlling five doesn't scale to controlling 100" — 같은 출처 [원문 확인]. 운용 형태는 "a single operator working alongside a swarm commander"(동 기사) → **실제로는 2인 팀**. Overt Defense도 "swarm commander"와 operator 1명의 팀으로 기술 — [Overt Defense, 2021-12-16](https://overtdefense.com/2021/12/16/darpa-runs-final-test-for-offset-program-drone-swarm) [검색 요약]
- "fully developed" 시 1인 운용은 **전망(projection)**: "if this technology is fully developed, one Soldier is all it takes to control the swarm" — [army.mil](https://www.army.mil/article/252556) [원문 확인]
- 동료심사 논문(Adams 외, CCAST 팀 = Raytheon BBN + Oregon State Univ. + SIFT): "A near-the-battle human supervisor, the Swarm Commander (SC), deployed the heterogeneous robot swarm." / 인터페이스 "the CCAST Immersive Interaction Interface, a virtual reality based system"(I3, Unity + Valve Index) / FX-6 스웜 규모: 최대 UAV 139, UGV 44, 가상 최대 100 / "The SC's estimated overall workload was only classified as an overload state for 3.2% of the 12,181 usable workload estimates." / 결론: "The presented results demonstrate that a single human can deploy a swarm of 100 heterogeneous robots to conduct real-world missions." — [arXiv 2308.00102 (ar5iv), "Can A Single Human Supervise A Swarm of 100 Heterogeneous Robots?"](https://ar5iv.labs.arxiv.org/html/2308.00102) [원문 확인]. 같은 논문 초록은 workload가 "did cross the overload threshold frequently"라고도 서술(시간 비율 3.2%와 "빈번히 넘음"은 측정 단위가 다름에 유의).
- IEEE Spectrum 요약(2025-01-26): "The largest mission shift involved 110 drones, 30 ground vehicles, and up to 50 virtual vehicles" / "Human controllers managed their swarms of autonomous vehicles with a virtual display." — [IEEE Spectrum](https://spectrum.ieee.org/darpa-robot) [원문 확인]
- 서지 불일치: arXiv는 Field Robotics vol.3(2023), IEEE Xplore는 IEEE Transactions on Field Robotics vol.2 pp.46–80(2024-11-19)로 표기 — [IEEE Xplore](https://ieeexplore.ieee.org/document/10757435/references) [검색 요약]
- Raytheon 측 서술은 "130 physical + 30 simulated drone platforms"을 1인이 통제 — [Airforce Technology](https://www.airforce-technology.com/?p=218587) [검색 요약] (논문 수치와 다름 → 논문 수치 우선 인용 권장)

**DARPA CODE (Collaborative Operations in Denied Environment, 2019 시연)**
- "six RQ-23 Tigersharks lifted off, fitted with an array of sensors onboard." / "successfully carried out mission objectives, even when communications were offline and GPS was unavailable." / PM Scott Wierzbanowski: "Equipped with CODE, one operator can command multiple aircraft;" / "CODE is a government-owned system," / "The Naval Air Systems Command (NAVAIR) will take ownership of CODE" — [DARPA, 2019-03-22 "CODE success"](https://www.darpa.mil/news/2019/code-success) [원문 확인]
- Yuma Proving Ground 운용센터에서 실기 6대 + 가상기 최대 14대를 지도상에 표시, Raytheon 자율 SW + JHU APL White Force Network의 LVC 환경, 4회 시행 — [DSIAC](https://dsiac.dtic.mil/articles/darpa-successfully-tests-uav-swarming-technologies/); [Unmanned Systems Technology, 2019-03](https://www.unmannedsystemstechnology.com/2019/03/darpa-successfully-tests-uav-swarming-technologies/) [검색 요약]
- 핵심 개념: 기존엔 기체마다 운용자 1명, 링크 상실 시 마지막 프로그램 임무로 복귀 → CODE는 통신 두절 시에도 기체 간 정보 공유·적응. 한 매체는 "기체가 협조 행동을 제안 → mission supervisor가 승인/거부"로 기술(인간 승인 정도는 출처마다 다름) — [Intelligence Community News](https://intelligencecommunitynews.com/darpa-tests-code-program-for-collaborative-autonomous-systems/) [검색 요약]
- 주의: 실제 Yuma 시연에 몇 명이 운용했는지는 공개 자료에 없음. "1인 다기"는 DARPA의 능력 설명이지 인원 기록이 아님.

**AFRL IMPACT (Intelligent Multi-UxV Planner with Adaptive Collaborative/Control Technologies, ~2014–2017)**
- Draper, Calhoun, Hansen 외(2017, ISAP): 여러 자율기술(자산 할당, 경로계획, COA 추천, 분산 확장형 SW 아키텍처)을 통합한 지상통제소 프로토타입으로 1인 운용자가 이기종 무인기와 팀을 이룸. 운용자는 고수준 **"play" 명령**으로 지휘. 평가 결과 **시뮬레이션 차량 12대(a dozen)**의 기지방호 임무를 효과적으로 관리 — [Wright State CORE Scholar, ISAP 2017 #85](https://corescholar.libraries.wright.edu/isap_2017/85) [원문 확인; 초록은 125자 제한으로 의역]
- 1차년도 평가: 피험자 7명이 기지방호 시나리오에서 UxV 6대 관리, play calling·자율기능을 긍정 평가 — [Initial Evaluation of IMPACT (academia.edu, Doug Lange)](https://independent.academia.edu/DougLange) [검색 요약]
- 설계 철학: 인간을 대체하는 자동화가 아니라 인간-자율 "협업(collaborative)" 접근 — [Wright State 학위논문 2017](https://corescholar.libraries.wright.edu/etd_all/1722) [검색 요약]
- 선행 AFRL 과제 ICE-T: 두 AFRL 부서 협업으로 1인이 다수 비행체를 통제하는 연구(2011) — [Wright State newsroom 2011](https://webapp2.wright.edu/web1/newsroom/2011/06/01/wsri-supports-air-force-unmanned-vehicle-research/) [검색 요약]
- MIT Cummings 계열 연구: 분산 계획기에 인간 가이던스를 더하면 탐색·추적·무력화 임무 성과 최대 50% 향상, 정밀·고속 계산 과제에서는 이득 적음 — [DTIC ADA521990](https://apps.dtic.mil/sti/html/tr/ADA521990/index.html) [검색 요약]

### Inferences
- 피치에 쓸 수 있는 "검증된 비율" 사다리: CODE **1:6(+가상 14)** → IMPACT **1:12(시뮬)** → OFFSET **1(지휘관)+보조 : 100+ (실기)**. 공통 성공요인은 (a) 개별 조종이 아니라 **play/전술 라이브러리 호출**, (b) 자율기체가 저수준 판단 담당, (c) 인간은 승인·우선순위 결정. T1-1 데모의 "미션 템플릿 원클릭 할당" UI는 이 계보(IMPACT play-calling, OFFSET tactics library)로 정당화 가능.
- "1인 250대"는 DARPA 목표치이지 실증치가 아니므로 심사위원(미군 장교) 앞에서는 "목표 250, 실증 100+ (과부하 3.2%)"로 정확히 구분해 말하는 편이 신뢰도에 유리.

### Gaps
- **ACT3 / OpenUxAS**: 이번 조사에서 1차 출처를 열지 못함. OpenUxAS는 AFRL이 공개한 다중 무인기 임무계획 오픈소스(GitHub afrl-rq/OpenUxAS)로 알려져 있으나 이 세션에서 URL 검증 안 됨 → `confidence: 추정`.
- IMPACT의 실기(live) 시연 규모와 최종 보고서(DTIC) 수치 미확인.
- CODE의 NAVAIR 이관 후(2019~) 진행 상황 공개 자료 미발견.

## Q2. 미국 각 군의 현행 프로그램(2024–2026): Army HMIF·Project Convergence·공통 통제기, Navy TF59·Ghost Fleet Overlord·Hellscape, USMC, Replicator→DAWG, CCA

### Takeaway
2024–2026 미국의 공통 문제의식은 "**플랫폼마다 따로 노는 조종기(stove-piped controllers)**"이다. 육군 RCCTO 국장의 "Today, everything has its own controller."와 2026년 8월 육군의 공통 통제기·HMI 공모(“disparate, stove-piped control systems prevents soldiers from operating multiple robotic and autonomous systems as an integrated team”)가 T1-1 문제정의와 정확히 일치한다. 해군은 USV를 육상 운용센터에서 "supervised autonomy"로 운용하며, 공군 CCA는 "1 조종사 : 1→2 CCA"부터 시작해 다수 통제의 인지부하가 여전히 미해결 과제다.

### Cited Findings

**US Army — Human-Machine Integrated Formations (HMIF / H-MIF)**
- 2027년 첫 HMIF 배치 목표, 3개 증분(FY30까지): "aims to field new Human Machine Integrated Formation (HMIF) in 2027" / "broken up into three developmental increments that will run through fiscal 2030." / Increment 1(FY24–27): "the service is working on a common controller for both ground and aerial drones." / RCCTO 국장 Lt. Gen. Robert Rasch: **"Today, everything has its own controller."** / "We don't want a robot wandering off the battlefield." / 운용 인력: Increment 1에서는 "more soldiers will be required to teleoperate ground robots", Increment 2는 "reduce the number of soldiers required to operate them and provide a greater standoff distance." — [Breaking Defense, 2025-04](https://breakingdefense.com/2025/04/army-eyeing-first-human-machine-integrated-formations-in-2027-common-controller-for-robotics/) [원문 확인]
- 기사에 "로봇 1대당 병사 수"는 명시 없음 — 같은 출처 [원문 확인]
- FY2025 예산요청에서 HMIF 첫 반영, 1단계 $33M; 기계가 "offload risk"하고 "additional information for decision making" 제공 — [Military Times, 2024-03-25](https://www.militarytimes.com/unmanned/2024/03/25/the-robots-are-coming-us-army-experiments-with-human-machine-warfare/) [검색 요약]
- 개념 슬로건: 로봇으로 적과의 첫 접촉을 형성("no blood for first contact"); 첫 HMI 로봇 소대 = EXFOR, A중대 1-29보병대대(2023.9 지정) — [army.mil "Human-Machine Integration: Tactical-Level Employment and the EXFOR RAS Platoon"](https://www.army.mil/article/282372) [검색 요약]
- 공통 통제기 시제: AeroVironment Tomahawk Grip TA5가 RCCTO HMIF "Dismounted Common Controller"로 선정, $5.1M(2025-05) — [AeroVironment 보도자료, 2025-05-19](https://www.avinc.com/2025/05/19/avs-tomahawk-awarded-5-1m-contract-for-human-machine-integrated-formations-project-by-u-s-army-rccto/) [검색 요약; 업체 주장]
- **2026-08-13 육군 공모**(UAS Marketplace CSO 하위): 기체가 아니라 "controllers and human-machine interfaces for Group 1-3 UAS, Launched Effects and Unmanned Ground Vehicles"를 구함. 문제정의: "disparate, stove-piped control systems prevents soldiers from operating multiple robotic and autonomous systems as an integrated team" / 요구 통제 특성: "asymmetric, distributed, intelligent, intermodal, policy-based and resilient control" / "Vendors must build to a Modular Open Systems Approach", FACE 기술표준 "where applicable" / 상위 아키텍처: "Next Generation Command and Control" / 1차 제출 마감 Aug. 26 / UAS Marketplace는 2026-03-24 Redstone Arsenal 개설 — [Inside Unmanned Systems, 2026-08](https://insideunmannedsystems.com/army-seeks-commercial-controllers-for-drones-and-ground-robots-under-new-c2-architecture/) [원문 확인]. 이 기사에는 "cognitive load/workload" 단어는 없음.

**Project Convergence Capstone 5 (2025.2–4)**
- 6,000명+ 합동·다국적 인원, 캘리포니아·네바다·하와이 2개 시나리오 — [army.mil PC-C5 at NTC](https://www.army.mil/article/284397/project_convergence_capstone_5_experiments_at_ntc); [PACOM](https://www.pacom.mil/Media/NEWS/Article/4163276/project-convergence-capstone-5-delivering-future-capabilities-through-multi-dom/) [검색 요약]
- Fort Irwin에서 HMIF와 로봇 동반 전투, 주요 교훈 "need for more robots and combining offensive and defensive fires" — [Defense One, 2025-05](https://www.defenseone.com/technology/2025/05/armys-latest-networked-warfare-experiment-took-back-fort-irwin/405042) [검색 요약]
- 해상 파트: 샌디에이고 앞 무인보트 스웜이 적 함정 공격, 무인잠수정·자폭보트 — [National Defense Magazine, 2025-06](https://digital.nationaldefensemagazine.org/june-2025/page-30) [검색 요약]
- 육군 준위 발언 요지: 시스템 통합은 진전됐으나 human-machine teaming 최적화 훈련·절차가 동등한 우선순위 필요; AFOTEC이 운용자-기술 상호작용 데이터 수집 — [af.mil "Air Force, Army shaping the future of C2, together"](https://www.af.mil/News/Article-Display/Article/4155743/air-force-army-shaping-the-future-of-c2-together/) [검색 요약]
- 공개된 정량적 사후보고서(AAR)는 미발견.

**Drone Dominance (2025-07) / Replicator → DAWG**
- Hegseth 메모 "Unleashing U.S. Military Drone Dominance"(2025-07-10): 무인체계를 "the biggest battlefield innovation in a generation"로 규정, FY2026 말까지 모든 육군 분대에 소형 일방향 공격 드론 — [Breaking Defense, 2025-07](https://breakingdefense.com/2025/07/hegseth-signs-unleashing-us-military-drone-dominance-memo/); 9/1까지 각 군 실험부대 편성, INDOPACOM 우선 — [DefenseScoop, 2025-07-10](https://defensescoop.com/2025/07/10/hegseth-memo-unleashing-us-military-drone-dominance-deadlines/) [검색 요약]
- Replicator(2023-08-28 발표, DIU 주도, 2025-08까지 "thousands" of attritable autonomous systems 목표) — [CRS IF12611, 2026-01-21](https://www.everycrsreport.com/files/2026-01-21_IF12611_81d5e4534de2a2308c6ecd35829488685dacf6db.pdf) [검색 요약]
- 결과: 전 Replicator-1 책임자 T.S. Allen — "hundreds of drones to warfighters" 인도, "thousands more on contract" — [Inside Defense](https://insidedefense.com/node/224983) [검색 요약]; 펜타곤은 실제 배치 수량에 "tight-lipped" — [DefenseScoop, 2025-09-03](https://defensescoop.com/2025/09/03/dod-replicator-drone-tech-transition-fielding-questions-linger/) [검색 요약]
- 2025년 가을 SOCOM 산하 **Defense Autonomous Warfare Group(DAWG)**으로 이관(Replicator-1·2의 제도적 본거지), FY26 $225.9M → FY27 요청 $54.6B(요청액, 의회 미확정) — [GlobalSecurity DAWG](https://www.globalsecurity.org/military/agency/dod/dawg.htm); [Defense One, 2026-05](https://www.defenseone.com/ideas/2026/05/pentagons-54-billion-bet-autonomous-warfare/413735/); [DroneXL, 2026-04-21](https://dronexl.co/2026/04/21/pentagon-fy27-75-billion-drone-budget-dawg-largest-boost/) [검색 요약]
- Replicator 2 = 소형무인기 대응(C-sUAS), Austin 메모(2024-09) "within 24 months of Congress approving funding" — [Defense News, 2024-09-30](https://www.defensenews.com/pentagon/2024/09/30/small-drone-defense-is-next-in-pentagons-replicator-buying-push/) [검색 요약]

**US Navy — Task Force 59 (5함대, 바레인, 2021-09 창설)**
- 창설 목적: 무인체계·AI를 중동 작전에 통합 — [navy.mil, 2021](https://www.navy.mil/Press-Office/News-Stories/Article/2768479/us-5th-fleet-launches-new-task-force-to-integrate-unmanned-systems/) [검색 요약]
- VADM Brad Cooper 목표: 2023년 여름까지 USV 100척(대부분 동맹·역내 파트너 제공) — [USNI News, 2022-10-11](https://news.usni.org/2022/10/11/navy-wants-100-unmanned-ships-monitoring-middle-east-waters-by-next-year) [검색 요약]. 달성 여부 공개 자료 미발견.
- 운용 모델: 각 USV 센서 데이터를 해상작전센터로 송신, AI가 이상 탐지 시 **인간이 결정** — 같은 계열 보도 [검색 요약]
- 핵심 인력 21명(다수 예비역) — [DefenseScoop, 2022-02-08](https://defensescoop.com/2022/02/08/task-force-59-the-future-of-the-navys-unmanned-systems-or-a-one-off-win/) [검색 요약]; 2주년 시점 약 15종 드론, 55,000 운용시간 — [Defense One, 2023-10](https://www.defenseone.com/technology/2023/10/navys-2-year-old-robot-task-force-eyes-more-ai/390814/) [검색 요약]
- 2024-01 Task Group 59.1 창설(무인체계를 작전 영역으로) — [Breaking Defense, 2024-01](https://breakingdefense.com/2024/01/commander-navys-new-task-group-59-1-to-usher-unmanned-systems-into-operational-realm/) [검색 요약]
- 2026-09 보도: TF59 Corsair USV가 호르무즈 인근 헬기 추락 승무원 구조 지원, Corsair 3척이 이란 반다르아바스 기지 타격에 사용됐다는 내용 — [Defense News, 2026-09-22 "CENTCOM has become a battle lab for unmanned systems"](https://www.defensenews.com/news/your-military/2026/09/22/centcom-has-become-a-battle-lab-for-unmanned-systems/) [검색 요약 — 중대한 주장이므로 인용 전 원문 확인 필수]
- **TF59의 "운용자 1인당 USV 수" 공식 수치는 공개 자료에서 찾지 못함.**

**US Navy — Ghost Fleet Overlord / 중형 USV**
- IBP 23.2에서 4척 USV가 46,000nm+ 항해, 대부분 "almost exclusively in … autonomous mode", 통제는 Port Hueneme 무인작전센터 + 구축함 탑승 인원 — [USNI News, 2024-01-16](https://news.usni.org/2024/01/16/navy-wraps-first-unmanned-surface-deployment-to-westpac) [검색 요약]
- Phase I: COLREGS 준수 조우 시연, 자율모드 600시간+; Nomad 4,421nm 중 98% 자율; Ranger 2020-10 무인선 최초 파나마운하 통과(운하 규정상 최소 인원 수동 조타) — [Naval News, 2020-06](https://www.navalnews.com/naval-news/2020/06/ghost-fleet-overlord-test-vessels-continue-to-accelerate-u-s-navys-usv-programs/); [Defense News, 2021-07-13](https://defensenews.com/naval/2021/07/13/us-navy-pentagon-to-test-large-unmanned-ships-in-operationally-relevant-scenarios-as-program-winds-down) [검색 요약]
- 해군 선호 통제 모델 "supervised autonomy", 육상 운용센터가 "to change missions in situ" — 같은 계열 보도 [검색 요약]
- 현황: Nomad(OUSV1) 퇴역, Ranger·Mariner Port Hueneme, Vanguard 건조 중 — [navy.mil OUSV Fact File](https://www.navy.mil/Resources/Fact-Files/Display-FactFiles/Article/4288694/overlord-unmanned-surface-vessels-ousv/) [검색 요약]
- 2025: "optionally manned" 지양, 차세대 무인함엔 승조원 배제 선호; 로봇 전문 신규 부사관 특기 신설(Carnegie Mellon에서 첫 "A" school) — [USNI News, 2025-08-15](https://news.usni.org/2025/08/15/navy-moving-away-from-optionally-manned-vessels-as-service-mulls-unmanned-future) [검색 요약]
- 2026-03: MASC 사업 취소, 중형 USV(MUSV) 마켓플레이스 신설(FY27 인도 목표) — [Breaking Defense, 2026-03](https://breakingdefense.com/2026/03/navy-nixes-masc-program-unveils-new-musv-marketplace-amid-golden-fleet-push/) [검색 요약]
- 탑승 민간 선원이 자율기능을 13회 차단(그중 6회만 항법 성능 관련) — [StrategyPage, 2024-02](https://www.strategypage.com/htmw/htsurf/20240201.aspx) [검색 요약; 신뢰도 낮은 출처]
- 해군·해병대 Unmanned Campaign Framework(2021-03-16) 목표: MUM-T, 디지털 백본, "solve once" — [ExecutiveGov](https://www.executivegov.com/articles/u-s-navy-usmc-issue-unmanned-campaign-framework-frederick-stefany-quoted) [검색 요약]

**INDOPACOM "Hellscape" (2024-06)**
- Adm. Samuel Paparo(INDOPACOM 사령관), 샹그릴라 대화 중 Washington Post 인터뷰: **"I want to turn the Taiwan Strait into an unmanned hellscape using a number of classified capabilities,"** / **"I can make their lives utterly miserable for a month, which buys me the time for the rest of everything."** — [Business Insider via Yahoo, 2024-06-10](https://malaysia.news.yahoo.com/us-military-plan-turn-taiwan-201225060.html) [원문 확인]. "수천 대의 무인 잠수정·수상정·드론"은 기자의 의역(Paparo 직접 인용 아님).

**USMC**
- Force Design 2030 군수 비전(2023-02, Berger): 분산 소부대의 자족성, 무인 재보급 — [USNI News, 2023-02-23](https://news.usni.org/2023/02/23/unmanned-supply-drones-forward-basing-key-to-marines-new-logistics-plan) [검색 요약]
- TRUAS(전술재보급 무인기) 6대 배치(150lb, 약 9마일), Autonomous Low-Profile Vessel(반잠수 자율 재보급, NSM 2발 탑재 가능) — [Defense One, 2024-03](https://defenseone.com/technology/2024/03/marines-trade-slow-ships-drones-and-supply-caches-they-prep-modern-warfare/395212) [검색 요약]
- Lt. Gen. Karsten Heckl: man-in-the-loop vs man-on-the-loop 논쟁 정리 필요 — [USNI News, 2023-09-06](https://news.usni.org/2023/09/06/marines-considering-autonomous-systems-for-almost-everything-general-says) [검색 요약]

**USAF — Collaborative Combat Aircraft (CCA) — T3-2 교차 관련**
- 2023 ACC 사령관 Gen. Mark Kelly: "I think we're obviously going to start with one [CCA per crewed fighter] and see how that goes," / 제약은 "processing power and bandwidth of the platform—and the processing power and bandwidth of the aviator," — [Air & Space Forces, 2023-03-07](https://www.airandspaceforces.com/acc-boss-fighters-should-start-with-one-cca-then-see-where-it-takes-us/) [원문 확인]
- 2023 Kendall: 1,000 CCA는 "planning assumption"(NGAD 200 × 2 + F-35 300 × 2), 장기적으로 전투기당 최대 5대 언급 — [Air & Space Forces](https://www.airandspaceforces.com/kendall-new-details-air-force-plans-200-ngad-1000-ccas/); [DefenseScoop, 2023-03-07](https://defensescoop.com/2023/03/07/air-force-planning-for-1000-robotic-wingmen/) [검색 요약]
- 2026-07 현재도 미해결: "Whether a single fighter pilot can meaningfully supervise multiple CCAs"가 열린 질문, 권한 이동 "from human 'in the loop' to human 'on the loop,'" / Increment 1 "initial contracts were awarded to General Atomics and Anduril in recent weeks" — [Breaking Defense, 2026-07-10](https://breakingdefense.com/2026/07/the-autonomous-cca-wingmen-of-2030-may-look-nothing-like-todays-assumptions/) [원문 확인]
- FY2027 요청: Increment 1 생산 착수 조달 $996.5M, 개발 포함 총 약 $2.37B — [Defense News, 2026-04-30](https://www.defensenews.com/news/your-military/2026/04/30/from-prototypes-to-production-us-air-force-seeks-nearly-1b-for-initial-cca-procurement/) [검색 요약]
- Mitchell Institute(Penney): 조종사가 "task saturated" 되지 않아야 함, 음성 통제가 현재 선호되나 "may or may not be the best way", E-7 등 C2기에서 일부 지휘 가능성 — [Air & Space Forces](https://airandspaceforces.com/?p=170987) [검색 요약]
- Lockheed: 태블릿 형태로 다수 CCA 통제 제안(업체 주장) — [Air & Space Forces](https://www.airandspaceforces.com/lockheed-tech-f-35-ccas/) [검색 요약]

### Inferences
- 미 육군의 2026-08 공모 문구("integrated team", "policy-based … control", MOSA)는 T1-1 데모의 "공통 지휘통제 + 이기종 어댑터" 구조를 그대로 설명한다. 피치에서 "미 육군이 지금(2026.8) 시장에 요구하는 바로 그 기능"으로 연결 가능.
- 해군 USV 운용의 실제 모델은 "자율 항해 + 육상 센터의 감독형 자율(supervised autonomy) + 이상 시 인간 결정"이다. T1-1의 해상 UxV 시나리오는 이 모델(경보 기반 개입)을 따라야 현실성이 있다.
- CCA는 2023년 "1:1부터", 2026년에도 "1인 다기 감독 가능성"이 미해결 → 인지부하 저감 UI(우선순위 큐, 예외 기반 알림)는 T3-2와도 공유 가능한 가치 제안.

### Gaps
- **Robotic Combat Vehicle(RCV)** 2025–2026 상태(취소/재편 여부)와 **Launched Effects** 운용자 비율 — 이번 조사에서 1차 출처 확보 실패.
- **MADIS**(해병대 대드론 체계) — 다중 UxV 통제와 직접 관련 자료 미수집.
- TF59 운용자/USV 비율, Replicator 실제 배치 수량(분류됨), Drone Dominance 분대 목표(FY26 말) 달성 여부 — 공개 자료 미발견.
- Army Transformation Initiative(2025-04/05)와 HMIF의 관계 — 미확인.

## Q3. NATO·영국·호주 — 다중 무인체계 통제 실험과 운용 개념

### Takeaway
영국 Dstl 2025년 시험은 T1-1과 **거의 동일한 형상**(유인 지휘차량 안의 운용자 1명이 UAV 1 + UGV 2 = 이기종 3대를 동시 지휘, ATR로 위협 탐지·분류)을 "UK first"로 공식 발표했다. 호주 MQ-28 Ghost Bat은 E-7A 탑승 운용자 1명이 실기 2 + 가상 1대를 통제했다. NATO REPMUS 2025는 22개국 260개 체계가 참가한 다영역 무인체계 상호운용 실험이다.

### Cited Findings

**영국**
- Dstl 시험(2025-06-13 발표): "a single operator controlled three uncrewed air and land vehicles" / "a drone operated in tandem with two uncrewed ground vehicles" / "commanded by a single operator in a crewed vehicle" / "cameras and automatic target recognition software to detect and classify threats" / 다음 단계 "deploying swarming drones in an intelligence, surveillance and reconnaissance role" / 투자 "investing an extra £2 billion this Parliament" — [GOV.UK, 2025-06-13](https://www.gov.uk/government/news/successful-trial-paves-the-way-for-improved-reconnaissance-on-army-operations) [원문 확인]. 설계·개발은 Thales — 같은 출처 [검색 요약]
- 2022 영국 육군 나노 UAS 스웜 시험(Salisbury Plain): 태블릿으로 1인이 4대를 개별 수동 임무 할당하는 방식 vs 1인이 6대에 자율임무를 할당하는 방식 비교; 군항공당국(MAA)이 "1인 운용 스웜" 분류를 처음 발급 — [British Army, 2022-09](https://www.army.mod.uk/news/british-army-carries-out-successful-swarming-drone-capability/) [검색 요약]

**호주**
- MQ-28 Ghost Bat + E-7A Wedgetail(2025-06 발표, Woomera): Boeing 발표 인용 "a single operator onboard the E-7A took control of the uncrewed MQ-28s" / "a pair of real Ghost Bats and a third drone"(3번째는 디지털) / 통제 이양 개념: 이착륙 운용자가 "would oversee the [MQ-28] aircraft as it takes flight" → 유인기(E-7A, F-35A, F/A-18F) "whose crew tasks it to perform" missions → 착륙 시 다시 이착륙 운용자에게 반환 — [The War Zone, 2025-06-18](https://twz.com/air/mq-28-ghost-bats-controlled-from-e-7-wedgetail-in-loyal-wingman-test) [원문 확인]. E-7 운용자 워크로드 수치는 공개되지 않음.
- Ghost Shark(XL-AUV): Anduril·DSTG·RAN, 첫 3척 A$140M; RIMPAC에 C-17로 수송 — [The War Zone](https://www.twz.com/news-features/everything-we-just-learned-about-the-ghost-shark-uncrewed-submarine); [Defence Blog](https://defence-blog.com/australian-navy-buys-ghost-shark-autonomous-submarines/) [검색 요약]. 운용자 통제 개념은 공개 자료에서 확인되지 않음.

**NATO REPMUS / Dynamic Messenger 2025**
- 포르투갈 해군 주최, MARCOM·ACT 공동 조직, Troia·Sesimbra, 2025-09-01~26; "more than 3,800 participants and 260 systems from 22 nations", 관찰국 13개; 해저기반시설 보호, 지속 ISR-T, 기뢰전, 해상 대드론, **integrated multi-domain command and control** 시연; TTP를 시험해 NATO 교리 프레임워크 정교화 — [Baird Maritime](https://www.bairdmaritime.com/security/naval/unmanned-naval-systems/nato-completes-unmanned-systems-exercise-in-portugal) [검색 요약]
- 우크라이나 해군이 처음으로 대항군(OPFOR) 지휘, 우크라 해상드론이 적 역할 — [Kyiv Post](https://www.kyivpost.com/post/60947) [검색 요약]. 참가국 수는 22개(NATO) vs 24개(Kyiv Post)로 불일치.
- 업체 주장: ZeroUSV Oceanus12가 예인 음향배열 자율 전개·회수 — [Ocean News](https://oceannews.com/news/defense/zerousv-hits-key-milestones-at-natos-repmus-exercise/) [검색 요약; 업체 주장]

### Inferences
- Dstl 2025 시험은 "1인 · 3대 · 이기종(공중+지상) · 유인 차량 내 · ATR 보조"라는 점에서 T1-1 과제 정의와 1:1 대응한다. 피치에서 "영국이 2025년에 'UK first'로 발표한 능력을, 해상까지 포함한 3영역으로 확장"이라는 위치 설정이 가능.
- Ghost Bat의 "이착륙 운용자 ↔ 임무 운용자" 핸드오프 개념은 T1-1 UI의 "통제권 이양(handover)" 기능 근거로 쓸 수 있음.

### Gaps
- REPMUS 2025의 정량적 사후보고서, 다영역 C2에서 운용자/체계 비율 — 미공개.
- 영국 Dstl 후속 스웜 ISR 시험 결과 — 미확인.
- Ghost Shark 운용 부대(MASU 등)와 통제 개념 — 검색 요약에서 언급됐으나 출처 URL 특정 실패.

## Q4. 한국 — 국방혁신 4.0, 유무인복합전투체계(MUM-T), 아미타이거, 드론작전사령부(→국방드론본부), Navy Sea GHOST, 50만 드론전사, 병력 감소 수치

### Takeaway
한국의 MUM-T 추진 동력은 **인구절벽**이다. KIDA는 상비병력이 2040년 약 35만, 2040년대 중반 31~32만(2024.2 보고서), 현 추세 유지 시 **2045년 약 19.7만**(2026.7 분석)으로 줄 것으로 본다. 국방부는 드론·무인기 전력 약 30배 증강, 병사 비중 60%→2040년 37%, "50만 드론전사" 양성을 내걸었고, 2026.6 드론작전사령부를 국방드론본부로 개편했다. 해군 Navy Sea GHOST의 4대 과제에는 **"공통 아키텍처 구축"**이 들어 있다.

### Cited Findings

**국방혁신 4.0과 MUM-T 단계**
- 2023-03-03 대통령 재가, 국방개혁 2.0 대체, 5대 중점·16개 과제(AI 기반 핵심 첨단전력 확보 포함). 국방개혁실장: "핵심 첨단전력은 기술발전 추세에 따라 원격통제형, 반자율형, 자율형으로 구분해 추진하겠다" — [문화일보](https://www.munhwa.com/article/11347333); [경향신문, 2023-03-03](https://www.khan.co.kr/article/202303031607001/amp) [검색 요약]
- "국방예산은 한국형 3축 체계, 유·무인 복합전투체계 구축 등에 우선 투자된다." — [문화일보](https://www.munhwa.com/article/11347281) [검색 요약]
- 각 군 브랜드: 육군 Army TIGER, 해군 Navy Sea GHOST, 공군 Killweb 유무인 복합전투체계, 해병대 IRON Marine — [KAIS 논문](https://kais99.org/jkais/journal/Vol24No04/vol24no04p61.pdf) [검색 요약]
- 방위사업청–Anduril 첨단 무인전투체계 공동개발 MOU(2025-04-02) — [뉴스서울](https://newsseoul.co.kr/news/view/1065584421846695) [검색 요약]
- K-MOSA(무인체계 계열화·모듈화) 정책 2024년부터 추진 — [보안뉴스](https://m.boannews.com/html/detail.html?idx=125297) [검색 요약]

**2025 국정감사에서 각 군이 제시한 MUM-T 목표** — [헤럴드경제, 2025-10-25](https://www.heraldk.com/article/2025102515000031679) [원문 확인]
- 육군: "AI 기반 지휘통제체계와 드론·로봇 무인체계를 통합한 유무인 복합전투체계를 2040년까지 완성하겠다는" 목표; 2027년까지 대대급 시범부대 통합 실증, 2030년까지 AI 통합관제플랫폼 전력화.
- 해군: "수직이착륙형 유인 전투기 중심의 기존 경항공모함(CVX) 대신 탑재 전력을 유인에서 무인 중심으로 전환한 3만t급의 한국형 유무인전력모함(MuM-T Carrier)", "2030년대 후반을 목표".
- 공군: AI 기반 유무인 복합전투체계 명칭 "'에어 가디언'(Air Guardian)".
- 해군참모총장: "인구절벽에 따른 병역자원의 감소와 드론, AI 첨단과학기술 발전에 따른 전쟁의 패러다임 변화는" 국방환경 전반의 개혁을 요구.

**육군 — 아미타이거 / 드론봇 전투단**
- 드론봇 전투단: 2018-09-28 경기 용인 제3야전군사령부(현 지상작전사령부) 예하 지상정보단 소속으로 창설, '드론 운용병' 신설 — [Daum/연합, 2018-09-28](https://v.daum.net/v/20180928100458053) [검색 요약]
- 아미타이거 시범여단(25사단) 2022-06 선포, 2040년까지 전 전투여단 전환 목표 — [뉴시스, 2023-01-13](https://mobile.newsis.com/view/NISX20230113_0002158624) [검색 요약]
- 2024-07~08 KCTC 아미타이거 보병여단 전투실험: 장병 2,400여 명, 드론 120여 대, 다족보행로봇 등 장비 390여 대 — [한국경제, 2024-09-26](https://www.hankyung.com/amp/2024092687121) [검색 요약; 원문 403]
- 2022-12 보도: 드론봇 기반 전투체계를 2025년까지 주요 부대, 2030년까지 전 부대 구축 목표 — [서울신문, 2022-12-28](https://m.seoul.co.kr/news/2022/12/28/20221228003015) [검색 요약] (2040 목표와 연도 상이)
- 2026-08 육군 전술시범단 창설(드론 군집비행, 다족로봇·무인차량 복합운용 시연) — [파이낸셜뉴스, 2026-08-28](https://www.fnnews.com/news/202608281340565048) [검색 요약]

**드론작전사령부(2023) → 국방드론본부(2026)**
- 입법예고(2023-04): 2022-12 북한 무인기 침투와 드론 활용 확대가 제정 이유 — [법제처 입법예고 첨부](https://opinion.lawmaking.go.kr/file/download/8803012/GDL5IYFWCP084PQ5ZO5K); 2023-09-01 창설, 국군 최초 합동전투부대, 합참의장 지휘·감독, 임무: 전략·작전적 감시정찰·타격·심리전·전자기전, 드론 전투발전 — [뉴데일리, 2023-09-01](https://www.newdaily.co.kr/site/data/html/2023/09/01/2023090100085.html) [검색 요약]
- 2026-06-26 국방부 '국방 드론·대드론 발전 정책' 발표: "정부는 드론사의 작전 수행 기능을 각 군으로 이관하고, 본부는 드론 전력 발전과 획득을 전담하는 기능 조직으로 재편하기로 했다." / "사령부 본부는 국방부 직속 '국방드론본부'로 전환해 드론·대드론 전투 발전과 전력 획득을 전담하는 '기능사령부'로 재편" / "모든 장병이 드론을 제2의 개인화기처럼 활용할 수 있도록 50만 드론 전사를 양성하겠다" / "한국형 장거리 자폭무인기(K‑LUCAS)를 2030년 이전 전력화하고 저가·소모성 드론 2만 대 이상을 확보" / 우려: 실권 없으면 "간판만 바뀐 셈이 될 수 있다" — [뉴데일리, 2026-06-26](https://www.newdaily.co.kr/site/data/html/2026/06/26/2026062600194.html) [원문 확인]
- 같은 발표: 교육용 국산 상용드론 약 6만 대 도입, 중고도 정찰드론은 공군으로, 국방드론본부는 국방부 직속·소장급 지휘, 단기 전방 대드론 체계 배치·중장기 레이저/HPM·저가 요격드론 — [세계일보, 2026-06-26](https://www.segye.com/newsView/20260626508032) [원문 확인]
- 드론사 예산 2년간 114억 2,000만 원 전액 미집행·반납 보도 — [Daum/시대, 2026-07-31](https://v.daum.net/v/20260731053209500) [검색 요약]

**50만 드론전사**
- 2026 예산: 정부안 약 205억 → 국회 330억 → 최종 293억 원, 핵심부품 국산화 교육용 드론 11,265대, 분대당 1대 이상 — [리포테라](https://www.reportera.co.kr/military/the-first-stage-of-implementation-of-the-500000-drone-training-policy/?amp=1); [헤럴드경제, 2025-12-30](https://www.heraldk.com/article/2025123019072662814) [검색 요약]
- 2026-07 교육용 상용드론 도입 계약 체결 — [뉴스서울](https://newsseoul.co.kr/news/view/1065610818157476) [검색 요약]
- 육군 36사단 '50만 드론전사 양성' 실증 전담부대 최초 지정(2025-09) — [헤럴드경제, 2025-09-03](https://www.heraldk.com/article/2025090318300009637) [검색 요약]
- 아이뉴스24(2026-09-03): "국방부는 지난 6월 드론·무인기 전력을 현재보다 약 30배 증강한다는 목표를 제시했다." / "군은 AI 기반 유·무인 복합전투체계로 증강한 병력 절감형 군 구조를 목표로 2040년 국방개혁 기본계획을 수립하고 있다." / "현재 60%인 병사 비중을 2040년 37%로 낮추고, 40%인 간부 비중은 63%로 높이는 방안이 담겼다." / "장병 50만명에게 드론을 한 대씩 지급하거나 별도의 조종사 50만명을 육성한다는 의미는 아니다." — [아이뉴스24, 2026-09-03](https://www.inews24.com/view/2001302) [원문 확인]

**해군 Navy Sea GHOST**
- 2022-11 공개, "Guardian Harmonized with Operating manned Systems and Technology based unmanned systems"; UUV·USV·UAV — [USNI News, 2022-11-17](https://news.usni.org/2022/11/17/south-korea-reveals-new-unmanned-navy-sea-ghost-concept); [Naval News, 2022-11](https://www.navalnews.com/naval-news/2022/11/south-korea-reveals-new-navy-sea-ghost-concept/) [검색 요약]
- 2026-09-08 KAIST 콘퍼런스("AI 대전환 시대, Navy Sea GHOST의 새로운 도약", 400여 명): 김경률 해군참모총장 "해군은 최고도의 준비태세를 갖추기 위해 AI 기반 유무인 복합전투체계인 Navy Sea GHOST를 단계적으로 발전시켜 나가고 있다"; 4대 과제 = 해양무인체계 AI·자율화 기술, **공통 아키텍처 구축**, 전투실험, 전력의 단계적 발전; 해군·ADD·KRISO MOU; 2023-06 부산작전기지 시연에 USV·UAV 30여 대 — [파이낸셜뉴스, 2026-09-08](https://www.fnnews.com/news/202609080904320627) [원문 확인]
- 한화시스템 MADEX 2023 Sea Ghost USV(12m, 최대 40kt, 소형 USV M-Searcher 4척 군집 통제) — [Janes, 2023-06-09](https://www.janes.com/defence-news/weapons-headlines/latest/madex-2023-hanwha-systems-displays-naval-mum-t-concept) [검색 요약]
- 정찰용 USV 체계개발 LIG넥스원 우선협상, LIG넥스원은 USV 통합제어체계에 정부 주관 "해양무인체계 공통아키텍처" 선적용해 다수·다종 USV 상호운용성 확보 — [뉴데일리 비즈, 2025-05-22](https://biz.newdaily.co.kr/site/data/html/2025/05/22/2025052200169.html) [검색 요약]
- 2022-10 국감 해군 업무보고: 3개 함대→2개 축소, '해양무인전력사령부' 창설 구상(병역자원 감소 반영) — [경향신문, 2022-10-21](https://www.khan.co.kr/article/202210211340001) [검색 요약]. 실제 창설 여부 미확인.

**병력 감소(인구절벽) 수치**
- KIDA 2024-02 연구보고서(뉴데일리 인용): "2035년까지는 상비병력 정원 50만 명 대비 3만~4만 명이 부족하게 운영될 것이며" / "2040년 35만 명, 2040년대 중반 31만~32만 명대 수준으로 상비병력이 운영될 것으로 판단하고 있다" / "장기적으로 30만 명대 수준"; 입영 대상 병역자원 2020년 약 33.4만 → 2041년 약 13만(기사 내 출처 미명시) — [뉴데일리, 2024-09-04](https://www.newdaily.co.kr/site/data/html/2024/09/04/2024090400360.html) [원문 확인]
- KIDA 분석(서울경제 보도): 상비병력 2039년 39만 3,000여 명, 2040년 36만 명 수준 — [서울경제](https://m.sedaily.com/article/13820088) [검색 요약]
- **KIDA 2026-07 분석**(권현진 선임연구위원, 병무청 '미래 병무정책 추진방향' 세미나): 현 추세 유지 시 **2045년 상비병력 약 19만 7,000명**, 최낙관 시나리오에서도 최대 34만 2,000명; 국방부 구상은 2040년대까지 "현역 37만 명·민간 아웃소싱 13만 명" — [Korea Daily(중앙일보 미주판), 2026-07-08](https://www.koreadaily.com/article/20260708200709936); [인사이트](https://www.insight.co.kr/news/562337) [검색 요약; 원문 URL 410]
- 병무청 자료(임종득 의원실, 중앙일보 2025-10-06): 20세 남성 2025년 약 22.4만, 2032년 약 25.2만(정점), 2037년 약 18.8만(20만 붕괴), 2040년 약 14.3만, 2044년 12만 명대; "이르면 2033년부터 현역 입대자 수가 10만 명대로 내려앉을 것으로 예상된다."; 상비병력 2022년 약 50만 → 2025-07 약 45만 — [Daum/중앙일보, 2025-10-06](https://v.daum.net/v/20251006170145067) [원문 확인]
- KIDA 「한국군의 적정 상비병력 규모에 관한 연구」(김정혁 외, 『국방정책연구』 2025 여름호): 미군 '최소계획비율'(공격 3:1, 방어 1:3) 근거로 최소 50만 필요; 2022 총병력 북한 128만 vs 한국 50만(약 2.6:1); 2040년 20세 남성 14만으로 30만도 채우기 어려울 수 있음 — [머니투데이, 2025-07-27](https://www.mt.co.kr/politics/2025/07/27/2025072714064940371) [원문 확인]
- 2040년 한국군 27만 vs 북한군 113만 전망 보도 — [머니투데이, 2025-09-21](https://www.mt.co.kr/politics/2025/09/21/2025091805094468719) [검색 요약]

**예산**
- 2026 국방예산 국회 확정 65조 8,642억 원(+7.5%), 방위력개선비 19조 9,653억 원(+11.9%); 확정 설명에 "소형무인기 유무인복합체계 등 AI기반 유·무인 복합전투체계 전력을 확대 반영" — [뉴스서울](https://www.newsseoul.co.kr/news/view/1065611414841122); [Daum, 2025-12-03](https://v.daum.net/v/20251203114748705) [검색 요약]
- 2026 정부안 단계 AI·드론 등 국방 R&D 5.9조 원 — [헤럴드경제, 2025-09-02](https://www.heraldk.com/article/2025090216224508810) [검색 요약]

### Inferences
- 한국 심사위원에게 가장 강한 메시지: "병사 1인당 운용 무인체계 수를 늘리는 것 = 인구절벽 대응". 근거 체인: 상비병력 50만 → 2045년 19.7만(KIDA) + 병사 비중 60→37% + 드론 30배 증강 + 50만 드론전사 → **운용자 수는 줄고 무인체계 수는 늘어 1인당 통제 대수가 필연적으로 증가**. (이 연결은 추론이며 공식 문서가 '1인당 몇 대'를 제시한 것은 아님.)
- 해군 4대 과제 "공통 아키텍처", LIG넥스원 "해양무인체계 공통아키텍처", 미 육군 "stove-piped controllers" 문제는 같은 문제를 가리킨다 → T1-1 데모의 "벤더 중립 어댑터 계층"을 한·미 양측 요구에 동시에 맞출 수 있음.
- 드론사 해체·개편(작전기능 각 군 이관)은 각 군이 이기종 무인체계를 **자체 소부대 단위로** 운용하게 됨을 의미 → 소부대용 단일 운용자 콘솔 수요의 근거(추론).

### Gaps
- 국방혁신 4.0 MUM-T 단계(원격→반자율→자율)의 연도별 목표 — 공식 원문 미확인.
- 2027 국방예산 정부안 금액: 검색 요약에 "73조 2,777억 원(+8.2%)"이 나왔으나 2026 확정액 대비 산술이 맞지 않아(약 +11%) 신뢰 불가 → 국방부 보도자료 확인 필요.
- 국방일보 원문, KIDA 보고서 원문 PDF 직접 열람 실패(언론 재인용 기반).
- "1인당 몇 대" 같은 한국군 공식 운용자 비율 요구치는 공개 자료에서 찾지 못함.

## Q5. 공식 요구문서가 말하는 운용자 워크로드·상호운용 표준(STANAG 4586, JAUS, MAVLink, UCI/OMS)·인간 통제 정책(DoDD 3000.09, 2023)

### Takeaway
DoDD 3000.09(2023-01-25 개정)은 "human-in-the-loop"를 일률적으로 강제하지 않고 "**appropriate levels of human judgment over the use of force**"를 요구하며, 인간-기계 인터페이스가 "readily understandable to trained operators"일 것을 규정한다(비무장 플랫폼은 적용 대상 아님). 표준은 층위가 다르다: STANAG 4586(NATO UAV 지상통제소 아키텍처), JAUS(SAE AS-4, 다중 노드·발견·접근제어), MAVLink(소형 오토파일럿 사실상 표준, 보안 취약 지적), UCI/OMS(미 공군 임무수준 C2 메시지). 학술 근거로는 "숙련 운용자 1명이 감독은 최대 15대, 통제(임무·탑재체 관리)는 최대 3대"(Porat 외 2016)가 자주 인용된다.

### Cited Findings

**DoDD 3000.09 "Autonomy in Weapon Systems" (2012 제정, 2023-01-25 개정)**
- 정책: 체계는 "will be designed to allow commanders and operators to exercise appropriate levels of human judgment over the use of force." / HMI: "readily understandable to trained operators." / 훈련: "Adequate training, [tactics, techniques, and procedures], and doctrine are available, periodically reviewed, and used by system operators." / "the ability to disengage or deactivate deployed systems that demonstrate unintended behavior." / 자율무기 정의: "weapon system[s] that, once activated, can select and engage targets without further intervention by a human operator." / 반자율: "only engage individual targets or specific target groups that have been selected by a human operator." / 고위 검토: "before formal development", "urgent military need" 시 면제 가능 — [Wikipedia: DoDD 3000.09](https://en.wikipedia.org/wiki/Department_of_Defense_Directive_3000.09) [원문 확인; 원 지침 PDF](https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodd/300009p.pdf)는 403으로 직접 열람 실패]
- 2023 개정 변경점(HRW 비교): operator 정의 "a person who operates a platform or weapon system"(이전의 "human" 삭제), "will provide sufficient confidence" 문구 신설, 교전을 "geographic area, as well as other applicable environmental and operational parameters" 내로 제한, 고위 검토 판단용 "flow chart" 추가 — [Human Rights Watch, 2023-02-14](https://www.hrw.org/news/2023/02/14/review-2023-us-policy-autonomy-weapons-systems) [원문 확인]
- 해석: 지침은 보편적 human-in-the-loop 의무를 부과하지 않는다는 논평 — [War on the Rocks, 2025-05](https://warontherocks.com/2025/05/AUTONOMOUS-WEAPON-SYSTEMS-NO-HUMAN-IN-THE-LOOP-REQUIRED-AND-OTHER-MYTHS-DISPELLED) [검색 요약; 의견 기고]. 적용 제외: 사이버, **비무장 플랫폼(unarmed platforms)**, 기뢰 등 — [Wikipedia](https://en.wikipedia.org/wiki/Department_of_Defense_Directive_3000.09) [검색 요약]
- 2026-01-09 국방부(전쟁부) AI 전략이 AI 계약에 "any lawful use" 문구 사용 지시, 3000.09는 공식 폐지되지 않음 — [SOFREP](https://sofrep.com/news/who-controls-the-kill-chain-the-pentagons-ai-rules-dont-agree/) [검색 요약; 2차 출처]
- (기억 기반·미검증) 2023 지침 원문에는 HMI가 "Provide traceable feedback on system status"와 "Provide clear procedures for trained operators to activate and deactivate system functions"를 하도록 하는 조항이 있는 것으로 알려져 있으나, 이번 세션에서 원문 PDF가 403이라 확인하지 못함 → `confidence: 추정`.

**운용자 워크로드 — 학술 기준치**
- Porat, Oron-Gilad, Rottem-Hovev, Silbiger (2016), *Frontiers in Psychology* 7:568, DOI 10.3389/fpsyg.2016.00568: "an experienced operator can supervise up to 15 UASs efficiently using moderate levels of automation" / "control (mission and payload management) up to three systems." / "one experienced operator cannot control more than three UASs." / "In general, teams led to better performances." / 단, 과업이 유사하거나 관심 지역이 겹치면 "one operator seems to have an advantage over a team" / "fully autonomous operations (automation level VI) are not expected any time soon." — [PMC4878290](https://pmc.ncbi.nlm.nih.gov/articles/PMC4878290/) [원문 확인]

**상호운용 표준**
- STANAG 4586: UAV 제어 시스템을 Air Vehicle, VSM(Vehicle Specific Module), DLI(Data Link Interface), CCI/CUCS(Core UAV Control System), 운용자 인터페이스로 구성; 단일 지상통제소가 다수 UAV와 연동 가능, 각 UAV는 점대점 링크 — [NATO STO EN-SCI-271-03](https://www.sto.nato.int/publications/STO%20Educational%20Notes/STO-EN-SCI-271/EN-SCI-271-03.pdf) [검색 요약]
- JAUS(SAE AS-4, AS5710A 등): 각 차량·운용 콘솔이 공유 네트워크의 노드, 서비스에 publish/subscribe 이벤트, **선점 가능한 배타적 접근제어(preemptable exclusive access control)**, 자동 발견(discovery), liveness 등 — [OpenJAUS "Understanding JAUS"](https://openjaus.com/understanding-jaus) [검색 요약]
- NATO STO IST-206: 협업 무인 지상차량 그룹 통제를 위해 JAUS·ROS와 군사 표준 상호운용성 연구 — [Royal Military Academy (BE) research portal](https://researchportal.rma.ac.be/en/activities/nato-sto-rtg-ist-206-interoperability-for-cooperating-unmanned-gr/) [검색 요약]
- MAVLink: ArduPilot·PX4 등 오토파일럿의 메시지 프로토콜, 민간에서 가장 널리 쓰이나 보안·통신 취약성 지적 — [Koubâa 외, "MAVLink in a Nutshell: A Survey" (arXiv 1906.10641)](https://arxiv.org/pdf/1906.10641) [검색 요약]
- MAVLink↔STANAG 4586 상호운용 비교·개선 연구(한국, 2020) — [KoreaScience JAKO202034965760632](https://koreascience.or.kr/article/JAKO202034965760632.page?&lang=ko) [검색 요약]
- UCI/OMS(미 공군 Open Architecture Management 관리): UCI는 공중체계 임무수준 기계-기계 C2 메시지 어휘, OMS는 SW 서비스-HW 서브시스템 간 인터페이스 계층 정의(구현 방식은 규정 안 함), 단계적 준수 — [AFRL VDL OAM brochure](https://www.vdl.afrl.af.mil/programs/oam/brochure.php); [OMS in a Nutshell](https://www.vdl.afrl.af.mil/programs/oam/OMS_Marketing.pdf) [검색 요약]. 2019년 육·해·공 장관 메모가 OMS/UCI를 개방형 표준으로 지정(SOSA, FACE, VICTORY와 함께) — [Military & Aerospace Electronics](https://www.militaryaerospace.com/home/article/16709609/pentagon-reinforces-mandate-for-open-systems-standards-like-sosa-face-and-victory) [검색 요약]
- 2026-08 Boeing·Northrop: P-8A–MQ-4C Triton 표준 기반 유무인 팀 시뮬레이션 — [Boeing, 2026-08](https://www.boeing.com/features/2026/08/boeing-northrop-grumman-advance-standards-based-teaming) [검색 요약; 업체 발표]
- 미 육군 2026-08 공모: MOSA 필수, FACE "where applicable"; MAVLink/ROS/UCI는 명시 안 됨 — [Inside Unmanned Systems](https://insideunmannedsystems.com/army-seeks-commercial-controllers-for-drones-and-ground-robots-under-new-c2-architecture/) [원문 확인]
- 한국: 해군 "공통 아키텍처 구축"(4대 과제) — [파이낸셜뉴스, 2026-09-08](https://www.fnnews.com/news/202609080904320627) [원문 확인]; 정부 주관 "해양무인체계 공통아키텍처" — [뉴데일리 비즈, 2025-05-22](https://biz.newdaily.co.kr/site/data/html/2025/05/22/2025052200169.html) [검색 요약]

### Inferences
- T1-1 데모의 무기 사용 단계는 반드시 "인간 승인 게이트"로 설계해 3000.09의 "appropriate levels of human judgment" 및 HMI 요건("readily understandable to trained operators", 비활성화 능력)에 맞춰야 함. 데모가 정찰·감시 중심이면 "unarmed platforms"로 지침 적용 외이지만, 심사위원(미군 장교) 질문 대비로 승인 게이트를 보여주는 것이 유리.
- Porat 2016의 "감독 15 / 통제 3" 수치는 "왜 3대 이상부터 인지부하 저감 UI가 필요한가"를 정량적으로 설명하는 가장 인용하기 쉬운 근거. T1-1의 "3+ 이기종"은 정확히 "직접 통제의 한계(3)"를 넘는 지점.
- 표준 층위 정리(추론): 기체 저수준 = MAVLink(UAV), JAUS/ROS(UGV) / 지상통제소 아키텍처 = STANAG 4586(VSM 개념 = 어댑터 패턴) / 임무수준 tasking = UCI. 데모에서 "VSM 스타일 어댑터 + 공통 임무 모델"을 언급하면 NATO 표준 언어로 설명 가능.

### Gaps
- DoDD 3000.09 원문 PDF 직접 확인 실패(403) — "traceable feedback", "activate and deactivate" 조항 문구는 미검증.
- 미국 공식 RFI/요구문서 중 "운용자 1인당 N대"를 정량 요구로 명시한 문서는 발견하지 못함(HMIF·CCA 모두 정성적).
- STANAG 4586 최신판(Ed.4 등)과 후속 AEP-84 관계, JAUS 현행판 상태(판매처마다 AS5710 withdrawn vs AS5710A current 표기 불일치) — 미확인.
