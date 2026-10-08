# 로봇·다중로봇 임무 저작(시각 DSL)과 검증 — 학계·오픈소스 선행연구 지도, 우리 개념과의 비교

> 작성: 2026-10-08 (리서치 에이전트). **모든 URL 접근일 = 2026-10-08.**
> 출처 등급: **[학술]** 동료심사 논문 · **[프리프린트]** 미심사 arXiv · **[OSS]** GitHub 저장소(활동 수치는 GitHub API `pushed_at`/stars를 2026-10-08에 조회한 값. `pushed_at`은 "어느 브랜치든 마지막 push"라 기본 브랜치 커밋 날짜와 다를 수 있음) · **[문서]** 공식 문서/매뉴얼 · **[학위]** 학위논문.
> 인용 방식: **(원문-직접추출)** = PDF/소스를 내려받아 텍스트를 직접 뽑음(글자 그대로) / **(초록)** = Semantic Scholar API 등에서 받은 초록 원문(**본문은 안 읽음**) / **(원문)** = WebFetch 요약 도구가 본문에서 발췌 / **(검색발췌)** = 검색엔진 요약·스니펫(원문 미열람, 최종 인용 전 재확인 필요).
> 평가 대상 개념(요약): 계획자가 노코드 시각 편집기에서 "단계 카드 + 연결선"으로 행동을 만든다(구역 수색·순찰·표적 관측·접근·중계·신호 송수신·IF·정지조건 있는 반복·운용자 승인 게이트). 저장 시 IR로 컴파일 → 정적 검사(도달성, 모든 반복에 출구, 링크 상실/저전력/GPS 이상 비상 핸들러 존재, 위험 행동은 운용자 승인이 지배(dominate), 신호 송수신 짝, 파라미터 범위, 각 단계를 수행할 수 있는 기체 유형 ≥1) → 서명 → 할당 시 도메인(공중/해상/지상)별 확장 → 지상 인터프리터가 역할별 상태·도메인 간 역할 인계·계획 주입·수동 개입·명령마다 런타임 가드로 실행.
> 범위 밖(형제 노트에 이미 있음): RTA/Simplex·실드(shield)·CBF는 `knowledge/inbox/2026-10-08-multi-uxv-research/safety-floor-mechanisms.md` 참조. 여기서는 반복하지 않는다.

---

## Q1. 로봇/드론 임무 명세 DSL — PROMISE, FLYAQ, Dronology, MAPmAKER, PsALM, LTLMoP, RoboChart, MissionLab, Blockly 계열, 최종사용자 프로그래밍 연구

### Takeaway
"비전문가용 다중로봇 임무 DSL → 플랫폼 독립 중간표현(IR) → 로봇별 인터프리터"라는 뼈대는 **이미 학계에 있다**(PROMISE 2019/2020이 거의 같은 구조이고, 서울대 하순회 교수 그룹의 SeMo→HiSARM 2018–2025는 "형식 IR + 도메인 간 재타깃 배포"를 주장한다). 단, 2021년 설문조사(시각 임무 환경 30개)는 **대부분이 단일 로봇용**이고, 다중로봇을 지원하는 FLYAQ·PROMISE·MissionLab도 **로봇별 분해를 사람이 직접** 한다고 결론냈다. 검증은 주로 LTL 패턴·합성 쪽이다. 우리 정적 검사 목록에 있는 구조적 안전 점검(비상 핸들러 존재, 승인 게이트 지배, 송수신 짝)을 하는 임무 도구는 찾지 못했다.

### Cited Findings

**비교표(요약) — 표기법 / 다중로봇 / 이기종 / 검증 / 도구 상태 / 연도**

| 시스템 | 표기 | 다중로봇 | 이기종 | 검증 | 도구·유지보수(2026-10-08) | 연도 |
|---|---|---|---|---|---|---|
| PROMISE | 그래픽+텍스트(Eclipse Xtext+Sirius) | O (parallel 루트가 로봇별 분기) | "(possibly) heterogeneous" 목표 | LTL 패턴 기반 의미론 | `SergioGarG/PROMISE_implementation` 마지막 push 2021-06-04, ★3 | 2019/2020 |
| FLYAQ | 지도 기반 웹 그래픽(MML) | O (멀티콥터 군집) | 멀티콥터 중심(가족 DSL은 AUV도) | 비행계획 생성 시 충돌·비행금지구역 회피 | `iivanoo/FLYAQ` 마지막 push 2015-04-05 | 2015 |
| PsALM / 명세 패턴 | 구조화 영어 → LTL/CTL | 로봇 무관(주로 단일) | – | NuSMV·Spectra·플래너 연동 | roboticpatterns.com 접속 거부(ECONNREFUSED) | 2019 |
| MAPmAKER | LTL | O (하위팀 분해, 분산 계획) | – | LTL 계획 | 데모 영상만 확인 | 2019 |
| LTLMoP | 구조화 영어 → GR(1) 합성 | 주로 단일 | – | 정확성 보장 합성, 합성 불가 설명 | `VerifiableRobotics/LTLMoP` 마지막 push 2016-10-11(GPL-3.0) → 사실상 중단 | 2010/2013 |
| RoboChart/RoboTool | UML풍 상태기계(그래픽) | 컨트롤러 단위 | – | CSP(FDR)·PRISM·Isabelle | GitHub 릴리스로 배포, Eclipse 2021-12 기반 | 2019~ |
| MissionLab | FSA 그래픽 편집기(CfgEdit) | O | contract-net로 이기종 확장 | 사용성 평가 | v7.0(2006-07)이 마지막 공개판 | 1997~2006 |
| Dolphin (LSTS) | 텍스트(Groovy 내부 DSL) | O (다중 기체 오케스트레이션) | UUV+UAV 현장시험 | – | LSTS 툴체인 연동 | 2018 |
| Neptus/IMC/DUNE (LSTS) | 지도 위 기동(maneuver) 그래프 | O (단일·다중 기체 운용) | AUV/ASV/UAV/ROV | 기체별 가능 기동만 제시 | DUNE 문서 2024.09.0 버전 존재 | 2000년대~ |
| SeMo → HiSARM (서울대) | 고수준 스크립트(텍스트) | O (분산·군집·혼합) | "retargetable ... across various domains" | "multiple verification environments", 형식 IR | 논문만 확인 | 2018/2020/2025 |
| MutRoSe | 고수준 명세 + HTN 분해 | O | 능력 기반 분해 | (후속 학위논문: UPPAAL) | 논문만 확인 | 2023 |
| Doherty 등(Linköping) | Task Specification Tree + 시간논리 | O (협업 UAS) | 이기종 UAS | 분산 제약 해결로 할당 | 논문만 확인 | 2013 |

