# 국방·정부 무인체계 "임무/행동 저작(authoring)" 도구 비교 — 우리 컨셉(노코드 플레이 편집기 + 정적 검증 + 도메인별 전개 + 교차 도메인 역할 인계 + 런타임 가드) 대비

- 작성: 2026-10-08 (모든 URL 접근일 = 2026-10-08)
- 범위: 운용자·임무계획자가 코드 없이(또는 코드로) 무인체계의 행동·임무를 **조립(compose)** 하고 이종(공중·수상·지상) 기체에 배정하는 국방·정부 제품/프로그램. 비율(1:N) 수치와 일반 C2 시장은 `knowledge/inbox/2026-10-08-multi-uxv-research/products-market.md`, `military-programs.md`에 이미 있음. 이 파일은 **저작 방식**만 다룬다.
- 표기: [1차]=회사·기관 원문 / [언론]=언론 보도 / [마케팅]=회사 주장, 독립 검증 없음 / [연구]=논문·보고서 / [채용공고]=제품 기능 확정 근거 아님 / [검색 스니펫]=검색 결과 요약에서 본 문장, 원문 페이지를 직접 열어 확인하지 못함 / [2차]=애그리게이터·리서치 요약
- 비교 축(질문의 a~f): (a) 저작 방식 (b) 저작 주체 (c) 다중 도메인 (d) 저작물 검증·안전 보장 (e) 런타임 재임무·인계 (f) 공개 근거 품질

---

## Q1. Anduril Lattice (Lattice for Mission Autonomy, Lattice SDK, tasks/agents): 코드 없이 행동을 만들 수 있나? 시각적 빌더가 있나? 이종 자산에 어떻게 배정하나?

### Takeaway
공개 문서상 Lattice의 "task"는 **개발자가 Protobuf 메시지로 정의**하고, 각 기체(agent)가 `taskCatalog`에 "내가 할 수 있는 task 종류"를 광고하면 운용자가 Lattice UI 드롭다운에서 골라 배정하는 구조다. 행동(behavior)은 내부적으로 **behavior tree 엔진**으로 구현되는 것으로 보이나(채용공고 근거), 운용자·계획자용 노코드/시각적 행동 편집기는 공개 근거가 없다. 검증은 스키마 타입 안전성(breaking-change 탐지) 수준만 공개됐다.

