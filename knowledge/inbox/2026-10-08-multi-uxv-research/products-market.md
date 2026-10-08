# 단일 운용자 다중·이종 무인체계(Multi-UxV) 지휘통제: 상용 제품·시장·도입 경로 조사

> 조사일·모든 URL 접근일: **2026-10-08** (아래 "접근 2026-10-08" 표기는 동일 의미).
> 목적: KDTH 2026 T1-1(1인 운용자가 공중·지상·해상 무인체계 3대 이상을 동시에 임무 할당·감시·통제하면서 인지부하를 줄이는 문제)의 차별화 아이디어 근거.
> 표기 규칙
> - [1차] 회사·정부 공식 발표, [언론] 국방 전문지·일반 언론, [2차] 집계·프로필·블로그 사이트, [마케팅] 회사 자체 주장(독립 검증 없음), [미검증] 단일 2차 출처라 교차확인 못함.
> - 따옴표 안 영어/한국어 문장은 원문 발췌. "(검색 스니펫)"이라고 적은 것은 검색엔진이 원문에서 뽑아 보여준 문장이고 페이지 전체는 열어보지 못한 것.
> - 2023년 이전 정보는 연도를 명시.

## 1. Anduril Lattice (Lattice for Mission Autonomy, Lattice Mesh): 운용자 워크플로·비율 주장·이종 체계·공개 시연

### Takeaway
Anduril은 2023년부터 "하드웨어 무관(hardware-agnostic) + 운용자 의도를 과업으로 자동 분해 + 인간 감독" 구조를 내세운다. 2024년 IBP 24.1에서 공중·수상·수중 이종 자산 10여 종을 Lattice로 묶은 시연이 가장 구체적이다. "1명이 수백 대" 같은 비율은 2023년 회사 주장일 뿐 2025-26년에 갱신된 정량 수치는 공개되지 않았다. 2025년 10월에는 육군 NGC2 프로토타입이 "very high risk"라는 내부 보안 평가를 받았다.