**PROMISE (Chalmers/Gothenburg·L'Aquila·Luxembourg·Charles Univ.) — 우리 개념과 구조가 가장 비슷한 학술 시스템**
- [학술] García, Pelliccione, Menghi, Berger, Bures, "High-Level Mission Specification for Multiple Robots", SLE 2019, DOI 10.1145/3357766.3359535. ACM Artifacts Evaluated/Available 배지. (원문-직접추출) — [PDF (Chalmers)](https://www.cse.chalmers.se/~bergert/paper/2019-sle-promise.pdf), [DOI](https://doi.org/10.1145/3357766.3359535)
  - 초록: "We present PROMISE, a novel language that enables domain experts to specify missions on a high level of abstraction for teams of autonomous robots in a user-friendly way, while having well-defined semantics. ... The language is supported by a standalone tool that permits mission specification through a textual and a graphical interface"
  - 이기종 목표: "PROMISE stems from the necessity of allowing roboticists to specify missions for a team of (possibly) heterogeneous robots." PAL Robotics·Bosch Center of AI와 함께 정의(Co4Robots 프로젝트).
  - **컴파일러 → IR → 인터프리터 구조(우리 개념과 같음)**: "The compiler b transforms the mission specified through the DSL into an intermediate language c . The intermediate language is platform-agnostic and, therefore, users only need to write a new interpreter to support a new robot platform." / "PROMISE becomes robot-agnostic since only the interpreter has to be adapted when using a new robot platform."
  - 컴파일러는 "decomposes the global mission, and 3) automatically generates the encoding of missions of each robot in the intermediate language (one file for each robot). It also generates one readme file for each local mission, containing the translation of the mission into natural English." → **IR을 자연어로 역번역해 사용자에게 보여주는 아이디어**(우리 검증 결과 표시에 참고 가능).
  - 연산자: 문법에 `fallback`, `sequence`, `parallel`, `condition`, `combination`(TaskCombination), `delegate`, 이벤트 핸들러가 있다. "the operator parallel can only be used as a root operator. ... A robot is assigned to each branch associated with this operator". 예제에서 이벤트 `r1_low_battery`가 `charge_battery` 시퀀스를 트리거 → **저전력 비상 핸들러를 이벤트 핸들러로 표현**하는 선례. 단, 핸들러가 "있어야 한다"는 정적 검사는 언급 없음.
  - 한계(저자 스스로): "The synchronization among robots is currently performed by using events ... The adoption of a more flexible approach for synchronization remains as future work."
  - 평가: 시뮬레이터·실로봇 실험, 사용자 연구 2회. 구현: "an Eclipse plugin implemented in Xtext ... and Sirius". 참고문헌 [18]에 구현 저장소 `github.com/SergioGarG/PROMISE_implementation`.
  - 관련연구 비판(우리 포지셔닝에 유용): FLYAQ에 대해 "the mission specification becomes more complicated, since the operator is required to state precisely how the robots should behave"; MissionLab에 대해 "the only task that does not require specific knowledge from the user is the „assemblage" of robotic skills, whose semantics must be previously defined programmatically by users with knowledge of C++."; LTLvis에 대해 "even though graphical, the language is based on LTL operators ... Therefore, the specifier is requested to know the semantics of LTL."
- [학술] 도구 데모: García et al., "PROMISE: High-Level Mission Specification for Multiple Robots", ICSE 2020 Companion, DOI 10.1145/3377812.3382143. (초록) "PROMISE is built as an Eclipse plugin that provides a textual and a graphical interface for mission specification. Our tool is in turn integrated into a software framework, which provides functionalities as: (1) automatic generation from specification, (2) sending of missions to the robotic team; and (3) interpretation and management of missions during execution time." 로봇 모델 4종으로 검증. — [PDF](https://www.cse.chalmers.se/~bergert/paper/2020-icsedemo-promise.pdf), [DOI](https://doi.org/10.1145/3377812.3382143)
- [OSS] `SergioGarG/PROMISE_implementation`: 마지막 push 2021-06-04, ★3, 라이선스 표기 없음 → 재사용 대상이 아니라 **인용 대상**. — [GitHub](https://github.com/SergioGarG/PROMISE_implementation)

**FLYAQ (L'Aquila·VU Amsterdam·Chalmers) — 비전문가용 다중 멀티콥터 임무**
- [학술] Bozhinoski, Di Ruscio, Malavolta, Pelliccione, Tivoli, "FLYAQ: Enabling Non-expert Users to Specify and Generate Missions of Autonomous Multicopters", ASE 2015, pp. 801–806, DOI 10.1109/ASE.2015.104(Crossref로 서지 확인, 본문 미열람). — [DOI](https://doi.org/10.1109/ASE.2015.104)
  - 검색발췌(L'Aquila 저장소): "a platform enabling to (i) graphically define monitoring missions via a web interface, (ii) decompose the mission according to the number and nature of available quadrotors, and (iii) generate the implementation code orchestrating all the quadrotors of the swarm." / "a reconfiguration engine ... permits to change the mission at run-time." — [ricerca.univaq.it](https://ricerca.univaq.it/handle/11697/108441)
  - 비행계획 자동 생성(MODELS 2016): 최종사용자(예: 소방관) 대상 모델링 언어에서 드론별 저수준 행동을 생성하고 드론 간·장애물 충돌과 비행금지구역을 회피. (검색발췌) — [VU research portal](https://research.vu.nl/en/publications/automatic-generation-of-detailed-flight-plans-from-high-level-mis/)
  - 언어 가족: Di Ruscio, Malavolta, Pelliccione, "A family of domain-specific languages for specifying civilian missions of multi-robot systems", CEUR 1319 (2014); Ciccozzi 등 IEEE Access 2016은 멀티콥터와 AUV 두 도메인에 적용. (검색발췌) — [univaq IEEE Access PDF](https://ricerca.univaq.it/bitstream/11697/106776/1/IEEE_access.pdf)
  - Dragule 장(章)의 설명: "FLYAQ ... is an open-source research prototype ... The monitoring mission language (MML) allows specification of mission context such as obstacles, flight path (i.e., starting point, action points, ending point), and no-fly zones on a live map." (원문-직접추출) — [Dragule et al. 장 PDF](https://www.cse.chalmers.se/~bergert/paper/2021-bookchapter-roboticslanguages.pdf)
- [OSS] `iivanoo/FLYAQ` 마지막 push 2015-04-05, ★5. — [GitHub](https://github.com/iivanoo/FLYAQ)
- 연도 충돌 메모: 검색 요약은 "Springer 2013 copyright" 가능성을 언급했지만 확인하지 못했다. Crossref는 ASE 2015(2015-11)를 준다.

**설문조사 2편 (Chalmers 그룹) — "다중로봇 시각 임무 언어는 거의 없다"의 근거**
- [학술] Dragule, Berger, Menghi, Pelliccione, "A survey on the design space of end-user-oriented languages for specifying robotic missions", Software and Systems Modeling 20(4):1123–1158 (2021), DOI 10.1007/s10270-020-00854-x. (원문-직접추출, 저자 PDF) — [PDF](https://www.cse.chalmers.se/~bergert/paper/2020-sosym-missionspec.pdf), [DOI](https://doi.org/10.1007/s10270-020-00854-x)
  - 초록: "We present a survey of 30 mission specification environments for mobile robots that come with a visual and end-user-oriented language."
  - **다중로봇 핵심 결론**: "The large majority of our environments and their languages support one robot. ... Environments such as FLYAQ, PROMISE, and MissionLab support collaborative mission specification. ... Since the distribution of tasks to drones is done manually, there are no language concepts to express multi-robot mission specifications ... PROMISE ... however, the decomposition of the mission to local missions for each robot is also done manually. ... Beyond that, there is no more dedicated support for multi-robot missions, such as scheduling support or robot pooling for complex missions."
  - 시뮬레이터: "As many as 10 of the 30 environments provide a simulator ... Eight of these are limited to simulating single robots, while two, namely FLYAQ and PROMISE, even support multi-robot simulation using off-the-shelf simulators (Mavproxy and Gazebo, respectively)."
  - 프로그래밍 모델: "behavior trees, state machines, and the reactive control concepts in one of the languages (Aseba) are not more expressive, they provide a more abstract and restricted form of mission specification, forcing the developer to focus more on expressing the intelligence in an intuitive and comprehensible way." → **제한된 카드 어휘를 택하는 근거**로 인용 가능.
- [학술] Dragule, García Gonzalo, Berger, Pelliccione, "Languages for Specifying Missions of Robotic Applications", in *Software Engineering for Robotics* (Springer, 2020-12/2021), DOI 10.1007/978-3-030-66494-7_12. Table 2(DSL 표기법·스타일): Choregraphe(Visual), NaoText(Textual), Microsoft VPL(Visual), EasyC(Textual+Visual), SMACH(Textual, internal), Open Roberta(Visual), FLYAQ(Visual), Aseba(Textual+Visual), LEGO EV3(Visual), MissionLab(Visual), CABSL(Textual), BehaviorTree.CPP(Textual), ROS Behavior Tree(Textual), UE4 BT(Textual), PROMISE(Textual+Visual). "The types of robots supported by the respective languages and tools are mostly service mobile robots, including ground and flying types." (원문-직접추출) — [PDF](https://www.cse.chalmers.se/~bergert/paper/2021-bookchapter-roboticslanguages.pdf), [DOI](https://doi.org/10.1007/978-3-030-66494-7_12)

**명세 패턴 / PsALM (Menghi 등)**
- [학술] Menghi, Tsigkanos, Pelliccione, Ghezzi, Berger, "Specification Patterns for Robotic Missions", IEEE TSE, DOI 10.1109/TSE.2019.2945329(온라인 2019, Crossref 권호 2021-10), arXiv 1901.02077. (초록) "domain-specific languages are usually tied to specific robot models, while logical languages such as LTL are difficult to use by non-experts. We present a catalog of 22 mission specification patterns for mobile robots, together with tooling for instantiating, composing, and compiling the patterns to create mission specifications." — [arXiv](https://arxiv.org/abs/1901.02077), [DOI](https://doi.org/10.1109/TSE.2019.2945329)
  - 평가: 실무 도구(Spectra, LTLMoP 등)에서 모은 요구 436건 + BOSCH·PAL Robotics와 정의한 5건, 총 441건. 대부분 모호했고 패턴으로 표현 가능, 패턴 사용 시 모호성 감소. (검색발췌) — [ICSE 2020 Journal-First](https://2020.icse-conferences.org/details/icse-2020-Journal-First/83/Specification-Patterns-for-Robotic-Missions)
- [학술] PsALM 도구(ICSE 2019 Demo): 구조화 영어 문법(패턴=블록, 연산자로 조합) → LTL/CTL. Spectra, 플래너, NuSMV, Simbad와 연동, 로봇 무관. (검색발췌) — [ICSE 2019 Demo 페이지](https://2019.icse-conferences.org/details/icse-2019-Demonstrations/4/PsALM-Specification-of-Dependable-Robotic-Missions), [PDF](https://www.cse.chalmers.se/~bergert/paper/2019-icse-psalm.pdf)
- 접근 메모: 공식 사이트 roboticpatterns.com은 2026-10-08 접속 시 ECONNREFUSED.

**MAPmAKER**
- [학술] García, Menghi, Pelliccione, "MAPmAKER: Performing multi-robot LTL planning under uncertainty", RoSE 2019, DOI 10.1109/RoSE.2019.00008. 분산 계획: "decomposing the robotic team into subteams based on their missions, and then by running a classical planning algorithm"; 부분 지식은 "calling several times a classical planning algorithm"으로 처리. (검색발췌, 초록만) — [Chalmers research](https://research.chalmers.se/en/publication/523093)

**Dronology (Notre Dame) — DSL이 아니라 연구용 sUAS 관리 플랫폼**
- [학술] Cleland-Huang, Vierhauser, Bayley, "Dronology: An Incubator for Cyber-Physical System Research", ICSE 2018 NIER, arXiv 1804.02423. sUAS 비행을 관리·조정하는 시스템과 여러 릴리스의 산출물(요구사항·안전 등)을 공개하고, 고충실도 시뮬레이션과 실기체를 모두 지원. (검색발췌, 초록만) — [arXiv](https://arxiv.org/abs/1804.02423)
- [OSS] `JaneClelandHuang/Dronology` 마지막 push 2017-03-13(MIT). 후속 DroneResponse는 같은 그룹의 반자율 sUAS 관리 연구 환경이다. 공개 저장소는 찾지 못했다. — [GitHub](https://github.com/JaneClelandHuang/Dronology), [ND CSE](https://cse.nd.edu/?p=3535)

**LTLMoP / 반응형 합성 (Kress-Gazit, Cornell)**
- [학술] Finucane, Jing, Kress-Gazit, "LTLMoP: Experimenting with language, Temporal Logic and robot control", IROS 2010, DOI 10.1109/IROS.2010.5650371. Wong, Finucane, Kress-Gazit, "Provably-correct robot control with LTLMoP, OMPL and ROS", IROS 2013, DOI 10.1109/IROS.2013.6696636. (서지만 Crossref 확인, 초록 미확보) — [DOI 2010](https://doi.org/10.1109/IROS.2010.5650371), [DOI 2013](https://doi.org/10.1109/IROS.2013.6696636)
- 동작 방식(검색발췌, Cornell 뉴스 2011): 구조화 영어 명세 → 과제가 가능하면 완수를 보장하는 컨트롤러. 불가능하면 문제를 사용자에게 알려 준다. — [Cornell Chronicle](https://news.cornell.edu/stories/2011/11/structured-english-brings-robots-closer-everyday-users)
- [프리프린트] Raman & Kress-Gazit, "Unsynthesizable Cores — Minimal Explanations for Unsynthesizable High-Level Robot Behaviors", arXiv 1409.1455. 검증 실패 이유를 최소 단위로 설명 → **"왜 저장이 거부됐는지"를 보여주는 UX 선례**. — [arXiv](https://arxiv.org/abs/1409.1455)
- [OSS] `VerifiableRobotics/LTLMoP` 마지막 push 2016-10-11, ★56, GPL-3.0. 유지보수 중단 상태이므로 24시간 안에 재사용할 대상이 아니다. — [GitHub](https://github.com/VerifiableRobotics/LTLMoP)
- [학술] Spectra(GR(1) 명세 언어): Maoz & Ringert, "Spectra: a specification language for reactive systems", SoSyM 2021, DOI 10.1007/s10270-021-00868-z (서지만). `SpectraSynthesizer/spectra-synt` 마지막 push 2024-03-14, ★9, BSD-3. — [DOI](https://doi.org/10.1007/s10270-021-00868-z), [GitHub](https://github.com/SpectraSynthesizer/spectra-synt)

**RoboChart / RoboTool (York, RoboStar)**
- [학술] Miyazawa et al., "RoboChart: modelling and verification of the functional behaviour of robotic applications", SoSyM 2019, DOI 10.1007/s10270-018-00710-z. (초록) "we present RoboChart, a domain-specific modelling language based on UML, but with a restricted set of constructs to enable a simplified semantics and automated reasoning. ... using an implementation of RoboChart and its semantics as a set of Eclipse plug-ins called RoboTool." — [DOI](https://doi.org/10.1007/s10270-018-00710-z)
- [문서] RoboTool은 "supports graphical modelling, validation, and automatic generation of mathematical definitions". 배포는 GitHub 릴리스 패키지(또는 Eclipse 2021-12 업데이트 사이트). 플러그인에 "RoboChart Prism Generator", "RoboChart CSP Generator"가 있다. (원문) — [RoboTool 페이지](https://robostar.cs.york.ac.uk/robotool/)
- 검증 경로(검색발췌): tock-CSP → FDR4 시간 정제 검사. 확률 확장은 PRISM으로 변환한다. Isabelle 기반 Interaction Trees 의미론도 있다. 2025 arXiv는 핵 방사선 점검 UGV의 안전 아키텍처에 적용했다. — [arXiv 2511.14805](https://arxiv.org/pdf/2511.14805), [RoboStar 출판물](https://www.cs.york.ac.uk/robostar/publications/)
- 메모: 사용자는 로봇 공학자다(최종사용자 아님). Eclipse 기반이라 React 스택에 넣기 어렵다.

**MissionLab (Georgia Tech, Arkin) — 군용 다중로봇 시각 임무 명세의 원조**
- [학술] MacKenzie, Arkin, Cameron, "Multiagent Mission Specification and Execution", Autonomous Robots 4(1):29–52 (1997). 임무를 유한상태 수용기(FSA) 다이어그램으로 표현한다. 행동은 원, 지각 트리거는 화살표다(temporal sequencing). (검색발췌) — [GT TMR PDF](https://sites.cc.gatech.edu/ai/robot-lab/tmr/mission-auro.pdf), [MTU 서지](https://digitalcommons.mtu.edu/michigantech-p/8233)
- [문서] MissionLab은 "multiagent mission specification and control software"로 고수준 군사식 계획을 실·모의 로봇 팀이 실행하게 한다. 그래픽 편집기는 CfgEdit다. DARPA Tactical Mobile Robotics(도시전·정보수집)에서 사용성 시험을 했다. v7.0(2006-07)에 이기종 플랫폼용 스크립트 기반 임무 관리가 추가됐다. (검색발췌) — [MissionLab v7.0](https://sites.cc.gatech.edu/ai/robot-lab/research/MissionLab), [매뉴얼 v6.0 PDF](https://www.cc.gatech.edu/ai/robot-lab/research/MissionLab/mlab_manual-6.0.pdf)
- 이기종 확장: Ulam, Endo, Wagner, Arkin(ICRA 2006)이 CBR 임무 마법사에 contract-net 과제 할당을 추가했다. 자동 임무 수리(mission repair) 사용성 평가는 Moshkina & Endo 2005. (검색발췌) — [Ulam et al. PDF](https://sites.psu.edu/real/files/2016/08/UlamEtAlICRA12006-21j7cjy.pdf), [GT repository](https://repository.gatech.edu/entities/publication/46f90c68-bf6a-4df8-8644-dae995c6b9a5)
- 혼동 주의: 2024년 독일 연방군 dtec.bw "MissionLab"(UniBw München, 군용기 임무기술)은 별개 프로젝트다. — [ESUT](https://esut.de/en/2024/10/fachbeitraege/52633/das-projekt-missionlab/)

**LSTS 툴체인(포르투갈 Porto) — "지도 위 기동 그래프 + 기체별 능력 필터"를 이기종 공중·해상에 실제 운용한 사례**
- [문서] Neptus 매뉴얼(검색발췌): "The planning of each mission plan is in the form of a graph and, for ease of use, can be drawn directly into the map previously created." / "Each vehicle has a configuration file in Neptus describing several capabilities that it can provide. This encompasses its feasible maneuvers ... As a result, for each vehicle only the set of feasible maneuvers are presented to the user." — [Neptus concepts](https://lsts.pt/neptus/manual/trunk/concepts.html)
- [학술] LSTS 툴체인은 "heterogeneous autonomous vehicles like AUVs, ASVs, UAVs and ROVs in both single and multi-vehicle operations"를 통제하는 데 쓰였다(검색발췌). DUNE API 문서(2024.09.0)에 PlanSpecification·PlanManeuver·PlanTransition 클래스가 있다. 그래서 IMC 계획은 "기동 노드 + 전이 엣지" 구조로 **추정**된다(필드 정의는 미확인). — [ngcuv12 PDF](https://www.dcc.fc.up.pt/~edrdo/publications/papers/ngcuv12.pdf), [DUNE 2024.09.0 classes](https://www.lsts.pt/docs/dune/master/classes.html)
- [학술] Lima, Marques, Pinto, Sousa, "Dolphin: A Task Orchestration Language for Autonomous Vehicle Networks", IROS 2018, DOI 10.1109/IROS.2018.8594059, arXiv 1803.00944. (초록) "A Dolphin program expresses an orchestrated execution of tasks defined compositionally for multiple vehicles. Building upon the base case of elementary one-vehicle tasks, the built-in operators include support for composing tasks in several forms, for instance according to concurrent, sequential, or event-based task flow. The language is implemented as a Groovy DSL ... field tests using unmanned underwater vehicles (UUVs) and unmanned aerial vehicles (UAVs)". 논문은 "an IMC plan is a sequence of maneuvers for a single vehicle"라고 설명한다(검색발췌). → IMC 계획은 **기체 1대 단위**이고, 다중 기체 조율은 Dolphin 텍스트 DSL이 맡는다. — [arXiv](https://arxiv.org/abs/1803.00944), [DOI](https://doi.org/10.1109/IROS.2018.8594059)

**서울대 하순회 교수 그룹 (한국 선행연구 — 국내 심사위원 대상으로 반드시 언급)**
- [학술] Hong, Jung, Park, Ha, "SeMo: Service-Oriented and Model-Based Software Framework for Cooperating Robots", IEEE TCAD 2018, DOI 10.1109/TCAD.2018.2857339. (초록) "we propose a novel software development framework that separates mission specification and robot behavior programming. For mission specification, a novel scripting language is proposed with the expression capability of dynamic mode change and multitasking. ... the actual robot software is automatically generated from the model." — [DOI](https://doi.org/10.1109/TCAD.2018.2857339)
- [학술] Hong, Kang, Ha, "Software Development Framework for Cooperating Robots with High-level Mission Specification", IROS 2020, DOI 10.1109/IROS45743.2020.9341328. (초록) "To enable a casual user to specify various types of cooperative missions easily, the high-level mission scripting language is extended with new features such as team hierarchy, group service, one-to-many communication. The script program is refined to the robot codes through two intermediate steps, strategy description and task graph generation". — [DOI](https://doi.org/10.1109/IROS45743.2020.9341328)
- [학술] Kang, Jeong, Yoon, Ha, "A Framework for Multi-Robot Programming: From High-Level Specification to Retargetable Deployment"(HiSARM), ACM TECS 2025, DOI 10.1145/3747325. (초록) "HiSARM employs a high-level language to enable mission planners to specify collaborative tasks among multiple robots intuitively. ... HiSARM provides multiple verification environments by introducing a formal intermediate representation and enabling retargetable deployment of the binary file across various domains, including simulation and real robots." — [DOI](https://doi.org/10.1145/3747325)
  - 메모: 여기서 "domains"는 시뮬레이션/실로봇 같은 **배포 대상**을 뜻하고, 공중/해상/지상 같은 **운용 도메인**은 아니다(초록 문맥 기준. 본문 미열람).

**기타 다중로봇 임무 명세**
- [학술] Gil, Rodrigues, Pelliccione, Calinescu, "Mission specification and decomposition for multi-robot systems"(MutRoSe), Robotics and Autonomous Systems 163 (2023), DOI 10.1016/j.robot.2023.104386, CC-BY. (검색발췌) "users have limited or no robotics experience, and they often find the process of allocating concrete tasks to each robot within a multi-robot system very challenging". — [White Rose](https://eprints.whiterose.ac.uk/204904/), [DOI](https://doi.org/10.1016/j.robot.2023.104386)
- [학술] Doherty, Heintz, Kvarnström, "High-Level Mission Specification and Planning for Collaborative Unmanned Aircraft Systems Using Delegation", Unmanned Systems 1(1):75–119 (2013), DOI 10.1142/S2301385013500052. Task Specification Tree는 "a highly expressive specification language for complex multiagent tasks that supports mixed-initiative delegation with adjustable autonomy". 경매와 분산 제약 해결로 할당하고, 응급 서비스 시나리오에서 운용자 1명이 UAV 여러 대와 상호작용한다. (검색발췌. PDF 쪽수 표기가 저널 쪽수와 다름) — [LiU PDF](https://www.ida.liu.se/~frehe08/publications/us2013.pdf), [DOI](https://doi.org/10.1142/S2301385013500052)
- [학술] Palomeras et al., "Using Petri nets to specify and execute missions for autonomous underwater vehicles", IROS 2009, DOI 10.1109/IROS.2009.5354045 (서지만). — [DOI](https://doi.org/10.1109/IROS.2009.5354045)

**최종사용자 로봇 프로그래밍 연구 (Blockly·BT 편집기·PbD)**
- [학술] Ajaykumar, Steele, Huang, "A Survey on End-User Robot Programming", ACM Computing Surveys 54(8) (2021; DBLP는 2022로 표기), DOI 10.1145/3466819, arXiv 2105.01757. (초록) "This article surveys work on end-user robot programming, with a focus on end-user program specification." — [arXiv](https://arxiv.org/abs/2105.01757), [DOI](https://doi.org/10.1145/3466819)
- [학술] CoSTAR: Paxton, Hundt, Jonathan, Guerin, Hager, "CoSTAR: Instructing collaborative robots with behavior trees and vision", ICRA 2017, DOI 10.1109/ICRA.2017.7989070. 2016 KUKA Innovation Award 우승작으로, BT 편집기에 인식·공간추론을 통합했다. IROS 2018 사용자 연구(N=35)에서 SUS 평균 73.4/100이 나왔다. (검색발췌) — [arXiv 1611.06145](https://arxiv.org/abs/1611.06145), [Wisconsin 논문 페이지](https://peopleandrobots.wisc.edu/publications/evaluating-methods-for-end-user-creation-of-robot-task-plans/)
- [학술] Code3: Huang & Cakmak, HRI 2017, DOI 10.1145/2909824.3020215. 인식·조작(시연 학습)·고수준 drag-and-drop 프로그래밍 3요소로 구성된다. 비로봇공학자 N=10이 PR2를 빠르게 프로그래밍했다. (검색발췌) — [UW HCR Lab](https://hcrlab.cs.washington.edu/publications/huang2017hri)
- [학술] CoBlox(ABB): block-based 언어 + lead-through이며 ABB "Wizard Easy Programming"으로 출시됐다(검색발췌). 튜토리얼 연구는 Ritschel, Sawant, Weintrop 외, SPE 2023, DOI 10.1002/spe.3167, N=79. — [ZORA (UZH)](https://www.zora.uzh.ch/entities/publication/2eff1b79-bdb4-4d36-b70c-b05649c5526c), [UBC PDF](https://www.cs.ubc.ca/~rtholmes/papers/spe_2022_ritschel.pdf)
- [학술] Mayr-Dorn, Winterer, Salomon, Hohensinger, Ramler, "Considerations for using Block-Based Languages for Industrial Robot Programming – a Case Study", RoSE 2021, DOI 10.1109/RoSE52553.2021.00008. (검색발췌) "while Blockly is able to express large and complex real-world robot programs, a major contributing factor is not just the language itself but the presentation of the robot's run-time environment as well as support by the development environment (i.e., editor)." → **편집기와 런타임 표시가 언어만큼 중요하다**는 근거. — [RoSE 2021](https://conf.researchr.org/details/rose-2021/rose-2021-papers/4/Considerations-for-using-Block-Based-Languages-for-Industrial-Robot-Programming-a-)
- [OSS] Blockly+ROS: `erlerobot/robot_blockly`(드론·로봇용 웹 블록 프로그래밍)은 **archived**, 마지막 push 2018-11-22, GPL-3.0. ROSBLOCKS(2025, SciTePress)는 React+Blockly+Node.js+Electron 기반 ROS 2 시각 프로그래밍이다(코드 공개 여부 미확인). Rockly(TU Wien 학위논문 2019)는 HOBBIT PT2에서 시험했다. — [GitHub robot_blockly](https://github.com/erlerobot/robot_blockly), [ROSBLOCKS](https://scitepress.org/PublishedPapers/2025/137140), [TU Wien](https://repositum.tuwien.at/handle/20.500.12708/1761)
- [학술] BT vs 상태기계 언어 비교: Ghzouli, Berger, Johnsen, Wasowski, Dragule, "Behavior Trees and State Machines in Robotics Applications", IEEE TSE 2023, DOI 10.1109/TSE.2023.3269081, arXiv 2208.04211. (초록) "We identify similarities between behavior trees and state machines in terms of language design ... We observed that the usage of behavior-tree DSLs in open-source projects is increasing rapidly." 후속으로 "Effects of specifying robotic missions in behavior trees and state machines", J. Computer Languages 2025, DOI 10.1016/j.cola.2025.101330가 있다(**제목만 확인**, 초록 미확보). — [arXiv](https://arxiv.org/abs/2208.04211), [DOI COLA](https://doi.org/10.1016/j.cola.2025.101330)

### Inferences
- 우리 "카드+엣지" 편집기는 표기법만 보면 **MissionLab의 FSA(행동=노드, 트리거=엣지)와 Neptus의 기동 그래프 계보**에 속한다. PROMISE·BT처럼 트리 구조가 아니라 **그래프(상태기계형)**다. 그래서 "모든 반복에 출구", "도달성", "승인 게이트 지배" 같은 **그래프 정적 분석이 자연스럽게 정의된다**. BT는 구조가 반복·출구를 강제하므로 같은 검사가 덜 필요하다.
- PROMISE의 "글로벌 임무 → 로봇별 IR 파일"은 **설계 시점 분해**다. 우리 개념은 **할당 시점에 도메인별로 확장**한다. 늦은 바인딩이므로 차별점으로 내세울 수 있다. 단, HiSARM의 retargetable deployment는 비슷한 늦은 바인딩을 다른 축(시뮬/실기체)에서 이미 한다.
- Dragule SoSyM 2021의 "다중로봇 분해는 수동, 스케줄링·로봇 풀링 언어 지원 없음"은 **2021년 시점** 진술이다. 그 뒤로 MutRoSe(2023), HiSARM(2025), Heppner BT capabilities(2024)가 이 빈칸을 일부 채웠다. 발표에서 "아무도 안 했다"라고 말하면 안 된다.

### Gaps
- Polyscope(UR) 최종사용자 연구는 이번 조사에서 직접 찾지 않았다(설문 Ajaykumar 2021이 포괄하는 것으로 추정, 미확인).
- FLYAQ·LTLMoP·MissionLab·HiSARM·MutRoSe는 본문을 읽지 않았다. 특히 HiSARM의 "formal intermediate representation"이 어떤 형식이고 어떤 성질을 검증하는지 미확인.
- IMC PlanSpecification/PlanTransition의 필드 정의(조건 표현식이 있는지)는 미확인.
- PROMISE 저장소 라이선스 미표기 → 코드 재사용 가능 여부 불명.

---

## Q2. 시각 편집기가 있는 행동 저작 프레임워크 — 2026년 유지보수 현황과 Python+React 스택 24시간 내 사용 가능성

### Takeaway
활발한 프레임워크는 BehaviorTree.CPP(+Nav2), py_trees, FlexBE(WebUI), SMACH, PlanSys2, RAFCON, XState, Node-RED다. 하지만 **"React 안에 넣을 수 있고, 오프라인이고, ROS 없이 돌아가는 시각 편집기"는 없다.** Groot2는 소스 비공개 데스크톱 앱(무료/PRO), FlexBE WebUI는 ROS 2가 필요하다. Stately Studio는 호스팅 SaaS라 오프라인 정책(POLICY 1)에 맞지 않는다. 24시간 안에 할 수 있는 현실적 조합은 **React Flow(xyflow) 편집기 + pydantic IR + networkx 그래프 검사 + 자체 Python 인터프리터(또는 py_trees) + RTAMT 런타임 모니터**다. 개념 측면에서 가장 많이 빌릴 곳은 FlexBE의 "전이별 자율 수준(autonomy level)과 운용자 강제·차단 전이"다.

### Cited Findings

**유지보수 현황표 (GitHub API, 2026-10-08 조회)**

| 저장소 | 마지막 push | ★ | 라이선스 | 비고 |
|---|---|---|---|---|
| [BehaviorTree/BehaviorTree.CPP](https://github.com/BehaviorTree/BehaviorTree.CPP) | 2026-10-03 | 4237 | MIT | C++ BT 엔진, XML 트리 |
| [BehaviorTree/Groot2](https://github.com/BehaviorTree/Groot2) | 2026-01-19 | 62 | 없음 | 저장소에 `README.md`·`.github`만 있음 → **소스 비공개**, 이슈 트래커 용도 |
| [BehaviorTree/Groot](https://github.com/BehaviorTree/Groot) (v1) | 2025-02-28 | 892 | 표기 없음 | 구버전 편집기 |
| [BehaviorTree/BehaviorTree.ROS2](https://github.com/BehaviorTree/BehaviorTree.ROS2) | 2025-11-25 | 343 | Apache-2.0 | ROS 2 래퍼 |
| [ros-navigation/navigation2](https://github.com/ros-navigation/navigation2) | 2026-10-07 | 4771 | 혼합 | Nav2, BT.CPP 기반 내비 BT |
| [splintered-reality/py_trees](https://github.com/splintered-reality/py_trees) | 2026-09-17 | 641 | BSD계(NOASSERTION) | Python BT |
| [splintered-reality/py_trees_ros](https://github.com/splintered-reality/py_trees_ros) | 2026-09-15 | 233 | 〃 | ROS 확장 |
| [splintered-reality/py_trees_js](https://github.com/splintered-reality/py_trees_js) | 2026-09-15 | 23 | 〃 | "Javascript library for behaviour tree visualisation" |
| [FlexBE/flexbe_behavior_engine](https://github.com/FlexBE/flexbe_behavior_engine) | 2026-05-20 | 76 | 〃 | 온보드 HFSM 엔진 |
| [flexbe/flexbe_webui](https://github.com/flexbe/flexbe_webui) | 2026-09-10 | 15 | Apache-2.0 | Python FastAPI + JS 웹 UI, **ROS 2 필요** |
| [FlexBE/flexbe_app](https://github.com/FlexBE/flexbe_app) | 2024-05-02 | 50 | BSD-3 | 구형 UI |
| [ros/executive_smach](https://github.com/ros/executive_smach) | 2026-09-30 | 185 | 〃 | SMACH(Python), 편집기 없음 |
| [ros-visualization/executive_smach_visualization](https://github.com/ros-visualization/executive_smach_visualization) | 2025-09-29 | 20 | 없음 | smach_viewer(보기 전용) |
| [PlanSys2/ros2_planning_system](https://github.com/PlanSys2/ros2_planning_system) | 2026-09-02 | 494 | Apache-2.0 | PDDL 계획 + BT 실행, 시각 편집기 없음 |
| [DLR-RM/RAFCON](https://github.com/DLR-RM/RAFCON) | 2026-09-18 | 212 | EPL-1.0 | Python HSM + GUI(데스크톱) |
| [statelyai/xstate](https://github.com/statelyai/xstate) | 2026-10-08 | 30265 | MIT | JS 상태기계/statechart |
| [statelyai/xstate-viz](https://github.com/statelyai/xstate-viz) | 2023-11-03 | 452 | MIT | **archived** |
| [statelyai/inspect](https://github.com/statelyai/inspect) | 2026-08-18 | 83 | MIT | XState 실행 검사기 |
| [Phrogz/visual-scxml-editor](https://github.com/Phrogz/visual-scxml-editor) | 2026-08-24 | 24 | MIT | VS Code용 SCXML 시각 편집 |
| [node-red/node-red](https://github.com/node-red/node-red) | 2026-10-07 | 23721 | Apache-2.0 | 저코드 흐름 편집기 |
| [cmc0619/node-red-contrib-mavlink](https://github.com/cmc0619/node-red-contrib-mavlink) | 2026-10-06 | 1 | MIT | MAVLink 노드(미성숙) |
| [aerostack2/aerostack2](https://github.com/aerostack2/aerostack2) | 2026-09-16 | 392 | BSD-3 | ROS 2 다중 공중로봇 프레임워크 |
| [xyflow/xyflow](https://github.com/xyflow/xyflow) (React Flow) | 2026-10-07 | 38601 | MIT | 노드-엣지 편집기 라이브러리 |
| [RaspberryPiFoundation/blockly](https://github.com/RaspberryPiFoundation/blockly) (구 google/blockly) | 2026-10-05 | 13578 | Apache-2.0 | 블록 편집기 |
| [retejs/rete](https://github.com/retejs/rete) | 2026-09-27 | 12291 | MIT | 노드 편집기 프레임워크 |

**Groot2 (BT.CPP 공식 편집기)**
- [문서] Free/PRO 이원 구조다. Free는 "full behavior tree editor"와 다중 파일 프로젝트를 주지만 모니터·로그 시각화는 "20 nodes"로 제한된다. PRO는 무제한 모니터, 블랙보드 시각화, 인터랙티브 브레이크포인트, 결함 주입을 준다. "Floating License" "€590/year". 플랫폼은 Windows/Linux 설치본과 AppImage(x86_64, aarch64). (원문) — [behaviortree.dev/groot](https://www.behaviortree.dev/groot/)
- 추론: 데스크톱 앱이고 소스가 비공개라 **우리 React UI에 내장할 수 없다**. BT.CPP XML을 IR 교환 포맷으로 쓸 때만 쓸모가 있다.

**FlexBE — 운용자 승인 게이트와 계획 주입의 가장 가까운 선례**
- [OSS/문서] README(원문-직접추출): "The main advantage of FlexBE over similar approaches is the good operator integration and an intuitive user interface. Besides executing behaviors in full autonomy, the operator can restrict execution of certain transitions or trigger them manually. Furthermore, FlexBE supports modifying the whole structure of a behavior during its execution without restarting it." — [flexbe_behavior_engine README](https://github.com/FlexBE/flexbe_behavior_engine)
- [OSS/문서] 자율 수준 동작(turtlesim 데모 문서, 원문-직접추출): "FlexBE supports variable autonomy levels, so choosing "Full" autonomy allows the system to automatically choose to autonomously repeat the "Eight" transition. As shown below, the other transitions in the `OperatorDecisionState` are configured to require "Full" autonomy, but "Eight" only requires "High" autonomy". README: "The behavior starts in `Full` autonomy, you can use the runtime view to drop to `Low` autonomy, which will pause the behavior". → **전이마다 요구 자율 수준을 달고, 현재 수준이 낮으면 운용자 확인을 기다린다.** 우리 "승인 게이트"의 실행 시점 버전이다. — [quickstart_details.md](https://github.com/FlexBE/flexbe_turtlesim_demo/blob/ros2-devel/docs/quickstart_details.md), [turtlesim demo README](https://github.com/FlexBE/flexbe_turtlesim_demo)
- [OSS/문서] WebUI: "a graphical editor for designing Hierarchical Finite State Machines (HFSMs) ... the UI enables the operator to supervise the execution of the onboard behavior, provide input where necessary, and take control if needed in what we term "collaborative autonomy"." 기술 스택은 "native Python and FastAPI along with a JavaScript-based browser interface". `ros2 launch`로 실행하며 flexbe_behavior_engine 4.1+가 필요하다. (원문-직접추출/원문) — [flexbe_webui](https://github.com/flexbe/flexbe_webui)
- [학술] Schillinger, Kohlbrecher, von Stryk, "Human-robot collaborative high-level control with application to rescue robotics", ICRA 2016, DOI 10.1109/ICRA.2016.7487442(서지만). Romay et al., "Collaborative autonomy between high-level behaviors and human operators for remote manipulation tasks using different humanoid robots", J. Field Robotics 2016, DOI 10.1002/rob.21671. ROS wiki(검색발췌): "the operator is able to influence the execution during runtime, e.g., by forcing transitions and the robot can request help or confirmation from the operator, if required." — [DOI ICRA](https://doi.org/10.1109/ICRA.2016.7487442), [ROS wiki 미러](https://mirror.umd.edu/roswiki/flexbe_behavior_engine.html)
- 차이(추론): FlexBE의 게이트는 **실행 시점 설정**이다. "위험 행동은 반드시 승인이 지배해야 한다"를 **저장 전에 정적으로 보장**하는 기능은 문서에서 찾지 못했다. 또한 단일 로봇 대상이다.

**SMACH / PlanSys2 / RAFCON / Aerostack2**
- SMACH: Bohren & Cousins, "The SMACH high-level executive", IEEE RAM 17(4) 2010(Dragule 장 참고문헌, 원문-직접추출). Python 절차형 상태기계이고 편집기 없이 뷰어만 있다. — [executive_smach](https://github.com/ros/executive_smach)
- RAFCON(DLR): Brunner et al., IROS 2016 DOI 10.1109/IROS.2016.7759506. 저장소 설명: "uses hierarchical state machines, featuring concurrent state execution ... ships with a graphical user interface supporting the creation of state machines and contains IDE like debugging mechanisms." (OSS 설명 원문) — [GitHub](https://github.com/DLR-RM/RAFCON), [DOI](https://doi.org/10.1109/IROS.2016.7759506)
- PlanSys2: "a PDDL-based planning system for ROS2"(저장소 설명). 최종사용자 시각 저작 도구가 아니다. — [GitHub](https://github.com/PlanSys2/ros2_planning_system)
- Aerostack2: "a ROS 2 framework developed to create autonomous multi-aerial-robot..."(저장소 설명). 깊게 조사하지 않음. — [GitHub](https://github.com/aerostack2/aerostack2)

**XState / Stately / SCXML**
- [문서] Stately Studio는 "a suite of tools for building app logic"이고 "export your code from Stately Studio into your codebase"가 가능하다. "As a premium user" 팀 기능이 있다 → 유료 호스팅 도구. 오프라인 동작은 문서에 없다. (원문) — [Stately docs](https://stately.ai/docs/studio)
- 추론: XState **라이브러리**(MIT)는 프런트엔드 실행 시각화에 쓸 수 있다. 하지만 Studio 편집기는 POLICY 1(시연 경로 외부 API 금지)에 걸리므로 쓰지 않는다. xstate-viz는 archived 상태다.

**Node-RED (ROS/MAVLink)**
- [OSS] Node-RED 본체는 활발하다(★23.7k). MAVLink·ROS 2 노드는 ★0–3짜리 개인 저장소뿐이다. DroneBlocks의 `dexi-sim-ftw`는 PX4+ROS2+Node-RED+Unity 시뮬레이터(★3, 2026-10-06 push)다. — [node-red](https://github.com/node-red/node-red), [node-red-contrib-mavlink](https://github.com/cmc0619/node-red-contrib-mavlink), [dexi-sim-ftw](https://github.com/DroneBlocks/dexi-sim-ftw)
- 추론: Node-RED는 데이터 흐름(메시지 전달)이 의미론이라 "단계 카드 + 상태 전이" 의미론과 맞지 않는다. 런타임까지 들여오면 우리 IR·검사를 Node-RED 흐름에 다시 매핑해야 한다. 24시간 안에서는 비추천.

**24시간 재사용 후보 — 우리 스택(FastAPI·pydantic·React, `pyproject.toml` 확인)과의 궁합**
- 편집기: React Flow(xyflow, MIT, ★38.6k, 2026-10-07 push)로 카드=노드, 연결선=엣지를 구현한다. Blockly(Apache-2.0)는 "블록 끼우기" 메타포라 카드+엣지 그래프와는 결이 다르다. Rete.js(MIT)도 대안이다. — 위 표 링크
- 그래프 정적 검사: networkx 3.6.1에 `immediate_dominators`, `simple_cycles`, `strongly_connected_components`가 있음을 로컬에서 확인했다(`python3 -c "import networkx as nx; hasattr(nx,'immediate_dominators')"` → True). "위험 행동 노드의 지배자 집합에 승인 노드가 있는가", "각 SCC에 바깥으로 나가는 엣지가 있는가(반복 출구)", "시작에서 도달 가능한가"를 몇십 줄로 구현할 수 있다. — [networkx immediate_dominators 문서](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.dominance.immediate_dominators.html)
- 런타임 실행: py_trees(Python, 활발)를 쓰거나 자체 인터프리터를 쓴다. py_trees를 쓰면 BehaVerify(아래 Q3)로 nuXmv 모델을 뽑을 수 있다는 부가 이점이 있다.
- 런타임 가드: RTAMT(Python STL 모니터, pip, BSD-3) — Q3 참조.

### Inferences
- "노코드 + 오프라인 + 이기종 다중기체 + 정적 안전검사"를 한 번에 주는 기성 오픈소스는 없다. 그래서 편집기와 검사기는 **직접 만들고**, 의미론·용어는 FlexBE(자율 수준·강제 전이), PROMISE(IR·인터프리터), Neptus(능력 필터)에서 빌려 인용하는 전략이 맞다.
- BT.CPP XML이나 SCXML을 IR로 쓰면 외부 검증 도구(BehaVerify, AS2FM)와 연결할 여지가 생긴다. 다만 24시간 안에서는 pydantic JSON IR이 더 싸다. "SCXML/BT XML로 내보내기 가능"은 로드맵으로만 말하는 편이 안전하다.

### Gaps
- Groot2 라이선스 FAQ 본문은 읽지 못했다(가격표만 확인).
- FlexBE 자율 수준의 정확한 단계명(Off/Low/High/Full 중 "Off" 포함 여부)은 공식 문서(flexbe.readthedocs.io, wiki.ros.org)가 봇 차단(Anubis)으로 열리지 않아 확인하지 못했다. 데모 문서에서 "Low/High/Full"만 확인했다.
- Aerostack2의 미션/BT 편집 기능, Nav2 BT 편집 UX는 깊게 보지 않았다.

---

## Q3. 로봇 임무·행동의 검증 — 모델 검사, 런타임 검증, 최종사용자 프로그램의 정적 안전 검사

### Takeaway
BT·상태기계를 모델 검사기로 옮기는 도구는 성숙해지고 있다(Biggar&Zamani 2020 LTL, BehaVerify→nuXmv 2022~, Ingrand→Fiacre/Tina 2025, AS2FM→JANI 통계적 모델검사 2025, RoboChart→FDR/PRISM). 런타임 모니터도 Python으로 바로 쓸 수 있다(RTAMT, ROSMonitoring, NASA FRET→Ogma→Copilot). **최종사용자가 시각적으로 만든 프로그램을 저장 시점에 형식 검증하고 쉬운 말로 피드백하는 선례는 RoVer(UIST 2018, 사회규범)**가 가장 가깝다. 산업계에서 비행 전 정적 검사의 예는 PX4 FeasibilityChecker(기체 유형 적합성 포함)다. "비상 핸들러 존재·승인 게이트 지배·송수신 짝"을 묶은 임무 정적 검사기는 찾지 못했다.

### Cited Findings

**BT/상태기계 모델 검사**
- [학술] Biggar & Zamani, "A Framework for Formal Verification of Behavior Trees With Linear Temporal Logic", IEEE RA-L 2020, DOI 10.1109/LRA.2020.2970634. (초록) "there does not currently exist a method to formally verify their correctness without compromising their most valuable traits: modularity, flexibility and reusability. ... we prove that this method does not compromise the flexible design process of BTs, i.e. changes to subtrees can be verified separately and their combination can be assured to be correct." — [DOI](https://doi.org/10.1109/LRA.2020.2970634)
- [학술/OSS] Serbinowska & Johnson, "BehaVerify: Verifying Temporal Logic Specifications for Behavior Trees", SEFM 2022, DOI 10.1007/978-3-031-17108-6_19, arXiv 2208.05360. (초록) "BehaVerify is a tool that creates a nuXmv model from a py_tree. ... customized leaf nodes will require additional user input to be correctly modeled. ... BehaVerify is able to create a nuXmv model with over 100 nodes". 후속(Stateful BT, arXiv 2411.14165)에서는 DSL로 nuXmv 모델·py_trees 구현·Haskell 구현을 생성하고, 2025 학위논문은 contingency 런타임 모니터를 추가했다(검색발췌). 저장소 `verivital/behaverify`는 2026-08-26 push, ★29, MIT. — [arXiv](https://arxiv.org/abs/2208.05360), [GitHub](https://github.com/verivital/behaverify), [Vanderbilt 학위논문](https://ir.vanderbilt.edu/items/b381e658-e0fa-45be-ae68-3e8bd4c0b3b5)
- [프리프린트] Ingrand(LAAS-CNRS), "A formal implementation of Behavior Trees to act in robotics", arXiv 2502.11904 (2025). (초록) "translating them to a formal language which enables us to perform verification of programs written with BT, as well as runtime verification while these BT execute. This allows us to formally verify BT correctness without requiring BT programmers to master formal languages" (Fiacre → Tina LTL/CTL, Hippo로 형식 모델을 BT 엔진 대신 온라인 실행). — [arXiv](https://arxiv.org/abs/2502.11904)
- [학술] AS2FM(EU Horizon CONVINCE, grant 101070227), IROS 2025, arXiv 2508.18820. (초록) "We introduce an extension of the SCXML format, designed to model system components including both Robot Operating System 2 (ROS 2) and Behavior Tree (BT) features. Further, we contribute Autonomous Systems to Formal Models (AS2FM), a tool to translate the full system model into JANI. ... verifiable in less than one second using consumer hardware ... the verification runtime scales linearly with the size of the model". 관련 SCAN 통계적 모델검사기 arXiv 2603.28794(2026)는 "The SCXML modeling language has been chosen for its expressivity and because it can be specified via a graphical notation."(검색발췌). — [arXiv AS2FM](https://arxiv.org/abs/2508.18820), [arXiv SCAN](https://arxiv.org/pdf/2603.28794)
- [학술] RoboChart → CSP(FDR)/PRISM: Q1 참조.
- [학술/학위] UPPAAL 계열: Galvão(UnB, 2023 학위논문)는 계층 도메인 정의에서 UPPAAL 템플릿을 생성하고 다중로봇 임무 성질을 TCTL로 검사했다(MutRoSe 계열, 검색발췌). TAMAA(MDU 2020)는 UPPAAL 기반 임무계획에서 배터리 같은 감시자(monitor)를 시간 오토마타로 표현했다(검색발췌). Cranfield는 다중 UAV 협동 수색을 SMV로 CTL 검사했다(arXiv 1003.0381). **UPPAAL + 다중 UAV 비행 전 계획 검증을 직접 다룬 논문은 찾지 못함.** — [UnB 학위논문 PDF](https://repositorio.unb.br/bitstream/10482/49798/1/DaniloJoseBispoGalvao_DISSERT.pdf), [TAMAA](https://www.es.mdu.se/publications/5685-TAMAA__UPPAAL_based_Mission_Planning_for_Autonomous_Agents), [arXiv 1003.0381](https://arxiv.org/abs/1003.0381)
- [학술] 서베이: Luckcuck, Farrell, Dennis, Dixon, Fisher, "Formal Specification and Verification of Autonomous Robotic Systems: A Survey", ACM Computing Surveys 52(5), DOI 10.1145/3342355, arXiv 1807.00048. 2025 후속 "Revisiting Formal Methods for Autonomous Robots: A Structured Survey"(arXiv 2509.20488, 미심사)은 형식 합성·확률 검증 채택이 늘었다고 보고한다(검색발췌). — [arXiv 1807.00048](https://arxiv.org/abs/1807.00048), [arXiv 2509.20488](https://arxiv.org/abs/2509.20488)

**런타임 검증(모니터)**
- [학술/OSS] ROSMonitoring: Ferrando, Cardoso, Fisher, Ancona, Franceschini, Mascardi, TAROS 2020, DOI 10.1007/978-3-030-63486-5_40. 장점은 "portability across multiple ROS distributions and its agnosticism w.r.t. the specification formalism"(검색발췌). ROSMonitoring 2.0(FMAS 2024, arXiv 2411.14367)은 서비스와 ordered topic까지 확장했다. 저장소 `autonomy-and-verification-uol/ROSMonitoring`은 2026-06-29 push, ★44, MIT. — [ICRA2020 PDF(UniGe)](https://iris.unige.it/retrieve/e268c4cd-59c8-a6b7-e053-3a05fe0adea1/ROSMonitoring_ICRA2020.pdf), [GitHub](https://github.com/autonomy-and-verification-uol/ROSMonitoring), [arXiv 2.0](https://arxiv.org/abs/2411.14367)
- [학술/OSS] RTAMT(Ničković 외): ATVA 2020 "RTAMT: Online Robustness Monitors from STL", STTT 2024 저널판, arXiv 2501.18608(2025). Python API, 이산/연속 시간 STL, 온라인 모니터는 bounded-future 부분집합만, C++ 백엔드는 선택이다(순수 Python 가능). ROS 브리지 RTAMT4ROS가 있다(검색발췌). 저장소 `nickovic/rtamt`는 2026-09-19 push, ★79, BSD-3, PyPI `rtamt`. → **우리 "명령마다 런타임 가드"를 STL 규칙(예: "고도 < X 항상", "링크 끊기면 5초 안에 RTL")으로 쓰는 가장 빠른 길.** — [arXiv](https://arxiv.org/abs/2501.18608), [PyPI](https://pypi.org/project/rtamt/), [GitHub](https://github.com/nickovic/rtamt)
- [학술/OSS] NASA FRET → Ogma → Copilot: Perez, Mavridou, Pressburger, Will, Martin, "Monitoring ROS2: from Requirements to Autonomous Robots", FMAS 2022, arXiv 2209.14030. (초록) "FRET is used to specify requirements with unambiguous semantics, which are then automatically translated into temporal logic formulæ. Ogma generates monitor specifications from the FRET output, which are compiled into hard-real time C99. ... we have extended Ogma to generate ROS2 packages defining monitoring nodes". Ogma는 Space ROS 권장 모니터링 솔루션으로 언급된다(검색발췌, Haskell discourse). `nasa/ogma` 2026-09-27 push ★584 Apache-2.0, `Copilot-Language/copilot` 2026-09-08 push ★835. — [arXiv](https://arxiv.org/abs/2209.14030), [nasa/ogma](https://github.com/nasa/ogma), [copilot](https://github.com/Copilot-Language/copilot), [Ogma 1.0.9 공지](https://discourse.haskell.org/t/ann-nasas-ogma-1-0-9/6301)
- 실드(shield)·RTA·CBF: 형제 노트 `safety-floor-mechanisms.md` 참조(Alshiekh AAAI-18 등).

**최종사용자 작성 프로그램의 정적/형식 검사 — 가장 가까운 선례**
- [학술] Porfirio, Sauppé, Albarghouthi, Mutlu, "Authoring and Verifying Human-Robot Interactions"(RoVer), UIST 2018 **Best Paper**, DOI 10.1145/3242587.3242634(Crossref 확인. 연구실 페이지는 다른 DOI 10.1145/3379337.3415872를 함께 적어 혼선 있음). (초록) "We have developed an authoring environment that utilizes these methods to provide developers of social-robot applications with feedback at design time ... Our evaluation with application developers (N=9) shows that the use of formal-verification methods increases designers' ability to identify and contextualize social-norm violations." 연구실 설명(검색발췌): "Designers drag and drop robot behaviors into the editing environment to create an interaction flow, which RoVer converts into an executable program." / "If RoVer detects that a designer-created program will violate a social norm, the social norm is flagged and presented in plain English." — [DOI](https://doi.org/10.1145/3242587.3242634), [Wisconsin 연구실](https://robotics.wisc.edu/authoring-and-verifying-interactions)
  - 후속: Figaro(CHI 2021, DOI 10.1145/3411764.3446864). Porfirio는 현재 미 해군연구소(NRL) 박사후연구원(검색발췌) → **국방 맥락 연결고리**. — [DOI](https://doi.org/10.1145/3411764.3446864), [Porfirio](https://peopleandrobots.wisc.edu/staff/porfirio-david/)
- [OSS] **PX4 비행 전 임무 타당성 검사**(`src/modules/navigator/MissionFeasibility/FeasibilityChecker.hpp`, 마지막 커밋 2026-09-26). 검사 항목(원문-직접추출): `mission_validity_failed`, `takeoff_failed`, `land_pattern_validity_failed`, `distance_between_waypoints_failed`, `fixed_wing_land_approach_failed`, `takeoff_land_available_failed`, `items_fit_to_vehicle_type_failed`. 주석: "@brief Check if the mission items fit to the vehicle type" / "@brief Check general mission item validity, e.g. supported commands." → 우리 "각 단계를 할 수 있는 기체 유형 ≥1" 검사의 **산업계 단일 기체 버전**. — [PX4 FeasibilityChecker.hpp](https://github.com/PX4/PX4-Autopilot/blob/main/src/modules/navigator/MissionFeasibility/FeasibilityChecker.hpp)
- [학술] Dragule SoSyM 2021: 30개 환경 중 "five of the environments offer semantic services", 오류 표시(ErrorMarking) 기능이 있다(원문-직접추출). 안전 성질 정적 검사를 기능으로 분류한 항목은 없다. — [PDF](https://www.cse.chalmers.se/~bergert/paper/2020-sosym-missionspec.pdf)
- [학술] LTLMoP의 합성 불가 설명(Raman & Kress-Gazit), PsALM의 패턴 → LTL/CTL → NuSMV 연동: Q1 참조. 둘 다 "사용자가 원하는 성질"을 검사하고, "모든 임무가 지켜야 할 고정 안전 규칙"을 검사하지는 않는다.

### Inferences
- 우리 정적 검사의 대부분(도달성, 반복 출구, 승인 지배, 송수신 짝, 파라미터 범위, 능력 커버리지)은 **모델 검사가 아니라 그래프·타입 검사**다. 그래서 networkx 수준으로 24시간 안에 구현할 수 있다. 학술적으로는 "고정된 안전 정책을 구조적으로 강제하는 린터(linter)"로 포지셔닝하고, "임의 LTL 성질 검증(PsALM/BehaVerify/AS2FM)은 향후 IR → nuXmv/JANI 내보내기로"라고 말하는 편이 정직하다.
- "승인 노드가 위험 행동을 지배(dominate)해야 한다"는 컴파일러의 지배자(dominator) 개념을 임무 그래프에 적용한 것이다. 조사 범위에서 같은 표현을 쓴 로봇 임무 도구는 찾지 못했다. FlexBE는 실행 시점 자율 수준으로 같은 목적을 달성한다.
- **IR 서명(signing)**: 조사한 학술·오픈소스 임무 도구(PROMISE, FLYAQ, HiSARM, FlexBE, Neptus, PX4) 어디에서도 "검증된 임무 IR에 서명하고 실행기가 서명을 확인한다"는 기능을 보지 못했다(부재 확인이지 부재 증명은 아님).

### Gaps
- Groot2 PRO의 "fault injection"이 정적 검사를 포함하는지 미확인.
- 국방·항공 분야 비공개/상용 임무 계획기(예: 각 사 GCS)의 비행 전 검사 기능은 공개 자료가 없어 조사하지 못함.
- RoVer 본문(어떤 모델 검사기, 어떤 논리)은 미열람.

---

## Q4. 이기종 다중로봇 역할 할당·인계 — 능력 매칭(MRTA·CBBA)과 "같은 단계에서 이어받기"

### Takeaway
할당 이론(Gerkey&Matarić 2004 분류, CBBA 2009)과 **능력 기반 BT 하위트리 런타임 재할당**(Colledanchise 2015, Heppner ICRA 2024)은 있다. 시간논리 계획에서 고장 시 국소/전역 재할당하는 연구도 있다. 하지만 **진행 중인 단계의 상태를 넘겨 다른 도메인 기체가 "같은 단계에서 이어받는" 인계 프로토콜**은 찾지 못했다. 공중↔해상(UAV↔USV) 추적 인계도 리더-팔로워나 단계 분할(마수피얼 회수)만 있고, 추적 소유권(custody) 이전 절차는 찾지 못했다.

### Cited Findings
- [학술] Gerkey & Matarić, "A Formal Analysis and Taxonomy of Task Allocation in Multi-Robot Systems", IJRR 23(9):939–954 (2004), DOI 10.1177/0278364904045564. "Most work on MRTA has been ad hoc and empirical ... we present a formal study of MRTA problems." 분류 축은 과제 유형(ST/MT), 로봇 유형(SR/MR), 할당 유형(IA/TA)이다(검색발췌). 확장으로 Korsah 등(상호의존 효용·제약), Nunes 등 2017이 있다. — [TAMU PDF](https://cse-robotics.engr.tamu.edu/dshell/cs689/papers/gerkey04formal.pdf), [USC](https://robotics.usc.edu/publications/347)
- [학술] Choi, Brunet, How, "Consensus-Based Decentralized Auctions for Robust Task Allocation", IEEE T-RO 25(4):912–926 (2009), DOI 10.1109/TRO.2009.2022423. (초록) "consensus-based auction algorithm (CBAA) and its generalization to the multi-assignment problem, i.e., the consensus-based bundle algorithm (CBBA) ... robust to both inconsistencies in the situational awareness across the fleet and variations in the communication network topology." 2010 ACC 확장은 협력 규칙이 있는 이기종 에이전트용이다(검색발췌). — [DOI](https://doi.org/10.1109/TRO.2009.2022423), [MIT DSpace](https://dspace.mit.edu/handle/1721.1/52330)
- [프리프린트] Colledanchise, Marzinotto, Dimarogonas, Ögren, "Adaptive Fault Tolerant Execution of Multi-Robot Missions using Behavior Trees", arXiv 1502.02960 (2015). (초록) "By extending the single robot BT to a multi-robot BT, we are able to combine the fault tolerant properties of the BT, in terms of built-in fallbacks, with the fault tolerance inherent in multi-robot approaches, in terms of a faulty robot being replaced by another one. ... how mission performance is affected by minor faults (a robot losing one capability) as well as major faults (a robot losing all its capabilities)." — [arXiv](https://arxiv.org/abs/1502.02960)
- [학술] Heppner, Oberacker, Roennau, Dillmann, "Behavior Tree Capabilities for Dynamic Multi-Robot Task Allocation with Heterogeneous Robot Teams", ICRA 2024, arXiv 2402.02833. (초록) "we propose and implement a system that allows a user to specify missions using Behavior Trees (BTs), which can then, at runtime, be dynamically allocated to the current robot team. The system allows to statically model an individual robot's capabilities within our ros_bt_py BT framework. It offers a runtime auction system to dynamically allocate tasks to the most capable robot in the current team. The system leverages utility values and pre-conditions to ... prevent faulty assignments." 전작(CASE 2023 "Distributed Behavior Trees for Heterogeneous Robot Teams")은 "shovable" 데코레이터를 임무 시작 시 평가했기 때문에 런타임 재할당이 제한됐다(검색발췌). → **"사용자가 쓴 임무 + 정적 능력 모델 + 런타임 능력 매칭"으로 우리 개념과 가장 가까운 할당 연구.** — [arXiv](https://arxiv.org/abs/2402.02833)
- [프리프린트] 시간논리 + 고장 재할당: "Minimum-Violation Temporal Logic Planning for Heterogeneous Robots under Robot Skill Failures"(arXiv 2410.17188)는 고장 난 드론의 전송 과제를 다른 드론에 넘기는 연쇄 대체 예를 제시한다(검색발췌). 국소(문제 로봇만)/전역(팀 전체) 재할당으로 "eliminate reconstructing the entire plan or resynthesizing a new task"를 주장하는 연구도 있다(검색발췌. 검색 결과 목록상 arXiv 2110.08436로 보이나 **제목·저자 귀속 미확인**). — [arXiv 2410.17188](https://arxiv.org/abs/2410.17188), [arXiv 2110.08436](https://arxiv.org/abs/2110.08436v2)
- [학술] Mayya, Saldaña, Kumar의 회복탄력적 할당은 가장 많이 열화된 능력을 기준으로 재할당하고, 자원 제약을 최소한으로 완화해 성능이 점진적으로 저하되게 한다(검색발췌). — [academia.edu 사본](https://www.academia.edu/101355036/Resilient_Task_Allocation_in_Heterogeneous_Multi_Robot_Systems)
- [학술] 이기종 장기 임무 프레임워크(arXiv 2411.02062)에서는 로봇별 BT가 과제 결과와 상태를 감시한다. 실패 시 폴백(예: 저전력 드론 비상착륙)을 실행하고, 중앙 Monitor가 계획 유효성을 판단해 재계획한다(검색발췌). — [arXiv 2411.02062](https://arxiv.org/abs/2411.02062)
- [학술] 공중-해상: UAV-USV 협동은 대체로 리더-팔로워다("the UAV first plans a path to rapidly detect targets and relay information, followed by a USV tracking this path", arXiv 2511.02592 관련연구 서술, 검색발췌). 해상-공중 마수피얼 회수(2014)는 USV 원거리 접근 → UAV 상대위치 제공 → USV 견인으로 **단계별 주도권이 바뀐다**(검색발췌). — [arXiv 2511.02592](https://arxiv.org/abs/2511.02592), [CROSBI 753019](https://www.bib.irb.hr/753019)
- [학술] MissionLab(contract-net 이기종 확장)과 Doherty TST(경매 + 분산 제약, 조정 가능 자율)도 이 계보에 속한다: Q1 참조.

### Inferences
- "같은 단계에서 이어받기"를 구현하려면 단계 상태(예: 수색 구역 중 완료된 셀, 추적 중 표적 트랙 ID, 반복 카운터)를 **역할 단위로 IR 밖에 저장**해야 한다. 그래야 다른 기체의 도메인 확장본이 그 상태에서 다시 시작한다. 조사한 문헌은 대부분 "과제 단위로 재할당(처음부터 다시)"이었다. 그래서 **역할 상태 직렬화 + 도메인 재확장**은 우리 차별점이 될 수 있다(부재 확인이지 부재 증명은 아님).
- 발표에서는 Heppner 2024와 Colledanchise 2015를 "능력 기반 재할당은 선행연구가 있다"로 인정하고, "도메인이 다른 기체로 진행 상태를 넘긴다"를 새 부분으로 좁혀 말하는 편이 방어하기 쉽다.

### Gaps
- Korsah 등 iTax(2013)의 DOI·내용은 직접 확인하지 못했다.
- STEAM/팀워크 이론(Tambe)의 역할 재배정, RoboCup 동적 역할 할당은 시간 관계로 조사하지 않았다.
- 2001년 "미완료 하위과제 트리" 논문(검색 요약에 언급)의 서지 미확인.

---

## Q5. 결론 — 가장 가까운 연구, 남은 새로움, 인용 권고

### Takeaway
요소별로는 선행연구가 거의 다 있다. 비전문가 다중로봇 DSL→IR→인터프리터(PROMISE), 형식 IR과 재타깃 배포(HiSARM, 한국), 지도 위 기동 그래프와 기체별 능력 필터(Neptus/IMC), 전이별 운용자 자율 수준과 실행 중 행동 수정(FlexBE), 시각 저작 + 형식 검증 + 쉬운 말 피드백(RoVer), 능력 기반 런타임 재할당(Heppner 2024), 비행 전 기체 적합성 검사(PX4), Python 런타임 모니터(RTAMT)가 그 예다. **남은 새로움은 "조합"과 "정적으로 강제하는 안전 정책"**이다. 즉 노코드 카드 편집 → 구조적 안전 린트(비상 핸들러 필수·승인 지배·송수신 짝·능력 커버리지) → 서명 → 할당 시 도메인 확장 → 도메인 간 역할 상태 인계 → 명령마다 가드. 이 묶음을 한 시스템에서 하는 선례는 찾지 못했다.

### Cited Findings
- 가장 가까운 시스템(가까운 순서, 각 근거는 위 Q1–Q4):
  1. **PROMISE**: 그래픽+텍스트 DSL, "(possibly) heterogeneous" 팀, 컴파일러가 로봇별 IR 생성, 플랫폼별 인터프리터, 저전력 이벤트 핸들러 예제. 차이: 분해가 수동이고(Dragule 2021), 정적 안전 검사·승인 게이트·인계가 없다. Eclipse 기반이며 2021년 이후 정지. — [SLE'19 PDF](https://www.cse.chalmers.se/~bergert/paper/2019-sle-promise.pdf)
  2. **HiSARM / SeMo (서울대)**: 고수준 스크립트 → 전략 기술 → 태스크 그래프 → 로봇 코드, "formal intermediate representation", 재타깃 배포. 차이: 텍스트 스크립트이고, 운용자 승인·도메인 간 인계는 초록에 언급이 없다. — [DOI HiSARM](https://doi.org/10.1145/3747325)
  3. **Neptus/IMC + Dolphin (LSTS)**: 지도 위 기동 그래프, 기체별 가능 기동만 제시, AUV/ASV/UAV 실운용, 다중 기체는 Dolphin 텍스트 DSL. 차이: IMC 계획은 기체 1대 단위이고 정적 안전 정책 검사·역할 인계는 확인되지 않았다. — [Neptus](https://lsts.pt/neptus/manual/trunk/concepts.html), [Dolphin](https://arxiv.org/abs/1803.00944)
  4. **FlexBE**: 전이별 자율 수준, 운용자의 전이 강제·차단, 실행 중 행동 구조 수정(= 계획 주입), 웹 UI. 차이: 단일 로봇이고 ROS 2가 필요하며 게이트는 실행 시점 설정이다. — [README](https://github.com/FlexBE/flexbe_behavior_engine)
  5. **RoVer**: drag-and-drop 저작 → 실행 프로그램 변환 → 형식 검증 → 쉬운 영어로 위반 표시. 차이: 사회규범이 대상이고 단일 로봇·HRI다. — [DOI](https://doi.org/10.1145/3242587.3242634)
  6. **MissionLab**: 군용(DARPA TMR) 다중로봇 FSA 시각 명세, contract-net 이기종 확장. 차이: 2006년 이후 정지. — [MissionLab](https://sites.cc.gatech.edu/ai/robot-lab/research/MissionLab)
  7. **Heppner 2024 / Colledanchise 2015**: 능력 모델 기반 BT 하위트리 런타임 할당·고장 대체. 차이: 진행 상태를 넘기는 이어받기와 도메인 확장이 없다. — [arXiv 2402.02833](https://arxiv.org/abs/2402.02833), [arXiv 1502.02960](https://arxiv.org/abs/1502.02960)
  8. **PX4 FeasibilityChecker**: 업로드 임무의 비행 전 정적 검사(기체 유형 적합성 포함). 단일 기체용이다. — [소스](https://github.com/PX4/PX4-Autopilot/blob/main/src/modules/navigator/MissionFeasibility/FeasibilityChecker.hpp)
- 공백의 근거(인용용): Dragule SoSyM 2021 "The large majority of our environments and their languages support one robot ... there is no more dedicated support for multi-robot missions, such as scheduling support or robot pooling" — [PDF](https://www.cse.chalmers.se/~bergert/paper/2020-sosym-missionspec.pdf). Biggar & Zamani 2020 "there does not currently exist a method to formally verify their [BT] correctness without compromising ... modularity, flexibility and reusability"(2020년 시점 진술. 이후 BehaVerify·AS2FM 등장) — [DOI](https://doi.org/10.1109/LRA.2020.2970634). AS2FM 사본의 "model checking remain uncommon in the robotics domain due to usability and accessibility challenges"(검색발췌, Scribd 사본) — [arXiv](https://arxiv.org/abs/2508.18820).

### Inferences
- **새로움으로 주장할 만한 것(조사 범위 내에서 선례를 못 찾은 것):**
  (a) 위험 행동에 대한 **운용자 승인 게이트를 지배(dominator) 관계로 저장 시점에 강제**하기(FlexBE는 실행 시점 설정).
  (b) **비상 핸들러(링크 상실·저전력·GPS 이상) 존재를 임무 저장 조건으로 강제**하기(PROMISE는 표현만 가능하고 강제하지 않음).
  (c) **검증된 IR에 서명하고 실행기가 서명된 것만 실행**하기(조사한 도구 어디에도 없음).
  (d) **할당 시점 도메인별 확장 + 도메인 간 역할 진행 상태 인계**(Heppner·Colledanchise는 과제 재할당, HiSARM은 배포 대상 재타깃).
  (e) 위 전부를 **한 노코드 편집기와 한 실행기**로 연결하기.
- **새로움으로 주장하면 안 되는 것:** "비전문가 다중로봇 시각 DSL"(FLYAQ·PROMISE·MissionLab), "DSL→IR→인터프리터"(PROMISE·HiSARM), "BT/상태기계 검증"(Biggar·BehaVerify·AS2FM·RoboChart), "능력 기반 할당"(CBBA·Heppner), "운용자 협업 자율/실행 중 수정"(FlexBE), "런타임 모니터"(RTAMT·ROSMonitoring·Ogma).
- **인용 권고(발표·README용 최소 세트, 8편):** PROMISE SLE'19(구조적 쌍둥이) · Dragule SoSyM 2021(다중로봇 공백) · HiSARM TECS 2025(국내 선행, 존중하며 차별화) · FlexBE(Schillinger ICRA 2016 / 저장소) · Neptus/Dolphin IROS 2018(이기종 공중·해상 실운용) · RoVer UIST 2018(저작 시점 검증 + 쉬운 말 피드백) · Heppner ICRA 2024(능력 기반 BT 할당) · RTAMT(런타임 가드 구현에 실제 사용 시). 여유가 있으면 Menghi TSE(명세 패턴), Gerkey&Matarić 2004, CBBA 2009, Luckcuck CSUR 2019를 추가한다.
- **24시간 재사용 권고:** React Flow(편집기) + pydantic IR(이미 의존성) + networkx(지배자·SCC·도달성 검사) + RTAMT(STL 런타임 가드, pip). 피할 것: Groot2(비공개 데스크톱), FlexBE WebUI(ROS 2 필요), Stately Studio(SaaS, 오프라인 정책 위반), Node-RED(의미론 불일치), LTLMoP·PROMISE·FLYAQ 코드(중단·Eclipse).

### Gaps
- "선례를 못 찾았다"는 주장은 이번 웹 검색 범위(영어권 공개 문헌·GitHub)에 한정된다. 국방 비공개 체계와 한국어 문헌(국방과학연구소·KIDA 보고서 등)은 조사하지 않았다.
- 서명된 임무 IR에 대한 선행(예: 코드 서명·MAVLink 2 서명 외에 "임무 계획 서명")은 별도 검색을 하지 않았다. 형제 노트 `cyber-ew-threats.md`에 MAVLink 서명 관련 내용이 있다.