### Cited Findings
**Task 모델 (개발자 문서, [1차])**
- task 정의 원문: "a data structure for modeling deliberate, sequential actions that an operator can execute on an asset or team of assets." / taskable agent: "a service, asset, group, or human that can accept and perform tasks." / "Task Manager manages the distribution and persistence of tasks across Lattice." / 수명주기 "Tasks have a well-defined lifecycle: create, update, and delete." / 결과 상태 `STATUS_DONE_OK`, `STATUS_DONE_NOT_OK` — [Lattice Developers: Tasks overview](https://developer.anduril.com/guides/tasks/overview)
- custom task는 Protobuf 코드로 정의: "A custom task is a Protobuf message type that contains the information your asset requires to execute a task autonomously." / "At its simplest, a task definition is a single Protobuf message." / "Use Message types to compose a more complex Task"(메시지 타입 조합 = 데이터 구조 조합이지 행동 조합이 아님) — [Lattice Developers: Define a task](https://developer.anduril.com/guides/tasks/define)
- 배정 제약 = 능력 광고: "An operator can only assign a task to an asset if the asset's `taskCatalog` advertises that task's type URL." — 같은 페이지
- 검증은 스키마 수준: "The Schema Registry enforces breaking change detection on all packages, regardless of the stability marker." / "Custom tasks give you the flexibility to model domain-specific workflows while maintaining type safety and compatibility across your Lattice deployment." 페이지에 노코드·시각 편집·행동 조합·안전 검사 언급 없음 — 같은 페이지
- [검색 스니펫] "Work with your Anduril representative to determine a list of task definitions for your use-case." / "An operator, using the Lattice UI or an a programmatic SDK integration, can use an entity override to modify the asset's TaskCatalog." / "Each displayed task in the drop down corresponds with a TaskDefinition item in the agent's TaskCatalog component." — 후보 페이지 [Integrate an agent](https://developer.anduril.com/guides/tasks/integrate-an-agent), [docs.anduril.com tasking/integrate](https://docs.anduril.com/guide/tasking/integrate) (어느 페이지 문장인지 직접 확인 못함)
- [검색 스니펫] 기체 측은 `ListenAsAgent`(task 수신), `UpdateStatus`(진행 보고)만 쓰도록 권장. 정기적 운용자 개입이 없는 용도는 task 대신 "configuration settings"를 권장 — [Integrate an agent](https://developer.anduril.com/guides/tasks/integrate-an-agent), [Tasks overview](https://developer.anduril.com/guides/tasks/overview)

**행동(behavior) 구현 — behavior tree (채용공고, 2026-01-21 내려감)**
- [채용공고] "The Lattice Autonomy Platform team owns the behavior tree engine and extension points" / "Design and implement autonomy capabilities that extend our behavior tree engine." / "operators can build high-level behaviors that make the best use of the information" / 검증은 "Test and validate capability modules through unit testing, simulation testing and performance benchmarks." — [Built In: Senior Software Engineer, Autonomy Platform](https://builtin.com/job/senior-software-engineer-autonomy-platform/7723240)
- [채용공고·검색 스니펫] "Our customers use teams of heterogeneous vehicles that can sense the world …" 고수준 계획을 받아 자율 협응 — [Built In: Senior SWE – Distributed Autonomous Systems](https://builtin.com/job/senior-software-engineer-distributed-autonomous-systems/6215425)

**Lattice for Mission Autonomy (2023) — 운용자 워크플로**
- [1차·검색 스니펫] "a hardware-agnostic, end-to-end software platform" (2023 출시, 정확한 날짜 미확인) — [Anduril blog: Unveils Lattice for Mission Autonomy](https://blog.anduril.com/anduril-unveils-lattice-for-mission-autonomy-8e0c5fa0e94b)
- [언론] 운용자 의도를 자동으로 개별 task로 분해해 자산에 배분: "This feature automatically breaks down operator intent into discrete tasks" — [Maginative](https://www.maginative.com/article/anduril-announces-lattice-for-mission-autonomy-an-ai-powered-platform-to-manage-drone-swarms/)
- [1차·마케팅·검색 스니펫, 2023] EDGE23: "a single soldier used Lattice for Mission Autonomy software"로 임무 전 계획·분석·다수 기체 통제, ALTIUS-600 + Aerosonde 탐색 → 드론 쌍 재임무 → "Upon gaining positive identification of the SAM site, the soldier then designated the target as "hostile"" → 타격 후 감시 드론이 자동으로 BDA 재임무 — [Anduril blog EDGE23](https://blog.anduril.com/anduril-demonstrates-lattice-for-mission-autonomy-controlling-teams-of-autonomous-assets-at-us-f617c489441)

**SDK 공개·개방성**
- [언론] Lattice SDK 공개(12월 10일, 연도 미표기 — 같은 기사의 OpenAI 협력(12월 4일)으로 미루어 2024년 추정), 파트너 10곳 이상(Apex, Forterra, Saronic, Scale AI 등) — [OCBJ](https://www.ocbj.com/defense-2/anduril-industries-enabling-partners-to-operate-on-lattice/)
- [1차] 샌드박스는 신청제 개발자 프로그램, 시뮬 데이터 제공 — [Lattice Sandboxes](https://developer.anduril.com/guides/developer-tools/sandboxes); Python 패키지 `anduril-lattice-sdk` — [PyPI](https://pypi.org/p/anduril-lattice-sdk)

### Inferences
- (a) 코드/SDK(Protobuf) (b) 엔지니어·통합업체(+Anduril 담당자), 운용자는 "카탈로그에서 고르기" (c) 다중 도메인 지향(하드웨어 무관) (d) 타입 안전성·스키마 호환성뿐 — "무한 루프 없음 / 비상 핸들러 존재 / 위험 행동 승인 게이트" 같은 **임무 논리 정적 검증은 공개 근거 없음** (e) 의도→task 자동 분해·재임무(EDGE23 BDA) 있음, 기체 이탈 시 역할 인계 방식은 비공개 (f) 개발자 문서는 1차·양호, 운용자 UI/BT 엔진은 채용공고 수준.
- 우리 컨셉과 가장 겹치는 지점은 **`taskCatalog`(기체가 수행 가능한 task 타입 광고) → 배정 제약**이다. 이것은 "도메인별 전개 + 도메인 규칙 검사"의 단순한 형태(되는가/안 되는가)이고, 우리처럼 같은 액션을 드론/USV/UGV마다 다르게 **전개(expand)** 하는 단계는 공개 문서에 없다.
- Lattice의 task 정의 자체가 "sequential actions"를 표현하는 데이터 구조이므로, 우리 "플레이(스텝 카드 + 액션 시퀀스)"를 Lattice 용어로 설명하면 심사위원(미군)에게 익숙하게 들릴 것이다(추정).

### Gaps
- Lattice UI에서 운용자가 다단계 task 시퀀스·조건·반복을 GUI로 조립하는 기능이 있는지 공개 자료 없음.
- behavior tree 엔진의 저작 도구(시각 편집기 여부), 행동 검증 방식, 기체 탈락 시 task 재할당 규칙은 비공개.

---

## Q2. Shield AI Hivemind (Hivemind Enterprise / EdgeOS / Pilot / Commander / Forge / "Hivemind Design"): 누가 어떻게 행동을 만드나?

### Takeaway
Hivemind 행동은 **개발자가 SDK(C++ 코드베이스 Pilot) + Forge(SDK·CLI·웹 포털)로 만든다**. 2022년 자료에 "re-composable blocks 카탈로그"와 개발자·디자이너용 "Hivemind Design"이 있었지만, 운용자·계획자용 노코드 저작 근거는 없다. 검증은 시뮬레이션 기반 자동 시험·V&V(개발 단계)이지 저작된 임무의 정적 검증이 아니다. Commander는 기존 C2와의 연동 계층이다.

### Cited Findings
- [1차, 2022-08-19] 조합형 블록: "through a catalog of re-composable "blocks" that can be combined to leverage the capabilities of a vehicle" / Hivemind Design: "Software for AI-developers and designers, intended to accelerate capability development and testing" / "environment modeling, automated testing, verification, and validation of algorithms" / "heterogenous teams of crewed-and-uncrewed aerial systems" / "Hivemind supports multiple platforms via its modular open system architecture." — [Shield AI: Hivemind for operational read-and-react swarming](https://shield.ai/hivemind-for-operational-read-and-react-swarming/)
- [1차, 2025-03-06] 대상은 개발자: "an autonomy software suite for developers and organizations" / "developers to build and own their mission-ready autonomy solutions". 제품군 명칭 EdgeOS, Hivemind Pilot, Hivemind Commander, Hivemind Forge 나열. 노코드·시각 저작 언급 없음 — [PR Newswire, Shield AI $240M](https://www.prnewswire.com/news-releases/shield-ai-raises-240m-at-5-3b-valuation-to-scale-hivemind-enterprise-an-ai-powered-autonomy-developer-platform-302393843.html)
- [1차·검색 스니펫, 2025-03-19] "design, test, evaluate and deploy autonomous behaviors across domains" / 구성 "integrated autonomy factory, industrial-grade production ready middleware, a rich autonomy catalogue, and seamless mission control" — [Shield AI–RSAF/DSTA](https://shield.ai/shield-ai-partners-with-republic-of-singapore-air-force-and-dsta-to-advance-ai-powered-autonomy-with-hivemind-enterprise/)
- [채용공고] Forge: "Forge is the engineering platform used to build, integrate, test, and operate Hivemind capabilities" / 외부 엔지니어링 팀이 채택·확장 가능 — [Lever: Senior Engineer, Full-Stack – Forge Platform](https://jobs.lever.co/shieldai/3666037e-b201-4ef4-82e1-a78802047a96); Forge = "service-oriented architecture leveraged through an SDK, CLI, and web portal", Go/Python/TypeScript, Pilot = "models-based, modular and open architecture C++ codebase" — [euremotejobs 채용 게시](https://euremotejobs.com/?p=44933)
- [2차] Commander = "Integration layer for seamless connection of Hivemind-enabled machines with any command & control or fleet management system." / Pilot = "pre-built autonomy behaviors and reference pilots for state estimation, mapping, sensing, object tracking, and mission planning" — 검색 결과 요약(출처 후보 [OODA Loop 회사 프로필](https://oodaloop.com/company-profiles/ai/shield-ai/), [apis.io](https://apis.io/apis/shield-ai/hivemind-enterprise/))
- [2차] 접근 제한: "there is no public API endpoint or self-service developer portal at this time", ITAR/EAR 적용 — [apis.io Shield AI](https://apis.io/providers/shield-ai/)
- [언론] Willy Logan(엔지니어링 디렉터): "move to the step where autonomy is committed to behaviors and humans are prioritizing tasks" — [Inside Unmanned Systems](https://insideunmannedsystems.com/hivemind-and-v-bat-shield-ais-autonomy-isr-and-teaming-move-forward/)
- [1차, 2024-11-14·검색 스니펫] "The Hivemind SDK serves as a foundational framework, providing reference architectures, extensive autonomy libraries, and a full suite of simulation, testing, and analysis tools." — [Shield AI blog](https://shield.ai/?p=12342)
- [채용공고·검색 스니펫] "Hivemind Generative AI" — "Design and prototype generative AI experience focused on accelerating autonomy development"(날짜 미상, Special Projects 채용 게시. 정확한 게시 URL은 검색 요약에 없어 특정 못함) — 제품 출시 근거 아님. 같은 검색에서 Forge 시험 오케스트레이터 관련 채용: "build custom wrappers around the HMP Forge test orchestrator, and programmatically generate complex testing environments using domain randomization" — [startup.jobs](https://startup.jobs/staff-engineer-hms-factory-r5276-shield-ai-8644202)
- [1차, 2026-02-11] 대만 NCSIST 계약: Hivemind로 자국 AI 파일럿 개발 가속 — [Shield AI](https://shield.ai/shield-ai-signs-contract-with-taiwans-national-chung-shan-institute-of-science-and-technology-to-accelerate-and-indigenize-taiwan-developed-ai-pilots/)
- [언론, 2024-12] Palantir와 협력: Hivemind + Palantir 지리·운영 도구로 다수 기체 실시간 C2 — [Maginative](https://www.maginative.com/article/shield-ai-and-palantir-join-forces-on-autonomous-defense-operations/)

### Inferences
- (a) 코드/SDK(C++·Python), 블록 카탈로그 재조합은 개발 단계 개념 (b) AI 개발자·OEM·정부 엔지니어 (c) 공중 중심, "across domains"는 마케팅 표현 (d) 시뮬 기반 자동 시험·V&V(개발 산출물 대상) — 운용자가 만든 임무의 정적 검증은 없음 (e) 팀 자율(V-BAT Teams), 인계 규칙 비공개 (f) 1차 자료는 개괄적, 세부는 채용공고 수준.
- Shield AI는 "autonomy factory"(개발자 도구)와 "mission control"(운용) 사이를 메우는 **운용자용 저작 계층을 공개하지 않았다** → 우리 컨셉의 빈자리와 일치(추정).
- "Hivemind Design"(2022)은 이름과 달리 개발자·디자이너용 도구다. 2025년 이후 제품군 명칭에서는 사라지고 Forge로 흡수된 것으로 보인다(추정, 확인 안 됨).

### Gaps
- Forge/Pilot에서 행동을 behavior tree, 상태기계, 학습 정책 중 무엇으로 표현하는지 공개 자료 없음.
- Commander가 운용자에게 임무 조립 UI를 주는지 불명.

---

## Q3. 대형 방산·신생 기업 제품 (L3Harris, Lockheed, Northrop, Raytheon, BAE, Leidos, Palantir, EpiSci/Applied Intuition, Scale AI, NODA AI·DIU Orchestrator, Swarm Forge, Auterion, Swarmer, Milrem, Ghost Robotics, Saronic, HavocAI, SeeByte, AeroVironment)

### Takeaway
공개된 제품은 거의 모두 **(1) 사전 정의된 임무 유형/목표를 고르고 매개변수를 넣는 형태**(Milrem의 search/intercept/shadow, SeeByte의 goal 기반, Auterion의 목표·효과 승인)이거나 **(2) 개발자 SDK**다. 사용자가 조건·반복·승인 게이트를 가진 행동을 노코드로 조립하는 제품은 찾지 못했다. 미 국방부의 최신 수요(DIU Orchestrator, 2026-01)는 오히려 "메뉴 클릭이나 행동 프로그래밍이 아닌" 자연어 의도 입력을 명시한다.

### Cited Findings
**미 국방 수요 신호**
- [1차, 2026-01-13] DIU·DAWG·해군 $100M Orchestrator: "translate a battlefield commander's intent from voice, text, and haptic input into machine execution" / "vehicle-agnostic capability for understanding, tasking and coordinating autonomous systems at the fleet level" / "through plain language that expresses desired effects, constraints, timing, and priorities" / DAWG 국장 Donovan: "not by clicking through menus or programming behaviors" / "the human - the ethical decision maker - always maintains a clear understanding of what the system is doing and why" — [DIU](https://www.diu.mil/latest/diu-and-dawg-launch-autonomous-vehicle-orchestrator-prize-challenge)
- [검색 스니펫] 공모 요구: "The orchestrator does not change existing craft autonomy structure, command actuators directly, or interfere with platform-level data transfer and communication." / "These agentic models must be aligned specifically for military missions, rules of engagement, authorities, phasing, timing, and domain constraints." — [DIU 공모 페이지(현재 404)](https://www.diu.mil/work-with-us/submit-solution/PROJ00643), [FIE UNDEF 요약](https://www.fie.undef.edu.ar/ceptm/?p=18088)
- [언론·익명 소식통] SpaceX·xAI가 소수 선정 참가자 중 하나(Bloomberg 보도 재인용), OpenAI는 음성→명령 변환에 한정 — [Stars and Stripes, 2026-02-16](https://www.stripes.com/theaters/us/2026-02-16/spacex-pentagon-autonomous-drone-tech-20768663.html), [TechRadar](https://www.techradar.com/pro/the-pentagon-wants-swarms-of-voice-controlled-ai-drones-and-is-offering-a-usd100-million-prize-as-a-reward-and-elon-musks-spacex-is-taking-pole-position)
- [언론, 2026-08-17] NODA AI가 $100M 수주 주장(URZA: "interprets a commander's intent", 통합 표준 MELD, 10개 플랫폼 시연·30+ 시스템 연동 주장). 기사: DIU 공지는 "up to $100 million across multiple awards"이며 NODA $100M 계약을 특정하지 않음. 임무 저작 방식·노코드 언급 없음 — [RuntimeWire](https://runtimewire.com/article/noda-ai-100m-autonomous-military-command-contract)
- [언론] CDAO Swarm Forge Crucible 2(2026-06-22~26, Camp Blanding)에 25개사 선정, 명단은 기사에 없음 — [ExecutiveGov](https://www.executivegov.com/articles/cdao-crucible-2-swarm-forge-initiative-pentagon); "heterogeneous swarming implies multi-vendor UAS command, control and autonomy" — [DefenseScoop, 2026-03-31](https://defensescoop.com/2026/03/31/pentagon-preparing-drone-swarm-crucible/)

**대형 방산**
- L3Harris AMORPHOUS [언론·마케팅, 2025-02]: 단일 UI로 수천 대 목표, 분산 의사결정, 타사 플랫폼 지원. "To date, the company has demonstrated the ability to connect multiple systems" — 저작 방식 공개 없음 — [Defense News, 2025-02-10](https://www.defensenews.com/unmanned/2025/02/10/l3harris-unveils-amorphous-autonomy-software-to-manage-drone-swarms/), [Seapower](https://seapowermagazine.org/l3harris-unveils-amorphous-c2-software/)
- Lockheed Martin MDCX [1차·마케팅]: XTEND OS 통합으로 한 스테이션에서 여러 급 UAS 동시 C2, 대형 UAS가 Class 1 드론을 투하해 근접 임무("marsupial") — [Lockheed 보도자료, 2025-12-18](https://news.lockheedmartin.com/2025-12-18-Skunk-Works-R-and-XTEND-Expand-Joint-All-Domain-Command-and-Control-for-Advanced-Mission-Execution); 영국 시연(2026-01)에서 Indago 2 + Stalker 동시 통제 — [Lockheed feature 2026](https://www.lockheedmartin.com/en-us/news/features/2026/Lockheed-Martin-Demos-Next-Gen-Multi-Domain-Autonomy.html); MQ-25 MD-5C의 임무계획·실행 SW — [NAVAIR, 2024-11](https://www.navair.navy.mil/news/US-NAVY-GENERAL-ATOMICS-AND-LOCKHEED-MARTIN-COMPLETE-UNMANNED-AVIATION-CONTROL-STATION-FLIGHT). 행동 저작 방식 공개 없음
- BAE Systems [1차, 2022-11-09]: AFRL Fight Tonight($17M) 항공임무계획 게임형 UI — "The drag-and-drop video game-like interactions would reduce the time it takes to make a series of incremental adjustments to a plan from hours to minutes." (ATO 계획 대상이지 무인기 행동 저작 아님) — [BAE Systems](https://www.baesystems.com/en/article/bae-systems-to-develop-autonomy-based-video-game-experience-for-mission-planners)
- Northrop Grumman·Raytheon BBN: DARPA OFFSET "swarm system integrators"로 전술 교환소 구축(Q4 참조) — [Janes](https://www.janes.com/defence-news/darpa-hosting-final-drone-swarm-demo-in-november-companies-look-for-service-buy-in)
- Raytheon [검색 스니펫, 날짜 미상]: "a common ground control system that helps the U.S. Navy operate multiple unmanned platforms using a single cyber-hardened workstation" — 출처 매핑 불확실(같은 검색 결과 묶음의 후보: [Military Embedded Systems](https://militaryembedded.com/comms/communications/command-control-system-completes-demo-on-unmanned-vehicle-adds-to-u-s-navy-portfolio))
- Palantir [언론]: 자체 군집 오케스트레이터 제품 확인 못함. Shield AI·Red Cat·Ondas와 데이터·C2 계층 협력, Ondas는 Palantir와 새 AI 지휘체계 구축 "계획"(2026-07) — [Breaking Defense, 2026-07](https://breakingdefense.com/2026/07/ondas-makes-876m-acquisition-of-dyzne-latest-in-acquisition-spree/)
- Applied Intuition(EpiSci 인수) [1차·마케팅, 2025-05-20]: Axion = "one unified environment for engineers and operators to build, test, and deploy together", Acuity = 탑재 자율 SW(EpiSci 기술 기반), "air, land, sea, and space and the electromagnetic spectrum" — [Kyodo PR 보도자료](https://kyodonewsprwire.jp/release/202505209193), [Tectonic Defense](https://www.tectonicdefense.com/applied-intuition-expands-its-autonomy-suite-with-axion-and-acuity/). 운용자 저작 UI 세부 없음
- Scale AI Thunderforge [언론, 2025-03]: 작전계획·COA 계층(기체 행동 저작 아님) — [getcoai](https://getcoai.com/news/scale-ai-wins-pentagon-contract-to-bring-ai-agents-to-military-planning)
- Leidos: 저작 도구 관련 공개 자료를 이번 조사에서 찾지 못함(Gaps)

**신생·전문 기업**
- Auterion Nemyx [1차·언론, 2026-01]: 운용자는 목표 지정·효과 승인, Nemyx/Skynode가 항법·대형·분산·종말유도 담당. 드론 손실 시 다른 드론이 표적 승계(검색 스니펫) — [Inside Unmanned Systems](https://insideunmannedsystems.com/auterion-demonstrates-one-operator-drone-swarm-strike-in-u-s-live-fire-test/); JPMRC에서 Auterion Mission Control로 병사가 "within two hours of training" 군집 타격 운용(회사 주장) — [Auterion](https://auterion.com/how-auterions-nemyx-accelerated-swarming-in-days-at-jpmrc/)
- Swarmer(우크라이나) [언론]: SW 3층 = 데이터 OS / 군집 AI 엔진 / "a user interface for planning missions, defining targets, and authorizing use of force"(검색 스니펫), 운용자는 탐색 구역 지정·공격 명령·중단, 드론 소실 시 타 드론이 목표 승계, 운용 인원 9→3명(항법·임무계획·조종) — [Defense One, 2025-09](https://www.defenseone.com/business/2025/09/ukrainian-startup-has-re-invented-drone-swarming/408099/), [Ukrainska Pravda(WSJ 인용), 2025-09-03](https://www.pravda.com.ua/eng/news/2025/09/3/7529154/)
- Milrem Robotics [1차·언론]: MIFIK Mission Planner — 경로 설정·임무 중 수정·다중 임무 동시 계획 — [Milrem Autonomy](https://milremrobotics.com/autonomy/); 2022 C2: "The autonomy engine autonomously creates routes against pre-determined mission sets such as search, intercept, shadow etc, considering the selected vehicles' mobility & intelligence character", 운용자 1명 최대 6대 — [Janes, Eurosatory 2022](https://janes.com/osint-insights/defence-news/c4isr/eurosatory-2022-milrem-robotics-launches-new-c2-system-for-unmanned-platforms); ARCOS(DSEI 2025-09-08): 다수 UGV 동기 통제·임무계획·자산 배정 — [Milrem](https://milremrobotics.com/milrem-robotics-launches-arcos-next-gen-command-suite-for-collaborative-robotic-operations-at-dsei-2025/)
- Saronic Echelon [1차·마케팅, 2025-07-30]: "allows a single operator to plan, simulate, and execute complex missions across multiple autonomous assets"; 시뮬 통과 계획을 선택 함정에 배포, 운용자 실시간 개입 — [Seapower(보도자료)](https://seapowermagazine.org/saronic-unveils-echelon-a-unified-platform-for-mission-planning-simulation-and-command-and-control-of-autonomous-surface-vessels/?print=pdf). 저작 방식(GUI/코드) 세부 없음
- HavocAI [2차·마케팅]: Havoc Control(브라우저 콘솔: 계획·과업·오버라이드), "The operator defines intent and constraints; software handles routing, formation, sensor fusion and task allocation", 1인 25척 시연 — [Sacra](https://sacra.com/research/havocai); 2025-12 포르투갈 Troia에서 USV+UAV를 "single command interface"로 GPS 없이 협응 — [Naval Technology](https://www.naval-technology.com/news/havocai-gps-demonstration-autonomy/)
- SeeByte Neptune(해양, 영국) [1차·마케팅]: "Neptune assigns goal-based plans and objectives based on the assets capabilities." / "Pre-mission Neptune presents a time optimised objective delegation based on the assets' capabilities." / 운용자는 "manually refine" 가능 / 고장 시 "the other vehicle(s) will execute the failed vehicles missing objectives"(임무시간 증가 감수) / "The rehearsal provides a pre-mission summary of the path that each vehicle may take" / SDK로 "third-party vehicles, sensors, autonomy behaviours" 통합 / UI는 SeeTrack 플러그인 — [SeeByte Neptune](https://www.seebyte.com/products/neptune); MIT MOOS-IvP와 결합 실험(2021-07, Charles River) — [Univ. Pisa 논문 AAM](https://arpi.unipi.it/retrieve/14955b06-d9ee-4f19-854a-6386d3ebc188/Coordinating%20multiple%20autonomies_AAM.pdf)
- AeroVironment Tomahawk(Kinesis + Grip TA5) [1차·언론, 2025-09]: 육군 RCCTO HMIF의 Dismounted Common Controller로 선정($5.1M), "single pane of glass" 다영역 공통 통제 — [BusinessWire](https://www.businesswire.com/news/home/20250911519613/en), [Inside Unmanned Systems](https://insideunmannedsystems.com/aerovironments-tomahawk-ecosystem-unifies-command-and-control/). 행동 저작 기능 공개 없음
- Ghost Robotics: 임무 저작 UI 공개 자료 찾지 못함(Gaps)

**참고: 비국방 노코드 사례**
- [1차] DroneBlocks: 블록 → Python 생성(교육용, Crazyflie) — [DroneBlocks](https://droneblocks.io/drone-programming/)
- [연구] Aerostack2: 임무를 JSON의 "behavior activation and deactivation" 시퀀스 + 조건문으로 표현 — [arXiv 2303.18237](https://arxiv.org/pdf/2303.18237)

### Inferences
- 업계 공통 패턴: **"목표/임무 유형 선택 + 매개변수 + (필요 시) 효과 승인"**. 사용자가 조건(IF)·반복(종료 조건)·통신 릴레이·신호 동기화를 가진 "플레이"를 조립하는 제품은 공개 근거가 없다.
- "도메인별 전개"의 상업적 선례는 Milrem(2022: 같은 mission set을 선택 기체의 기동성에 맞춰 경로 생성)과 SeeByte(자산 능력 기반 목표 위임)다. 둘 다 단일 도메인(지상 또는 해양) 안에서다.
- "역할 인계"의 선례는 단일 도메인 안의 동종 대체(Auterion·Swarmer 표적 승계, SeeByte 목표 재수행)뿐이다. 공중↔수상↔지상으로 같은 스텝을 이어받는 공개 시연은 찾지 못했다. HavocAI의 공중+수상 단일 인터페이스(2025-12)가 가장 가깝지만 인계 방식은 비공개다.
- DIU Orchestrator(2026)의 방향은 "자연어 의도 → 플랫폼이 이미 아는 행동(playbook)으로 매핑"이다. 우리 컨셉은 이와 충돌하지 않고, **자연어 의도가 매핑될 '검증된 플레이 라이브러리'를 사전에 만드는 계층**으로 위치시킬 수 있다(추정). 다만 "운용자가 행동을 프로그래밍하는 것"으로 보이면 Donovan 발언과 정면으로 부딪히므로, 저작 주체를 **임무 전 계획자**로 분명히 해야 한다.

### Gaps
- Orchestrator 선정 업체·스프린트 결과, Swarm Forge Crucible 2 참가 25개사 명단·결과는 공개 자료를 찾지 못함.
- Leidos, Ghost Robotics, Northrop(OFFSET 이후), Palantir의 저작 UI 정보 없음.
- Saronic Echelon, HavocAI Control, Auterion Mission Control의 실제 임무 편집 화면(조건·분기 지원 여부) 미확인.

---

## Q4. 플레이북식 위임 도구와 정부 연구 (SIFT Playbook, AFRL IMPACT·OpenUxAS, DARPA OFFSET 전술 교환, NPS 미션 언어·검증, 해군 CCS, 육군 공통 통제기, 영국 Dstl/Thales)

### Takeaway
우리 컨셉의 개념 대부분은 **정부 연구에 흩어져 존재**한다. SIFT Playbook(2002~)은 "임무 전 play 개발 ↔ 비행 중 play calling" 구분을, AFRL IMPACT(~2017)는 1인 이종 UxV play calling을, DARPA OFFSET CCAST(2017~2021)는 **노드(각 노드에 tactic 1개 이상) + 신호로 노드 실행 게이트 + 실행 시 역할/그룹 바인딩 + 능력 기반 기체 배정 + 배터리 부족 시 교대(같은 tactic 계속)** 를, NPS(2011~2020)는 **임무 명령의 성공/실패/예외 분기와 실행 전 논리 검증**을 보여줬다. 하나로 통합해 노코드로 계획자에게 준 사례는 없다.

### Cited Findings
**SIFT Playbook (2002~, 연구·상표)**
- [연구·검색 스니펫, 2002] 상호작용 스타일이 "extremely detailed (for use in pre-mission planning and play development) to extremely streamlined (for in-flight "play calling")" 범위 — Miller, Funk, Dorneich, Whitlow — [DASC 2002 PDF](https://www.imse.iastate.edu/dorneich/files/2013/02/2002-07-31_DASC02_367_Miller.pdf)
- [연구·검색 스니펫, 2005] 위임 5방식: 목표, 전체/부분 계획, 부정 제약, 긍정 제약, 우선순위·정책 — [Miller, MIPAS 2005](https://www.cs.rochester.edu/research/mipas2005/final-drafts/miller.pdf)
- [연구·검색 스니펫] Playbook을 Geneva Aerospace VACS 지상국과 통합해 이종 회전익·고정익 UAV 통제; 과제약 임무용 "best-effort" 계획 모드 추가 — [academia.edu: Optimizing to Satisfice](https://www.academia.edu/57005421/Optimizing_to_Satisfice_Using_Optimization_to_Guide_Users); NASA Ames 위임 방식 비교에서 Playbook이 Tools·Manual보다 정확도·종합 점수 최고, "Playbook is a registered trademark of Smart Information Flow Technologies" — 검색 스니펫, 정확한 문서 매핑 불확실(후보 [NTRS 20180003961](https://ntrs.nasa.gov/citations/20180003961), [NTRS 20190033886 PDF](https://ntrs.nasa.gov/api/citations/20190033886/downloads/20190033886.pdf))

**AFRL IMPACT (~2014~2017) / OpenUxAS**
- [연구] "With IMPACT, the human-autonomy team controls multiple UxVs by utilizing high level commands called plays." 1차년도 평가: 참가자 7명, UxV 6대, 기지방호, play calling 긍정 평가, 입력 모달리티(마우스·터치·음성) 비교 — [Initial Evaluation of IMPACT (academia.edu)](https://independent.academia.edu/DougLange)
- [연구·검색 스니펫] play 호출 시 지능형 에이전트가 기체 추천, 협동제어 알고리즘이 경로, autonomics 프레임워크가 play 상태 추적 — [AHFE 2022 PDF](https://openaccess-api.cms-conferences.org/articles/download/978-1-958651-33-9_11); 기체 유형별 행으로 아이콘 배치 시 선택 시간·주관 평가 개선 — [HFES DOI 10.1177/1541931213601028](https://https-sage-cnpereading-com-443.webvpn1.xju.edu.cn/doi/10.1177/1541931213601028)
- IMPACT에 "play composer/play workbook" 같은 운용자용 play 저작 도구가 있었다는 공개 근거는 찾지 못함(검색 결과 일관되게 없음)
- [1차] OpenUxAS: "Project for multi-UAV cooperative decision making." / "UxAS is a collection of modular services that interact via a common message-passing architecture." / 메시지 클래스는 "automatically generated from simple XML description documents" / "The SPARK proofs can be replayed and compared to prior results"(CI 배지 "Build and Prove OpenUxAS Ada") — [GitHub afrl-rq/OpenUxAS](https://github.com/afrl-rq/OpenUxAS)
- [연구] UxAS는 임무 요구를 Process Algebra로 기술하나 "the current implementation of PA in UxAS utilizes assigned semantics which does not guarantee the order of task completion" → 동기 합성 연산자 추가 제안 — [Nguyen, Hoxha, Johnson, Fainekos (ASU)](https://asu.elsevierpure.com/en/publications/mission-planning-for-multiple-vehicles-with-temporal-specificatio); 원조 개념 Karaman 외 2009 — [MIT DSpace](https://dspace.mit.edu/handle/1721.1/59413)
- [연구·검색 스니펫] AdaCore·AFRL 논문: OpenUxAS 핵심 서비스 하나를 SPARK로 재작성해 일부 기능 정확성 증명(임무 저작물 검증이 아니라 **플래너 코드** 검증) — [AdaCore SPARK UxAS FM19 (현재 404)](https://www.adacore.com/uploads/techPapers/adacore-spark-uxas-fm19-id.pdf)

**DARPA OFFSET (2017~2021) — CCAST(Raytheon BBN + Oregon State Univ. + SIFT) / RISE**
- [1차] 목표: 소부대가 "upwards of 250" 소형 UAS/UGS 군집 운용, "swarm tactics exchange" 생태계 — [DARPA OFFSET](https://www.darpa.mil/research/programs/offensive-swarm-enabled-tactics)
- [연구] CCAST 임무계획기: "developing multi-dimensional, multi-phase mission plans", "integrated with CCAST's multi-resolution swarm simulation"(계획 평가·정제) / "Mission plans are developed a priori"(중앙 저장소에서 SC가 로드) / **"Mission plans contain nodes, each containing one or more tactics."** / 실행 시 "binding available vehicles on the LTE network to roles or groups" / SC는 "trigger signals relative to the mission plan that gate the execution" / 디스패처가 "automatically select and assign vehicles with the necessary capabilities" / "swarm labels"로 라벨 보유 기체 누구나 tactic 수락 / 배터리 부족 UAV는 "can automatically Swap in order to continue tactic execution" / SC가 런타임에 "explicitly select the tactic and vehicle(s)", Stop·RTL 발행 가능 — [Adams et al., "Can A Single Human Supervise A Swarm of 100 Heterogeneous Robots?" (arXiv 2308.00102, Field Robotics 2023)](https://ar5iv.labs.arxiv.org/html/2308.00102)
- [연구] 같은 논문의 한계·운용 실태: "It was predetermined that SC2 was responsible for the mission plan and any associated signals." / 계획 검증은 사람이 수동으로: "wanted to verify that the mission plan was not going to task hardware vehicles in the launch area" / SC1: **"There is no real mechanism for [the SC] to consider modification or amendments to the mission plan structure"** / 로그 문제 "the mission plan tactics do not appear in the log file" — 같은 출처
- [연구·검색 스니펫] tactic 교환소 예시 이름: Inward Scan, Move To, Ring around POI, Safe Land, Sector split leader follower — [DSIAC/DTIC 브리프 2022-02-09](https://dsiac.dtic.mil/wp-content/uploads/2022/02/2022-02-09_DTICBrief_final.pdf)
- [연구] RISE(다른 OFFSET 시스템, Taranta 외, Field Robotics 2023): "enables rapid integration of third-party swarm tactics and behaviors" / "Both virtual and physical agents are controlled with a unified gesture-based interface" — [arXiv 2304.07651](https://arxiv.org/abs/2304.07651); [검색 스니펫] FX-6에서 타이머로 tactic 3개를 연결한 "tactic chain" 사용 — 같은 논문(원문 미확인)

**NPS(해군대학원) — 임무 명령 언어·검증 (2011~2020, 연구)**
- [연구] Mission Execution Automata: "allows communication with one or more "external agents" that interact with the physical world" / Mission Execution Ontology: "Formal description logics are used to enforce mission structure and semantics" / "ensure suitability of a mission definition for execution by a specific vehicle, all prior to mission parsing and execution" / "provide operator assurance of correct mission definition" / "maintains human accountability at every level of robot mission planning and execution" / "language independent and results in mission definitions equally well suited to human or robot execution" — [NPS Ethical Control of Unmanned Systems](https://savage.nps.edu/AuvWorkbench/documentation/papers/ethics.html)
- [연구·검색 스니펫] 각 목표는 성공·실패·예외 3분기, 예외 종료 "Halt and await further orders: Unplanned failure, final exception state" — [NPS 질의 예시](https://savage.nps.edu/EthicalControl/queries/LifeboatTrackingConverted.MissionQuery_01_GoalBranches.rq.txt), [Canonical Missions 다이어그램](https://savage.nps.edu/EthicalControl/missions/diagrams/EthicalControlCanonicalMissions.pdf); 2020 보고서: 명령을 온톨로지로 인코딩 → 논리 일관성 검사 → 시뮬 → 구현 반복 — [NPS-USW-20-001](https://calhoun.nps.edu/bitstream/handle/10945/65637/NPS-USW-20-001.pdf?sequence=1); 런타임 윤리 검사 논문(2012) — [IEEE OES AUV 2012 PDF](https://savage.nps.edu/AuvWorkbench/documentation/papers/IeeeOesAuv2012UniversalMissionControllerRunTimeEthicsChecking.pdf)
- [1차, 2016] AUV Workbench: "Missions are written using the Autonomous Vehicle Command Language (AVCL)", "autonomous unmanned underwater, surface and air vehicles" 지원, 물리 기반 임무 리허설, 마지막 갱신 2016-09-18 — [NPS AUV Workbench](https://savage.nps.edu/AuvWorkbench/); AVCL 2.0 스키마에 UGV 특성 타입 존재 — [AVCL ugvCharacteristicsElementType](https://savage.nps.edu/AuvWorkbench/documentation/schemas/AVCL.2.0/AVCL.2.0_ugvCharacteristicsElementType.html)

**해군 CCS / 육군 / 영국**
- [언론, 2016] 해군 CCS(PMA-281, UCS 표준 기반 정부 소유 SW): 2015-12 Keyport에서 UUV 대리 기체에 사전 계획 경로 전송, OPNAV N99 로드맵은 공중·수상·수중·지상 호환 목표 — [C4ISRNET, 2016-12-13](https://www.c4isrnet.com/unmanned/uas/2016/12/13/navy-moves-closer-to-common-control-system); MQ-25 UMCS 설계에 CCS 참고(2017) — [C4ISRNET, 2017-08-14](https://c4isrnet.com/c2-comms/2017/08/14/future-c2-system-key-to-drones-flying-off-navy-carriers). 2024~2026 CCS 저작 기능 근거 없음
- [1차, 2025-06-13] 영국 Dstl/Thales: Salisbury Plain에서 유인 차량 안의 운용자 1명이 드론 1 + UGV 2를 통제, ATR로 위협 탐지·분류, GVA(Generic Vehicle Architecture)를 자율 플랫폼으로 확장 — [GOV.UK](https://www.gov.uk/government/news/successful-trial-paves-the-way-for-improved-reconnaissance-on-army-operations)
- [1차, 2022-01-24] Dstl AMAPS(QinetiQ, SeeByte, L3Harris ASV, Thales): "Apps were developed that enable multiple UXVs to be command and controlled from a single operator to protect assets." — [GOV.UK AMAPS](https://gov.uk/government/news/dstl-trials-autonomous-maritime-asset-protection-system-amaps)
- 육군 공통 통제기: Tomahawk Grip TA5가 HMIF Dismounted Common Controller로 선정(Q3 참조) — 행동 저작 기능 근거 없음

### Inferences
- **CCAST가 우리 컨셉의 구조와 가장 많이 겹친다**: 노드(=스텝 카드) ⊃ tactic(=액션), 신호로 노드 실행 게이트(=signal/승인 게이트 유사), 실행 시 역할 바인딩(=role), 능력 기반 배정(=도메인 규칙의 약한 형태), 배터리 교대 후 같은 tactic 계속(=인계), 사전 시뮬 평가. 빠진 것: 계획자용 노코드 편집기 근거, 정적 검증(사람이 눈으로 확인), 공중↔지상 간 인계(UAV끼리 교대만 확인), 운용자 명령에 대한 런타임 가드, 임무 중 계획 구조 수정 불가(현장 지휘관 직접 불만).
- **NPS MEA/MEO가 "정적 검증"에 가장 가깝다**: 성공/실패/예외 분기 강제, 실행 전 특정 기체 적합성 검사, 명령의 논리 일관성 검증. 다만 GUI 없음, 해양 중심, 2020 이후 활동 근거 약함.
- **SIFT Playbook은 "play" 어휘와 "임무 전 play 개발 vs 비행 중 play calling" 구분의 원조**다. 우리 피치에서 "Playbook(SIFT)·IMPACT 계열 계보 + CCAST 실험 교훈을 노코드·검증 가능하게 만든 것"으로 설명하면 학술적 정당성이 생긴다(추정).
- OpenUxAS의 SPARK 증명은 "플래너 구현 코드"의 증명이지 "사용자가 만든 임무"의 검증이 아니다. 둘을 혼동하지 않아야 한다.

### Gaps
- CCAST 임무계획기(Swarm Tactics and Operations Mission Planner)의 UI 형태(그래프 편집기인지 폼인지)와 저작자(개발팀 vs 군인)는 공개 논문에서 확인 못함(Clark et al. 2021 원문 미확보).
- IMPACT의 play 목록·play 작성 도구 존재 여부, DTIC 최종 보고서 미확보.
- OpenUxAS의 지상·수상 기체 설정 지원 여부를 공식 문서로 확인하지 못함.
- 해군 CCS·육군 공통 통제기의 2025~2026 임무 저작 기능 근거 없음.

---

## Q5. 한국 제품·프로그램 (한화, LIG넥스원, KAI, 현대로템, 파블로항공, 니어스랩, 한국형 MUM-T C2)에 임무 저작 UI가 있나?

### Takeaway
한국에서는 **임무 저작(authoring) UI를 공개한 제품을 찾지 못했다.** 공개된 것은 "군집 임무계획 기술", "AI 생성 임무계획", "통합 지휘통제" 같은 기술 이름과 시연 보도뿐이다. 파블로항공은 드론쇼 설계 SW(네오피카소)와 운영 SW(PADSS)를 갖고 있어 "시각적 군집 저작" 경험은 있으나 군사 행동 저작은 아니다.

### Cited Findings
- [언론, 2025-05-22] 한화시스템: 실해역 무인수상정 10대 군집기동 검증, "국내 최초로 '무인수상정 군집 자율운항' 기술을 개발해 전투용 무인수상정의 핵심 장비인 '통합임무관리체계'의 개발 준비도 마쳤다", 기술 3축 "군집임무계획기술 ▲군집자율운항기술 ▲군집통신네트워크기술". 저작 도구·GUI 언급 없음 — [뉴데일리](https://biz.newdaily.co.kr/site/data/html/2025/05/22/2025052200169.html)
- [1차·언론, 2026-08-03, 프로젝트 기존 조사 재인용] 한화시스템 대기뢰전 시연: AI 생성 임무계획에 따라 AUV 탐색, 무인수상정 2종 동시 운용, "다수·다종의 무인체계를 동시에 통제할 수 있는 통합 지휘통제 기술" — [한화시스템 보도자료](https://www.hanwhasystems.com/kr/prcenter/newsView.do?bbidx=812), [뉴시스](https://www.newsis.com/view/NISX20260803_0003734434)
- [언론, 2025-05-22] LIG넥스원 해검: K-MOSA 적용 "무인수상정의 임무 중심 모듈화" — [뉴데일리](https://biz.newdaily.co.kr/site/data/html/2025/05/22/2025052200169.html)
- [2차·검색 스니펫] 핵심기술 과제 "전술 군집 무인기 임무계획 및 자율 임무 재계획 기술"('22.10~'26.09): 표적 우선순위·임무 재할당 요구 / ADD "인공지능 기반 군집 무인기 통제기술 연구"(2022-11~), 1·2과제 LIG넥스원, 3과제 한화시스템 — [Sheldon 뉴스레터(maily.so)](https://maily.so/sheldon/posts/l1zqgx6yr5x), [비즈한국](https://bizhankook.com/articles/31593.html) (과제 분담 문장의 정확한 출처 기사는 미확인)
- [언론·마케팅, 2025-07-30] 파블로항공 "군집조율 4단계": "4단계부터는 수십 대의 무인기를 단 한 명의 조종자가 통제할 수 있으며" — [유니콘팩토리](https://www.unicornfactory.co.kr/article/2025073009445511499)
- [언론, 2026-05-07] 파블로항공 "AI 기반 공연 설계 및 디자인 전용 소프트웨어 '네오피카소'", "공연 전주기 운영 소프트웨어 'PADSS'", "다른 제조사의 드론도 군집 전용 임무컴퓨터 및 통신 모듈 등을 추가 장착해 군집 운용할 수 있다" — [유니콘팩토리](https://www.unicornfactory.co.kr/article/2026050711480864566)
- [1차, 2025-03-20, 프로젝트 기존 조사 재인용] KAI–Shield AI Hivemind Enterprise 협력(유무인 복합 강화) — [Kyodo PR](https://kyodonewsprwire.jp/release/202503216075) (이번 조사에서 직접 열지 않음, 기존 노트의 URL 그대로)
- [언론, 2025-10] 대한항공–파블로항공: "군집 AI 기반의 자율비행 제어 기술과 지능형 분산 임무 통제 및 군집 운용체계를 공동으로 개발" — [유니콘팩토리](https://www.unicornfactory.co.kr/article/2025102314494091338)

### Inferences
- 한국 업체는 **"임무계획 알고리즘"(자동 생성·재할당)** 을 강조하고, 사람이 임무 논리를 조립·검증하는 저작 계층은 공개하지 않았다. 해외 자율 SW(Shield AI, HavocAI)와 짝을 맺는 흐름(기존 조사)과 합치면, 한국 생태계에서 "벤더 중립 노코드 플레이 편집기 + 검증"은 비어 있는 자리로 보인다(추정).
- 드론쇼 저작(파블로항공 네오피카소)은 "시각적 타임라인으로 다수 기체 행동을 사전 저작"하는 국내 선례로 언급할 수 있다. 다만 조건·분기·안전 게이트가 있는 임무 논리는 아니다.

### Gaps
- 한화·LIG넥스원·KAI·현대로템의 임무계획 SW 화면, 저작 주체, 검증 방식 공개 자료 없음.
- 니어스랩의 군 임무 저작 관련 자료는 이번 조사에서 찾지 못함.
- ADD 군집 과제의 수행 기관별 분담을 1차 자료로 확인하지 못함.

---

## Q6. 항목별 비교 (a 저작 방식, b 저작 주체, c 다중 도메인, d 검증·안전, e 런타임 재임무·인계, f 근거 품질)

### Takeaway
(a) 노코드 시각 저작은 공개 근거가 있는 곳이 없고, (d) 저작된 임무의 정적 검증은 NPS 연구뿐이며, (e) 교차 도메인 인계는 어디에도 공개되지 않았다. 나머지 요소(목표 기반 위임, 능력 기반 배정, 동종 대체, 승인 게이트)는 여러 곳에 흩어져 있다.

### Cited Findings
| 대상 | (a) 저작 방식 | (b) 저작 주체 | (c) 도메인 | (d) 저작물 검증·안전 | (e) 런타임 재임무·인계 | (f) 근거 |
|---|---|---|---|---|---|---|
| Anduril Lattice | Protobuf task 정의(코드) + UI 드롭다운 선택; 내부 BT 엔진 | 개발자/통합업체(+Anduril 담당자); 운용자는 선택·배정 | 다중 지향 | 스키마 breaking-change 탐지·타입 안전성만 | 의도→task 분해, 재임무(EDGE23) / 인계 규칙 비공개 | 개발자 문서 1차 양호, BT는 채용공고 — [Define a task](https://developer.anduril.com/guides/tasks/define), [채용공고](https://builtin.com/job/senior-software-engineer-autonomy-platform/7723240) |
| Shield AI Hivemind | SDK(C++ Pilot) + Forge(SDK·CLI·웹), 블록 카탈로그(2022) | AI 개발자·OEM | 공중 중심("across domains" 주장) | 시뮬 자동시험·V&V(개발 단계) | 팀 자율 / 인계 비공개 | 개괄 1차 + 채용공고 — [Shield AI 2022](https://shield.ai/hivemind-for-operational-read-and-react-swarming/), [PR 2025-03-06](https://www.prnewswire.com/news-releases/shield-ai-raises-240m-at-5-3b-valuation-to-scale-hivemind-enterprise-an-ai-powered-autonomy-developer-platform-302393843.html) |
| SeeByte Neptune | 목표(goal) 지정 + 위임안 수동 보정, SDK로 행동 추가 | 운용자(목표), 개발자(행동) | 해양(UUV·USV) | 사전 리허설(경로 미리보기) | 목표 변경, 고장 기체 목표 재수행 | 1차 마케팅 — [SeeByte](https://www.seebyte.com/products/neptune) |
| Milrem MIFIK/ARCOS | 사전 정의 mission set(search/intercept/shadow) + 경로 | 운용자 | 지상 | 공개 없음 | 경로 즉시 수정, 다중 임무 | 1차·언론 — [Janes 2022](https://janes.com/osint-insights/defence-news/c4isr/eurosatory-2022-milrem-robotics-launches-new-c2-system-for-unmanned-platforms), [Milrem](https://milremrobotics.com/autonomy/) |
| Auterion Nemyx | 목표 지정 + 효과 승인 | 운용자 | 공중 | 효과 승인(런타임) | 손실 시 표적 승계 | 1차·언론 — [IUS](https://insideunmannedsystems.com/auterion-demonstrates-one-operator-drone-swarm-strike-in-u-s-live-fire-test/) |
| Swarmer | 탐색 구역·표적·무력사용 승인 UI | 운용자(임무계획 담당 1명 포함) | 공중 | 무력사용 승인 | 소실 시 목표 승계, 중단 | 언론·창업자 인터뷰 — [Defense One](https://www.defenseone.com/business/2025/09/ukrainian-startup-has-re-invented-drone-swarming/408099/) |
| Saronic Echelon | 계획·시뮬·실행 단일 UI(세부 미공개) | 운용자 | 수상 | 시뮬 사전 검증(주장) | 실시간 개입 | 보도자료 — [Seapower](https://seapowermagazine.org/saronic-unveils-echelon-a-unified-platform-for-mission-planning-simulation-and-command-and-control-of-autonomous-surface-vessels/?print=pdf) |
| HavocAI | 의도·제약 지정(브라우저 콘솔) | 운용자 | 수상→공중·지상 확장 중 | 공개 없음 | 오버라이드 / 인계 비공개 | 2차 — [Sacra](https://sacra.com/research/havocai) |
| L3Harris AMORPHOUS / LM MDCX | 미공개 | 미공개 | 다중(주장) / 공중 다급 | 미공개 | 분산 과업 분배(주장) / 마수피얼 투하 | 언론·보도자료 — [Defense News](https://www.defensenews.com/unmanned/2025/02/10/l3harris-unveils-amorphous-autonomy-software-to-manage-drone-swarms/), [LM](https://news.lockheedmartin.com/2025-12-18-Skunk-Works-R-and-XTEND-Expand-Joint-All-Domain-Command-and-Control-for-Advanced-Mission-Execution) |
| DIU Orchestrator(요구) | 음성·텍스트·햅틱 의도 | 지휘관·운용자 | 이종 함대 | "constraints, timing, and priorities", 인간 이해 유지 | 의도 갱신 | 1차 — [DIU](https://www.diu.mil/latest/diu-and-dawg-launch-autonomous-vehicle-orchestrator-prize-challenge) |
| SIFT Playbook | 상세(임무 전 play 개발) ~ 간결(play calling) | 운용자/계획자(개념) | 공중(이종 UAV) | best-effort 계획 | play calling | 연구 2002~ — [DASC 2002](https://www.imse.iastate.edu/dorneich/files/2013/02/2002-07-31_DASC02_367_Miller.pdf) |
| AFRL IMPACT/OpenUxAS | play 호출(사전 정의) / XML·LMCP 메시지 | 운용자 호출, 개발자 정의 | 이종 UxV(시뮬) | 플래너 코드 SPARK 증명(저작물 아님) | 에이전트 기체 추천·재계획 | 연구 ~2017 — [IMPACT](https://independent.academia.edu/DougLange), [OpenUxAS](https://github.com/afrl-rq/OpenUxAS) |
| DARPA OFFSET CCAST | 사전 임무계획(노드⊃tactic, 신호) + 런타임 tactic 발행 | 지정된 팀원(SC2) | 공중+지상 | 사전 시뮬 평가, 수동 확인 | 역할 바인딩, 배터리 교대, 계획 구조 수정 불가 | 동료심사 연구 2023 — [arXiv 2308.00102](https://ar5iv.labs.arxiv.org/html/2308.00102) |
| NPS MEA/MEO·AVCL | 텍스트/XML 미션 언어(AVCL), 온톨로지 | 연구자(지휘관 명령 표현 목표) | UUV·USV·UAV(+UGV 스키마) | **실행 전 논리 검증, 성공/실패/예외 분기** | 런타임 윤리 검사(연구) | 연구 2011~2020 — [NPS](https://savage.nps.edu/AuvWorkbench/documentation/papers/ethics.html) |
| 한국(한화·LIG·KAI·파블로) | 미공개(AI 임무계획 강조) | 미공개 | 해상·공중 | 미공개 | 군집 재할당(과제 목표) | 언론 — [뉴데일리](https://biz.newdaily.co.kr/site/data/html/2025/05/22/2025052200169.html) |

### Inferences
- 우리 컨셉의 6개 요소 중 공개 사례가 있는 정도: ① 노코드 시각 저작 = 없음(BAE의 drag-and-drop은 ATO 계획) ② 정적 검증 = NPS 연구만 ③ 도메인별 전개 = 약한 형태(Lattice taskCatalog, Milrem mission set, SeeByte 능력 기반 위임, CCAST 능력 디스패처) ④ 교차 도메인 역할 인계 = 없음(동종 대체만) ⑤ 임무 중 플레이 주입·수동 전환 = 부분적(CCAST 런타임 tactic, Echelon·HavocAI 개입) ⑥ 운용자 명령까지 통과하는 런타임 안전 가드 = 공개 사례 없음(승인 게이트만 다수).

### Gaps
- 상용 제품 대부분이 임무 편집 UI 스크린샷·매뉴얼을 공개하지 않아, (a)의 "없음"은 **공개 근거 없음**이지 실제 부재 증명이 아니다.

---

## Q7. 결론 — "노코드 시각적 행동 저작 + 정적 검증 + 도메인별 전개 + 교차 도메인 역할 인계 + 런타임 가드" 조합을 공개적으로 제공하는 곳이 있나? 가장 가까운 경쟁자와 정확히 겹치는 부분은?

### Takeaway
**공개 자료 기준으로는 이 5요소 조합을 제공하는 제품·프로그램이 없다.** 구조적으로 가장 가까운 것은 연구 시스템인 DARPA OFFSET CCAST(2021 종료)이고, 상용으로는 Anduril Lattice(능력 카탈로그 기반 배정, 다중 도메인)와 SeeByte Neptune(목표 기반 위임 + 고장 기체 목표 재수행, 해양 한정)이 부분적으로 겹친다. 정적 검증은 NPS 연구에만 있다.

### Cited Findings
- CCAST와의 겹침: "Mission plans contain nodes, each containing one or more tactics." / "binding available vehicles … to roles or groups" / "trigger signals … that gate the execution" / "automatically select and assign vehicles with the necessary capabilities" / "can automatically Swap in order to continue tactic execution"; 차이: "There is no real mechanism for [the SC] to consider modification or amendments to the mission plan structure", 계획 확인은 사람이 수동 — [arXiv 2308.00102](https://ar5iv.labs.arxiv.org/html/2308.00102)
- Lattice와의 겹침: "deliberate, sequential actions … on an asset or team of assets", "An operator can only assign a task to an asset if the asset's `taskCatalog` advertises that task's type URL."; 차이: task 정의는 Protobuf 코드, 검증은 스키마 수준 — [Tasks overview](https://developer.anduril.com/guides/tasks/overview), [Define a task](https://developer.anduril.com/guides/tasks/define)
- SeeByte와의 겹침: "objective delegation based on the assets' capabilities", "the other vehicle(s) will execute the failed vehicles missing objectives", 리허설; 차이: 해양 한정, 사용자 저작 행동 없음(SDK로 개발자가 추가) — [SeeByte Neptune](https://www.seebyte.com/products/neptune)
- 정적 검증 선례: "ensure suitability of a mission definition for execution by a specific vehicle, all prior to mission parsing and execution" — [NPS](https://savage.nps.edu/AuvWorkbench/documentation/papers/ethics.html)
- 수요 측 경고: DAWG 국장 "not by clicking through menus or programming behaviors" — [DIU](https://www.diu.mil/latest/diu-and-dawg-launch-autonomous-vehicle-orchestrator-prize-challenge)

### Inferences
- **차별점으로 주장 가능한 것**(공개 근거 기준): (1) 계획자용 노코드 플레이 편집기 (2) 플레이의 **정적 검증**(반복 종료 조건 필수, 링크 손실·저배터리·GPS 이상 핸들러 존재, 위험 액션 승인 게이트, 신호 송수신 짝 맞춤) (3) 같은 액션의 **드론/USV/UGV별 전개 + 도메인 규칙 검사** (4) **공중↔수상↔지상 간 같은 스텝에서 역할 인계** (5) **운용자 명령까지 통과하는 런타임 가드**. 특히 (2)·(4)·(5)는 어떤 상용 제품도 공개하지 않았다.
- **피치 프레이밍 제안(추정)**: "Playbook(SIFT)·IMPACT의 play 개념 + CCAST의 노드·신호·역할 구조를, 계획자가 코드 없이 만들고 기계가 검증하는 형태로 만들었다." DIU Orchestrator와는 경쟁이 아니라 보완 관계로 말한다: "자연어 의도가 매핑될 대상인 **검증·서명된 플레이 라이브러리**." 운용자가 현장에서 행동을 프로그래밍한다는 인상은 피한다(Donovan 발언).
- **심사 리스크(추정)**: 미군 심사위원은 Lattice를 알 가능성이 높다. "Lattice도 task를 정의하고 배정한다"는 반문에는 "Lattice task 정의는 Protobuf 코드이고 검증은 스키마 수준, 우리는 임무 논리 자체를 검증"으로 답할 수 있다(위 출처 근거). CCAST 사례는 "연구에서 이미 효과가 확인된 구조이고, 현장 지휘관이 지적한 '계획 구조 수정 불가' 한계를 임무 중 플레이 주입으로 푼다"는 근거로 쓸 수 있다.
- 24시간 데모 범위로는 (2) 정적 검증 결과 화면과 (4) 드론→UGV 인계 장면이 "아무도 공개하지 않은 것"을 가장 짧게 보여주는 장면이다(추정).

### Gaps
- 비공개·기밀 프로그램(예: DAWG 내부, Orchestrator 선정 업체 제품)에 유사 기능이 있을 수 있으나 확인할 방법이 없다. "공개적으로 없다"까지만 주장할 수 있다.
- 오픈소스 behavior tree 시각 편집기(예: Groot)나 상용 드론 운영 SW(FlytBase 등)의 노코드 워크플로 기능은 이번 범위(국방·정부)에서 조사하지 않았다. 다른 조사 파일과 교차 확인이 필요하다.