### Cited Findings
**제품 개념과 운용자 워크플로**
- (2023-05) [1차·마케팅] Lattice for Mission Autonomy 출시 문구: "a hardware-agnostic, end-to-end software platform that enables teams of diverse robotic assets to work together under human supervision." (접근 2026-10-08) — [Anduril blog](https://blog.anduril.com/anduril-unveils-lattice-for-mission-autonomy-8e0c5fa0e94b) / [Anduril news](https://www.anduril.com/news/anduril-unveils-lattice-for-mission-autonomy)
- (2023-05) [언론] 회사 주장으로 "1명이 수백 대 무인체계를 통제할 수 있다"고 보도됐다. CEO는 "no technology limitations"라고 말함 — [Breaking Defense, 2023-05](https://breakingdefense.com/2023/05/andurils-new-tech-could-allow-single-operator-to-control-hundreds-of-autonomous-systems/)
- (2023) [언론] 운용자 의도를 개별 과업으로 자동 분해해 무인체계에 배분하는 기능: "automatically breaks down operator intent into discrete tasks, distributing them across unmanned systems to best accomplish missions under human supervision." 같은 기사는 이름과 달리 완전 자율이 아니라고도 지적함: "not fully autonomous, and still requires human oversight." (검색 스니펫, 접근 2026-10-08) — [Maginative](https://www.maginative.com/article/anduril-announces-lattice-for-mission-autonomy-an-ai-powered-platform-to-manage-drone-swarms/)
- (2023, EDGE23 @ Yuma) [언론] 병사 1명이 여러 제조사 항공기를 계획·지휘함. ALTIUS-600 변형 3대와 Textron Aerosonde HQ를 사용했고, 연동된 항공기들이 SAM 진지를 찾아 타격하는 시나리오도 시연됨 — [EX2 (Anduril 호주 협력사 게시)](https://www.ex2.com.au/news/anduril-demonstrates-enhanced-autonomy-os-at-us-armys-edge23/)

**이종(공중·수상·수중) 시연 — IBP 24.1 (2024-04)**
- [1차] Anduril 보도자료 제목: "Anduril demonstrates multi-domain unmanned systems command and control, undersea, and airborne capabilities at US Navy's IBP 24.1" (본문은 렌더링 안 됨) — [Anduril](https://www.anduril.com/news/ibp-24-1-command-and-control)
- [언론] "Anduril used its Lattice software to command and control teams of heterogeneous unmanned and autonomous assets operating in the air, on the sea, and below the surface across the Southern California Offshore Range." (검색 스니펫, 접근 2026-10-08) — [Unmanned Systems Technology, 2024-04](https://www.unmannedsystemstechnology.com/2024/04/unmanned-and-autonomous-systems-simultaneously-coordinated-with-command-and-control-software/)
- [언론] 연동 규모: "Lattice's open APIs and software development kit were used for rapid integration of more than a dozen different uncrewed systems and data feeds." (검색 스니펫) — 같은 출처
- [언론] Dive-LD(AUV)를 Lattice로 과업 할당해 120시간 임무를 완수함. 협력사 USV 여러 척에 고속 항행을 할당하고 협력사 USV에서 Altius를 발사함: "Operators tasked Dive-LD to navigate a series of undersea waypoints, tasked multiple partner USVs to conduct high-speed navigation, and executed multiple successful Altius launches from partner USVs." (검색 스니펫) — 같은 출처

**Lattice Mesh·개방성**
- [2차] Lattice Mesh는 센서·이펙터·지휘소 사이에 데이터와 과업을 분산 전달하는 탈중앙 메시라고 설명됨: "a decentralized mesh network, Lattice Mesh, which securely distributes data and tasks between sensors, effectors, and command posts, even over long distances and in contested environments." 이 출처는 국방부가 Lattice Mesh 기반 "Edge Data Mesh"를 발주했다고도 쓰지만 1차 출처는 확인 못함 — [warwingsdaily](https://warwingsdaily.com/anduril-lattice-the-open-os-that-brings-autonomy-to-combat/)

**프로그램·계약**
- (2024-11-20) [1차] DIU Replicator "Autonomous Collaborative Teaming(ACT)" 트랙: 132개사 165개 솔루션 중 Swarm Aero, Anduril, L3Harris가 프로토타입 계약을 받음. L3Harris는 UI·협업 자율·체계 통합 담당. DIU 목표는 "heterogeneous collaboration" — [DIU](https://www.diu.mil/latest/defense-innovation-unit-announces-software-vendors-to-support-replicator), [Defense One](https://www.defenseone.com/defense-systems/2024/11/diu-announces-software-awards-ai-enabled-drone-swarms/401197/), [Anduril](https://www.anduril.com/news/diu-selects-anduril-to-enable-collaborative-autonomy-for-replicator-systems)
- [1차] Ghost Shark(XL-AUV): 호주 해군이 A$1.7B(US$1.12B) Program of Record로 발주했고 이미 생산 중 — [Anduril](https://www.anduril.com/news/ghost-shark-enters-program-of-record-from-prototype-to-fleet-in-three-years). Ghost Shark는 Lattice for Mission Autonomy로 장기 임무를 자율 관리함(Anduril 담당자 발언: "This is actually a masterclass in use of Lattice.") — [The War Zone](https://www.twz.com/news-features/everything-we-just-learned-about-the-ghost-shark-uncrewed-submarine)
- [2차·미검증] Fury(YFQ-44A) CCA: 공군이 기체와 임무 자율 소프트웨어를 별도 계약으로 구매함(Reuters 인용). 2026-06 기준 자율 SW 풀은 6개사(GA, Lockheed, Northrop, Collins, Shield AI, Anduril)이고 단일 공급자 선정 목표는 2027년 여름 — [Venture Atlas](https://www.ventureatlas.org/company/anduril)
- (2025-03) [2차·미검증] USMC 10년 C-sUAS 계약, SOCOM 3년 mission autonomy SW 계약 — [Baidu Baike(신뢰도 낮음)](https://baike.baidu.com/en/item/Lattice/3141912)

**비판·리스크**
- (2025-10) [언론] 육군 CTO 내부 메모가 Anduril 주도 NGC2(차세대 지휘통제) 프로토타입을 "very high risk"로 평가함: "We cannot control who sees what, we cannot see what users are doing, and we cannot verify that the software itself is secure." 검토되지 않은 3rd-party 앱 1개에서 고위험 취약점 25건이 나옴. Anduril은 "The recent report reflects an outdated snapshot, not the current state of the program"이라고 반박. NGC2 프로토타입은 $100M 규모이고 Palantir·Microsoft가 협력사 — [Reuters via TradingView](https://de.tradingview.com/news/reuters.com,2025:newsml_L2N3VK0G9:0-anduril-and-palantir-battlefield-communication-system-very-high-risk-us-army-memo-says), [The Defense Post](https://thedefensepost.com/2025/10/09/us-army-security-platform-prototype/amp/)

**한국 관련**
- [언론] Anduril Industries Korea 서울 법인 설립(4월, 아시아 최초 법인. 기사상 연도 표기 확인 필요) — [이투데이](https://www.etoday.co.kr/news/view/2489593)
- HD현대·대한항공 협력은 4번 섹션 참조.

### Inferences
- Lattice의 핵심 차별점은 "의도 → 과업 분해 → 이종 자산 배분"과 "개방 API/SDK로 3rd-party 체계 연동"이다. 해커톤 데모에서 이 두 기능을 작게나마 재현하면 심사위원(미군)에게 익숙한 문법으로 보인다.
- 공개 자료는 "무엇을 연동했나"는 자세하지만 "운용자 화면에서 어떻게 보이고 1명이 실제로 몇 대를 감당했나(측정치)"는 비어 있다. 이 빈칸이 차별화 지점이다.
- NGC2 메모는 "빠른 통합 vs 접근통제·감사(audit)" 긴장을 보여준다. 운용자 행동 로그와 권한 표시를 데모에 넣으면 이 비판을 정면으로 다루는 셈이 된다.

### Gaps
- 2025-26년 Lattice 운용자 UI 스크린샷, 운용자:기체 비율 실측치는 공개 자료에서 찾지 못함.
- Fury CCA의 실제 자율 SW 공급자(Lattice인지 Hivemind인지) 1차 확인 실패. 2차 출처에 Hivemind 탑재 언급이 있으나 원문 미확인.
- Barracuda 관련 운용자 워크플로 자료는 이번 조사에서 찾지 못함.

## 2. Shield AI Hivemind (Hivemind Enterprise / Commander / V-BAT Teams): 팀 자율·"pilot-to-many"·다중 기체 시연·한국 파트너십

### Takeaway
Shield AI는 "AI 파일럿(Hivemind)"을 다양한 기체에 이식하는 SDK·플랫폼(Hivemind Enterprise)을 판다. 다중 기체 근거는 (a) 2023년 V-BAT 3대 GPS/통신 없는 팀 비행, (b) 2026-05 LUCAS 선정("single operator to command multiple platforms", 가을 시연 예정)이다. 한국에서는 KAI(2025-03), 현대로템(2025-10, HR-셰르파 군집 제어 포함), LIG넥스원(V-BAT 탄 시험)과 협력하며, 독점 파트너는 퀀텀에어로다.

### Cited Findings
**제품 구조**
- (2022) [1차] Hivemind 생태계는 엣지 SW, 개발·분석 환경, "end user and their trainers"용 SW로 나뉨 — [Shield AI, 2022-08](https://shield.ai/hivemind-for-operational-read-and-react-swarming/)
- (2025-04) [2차] Commander는 "Mission planning and C2 tools that allow operators to direct autonomous systems while incorporating human oversight." — [Contrary Research](https://research.contrary.com/report/shield-ai)
- (2025-03) [1차] Hivemind Enterprise 구성: "integrated autonomy factory, industrial-grade production ready middleware, a rich autonomy catalog, and seamless mission control." F-16, V-BAT, 쿼드콥터에서 비행 실적이 있음 — [Shield AI–KAI 보도자료(Kyodo PR)](https://kyodonewsprwire.jp/release/202503216075)
- [2차] 26종 기체(vehicle classes)에서 비행했다고 함 — [Sacra](https://sacra.com/c/shield-ai/)

**다중 기체 시연·운용 개념**
- (2023) [언론] V-BAT Teams: V-BAT 3대가 Hivemind 지휘로 GPS·통신 없이 산불 탐지·식별·위치·보고 임무를 수행함(North Dakota Devil's Lake, AFWERX STRATFI). 운용자는 목표·임무만 지정하고 사람이 필요할 때만 알림을 받음. 출시 시 팀 규모는 4대, 매년 2배 목표(2024년 8대, 이후 16대). Tseng은 물리적 발진·회수 로지스틱스가 병목이라고 언급 — [Defense News, 2023-10-10](https://www.defensenews.com/unmanned/2023/10/10/shield-ai-unveils-v-bat-teams-drone-swarm-tech-with-eye-to-replicator/), [Inside Unmanned Systems](https://insideunmannedsystems.com/shield-ai-demonstrates-ai-piloted-teaming-v-bats-with-afwerx/)
- (2026-05-19) [1차] LUCAS(저가 일회용 공격 드론)에 Hivemind 통합. 원문 발췌(접근 2026-10-08): "enabling a single operator to command multiple platforms at once" / "Humans remain in control of strike decisions while autonomy manages navigation, coordination, and execution." / "an operational demonstration this fall." 군집 대수는 명시 안 됨("large numbers"). 통신 환경은 "communications-constrained environments" — [Shield AI](https://shield.ai/?p=15350)
  - Brandon Tseng 인용: "LUCAS is about delivering affordable mass, but mass without coordination is limited in value." / "Hivemind is the AI pilot that makes that mass intelligent." — 같은 출처
  - [2차·미검증] "10대 이상" 군집이라는 블로그 수치는 1차 확인 실패 — [ai2.work](https://ai2.work/blog/shield-ai-wins-pentagon-drone-swarm-contract-at-12-7b-valuation)
- (2026-02) [2차·미검증] 대만 NCSIST 협약: 지상통제소 1개가 여러 무인 플랫폼을 감독하는 구성이고, GPS·통신 재밍 하 팀 운용을 겨냥함(검색 요약 기준, 원문 미확인. 아래 URL이 해당 기사인지도 미확인) — [Taiwan News](https://www.taiwannews.com.tw/en/news/6300973)
- (2026 초) [2차·미검증] HII ROMULUS USV에서 Shield AI와 통합 자율 시험을 마쳤다는 업계 블로그 보도 — 검색 요약 기준(1차 미확인)
- [언론] 인도 육군: V-BAT 기체 + Hivemind 자율 SW·개발 키트 라이선스(연도 미확인) — [Calibre Defence](https://www.calibredefence.co.uk/?p=5732)

**한국 파트너십**
- (2025-03-20) [1차] KAI와 Hivemind Enterprise 기반 AI 파일럿 협력. KAI의 유무인 복합(crewed-uncrewed teaming) 강화가 목적이고, 퀀텀에어로(Quantum Aero)가 "exclusive technology partner in Korea"로 통합을 맡음 — [Kyodo PR](https://kyodonewsprwire.jp/release/202503216075), [Airforce Technology](https://www.airforce-technology.com/news/shield-ai-kai/), [뉴스스페이스](https://newsspace.kr/mobile/article.html?no=6219)
- (2025-10-23, ADEX) [1차] 현대로템 MOU. 원문 발췌(접근 2026-10-08): "applying autonomous mission technologies, capable of responding to asymmetric threats on the battlefield." 단계는 ① 차세대 지상무기에 드론 탑재 ② "autonomous mission execution, swarm control … such as the multi-purpose unmanned vehicle HR-SHERPA or legged robots" ③ "integrated command and control of various types of MUM-T weapon systems." 기반 SW는 Hivemind Enterprise이고 퀀텀에어로가 협력 — [Shield AI](https://shield.ai/?p=14965), [Military Embedded Systems](https://militaryembedded.com/unmanned/test/ai-based-drone-operation-tech-to-be-co-developed-by-hyundai-rotem-shield-ai)
- [언론] LIG넥스원이 드론발사 유도탄 L-MDM을 V-BAT에 장착해 비행·발사 시험하는 계약(검색 요약 기준, 날짜·정확한 출처 URL 특정 못함. 후보: [파이낸스스코프 2026-01-22](https://www.finance-scope.com/article/view/scp202601220011), [비즈한국](https://bizhankook.com/articles/31593.html))

**자금**
- [2차] $12.7B 밸류에이션에 $1.5B 조달(이전 $5.3B 대비 약 140%↑)이라는 보도와, 2026-03 Series G $2B라는 보도가 엇갈림 — [The Next Web](https://thenextweb.com/news/shield-ai-2-billion-hivemind-autonomous-defence), [ai2.work](https://ai2.work/blog/shield-ai-wins-pentagon-drone-swarm-contract-at-12-7b-valuation)

### Inferences
- Shield AI의 판매 문법은 "AI 파일럿을 다른 회사 기체에 넣는다"(기체 측 자율)이고, 운용자 쪽 C2(Commander)는 상대적으로 덜 알려져 있다. 따라서 "기체 자율은 각 사 것을 그대로 두고 운용자 의도 계층만 통일"하는 방향(DIU Orchestrator와 같은 방향)은 Shield AI와 겹치지 않는 포지션이다.
- 현대로템 MOU 3단계("다종 MUM-T 통합 지휘통제")는 아직 미래 과제다. 한국 지상 유무인 복합의 1인 다종 통제 UI는 공백 상태로 보인다.
- V-BAT·Swarmer 모두 "SW보다 발진·회수 로지스틱스가 병목"이라고 말한다. 데모에서 발진 대기·재보급 상태를 시각화하면 현장감이 생긴다.

### Gaps
- Hivemind Commander의 실제 화면·운용자:기체 비율 수치는 공개 자료에서 찾지 못함.
- LUCAS 가을 2026 시연 실시 여부와 결과(조사일 기준 보도 없음).
- "EdgeOS"라는 Shield AI 제품명은 확인되지 않음(Hivemind Enterprise/Commander만 확인).

## 3. Auterion 및 기타 함대·군집 단일 운용자 제품 (Swarmer, Helsing, Palladyne/Red Cat, Skydio, Saronic, HavocAI, Overland AI, Applied Intuition, Scale AI, Palantir 등)

### Takeaway
"1 operator : N vehicles" 주장은 이제 업계 표준 마케팅 문구다. 다만 실증 규모는 대체로 3~8대이고(Auterion 3대, Swarmer 통상 3대·최대 8대, V-BAT 3대), 동종 기체 위주다. 공중·지상·해상을 섞은 진짜 이종 1인 운용은 Anduril IBP 24.1, Palladyne Ivy Mass(이종 UAS), Saronic의 "heterogeneous fleet of ASVs"(해상 내 이종) 정도다. 대부분의 업체가 "치명적 결정은 사람이, 항법·협응·종말유도는 자율"이라는 같은 분업을 내세운다.

### Cited Findings
**Auterion (Auterion OS / Skynode / Nemyx)**
- (2026-01-13, Camp Blanding FL) [1차·언론] 원문 발췌(접근 2026-10-08): "A single operator assigned objectives and authorized effects for three drones" / Nemyx·Skynode가 "handled navigation, formation control, deconfliction and terminal guidance" / "an 'early preview' of the Department of War's Swarm Forge program." / Lorenz Meier: "The one-pilot, one-drone model is obsolete." / 회사 주장: "validated a 1:N operator-to-target ratio under realistic range conditions." — [Inside Unmanned Systems](https://insideunmannedsystems.com/auterion-demonstrates-one-operator-drone-swarm-strike-in-u-s-live-fire-test/)
- [언론] 구조: 중앙 계획기가 표적·우선순위를 할당하고, 이륙 후에는 각 기체가 같은 군집 엔진을 로컬로 실행함. 1대를 잃으면 다른 기체가 그 표적을 재할당받음. Meier: "Even if all communication is lost, each drone will use its best efforts to hit its target." 다른 제조사 기체를 섞는 군집이 목표(공통 SW 계층 + 부착형 항전) — [Interesting Engineering](https://interestingengineering.com/military/pentagon-operator-three-targets-drone-swarm), [Resilience Media](https://resiliencemedia.co/auterion-conducts-live-fire-swarm-drone-strike-test/)
- [1차·마케팅] Nemyx 제품 페이지 원문(접근 2026-10-08): "Nemyx turns autonomous drones into a single, coordinated combat force." / "it amplifies the operator's effectiveness, reduces workload, and ensures mission success" / "works with your existing drones" / "With over 50,000 Skynode S units already in service". 이종·다제조사 지원과 통신두절 동작은 페이지에 명시 없음 — [Auterion Nemyx](https://auterion.com/product/nemyx/)
- (2025-07) [언론] 국방부 $50M 계약으로 우크라이나에 AI strike kit 33,000개 공급(종전 대비 10배). 운용자가 표적을 고른 뒤에만 자율 작동 — [The Register](https://www.theregister.com/2025/07/29/auterion_drone_ai_ceo_interview/), [Decrypt](https://decrypt.co/332212/us-taps-swiss-firm-massive-ai-drone-shipment-ukraine)
- [2차] 2025-09 Series B $130M, 밸류 $600M 이상(Bessemer 주도). CB Insights 추정 2025 매출 약 $115M(미감사) — [DroneXL 프로필](https://dronexl.co/de/drone-companies/auterion/), [robotics.press](https://www.robotics.press/news/auterion-competitive-response-anubis-merz-zelensky/)
- [2차·미검증] Nemyx를 영국 육군에도 시연("Commanded by a single operator…") — [LinkedIn 프로필 게시물](https://ua.linkedin.com/in/zach-ferrigno)

**Swarmer (우크라이나)**
- (2025-09, WSJ 보도의 2차 인용) [언론] 실전 상시 운용 첫 사례라는 평가. 정찰 1대 + 폭탄 탑재 2대 구성이 일반적이고, 일부 부대는 최대 8대 동시 운용. 운용 인원 9명 → 3명(planner, navigator, operator). 한 장교에 따르면 100회 이상 사용. CEO: 운용자가 탐색 구역을 지정하고 표적 발견 시 공격을 명령함. 병목은 SW가 아니라 물자: "Each drone requires a team that will carry it, prepare it, check it. This is what limits the scale." 초기 임무에서 네트워크 과부하 — [To Vima (WSJ 재게재)](https://www.tovima.com/wsj/ai-powered-drone-swarms-have-now-entered-the-battlefield), [Ukrainska Pravda](https://www.pravda.com.ua/eng/news/2025/09/03/7529154/)
- (2025-09) [언론] Series A $15M(Broadband Capital 주도). "우크라이나 방산테크 최대 공개 투자"라는 주장. 누적 $17.9M. Styx AI 기반 Swarmer Platform으로 1인 20대 이상 "potentially" 가능하나 실제 운용 수는 더 적음. 시험 최대 25대(GNSS 거부 환경). 공중·수상·지상·고정 발사대까지 100대 이상으로 확장 계획 — [DroneXL](https://dronexl.co/2025/10/13/ukrainian-drone-swarm-startup-swarmer), [Kyiv Post](https://www.kyivpost.com/amp/post/60321), [Vestbee](https://vestbee.com/blog/articles/swarmer-raises-15-m)

**Helsing (HX-2 + Altra)**
- (2024-12) [1차·마케팅] HX-2를 Altra(recce/strike SW)와 결합하면 "can be controlled in swarms by a single human operator"(검색 스니펫). Altra가 다수 HX-2를 ISR 자산·포병·전장관리 SW와 협응시킴. 데이터링크 없이 표적 탐색·재식별·타격이 가능하지만 "critical decisions"는 사람이 내림 — [Helsing](https://helsing.ai/newsroom/helsing-unveils-intelligent-strike-drone-for-mass-and-precision), [New Atlas](https://newatlas.com/military/helsings-ai-strike-drone-hx-2/)
- (2026-07-13) [언론] $18B 밸류에이션에 $1.8B 조달(CNBC). 다른 출처는 $1.2B로 엇갈림 — [CNBC](https://www.cnbc.com/2026/07/13/helsing-fund-raise-defense-18-billion.html)

**Palladyne AI (SwarmOS/IntelliSwarm) + Red Cat**
- (2026-02) [1차·마케팅] SwarmOS + BRAIN X2 비행컴퓨터(IntelliSwarm)가 자사 Banshee 배회탄과 Red Cat 드론과의 자율 협업으로 첫 비행. 통합에 3주 걸림. GPS·통신 거부 하에서도 동작한다고 주장 — [Unmanned Systems Technology](https://www.unmannedsystemstechnology.com/2026/02/palladyne-ai-validates-decentralized-edge-autonomy-heterogeneous-swarming/), [defence-industry.eu](https://defence-industry.eu/palladyne-ai-completes-first-flight-of-intelliswarm-autonomy-stack-milestone-on-banshee-and-red-cat-platforms/)
- (2026-06) [1차·마케팅] 4보병사단 Ivy Mass 연습: 운용자 1명이 이종 ISR 드론 + Gremlin-X 소형 폭격 드론을 지휘하고 표적 트랙을 육군 NGC2 프로토타입으로 보냄. 통신 경합 환경에서 동작 주장(보도자료 페이지는 403으로 직접 열람 실패, 검색 요약 기준) — [BusinessWire](https://secure.businesswire.com/news/home/20260616412957/en/Palladyne-AI-Deploys-True-Autonomy-Drone-Swarming-Software-SwarmOS-During-U.S.-Army-4th-Infantry-Division-Ivy-Mass-Exercise)
- (2026-08) [언론] Project Convergence Capstone 6(PC-C6, "largest Project Convergence experiment conducted to date")에서 SwarmOS 운용 시험 — [Las Vegas Sun](https://lasvegassun.com/news/2026/aug/06/palladyne-ais-swarmos-successfully-performs-again-/)
- [1차] Red Cat 군집 페이지는 Palladyne, Sentien Robotics, Apium Swarm Robotics를 파트너로 나열 — [Red Cat](https://redcat.red/swarming/)
- [마케팅] Palladyne 블로그는 운용자 인지부하 감소와 최소 연산·제한된 기체 간 통신을 주장 — [Palladyne blog](https://www.palladyneai.com/blog/autonomous-swarming-takes-flight-the-next-era-of-uav-operations/)

**Skydio (도크·원격 운용 — 민간/공공안전 쪽 1:N 규제 선례)**
- (2025-09~2026-03) [1차·언론] FAA 기관별 승인으로 원격 PIC 1명이 X10 최대 4대를 동시 운용하는 승인을 12개 공공안전 기관이 받음(첫 사례 LVMPD 2025-09, NYPA 2026-01). 두 번째 호출이 오면 두 번째 드론을 보내고 첫 드론의 복귀·착륙은 Skydio Autonomy가 처리함. 기존 BVLOS 웨이버는 1조종사 1드론이 기본 — [DroneXL, 2026-03-28](https://dronexl.co/2026/03/28/skydio-faa-multi-drone-bvlos-approval/), [Skydio blog](https://www.skydio.com/blog/bvlos-introducing-multi-drone-operations)
- [언론] 비교 사례: Matternet 20:1 웨이버(특정 시험장 한정, 2023), Percepto 1인 최대 30개 drone-in-a-box — [DroneLife, 2023-02](https://dronelife.com/2023/02/13/20-drones-1-pilot-matternets-new-waiver-could-change-the-economics-of-drone-delivery)
- (2026-03) [언론] 육군 X10D 2,500대 이상 발주(약 $52M). X10D는 RAS-A Interoperability Profile 준수 — [DroneDJ](https://dronedj.com/2025/05/06/skydio-x10d-drone-us-army/), [defence-blog](https://defence-blog.com/u-s-army-buys-2500-reconnaissance-drones-from-skydio/)

**Saronic (Echelon) — 해상**
- (2025-07-30) [1차] 원문 발췌(접근 2026-10-08, Seapower 게재 보도자료 PDF에서 추출): "Echelon allows a single operator to plan, simulate, and execute complex missions across multiple autonomous assets using a single interface." / "…reducing cognitive load for operators." / "combines ultra-low-latency video streaming with intelligent, autonomy-aware alerts … By surfacing only the most relevant data … Echelon helps operators stay focused" / "Saronic ASVs are uniquely capable of operating independently without persistent communications" / CTO Vibhav Altekar: "a vertically integrated system across both software and hardware will best enable our end users … While our vessels remain compatible with third-party C2 systems, Echelon was purpose-built to unlock the full potential of Saronic's autonomy stack" / "one-to-many operations, where a single operator can command and control a heterogeneous fleet of ASVs" — [Seapower Magazine](https://seapowermagazine.org/saronic-unveils-echelon-a-unified-platform-for-mission-planning-simulation-and-command-and-control-of-autonomous-surface-vessels/)
- (2026-06-08) [2차] 무인 Corsair가 호르무즈 해협 인근에서 육군 항공병 2명 구조에 기여(원래 감시 임무로 약 10주 전 배치) — [drone-warfare.com](https://drone-warfare.com/research/saronic-corsair/)
- [2차] 2025년 초 Series C $600M(밸류 약 $4B), 이후 $1.75B 조달로 밸류 $9.25B — [techbuzz.ai](https://www.techbuzz.ai/articles/defense-tech-startup-saronic-raises-1-75b-for-autonomous-warships)

**HavocAI — 해상 이종 함대**
- [언론] Metal Shark 협력: "allow a single operator to conduct complex operations involving multiple Metal Shark USVs simultaneously". 특정 선체·제조사에 묶이지 않는 이종 자율을 표방("eliminates the constraints of single-vendor solutions"). 미 해군·육군 사용 주장(날짜 미확인) — [Marine Log](https://www.marinelog.com/news/metal-shark-partners-with-swarm-autonomy-specialist-havocai/), [Baird Maritime](https://www.bairdmaritime.com/security/naval/unmanned-naval-systems/american-boatbuilder-and-ai-company-partner-on-unmanned-vessel-swarm-technology)
- [2차] 2025-10 Series B $85M(B Capital 주도, 누적 약 $97M). 2025-11 SAIC 협력으로 Link-16·JREAP에 HavocAI 데이터 연동 — [Sacra](https://sacra.com/c/havocai)
- 한화와의 협력은 4번 섹션 참조.

**Overland AI (ULTRA + OverWatch) — 지상**
- (2025-06, Fort Leonard Wood) [1차·마케팅] ULTRA 2대로 실전형 시나리오 15개 진행, 거의 전 과정을 병사가 수행함. 지형조성 임무 2개 병렬 계획(경유점 20개 이상, 기체당 과업 5개)을 3분 미만에 작성. 적 활동에 따라 임무 중 차량 재할당. OverWatch 교육 몇 시간 만에 "independent mission planning and multi-vehicle tasking capability" 확보 — [StreetInsider (GlobeNewswire)](https://www.streetinsider.com/Globe+Newswire/Overland+AI+Demonstrates+Soldier-Led+Autonomy+Across+Day+and+Night+Operations/24917720.html), [Military & Aerospace Electronics](https://www.militaryaerospace.com/uncrewed/article/55378431/overland-ai-demonstrates-autonomous-maneuver-and-battlefield-networking-in-joint-military-exercise)
- [2차] OverWatch는 1인이 자율 지상차량 군집을 조정·통제하는 인터페이스로 소개됨 — [OODA Loop](https://oodaloop.com/company-profiles/defense-tech/overland-ai/)

**Applied Intuition (Axion / Acuity)**
- (2025-05) [1차] Axion(개발·시뮬레이션 툴체인)과 Acuity(탑재 자율 SW)를 출시. Acuity는 2025년 인수한 EpiSci 기술 기반이며, X-62A VISTA 자율 공중전 시험 실적이 있음. "reducing the need for vertical integration"을 표방 — [Kyodo PR](https://kyodonewsprwire.jp/release/202505209193), [Applied Intuition Defense](https://www.appliedintuitiondefense.com/)

**Scale AI Thunderforge / Palantir**
- (2025-03) [언론] DIU가 Scale AI를 Thunderforge 주관사로 선정. 모델링·시뮬레이션, 의사결정 지원, 방책(COA) 제안, 자동 워크플로를 다루며 INDOPACOM·EUCOM부터 적용. 협력사는 Anduril·Microsoft. 이것은 작전 계획 계층이지 기체 통제가 아님 — [getcoai](https://getcoai.com/news/scale-ai-wins-pentagon-contract-to-bring-ai-agents-to-military-planning), [ODSC](https://opendatascience.com/scale-ai-secures-multimillion-dollar-defense-contract-for-ai-powered-military-operations/)
- Palantir는 NGC2 협력사로만 확인됨(1번 섹션). 다중 UxV 직접 통제 제품은 이번 조사에서 확인 못함.

**기타 참고 (업체·연구)**
- [언론] Lockheed Martin MDCX 자율 플랫폼 + XTEND OS: 단일 운용자가 여러 종류 UAV를 동시에 통제하고, 큰 무인기가 소형 Class 1 드론을 근접 임무에 투입함 — [UK Defence Journal](https://ukdefencejournal.org.uk/skunk-works-links-with-xtend-for-multi-drone-control/)
- [연구, 2021] Sandia "One-Control-Many": 운용자 1명이 무인 지상·공중 3~6대 팀을 "임무 결과 단위"로 지시함 — [Sandia](https://www.sandia.gov/research/one-control-many/)
- [언론] 미 육군 SCORCH: 자율 행동 + UI로 운용자 1명이 최대 3대 UAS를 동시 통제하도록 설계. 아파치 사수가 1대에서 여러 대로 늘면 인지 병목이 생긴다는 연구 — [Warrior Maven](https://warriormaven.com/land/army-technology-accelerates-helicopter-drone-attacks)
- [시장 보고서 언급] Elbit Torch-X, General Dynamics FTUAS GCS도 소프트웨어 C2 계층 사례로 거론 — [MarketsandMarkets](https://www.marketsandmarkets.com/Market-Reports/unmanned-c2-c3-market-74094713.html)

### Inferences
- 공개 실증의 "N"은 대체로 3~8이다. 해커톤 문제의 "3대 이상 이종"은 업계 최전선 시연 규모와 겹친다. 심사위원 눈에는 "대수"보다 "이종 + 인지부하 측정"이 차별점이다.
- 회사 간 공통 패턴(운용자 = 목표·우선순위·교전 승인 / 자율 = 항법·편대·충돌회피·종말유도 / 손실 시 자동 재할당 / 통신두절 시 마지막 의도 유지)은 데모 기능 목록으로 그대로 쓸 수 있다.
- Saronic의 "autonomy-aware alerts / surfacing only the most relevant data"와 Skydio의 "두 번째 호출 → 두 번째 기체 배치, 첫 기체는 자율 복귀"는 인지부하 감소 UI의 구체적 선례다(예외 기반 알림, 자동 인계).
- Saronic(수직통합)과 Applied Intuition·HavocAI·Auterion(벤더 중립)의 대립은 "상호운용성"이 시장의 핵심 쟁점이라는 신호다.

### Gaps
- 어느 회사도 운용자 인지부하를 정량 측정(NASA-TLX 등)한 공개 결과를 내지 않았다(학술 연구 제외).
- Palladyne Ivy Mass·Echelon 실제 운용자 화면, 동시 운용 대수는 공개 자료에서 확인 못함.
- Red Cat 자체 다중 기체 GCS 상세, Sentient 계열 제품은 이번 조사에서 다루지 못함.
- Scale AI/Palantir의 다중 무인체계 직접 C2 제품은 찾지 못함.

## 4. 한국 업체·한국군의 다중 무인체계 / 유무인복합(MUM-T) C2

### Takeaway
한국군의 유무인복합은 계획·실증 초기 단계다. 육군은 2026년 분대급 실증(8명 = 전투원 4 + 무인체계 운용요원 4, 플랫폼 4종)으로 사실상 운용자 1명 : 플랫폼 1종에 가깝다. 업체 측은 해외 자율 SW(Shield AI, Anduril, HavocAI)와 짝을 맺는 형태가 지배적이다. 국산 다중 무인 통합관제 쪽은 한화시스템 해상 다종 동시통제 시연(2026-08)과 파블로항공의 "1명이 수십 대" 군집조율 주장(마케팅)이 대표적이다. 지상·공중·해상을 한 화면에서 섞는 국산 1인 C2 제품은 확인되지 않았다.

### Cited Findings
**한국군 계획·실증**
- (2025-10, 국정감사) [언론] 육군은 AI 기반 지휘통제와 드론·로봇 무인체계를 통합한 유무인 복합전투체계를 2040년까지 완성하겠다는 목표를 밝힘. 2027년까지 대대급 시범부대를 선정해 AI 지휘체계·드론·대드론·지상로봇 통합 실증. 공군은 킬웹(Kill-Web) 개념의 유·무인 전투임무기 복합체계를 3단계로 추진 — [헤럴드경제, 2025-10-25](https://www.heraldk.com/article/2025102515000031679)
- (2026-07-29) [언론] 원문 발췌(접근 2026-10-08): "분대는 전투원 4명과 무인체계 운용요원 4명, 총 8명으로 우선 편성됐다." / "운용되는 무인 플랫폼은 드론, 다족형 로봇(로봇개), 다목적 무인차량, 자율주행차량 등 4종으로, 임무별로 조합이 달라진다는 점이 특징이다." / "육군은 올해 분대급 실증을 시작으로 내년(2027년)에는 중대급, 2028년에는 대대급까지 실증 규모를 순차적으로 넓히겠다고 밝혔다." 운용자 1인당 대수와 인지부하는 언급 없음 — [뉴스스페이스](https://www.newsspace.kr/news/article.html?no=15018)
- [미검증] 2026 항공우주무기체계 기술발전 컨퍼런스에서 저가 소모성 자폭드론(K-LUCAS) 운용개념이 소개됐다는 개인 뉴스레터 요약 — [maily.so 뉴스레터](https://maily.so/sheldon/posts/2qzpgeyxz4x)

**한화시스템 (해상 다종 동시통제)**
- (2026-08-03) [1차·언론] 부산 해군작전사령부 기지에서 "AI 기반 유·무인 복합 전투체계 대기뢰전" 시연. AI 생성 임무계획에 따라 AUV가 기뢰를 탐색하고 AMDS(자동기뢰탐지체계)로 실시간 전송, 무인수상정·소해함이 소해함. 육상 통제소에서 Eutelsat OneWeb LEO 위성통신으로 AUV와 무인수상정 2종을 동시 운용·통제. "다수·다종의 무인체계를 동시에 통제할 수 있는 통합 지휘통제 기술"도 시연 — [한화시스템 보도자료](https://www.hanwhasystems.com/kr/prcenter/newsView.do?bbidx=812), [뉴시스](https://www.newsis.com/view/NISX20260803_0003734434)
- [언론] 군집 협업 과제는 3개이며 1·2과제는 LIG넥스원, 3과제는 한화시스템 담당(기사 날짜 미확인) — 검색 스니펫 기준([비즈한국](https://bizhankook.com/articles/31593.html) 등 결과 묶음)

**LIG넥스원**
- (2026-02, DSK 2026) [언론] 국방과학연구소 주관 "캐니스터 발사(다연장 발사형) 방식의 군집 운용이 가능한 자폭형 소형 무인기"(AI 기반 군집무인기) 첫 공개. LIG넥스원은 "체계종합과 AI 분야"에 참여. 자폭·정찰·수송 통합 무인기 솔루션도 전시 — [헤럴드경제, 2026-02-26](https://www.heraldk.com/article/2026022621310025978), [CEO스코어데일리](https://ceoscoredaily.com/page/view/2026022514460275943)

**KAI**
- [언론] KF-21, 자체 개발 전투기, 다목적 무인기 MUCCA·SUCA를 연동하는 "차세대 공중전투체계(NACS)"를 개발 중. 회전익 + 무인기 + AI 임무체계 결합도 추진 — [아이뉴스24, 2026-09-01](https://inews24.com/view/2000225)
- [언론] 차재병 대표: "미래 전장은 유인과 무인이 하나의 팀으로 통합 운용되는 방향으로 빠르게 진화하고 있으며, 그 중심에는 AI 기반 자율·지능화 기술이 있다" (DSK 2026 관련 보도, 검색 스니펫) — [메트로서울](https://www.metroseoul.co.kr/article/20260223500541)
- Shield AI Hivemind Enterprise 협력(2025-03)은 2번 섹션 참조.

**현대로템 (HR-셰르파)**
- [언론] 2026-02 사우디 WDS에서 C-UAS 결합 HR-셰르파 첫 공개("레이다가 드론을 탐지해 방어 체계를 구축하고 경계·감시 임무를 수행"). 2026-04 YIDEX에서 파블로항공·토리스스퀘어와 협력한 대드론 셰르파 UGV 공개(중동 수출 겨냥 해석). 2026-06 드론·감시장비·대전차미사일 탑재형 공개 — [현대자동차그룹 뉴스](https://www.hyundaimotorgroup.com/ko/news/hyundai-rotem-wds-2026-saudi-defense-exhibition), [딜사이트](https://dealsite.co.kr/articles/164767), [미주중앙일보](https://www.koreadaily.com/article/20260624140045875)
- [언론] 국내 다목적 무인차량 독자 개발사는 현대로템과 한화에어로스페이스 두 곳뿐이고 경쟁 관계 — [다음/서울경제 2024](https://v.daum.net/v/20240409070035843)
- Shield AI MOU(2025-10, HR-셰르파·다족로봇 군집 제어 → 다종 MUM-T 통합 C2)는 2번 섹션 참조.

**한화에어로스페이스·한화오션 계열**
- [언론] 아리온스멧(Arion-SMET)이 2028년부터 전력화 예정(보병과 함께 선두 정찰·수색). 미 국방부 FCT 비교시험을 하와이 해병대 훈련장에서 3주 진행(과거 보도) — [아이뉴스24](https://inews24.com/view/2000225), [문화일보](https://www.munhwa.com/article/11210224)
- (2025-10~2026-01) [언론] 한화–HavocAI: 거제에서 하와이 인근 HavocAI 탑재 USV를 원격 조종하는 시연(2025-10-28), 전략적 협력 검토(10-29), HavocAI Series B 투자 참여. 이후 한화디펜스USA·한화시스템·HavocAI가 200피트급 ASV 공동개발(필리 조선소 후보, 미 해군 MASC 연계) — [Maritime Executive](https://maritime-executive.com/article/hanwha-teams-up-with-american-swarming-boat-ai-startup-havoc), [WorkBoat](https://www.workboat.com/shipbuilding/hanwha-havocai-to-develop-200-autonomous-surface-vessels), [ESD](https://euro-sd.com/2025/10/major-news/47457/hanwha-and-havocai-teaming/)

**HD현대·대한항공 × Anduril**
- (2025-04 MOU → 2025-08 MOA) [언론] HD현대는 함정 자율화, Anduril은 "무인수상정들의 군집제어 및 임무수행을 자동화하는 자율 임무 수행 체계 개발"을 담당. 국내 시장은 HD현대 USV에 Anduril 임무자율 탑재, 미국 시장은 Anduril 주도 함정을 HD현대가 설계·건조 — [시대일보](https://www.sidae.com/article/2025040409135358006), [한국경제](https://www.hankyung.com/article/202508077552i), [뉴시스](https://mobile.newsis.com/view/NISX20251027_0003377998)
- (2025-04-02 MOU → 2025-08-07 TA) [언론] 대한항공–Anduril 자율형 무인기(AAV) 공동개발 + 아태 수출 거점화. DSK 2026에서 공동 개발 중인 아음속 무인기 공개 — [KPI뉴스](https://kpinews.kr/newsView/1065577194799480), [헤럴드경제](https://www.heraldk.com/article/2026022621310025978)

**국내 스타트업 — 파블로항공 (군집조율·통합관제)**
- (2025-07-30) [언론·마케팅] 원문 발췌(검색 스니펫, 접근 2026-10-08): "총 5단계로 구분되는 군집조율 기술은 단계가 높을수록 오퍼레이터 수는 줄어들고, 무인기 간 자율성과 협업 수준은 높아진다." / "4단계부터는 수십 대의 무인기를 단 한 명의 조종자가 통제할 수 있으며, 정밀 타격이나 저고도 정찰 등 복잡한 군사작전에도 투입이 가능해진다." 국내 최초 4단계 도달을 주장하고 '항공무기체계 기술발전 컨퍼런스 2025'에서 군과 공유 — [유니콘팩토리](https://www.unicornfactory.co.kr/article/2025073009445511499)
- [언론] 군집조율 = 메시통신 기반 자율비행·임무 협업, 8대 요소기술(지능형 분산 임무 통제, AI 예측·의사결정, 자율 탐지·회피 등). 국방 브랜드 PabloM(2025-02). DSK 2026에서 정찰(R10s/R20s)·공격(S10s/S20s, "살보 스트라이크")·요격(C05s/C10s) 3축 군집 라인업 공개 — [CEO스코어데일리](https://ceoscoredaily.com/page/view/2026022516282499579), [유니콘팩토리](https://www.unicornfactory.co.kr/article/2025022411573831542)
- [언론] 2023 '방산혁신기업 100' 2기 선정. 과제는 "군집드론 중심의 유·무인 협업 체계 개발"(소형 회전익 / 중형 VTOL / 대형 고정익을 고도별 3구간으로 나눠 다수 무인기 통제) — [유니콘팩토리, 2023-10](https://www.unicornfactory.co.kr/article/2023101013121185009)
- (2025-10 MOU → 2026-01 전략투자) [언론] 대한항공이 자사 중대형 무인기에 파블로항공의 군집AI 자율비행 알고리즘·통합관제 플랫폼 접목 계획 — [유니콘팩토리](https://www.unicornfactory.co.kr/article/2025102314494091338), [헬로티](https://hellot.net/mobile/article.html?no=106902)

**심사 관련 단체 — 한국대드론산업협회(KADIA)**
- [언론] 회장 양병희. 2025-11 청주 오스코에서 국내 최초 대드론 특화 박람회 'KOREA C-UAS 2025' 주최(육군방공학교 특별후원), '국방 대드론 협력센터' 출범 — [헤럴드경제, 2025-11](https://www.heraldk.com/article/2025110318194636521)
- [언론] 코리아스타트업포럼과 MOU를 맺고 방산 스타트업 기술의 "현장 검증" 연결 — [벤처스퀘어](https://www.venturesquare.net/1117629/)

### Inferences
- 한국군 분대 실증 비율(운용요원 4명 / 플랫폼 4종)은 "운용자 1명 ↔ 플랫폼 1종"에 가깝다. 해커톤 데모의 서사는 "이 4명을 1명으로 줄이거나, 4명이 각자 더 많은 대수를 맡게 한다"로 잡으면 한국 육군 로드맵(2027 중대급, 2028 대대급)과 바로 연결된다.
- 국내 대기업 협력이 모두 "외산 자율 SW + 국산 플랫폼" 구조라서, 국산 벤더 중립 운용자 계층(의도 → 플레이북 → 각 사 자율)은 주권·수출통제 측면에서도 논리가 선다(추정).
- KADIA가 심사위원이므로 대드론(C-UAS) 위협 대응을 다종 무인체계 임무 시나리오로 쓰면 공감대를 얻기 쉽다. 현대로템·파블로항공의 대드론 셰르파가 실제 사례다.

### Gaps
- 한국군 유무인복합 C2 체계의 공식 사업명·예산·발주처(방사청 공고)는 확인 못함.
- 국내 업체의 다중 이종(공·지·해) 단일 운용자 GCS 제품 사양은 찾지 못함.
- 퀀텀에어로, 본에이아이 등 국내 국방 AI 스타트업의 다중 무인 제품 상세는 이번 조사 범위 밖.

## 5. 시장 규모 추정과 최근 투자·인수 (2024-2026)

### Takeaway
"UxV C2 소프트웨어"만 따로 잰 신뢰할 만한 수치는 드물다. 가장 근접한 것은 MarketsandMarkets의 무인 C2/C3 시스템 시장(2025년 약 $4.2B → 2035년 약 $16.8B, CAGR 15%)이다. 보고서마다 정의가 달라 수치 편차가 100배까지 난다. 더 강한 신호는 정부 예산과 투자다. DAWG FY2027 요청 약 $54.6B(대부분 조정법안 조건부), DIU Orchestrator 상금 $100M, Anduril $61B·Saronic $9.25B·Helsing $18B·Shield AI $12.7B 밸류에이션이 있다.

### Cited Findings
**시장 보고서 (모두 유료 보고서 요약이며 방법론 비공개)**
- [시장보고서] MarketsandMarkets 무인 C2/C3: "USD 4,200 million in 2025 … USD 16,800 million by 2035", CAGR 15%(2026-2035). 추세 서술: "Dedicated ground stations built around one vehicle are being replaced by software-led command layers". 예시로 Anduril Lattice, Shield AI Hivemind, GD FTUAS GCS, Elbit Torch-X 언급(검색 스니펫) — [MarketsandMarkets](https://www.marketsandmarkets.com/Market-Reports/unmanned-c2-c3-market-74094713.html)
- [시장보고서] MarketsandMarkets 무인체계 전체: $27.13B(2024) → $43.54B(2030), CAGR 8.2%. 국방이 최대 응용 분야 — [MarketsandMarkets](https://www.marketsandmarkets.com/Market-Reports/unmanned-systems-market-18210274.html)
- [시장보고서] Astute Analytica 드론 군집 시장: 약 $3.2B(2025) → $20B(2035), CAGR 20.1%. SW만이 아닌 기체·방어 포함 — [Astute Analytica](https://www.astuteanalytica.com/industry-report/drone-swarm-market)
- [시장보고서] Roots Analysis 드론 소프트웨어 전체: $7.92B(2025) → $48.75B(2035). 군집 특화 아님 — [Roots Analysis](https://www.rootsanalysis.com/drone-software-market)
- [시장보고서] Lucintel 국방 MUM-T 시장: 2035년 $16B, 연 13.8% — [Lucintel](https://lucintel.com/defense-manned-unmanned-teaming-system-market.aspx)
- [2차 분석] 군집 가능 체계(플랫폼·조율 SW·통신·대군집 포함) 주소 가능 시장 2030년 $40-60B("moderate confidence"), 가치는 조율 SW 계층에 집중된다고 주장. 같은 페이지는 군집 시장 $28.7M(2025)이라는 상충 수치를 인용함(단위 오류 가능) — [robotics.press](https://www.robotics.press/news/drone-swarm-competitive-landscape/)
- [시장보고서·출처 혼선] 군용 로봇 $42.15B(2026) → $128.92B(2031), CAGR 25.1%. 다른 보고서 URL에 붙어 있어 귀속 확인 필요 — [MarketsandMarkets(ML 보고서 URL)](https://www.marketsandmarkets.com/MarketReports/machine-learning-market-218.html)

**정부 예산 신호**
- [언론] DAWG(Defense Autonomous Warfare Group) FY2026 $225.9M. FY2027 요청 약 $54.6B($1B 기본 + $53.6B 조정법안 조건부) — [Defense One, 2026-05](https://www.defenseone.com/ideas/2026/05/pentagons-54-billion-bet-autonomous-warfare/413735/), [Forecast International DSM, 2026-05-21](https://dsm.forecastinternational.com/2026/05/21/a-new-dawg-in-the-fight-the-pentagons-54-billion-bet-on-autonomous-warfare/)
- [언론] DIU 2024 예산 $983M(전년 대비 7배 이상), 2024-11 AI 기반 C2 등 SW 개발사들과 총 $1B 규모 계약 (검색 요약 기준, 아래 두 기사 중 하나) — [헤럴드경제](https://www.heraldk.com/article/2026022216300023084), [MTN](https://news.mtn.co.kr/news-detail/2026040816371870009)
- [언론] 국방부가 소형 드론 30만 대 이상의 신속 획득·배치를 추진(2025-12, 기사 제목 기준) — [Military Times](https://www.militarytimes.com/unmanned/2025/12/03/pentagon-seeks-to-acquire-rapidly-field-over-300000-small-drones/)

**투자 (2024-2026)**
- [언론] Anduril: 2026-05 Series H $5B, 밸류 $61B(a16z·Thrive 주도). 1년 전 $30.5B의 두 배 — [Crunchbase News](https://news.crunchbase.com/defense-tech/anduril-5b-valuation-vc-funding-record-data/)
- [2차] Shield AI: $12.7B 밸류(조달액 $1.5B vs $2B로 엇갈림) — [The Next Web](https://thenextweb.com/news/shield-ai-2-billion-hivemind-autonomous-defence)
- [2차] Saronic: 2025년 초 $600M(약 $4B) → 이후 $1.75B(밸류 $9.25B) — [techbuzz.ai](https://www.techbuzz.ai/articles/defense-tech-startup-saronic-raises-1-75b-for-autonomous-warships)
- [언론] Helsing: 2026-07 $1.8B, 밸류 $18B — [CNBC](https://www.cnbc.com/2026/07/13/helsing-fund-raise-defense-18-billion.html)
- [2차] Auterion: 2025-09 Series B $130M, 밸류 $600M 이상 — [DroneXL](https://dronexl.co/de/drone-companies/auterion/)
- [2차] HavocAI: 2025-10 Series B $85M(B Capital, 한화 참여) — [Sacra](https://sacra.com/c/havocai)
- [언론] Swarmer: 2025-09 Series A $15M — [Kyiv Post](https://www.kyivpost.com/amp/post/60321)
- [2차·미검증] 방산테크 VC 투자액: 2025년 $9.6B(사상 최대), 2026년 이미 $14.6B 이상이라는 집계. 다른 리스트는 2025년 $49.1B로 방법론 차이가 큼 — [Crunchbase News 2025 snapshot](https://news.crunchbase.com/defense-tech/funding-hits-record-high-2025-snapshot/), [ValueAdd VC](https://valueaddvc.com/pulse/defense-tech-funding-record-2026-analysis)

**인수**
- [1차] Applied Intuition의 EpiSci 인수(Acuity의 기반) — [Kyodo PR, 2025-05](https://kyodonewsprwire.jp/release/202505209193)

### Inferences
- 시장 보고서 수치는 정의 차이가 커서 피치에서는 하나만 쓰고 출처·연도를 함께 표기하는 편이 안전하다(예: "무인 C2/C3 $4.2B(2025, MarketsandMarkets)").
- 돈의 흐름은 "기체"보다 "다종 기체를 묶는 소프트웨어 계층"으로 이동 중이다. M&M 서술, DAWG의 "software that can be installed on any cheap drone frame" 방향, $100M Orchestrator가 모두 같은 방향을 가리킨다.

### Gaps
- UxV C2 "소프트웨어"만의 신뢰할 만한 시장 규모는 찾지 못함. 유료 보고서 본문 필요.
- 2024-2026 다중 무인 C2 분야 M&A(예: Palladyne의 Banshee 확보 경위)는 1차 확인 실패.
- 한국 내 유무인복합·군집 SW 시장 규모 추정치는 찾지 못함.

## 6. 기존 제품이 잘 풀지 못하는 것(갭)과 비판

### Takeaway
공개 근거로 확인되는 미해결 영역은 다섯 가지다. ① 벤더 간 상호운용성(국방부가 $100M 상금으로 "vehicle-agnostic orchestrator"를 따로 사야 할 정도) ② 운용자 인지부하의 정량 측정·적응(제품 쪽에는 공개 측정치가 거의 없고 연구에서는 과부하가 빈번) ③ 통신 저하 시 C2·네트워크 과부하 ④ 보안·접근통제·감사 ⑤ 신뢰·설명가능성(운용자가 군집이 무엇을 하는지 이해하는 것). 현장 병목이 SW가 아니라 발진·회수 로지스틱스라는 지적도 반복된다.

### Cited Findings
**상호운용성·벤더 종속**
- (2026-01-13) [1차] DIU·DAWG·해군이 $100M 상금 Autonomous Vehicle Orchestrator 챌린지를 출범함. 원문 발췌(접근 2026-10-08): "translate a battlefield commander's intent from voice, text, and haptic input into machine execution" / "vehicle-agnostic capability for understanding, tasking and coordinating autonomous systems" / "The challenge will include iterative sprints, tackling increasingly complex portions of the problem." / DAWG 국장 LtGen Frank Donovan: "We want orchestrator technologies that allow humans to work the way they already command." 그리고 "the human - the ethical decision maker - always maintains a clear understanding of what the system is doing." / DIU Emil Michael: "If a company can deliver, they will receive substantial rewards." "If they can't, we will move on." — [DIU](https://www.diu.mil/latest/diu-and-dawg-launch-autonomous-vehicle-orchestrator-prize-challenge)
- [언론] 공모 요구사항(검색 요약): 음성·텍스트·GUI 의도를 플랫폼 "playbook" 옵션에 매핑하고, 플랫폼이 이미 내보내는 데이터로 함대 상황을 인식하며, 갱신된 의도를 내려 함대 제약을 적용함. 기존 기체 자율 스택·차량 제어 계층을 수정하지 않아야 함. 마감 2026-01-25. Donovan은 지휘관이 "clicking through menus or programming behaviors"를 하지 않게 하겠다고 말함 — [ExecutiveGov](https://www.executivegov.com/articles/diu-dawg-navy-challenge-av-orchestrator), [DIU 공모 페이지(현재 404)](https://www.diu.mil/work-with-us/submit-solution/PROJ00643)
- [언론] NODA AI가 $100M 수주를 주장했으나 연방 공고는 다수 수상 상금 구조임. SBA 기록상 NODA의 관련 Phase I은 $74,504("vendor-agnostic orchestration of heterogeneous autonomous systems") — [RuntimeWire](https://runtimewire.com/article/noda-ai-100m-autonomous-military-command-contract)
- [언론] Replicator는 2025-08 "수천 대" 목표를 놓쳤고 DAWG로 흡수됨(해체 vs 편입으로 표현이 엇갈림). 수백 대 인도, 수천 대 계약. 한 지휘관은 필요량이 그 10배라고 말함 — [MeriTalk](https://www.meritalk.com/articles/replicator-drone-initiative-earns-good-grades-two-years-in/), [CRS IF12611](https://www.congress.gov/crs-product/IF12611)
- [언론·검색 요약] Replicator가 "massive swarms of different drones"를 오케스트레이션할 SW 조달에 실패했다는 평가와 DAWG의 "software that can be installed on any cheap drone frame" 우선순위(정확한 문장 출처는 아래 둘 중 하나, 원문 미확인) — [Defense One](https://www.defenseone.com/ideas/2026/05/pentagons-54-billion-bet-autonomous-warfare/413735/), [Forecast International DSM](https://dsm.forecastinternational.com/2026/05/21/a-new-dawg-in-the-fight-the-pentagons-54-billion-bet-on-autonomous-warfare/)
- (2026) [언론] CDAO Swarm Forge 공고: "For Swarm Forge, heterogeneous swarming implies multi-vendor UAS command, control and autonomy." / "The United States currently lacks the inventory and the doctrine to deploy massed, coordinated, low-cost robotic systems." Crucible 행사 군집 최소 4대 동시 운용 요건 — [DefenseScoop, 2026-03-31](https://defensescoop.com/2026/03/31/pentagon-preparing-drone-swarm-crucible/), [MeriTalk](https://www.meritalk.com/articles/dod-seeks-proposals-for-autonomous-drone-swarm-initiative/)
- [1차] Saronic CTO가 수직통합을 지지하고 Echelon은 자사 자율 스택 전용이라고 밝힘(3번 섹션 원문) — [Seapower](https://seapowermagazine.org/saronic-unveils-echelon-a-unified-platform-for-mission-planning-simulation-and-command-and-control-of-autonomous-surface-vessels/)
- (2025-10) [연구] CNA: 신규 소·중형 드론 플랫폼을 기존 전투체계에 통합하기 어렵다고 지적함. 미 해군 "드론 군집 모함" 개념은 함상 C2 관리 문제로 일부 실패 — [CNA](https://www.cna.org/reports/2025/07/PRC-Concepts-for-UAV-Swarms-in-Future-Warfare.pdf)

**인지부하·운용자 한계**
- [연구] 운용자 1명이 감당할 수 있는 대수("fan-out")는 상호작용 시간뿐 아니라 재정향(reorientation) 지연과 대기 시간에 제약됨. 개별 지휘는 세밀하지만 확장성이 낮고, 군집 수준 지휘는 부하가 낮지만 군집이 무엇을 하는지 가려짐 — [Bjurling et al., ISCRAM WiP](http://ojs.iscram.org/index.php/Proceedings/article/download/257/189), [Cummings, DoD CCRP](http://www.dodccrp.org/files/IC2J_v1n2_01_Cummings.pdf)
- [연구] 인간-군집 상호작용 프로토타입으로 1인 20대 이상 운용(인지부하 감소의 예비 증거). 운용자가 "frequently shift between individual drones or sub-swarms while keeping track of overall swarm behavior" — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S3050741325000291)
- [연구] 다중 드론 SAR(혼합현실): 여러 영상 피드 감시와 다중 계획이 높은 인지부하와 상황인식 저하를 낳음 — [ACM DOI](https://doi.org/10.1145/3829807.3829828)
- (2021 시험, 2023 논문) [연구] DARPA OFFSET FX-6: 군집 지휘관 1명이 이종 로봇 약 100대를 운용함. 다면 워크로드 추정으로 보면 과부하 임계를 "frequently" 넘었지만 임무는 완수함. IEEE Spectrum은 과부하 시간을 약 3%로 요약함(측정 방식 차이 가능). 실제로는 2명이 교대함 — [arXiv 2308.00102 (Field Robotics 3:837-881)](https://arxiv.org/abs/2308.00102v1), [IEEE Spectrum](https://spectrum.ieee.org/darpa-robot), [DARPA](https://www.darpa.mil/news/2021/offset-swarms-take-flight)
- [언론] 아파치 사수가 무인기 1대에서 여러 대로 늘면 인지 병목이 생김 → SCORCH는 최대 3대 UAS 동시 통제를 목표로 설계 — [Warrior Maven](https://warriormaven.com/land/army-technology-accelerates-helicopter-drone-attacks)
- [마케팅] 업체 쪽 인지부하 주장은 정성적임: Saronic "reducing cognitive load for operators", Auterion "reduces workload", Palladyne "reduces the cognitive load". 정량 측정 공개는 없음 — [Seapower](https://seapowermagazine.org/saronic-unveils-echelon-a-unified-platform-for-mission-planning-simulation-and-command-and-control-of-autonomous-surface-vessels/), [Auterion](https://auterion.com/product/nemyx/), [Palladyne](https://www.palladyneai.com/blog/autonomous-swarming-takes-flight-the-next-era-of-uav-operations/)

**통신 저하·네트워크·보안**
- [언론] Swarmer 초기 임무에서 네트워크 과부하가 발생함 — [To Vima (WSJ)](https://www.tovima.com/wsj/ai-powered-drone-swarms-have-now-entered-the-battlefield)
- (2025-11) [정책 브리프] 중앙집중 제어는 단일 실패점이고, 탈중앙 메시는 혼잡 주파수·재밍·스푸핑·허위데이터 주입에 노출됨. 군집 운용 개념에 대한 국제 합의 부재 — [IPRI Policy Brief](https://ipripak.org/wp-content/uploads/2026/01/Swarm-Drones-1.pdf)
- (2025-10) [언론] NGC2 "very high risk" 메모(1번 섹션)

**로지스틱스 병목**
- [언론] Swarmer CEO: "Each drone requires a team that will carry it, prepare it, check it. This is what limits the scale." / Shield AI Tseng: 다수 기체 동시 발진·회수가 어려움 — [To Vima (WSJ)](https://www.tovima.com/wsj/ai-powered-drone-swarms-have-now-entered-the-battlefield), [Defense News](https://www.defensenews.com/unmanned/2023/10/10/shield-ai-unveils-v-bat-teams-drone-swarm-tech-with-eye-to-replicator/)

**운용자:기체 비율 주장 정리표 (출처는 위 각 섹션)**

| 주체 | 주장/실증 | 성격 | 연도 |
|---|---|---|---|
| Anduril LfMA | 1명이 "수백 대" 가능 | 회사 주장 | 2023 |
| Anduril EDGE23 | 병사 1명이 이종 4대(ALTIUS-600×3 + Aerosonde) | 시연 | 2023 |
| Shield AI V-BAT Teams | 3대 팀 비행, 4대 → 매년 2배 목표 | 시연 + 목표 | 2023 |
| Shield AI LUCAS | "single operator … multiple platforms", 대수 미공개 | 계획(가을 시연) | 2026 |
| Auterion Nemyx | 1명 : 3대 : 표적 3개 실사격 | 시연(회사 해석 "1:N") | 2026-01 |
| Swarmer | 통상 3대, 최대 8대, 시험 25대, 9명 → 3명 | 실전 + 시험 | 2025 |
| Pablo Air | 4단계부터 "수십 대 1명" | 회사 주장 | 2025 |
| Skydio | FAA 승인 PIC 1명 : X10 최대 4대 | 규제 승인(민간) | 2025-26 |
| Percepto / Matternet | 1명 : 30 도크 / 20:1(시험장 한정) | 규제 승인(민간) | ~2023 |
| DARPA OFFSET | 지휘관 1명(교대 2명) : 이종 약 100대 | 연구 시험 | 2021 |
| 미 육군 SCORCH | 1명 : 최대 3 UAS | 설계 목표 | — |
| Sandia OCM | 1명 : 3~6대 | 연구 | 2021 |
| 한국 육군 유무인 분대 | 운용요원 4명 : 플랫폼 4종 | 실증 편성 | 2026 |

### Inferences
- 해커톤 차별화 후보(추정): (a) DIU Orchestrator 요구사항을 축소 구현한 "의도(텍스트/음성) → 플레이북 → 각 기체 자율" 계층과 벤더 어댑터 3종(공·지·해 시뮬). (b) 인지부하 계측 내장: 운용자 상호작용 수, 화면 전환, 응답 지연, 미처리 알림 큐를 실시간 지표로 표시하고 과부하 시 자동 위임·알림 묶음. 업계 공개 측정이 없는 영역이다. (c) 통신 저하 시 "마지막 의도 유지 + 재연결 시 상태 재동기화"를 시각화. (d) 왜 이 기체에 이 과업을 줬는지 설명하는 패널(Donovan 발언 "clear understanding of what the system is doing"과 연결). (e) 승인·감사 로그(NGC2 비판 대응).
- 대수 경쟁(수백 대)은 데모 신뢰성을 떨어뜨린다. "3~5대 이종 + 측정된 부하 감소"가 심사위원(미군·업계)에게 더 설득력 있을 것이다.

### Gaps
- 상용 제품의 인지부하 정량 평가(NASA-TLX, 이차과업 등) 공개 자료는 찾지 못함.
- 다중 UxV 운용 중 오인사격·사고 등 실패 사례 공개 보고는 찾지 못함.
- STANAG 4586, UK SAPIENT 등 상호운용 표준이 다중 UxV 단일 운용자 C2에서 실제로 얼마나 채택됐는지는 이번 조사에서 확인 못함.

## 7. 도입·수출 경로 (US DIU/Replicator·DAWG·Swarm Forge, Oregon Pendleton/SOAR, 한국 신속획득, 수출)

### Takeaway
미국은 DIU 상용 솔루션 공모(CSO)와 상금형 챌린지(Orchestrator $100M), CDAO Swarm Forge(분기별 Crucible, 90일 내 "validated swarm packages"), DAWG 예산이 주된 진입로다. 오리건 Pendleton UAS Range + Oregon UAS Accelerator는 TRL 3부터 받아주는 초기 시험·투자 준비 경로다. 한국은 방사청 신속시범사업(2020~, 2년 R&D·시범운용, 2026년 성숙기술은 12개월 단축 추진)과 2026-02 '방산 스타트업 육성방안'(방산 챌린지, 공모형 획득)이 스타트업 경로다. 수출은 대부분 해외 기업과의 MOU·합작 형태로 진행되고 있다.

### Cited Findings
**미국**
- [1차] DIU Orchestrator 챌린지(2026-01-13 출범, 01-25 마감, 반복 스프린트, 미완수 시 탈락, 다수 수상) — [DIU](https://www.diu.mil/latest/diu-and-dawg-launch-autonomous-vehicle-orchestrator-prize-challenge). 스프린트 평가는 2026년 말까지 진행 예정이라는 보도(2차) — [grantedai](https://grantedai.com/grants/diu-autonomous-vehicle-orchestrator-prize-challenge-for-ai-drone-swarm-c-defense-innovation-unit-58ced47e)
- [1차] DIU Replicator SW 공모 실적(2024-11): ACT 132개사·165개 솔루션 → 3개사, ORIENT 119개사·130개 제안 → Viasat·Aalyria·Higher Ground·IoT/AI — [DIU](https://www.diu.mil/latest/defense-innovation-unit-announces-software-vendors-to-support-replicator)
- [1차] DIU 최근 메모 제목: "Establishment of the Bridge Program"(2026-08-19), "Reorganization to Support the Revolution"(2026-07-18), "Converting Commercial Technology into Combat Power"(2026-03-02) — [DIU latest](https://www.diu.mil/latest)
- [언론] Swarm Forge(CDAO, Hegseth 2026-01 AI 전략 메모의 pace-setting 프로젝트): 분기별 Crucible 행사로 하드웨어·임무 SW·협응 로직·인터페이스·전술 패키지를 90일 이내 부대에 전달함. 2026-01 Camp Blanding에서 FPV 4대(리더 1 + 3) 실사격 시연 — [DefenseScoop, 2026-03-31](https://defensescoop.com/2026/03/31/pentagon-preparing-drone-swarm-crucible/), [DefenseScoop, 2026-01-15](https://defensescoop.com/2026/01/15/drone-swarm-forge-demonstration-us-military-camp-blanding/)
- [언론] 국방 CTO 설명: Drone Dominance는 소형 드론 구매, DAWG는 대형·편도 공격 드론 담당 — [Forecast International DSM](https://dsm.forecastinternational.com/2026/05/21/a-new-dawg-in-the-fight-the-pentagons-54-billion-bet-on-autonomous-warfare/)
- [언론] Edwards AFB "Game of Drones"(Drone Dominance 지원) — [Edwards AFB](https://www.edwards.af.mil/News/Display/Article/4391968/edwards-launches-game-of-drones-to-help-deliver-drone-dominance-for-the-warfigh/)

**오리건 (Pendleton UAS Range / Oregon UAS Accelerator)**
- [언론] 2026 챌린지는 TRL 3 이상 'pioneer' 트랙을 신설함(기존 TRL 6+). 지원 마감 2025-12-04. 무희석 보조금 USD 5,000-9,000, Pendleton UAS 시험장과 "14,000 sq miles of controlled airspace" 접근 제공 — [Unmanned Airspace](https://www.unmannedairspace.info/uncategorized/oregon-uas-accelerator-launches-2026-challenge/)
- [언론] 2026-04-22~23 Pendleton에서 AUVSI Cascade Spring Symposium과 함께 Innovation Showcase 결선. 35개사 중 12개 결선, 대드론 기업(American Tenet 저가 디코이, Ether Form SW 유도 요격기) 포함. 12주 투자 준비 교육 — [Silicon Florist, 2026-04-20](https://siliconflorist.com/2026/04/20/12-startups-to-pitch-at-the-oregon-uas-accelerator-innovation-showcase/)
- (2025-03) [언론] Eastern Oregon Regional Airport 시설 개소, 2025 봄 코호트에 각 $20,000 보조금, 이중용도(dual-use) 육성 표방 — [Unmanned Airspace](https://www.unmannedairspace.info/latest-news-and-information/oregon-uas-accelerator-announces-spring-2025-cohort/), [Elkhorn Media](https://elkhornmediagroup.com/?p=194419)
- SOAR Oregon 자체 프로그램 상세는 이번 조사에서 별도 확인 못함(Gaps).

**한국 — 신속획득·스타트업 경로**
- [연구] 신속시범획득사업은 2020년 신설. 4차 산업혁명 기술 제품을 군이 우선 구매·시범운용하는 트랙과, 신기술 무기체계를 2년 안에 연구개발한 뒤 군 시범운용으로 검증하는 트랙이 있음 — [KAIS 논문](https://www.kais99.org/jkais/journal/Vol23No06/vol23no06p13.pdf), [세계일보](https://www.segye.com/newsView/20241015520998)
- [언론] 2023 국방부 훈령 개정으로 시범사업자 수의계약이 가능해짐. 다만 개정 전(2022~23) 공모 사업에는 미적용이라 업계 불만이 있음(2026-03) — [한국경제, 2026-03-10](https://www.hankyung.com/article/2026031018261)
- [언론] 드론 관련 선정 사례: 2025-04 '지능형 전자기전 기반 대드론 대응체계', 2025-09 '대드론 하드킬 근접방호체계'(국방신속획득기술연구원 주관, 2년 R&D 후 2028 배치) — [헤럴드경제](https://www.heraldk.com/article/2025090715544410886), [보안뉴스](https://m.boannews.com/html/detail.html?idx=139146)
- (2026-09-18) [언론] 방사청 신속시범사업 설명회(양재 aT센터). 2027 공모 절차·1:1 컨설팅 안내. "성숙 기술 과제는 연구개발 기간 12개월 이내로 단축" — [파이낸셜뉴스](https://www.fnnews.com/news/202609180858361306)
- (2026-02-23) [언론] 중기부·방사청 '방산 스타트업 육성방안'. 드론·로봇·AI 분야 "스타트업이 무기체계 성능과 개념을 제안하는 공모형 획득 제도" 도입 계획. 방산발전추진단 구성 — [뉴시스](https://www.newsis.com/view/NISX20260223_0003522678)
- (2026-04) [언론] 방산 챌린지 10개 과제 선정(top-down + bottom-up), 과제당 최대 1억원, 군 실증·시범 구매·후속 R&D 연계 — [MTN](https://news.mtn.co.kr/news-detail/2026040816371870009)
- [언론] 한국 방산 매출 대비 수출 비중 12%(선진국 25~35%), 소요 결정부터 획득까지 10~15년 (검색 요약 기준, 아래 두 기사 중 하나) — [헤럴드경제](https://www.heraldk.com/article/2026022216300023084), [MTN](https://news.mtn.co.kr/news-detail/2026040816371870009)
- [오피니언] 유무인복합체계가 현행 방위사업 제도 전제와 충돌한다는 기고. 지속 시험평가와 신속획득 전용 예산 신설을 제안함(개인 의견) — [MTN 기고, 2026-06-29](https://news.mtn.co.kr/news-detail/2026062916270756219/share-modal)
- (2026-03-25) [언론] 워싱턴 스팀슨센터 라운드테이블에서 "미국의 DIU 혁신 모델을 한국 방산 생태계에 어떻게 구현할 것인가"가 의제로 다뤄짐. 한국 스타트업 본에이아이 참석 — [유니콘팩토리](https://www.unicornfactory.co.kr/article/2026032709245993870)

**수출·해외 협력 경로 (한국 관련)**
- 해외 SW + 국산 플랫폼 MOU 패턴: KAI–Shield AI(2025-03), 현대로템–Shield AI(2025-10), HD현대–Anduril(2025-04/08), 대한항공–Anduril(2025-04/08, 아태 수출 거점), 한화–HavocAI(2025-10 ~ 2026-01, 미 해군 MASC 연계), LIG넥스원–Shield AI(V-BAT 탑재 시험) — 4번·2번 섹션 출처 참조
- [언론] 현대로템 대드론 셰르파는 중동 수출 겨냥(WDS 2026 사우디, YIDEX 2026) — [딜사이트](https://dealsite.co.kr/articles/164767), [현대자동차그룹](https://www.hyundaimotorgroup.com/ko/news/hyundai-rotem-wds-2026-saudi-defense-exhibition)
- [언론] Anduril "韓 방산 속도 전례 없어…글로벌 공급망 편입 추진"(2026-05) — [헤럴드경제](https://www.heraldk.com/article/2026050623162059124)
- [2차·미검증] Shield AI–대만 NCSIST(2026-02)는 아시아 동맹국 대상 다중 플랫폼 GCS 수출 사례 — [Taiwan News](https://www.taiwannews.com.tw/en/news/6300973)

### Inferences
- 심사위원 구성(미군 + 업계 CEO + KADIA)을 고려하면, 데모 마지막에 "다음 단계 경로"로 ① DIU Orchestrator·Swarm Forge가 요구하는 것과 같은 인터페이스(의도 → 플레이북, 벤더 중립, 기존 자율 스택 무수정), ② 한국 신속시범사업·방산 챌린지(드론·AI 공모형 획득), ③ Pendleton 같은 시험장 실증을 한 줄씩 보여주면 설득력이 있다(추정).
- 한국 대기업이 해외 자율 SW와 손잡는 흐름 속에서 "국산 벤더 중립 운용자 계층"은 수출통제(ITAR 등) 회피와 소버린 관점의 서사가 가능하다. 이 부분은 근거 문서를 찾지 못했으므로 추정이다.

### Gaps
- SOAR Oregon(오리건 무인항공 산업 협회/가속기) 자체 프로그램·2026 일정 상세는 확인 못함. 이번 결과는 Oregon UAS Accelerator 중심.
- Orchestrator 챌린지 스프린트 결과·수상자 공식 발표는 조사일 기준 찾지 못함.
- Swarm Forge 2026-06 Crucible 결과 보도는 찾지 못함.
- DIU와 한국 정부 간 공식 협력 MOU, 한국 내 DIU 거점 소식은 확인되지 않음.
- 2026년 신규 선정된 드론·무인체계 신속시범사업 목록은 확인 못함(방사청 공고 직접 확인 필요).
