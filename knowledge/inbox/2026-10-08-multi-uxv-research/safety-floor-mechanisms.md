# 하방 차단(Safety Floor) 메커니즘 — 자율·무인체계의 최악 결과를 묶어두는 공학 기법과 1인-다수 이종 UxV 통제 적용

> 작성: 2026-10-08 (리서치 에이전트). 모든 URL 접근일 = **2026-10-08**.
> 출처 등급 태그: **[공식]** 정부·군 문서/발표 · **[표준]** 표준기구·오토파일럿 공식 문서 · **[학술]** 동료심사 논문 · **[프리프린트]** 미심사 arXiv · **[기업]** 제조사 주장 · **[언론]** 기자 보도 · **[분석]** 싱크탱크/블로그 · **[시민단체]** 옹호단체 입장문.
> 인용 방식 표시: **(원문-직접추출)** = PDF/HTML을 내려받아 텍스트를 직접 뽑은 것(글자 그대로, 가장 신뢰도 높음) / **(원문)** = WebFetch 요약 도구가 페이지 본문에서 발췌한 것(도구가 긴 문장을 끊어 인용함) / **(검색발췌)** = 검색엔진 요약·스니펫(원문 미열람, 최종 인용 전 재확인 필요).
> 프로젝트 맥락: T1-1 Multi-UxV Control(운용자 1명이 3대 이상 이종 무인체계를 임무할당·감시·통제). 팀 차별화 = **"하방을 막는다"** — AI 할당기·LLM·과부하 운용자·공격자 어느 쪽 명령이든 안전/보안 경계를 넘지 못하게 하고, 데이터를 신뢰할 수 없는 기체는 자동 격리.
> 접근 주의: DoDD 3000.09 공식 URL(esd.whs.mil)과 FAA·Edwards AFB·ACC 일부 페이지는 자동 접근 시 403. DoDD 3000.09는 Wayback 사본 PDF에서 직접 텍스트를 추출했음(아래 각 항목에 두 URL 병기).

---

## Q1. 런타임 보증(RTA)/Simplex — 정의, AFRL·NASA 사례, ASTM F3269, Auto-GCAS 실적, 다중에이전트(CBF·지오펜스·RL 실드) 적용

### Takeaway
RTA는 **"검증할 수 없는 주 제어기(사람·고급 제어기·AI)의 출력을, 단순하고 검증된 모니터와 백업 제어기로 걸러내는 온라인 검증 장치"**다(AFRL Hobbs 등). 실전 대표 사례는 F-16 Auto-GCAS로, 2014년 말 배치 후 미 공군은 F-16·F-22에서 **16명 구조**로 집계했다(Air Force Times 2024-11 보도. 제조사 집계는 2024-01 기준 13명/12기). 표준은 **ASTM F3269-21**이고 "사람이 Complex Function 역할을 할 수도 있다"고 명시한다. 다중 로봇에는 **CBF-QP 안전 필터**(Robotarium이 신뢰할 수 없는 사용자 코드에 실제로 적용), 강화학습에는 **실드(shield)**를 쓴다. 심사위원용 설계 원칙은 Auto-GCAS의 요구 우선순위 **"do no harm → do not interfere → prevent collisions"**다.

### Cited Findings

**RTA 정의·분류 (AFRL 튜토리얼, 핵심 원전)**
- [학술/공식] Hobbs, Mote, Abate, Coogan, Feron, "Run Time Assurance for Safety-Critical Systems: An Introduction to Safety Filtering Approaches for Complex Control Systems", arXiv 2110.03506v2(2022-06-07). 표지에 "Approved for public release: distribution unlimited. Case Number AFRL-2021-2407." 이후 IEEE Control Systems Magazine 2023 게재(DOI 10.1109/MCS.2023.3234380). (원문-직접추출) — [arXiv 2110.03506](https://arxiv.org/abs/2110.03506)
  - 정의(원문-직접추출): "RTA Systems are online verification mechanisms that filter an unverified primary controller output to ensure system safety. The primary control may come from a human operator, an advanced control approach, or an autonomous control approach that cannot be verified to the same level as simpler control systems designs. The critical feature of RTA systems is their ability to alter unsafe control inputs explicitly to assure safety."
  - "An important quality of an RTA system is that the assurance mechanism is constructed in a way that is entirely agnostic to the underlying structure of the primary controller. By effectively decoupling the enforcement of safety constraints from performance-related objectives, RTA offers a number of useful advantages over traditional (offline) verification."
  - Plan B 사이드바: "A fundamental concept underlying RTA is: always maintaining a safe “Plan B” during mission execution, with the purpose of executing “Plan B” as soon as the nominal activity appears to be dangerous."
  - 분류(원문-직접추출): "RTA approaches can be classified as: explicit or implicit, zero or first order, and latched or unlatched. Explicit approaches precisely define a specific safe set, while implicit RTA approaches define recovery trajectories under a predefined backup control law. Zeroth order RTA methods ... are often associated with RTA systems that use methods described in the Section “The Simplex Architecture,” while first order methods take advantage of gradient computations and are used in methods such as those described in the Section “Active Set Invariance Filtering.” Latched RTA systems switch to a backup controller and remain under its control until a specified release condition is met, while unlatched implementations return to the primary control as soon as the system returns to a safe set."
  - 0차(Simplex식 전환)의 단점: "one may observe the effects of chatter ... These effects may be handled with various heuristics; e.g. hysteresis, or interpolating between ub and udes". 1차(ASIF/CBF)는 "A common cost specification requires that the RTA choose the control that is closest (in a 2-norm sense) to the desired input. RTA filters constructed in this way will have smooth variations in the output signal".
  - 래치 예: "Auto GCAS is an example of a temporary latched system that holds the maneuver until the aircraft is on a collision free course".
  - 이름 정리(Aliases 사이드바): RTA는 "active set invariance, active collision avoidance, advanced driver assistance, active safety, safety filtering, emergency braking, sandboxing, conflict resolution, and constraint-based planning" 등으로 불림. Recovery controller(비상시 개입 후 곧 주 제어기에 권한 반환) vs reversionary controller(주 제어기 이상 감지 시 단순 검증 제어기로 남은 임무 수행) 구분.
  - RL 사이드바: "reward shaping does not guarantee safety during operations. By contrast, RTA can be used to filter the actions of the RL algorithms to ensure safety."

**Simplex 원형 (Sha, 2001)**
- [학술] Lui Sha, "Using Simplicity to Control Complexity" (2001). 고신뢰(high-assurance) 제어 서브시스템과 고성능(high-performance) 제어 서브시스템을 전환하는 구조. "the Simplex architecture is a solution-creating technique for combining two algorithms such that a system retains the safety of the first while gaining the features of the second" (검색발췌, 2008 학위논문의 Sha 인용) — [IDEALS, Illinois](https://www.ideals.illinois.edu/items/11503)
- [학술] 3요소: complex controller(고성능, 검증 불가) + safety controller(성능 제한, 단순해서 철저히 검증 가능) + decision module(안전 포락선 위반 감지 시 safety controller로 전환). (검색발췌) — [arXiv 1812.02834 (컨테이너 기반 DoS 내성 UAV 제어)](https://arxiv.org/pdf/1812.02834); "assures that the plant is properly controlled even if the advanced controller has bugs" (검색발췌) — [arXiv 1704.04759](https://arxiv.org/pdf/1704.04759)

**ASTM F3269 (RTA 표준)**
- [표준] 제목: "Standard Practice for Methods to Safely Bound Behavior of Aircraft Systems Containing Complex Functions Using Run-Time Assurance" (F3269-21, ASTM 페이지 "Last Updated: Nov 19, 2021"; F3269-17은 Historical). (원문) — [ASTM store F3269-21](https://store.astm.org/f3269-21.html)
  - 1.1: "A set of components that comprise an RTA system." / "Requirements and best practices to determine safe boundaries and RTA system coverage."
  - 1.2: "RTA components are required to meet the design assurance level dictated by a safety assessment process." (ARP4754A, ARP4761, F3178 등 참조)
  - **1.3**: "This practice was developed with UAS in mind." ... "The scope of this practice is also envisioned to allow a variety of aircraft implementations" "where a human may perform the role of either the Complex Function or a Recovery Function."
  - 5절 구성요소 제목: **Input Manager, Safety Monitor, RTA Switch, Recovery Function** (본문은 유료라 미열람).
  - Note 1: "This practice does not suggest a one-size-fits-all strategy".
- [학술] F3269 아키텍처 요약: 비인증(untrusted/non-pedigreed) complex function을 인증 가능한 UAS 항전에 넣고, 안전규칙 위반 명령 시 검증된 모니터가 제어권을 가져감. (검색발췌) — [NSF PAR 10215462](https://par.nsf.gov/servlets/purl/10215462)

**Auto-GCAS (가장 강력한 실전 선례)**
- [학술/공식] 2016-05 실사례(Hobbs 서두, 원문-직접추출): F-16 학생조종사가 "nearly 9Gs ... flying over 400 knots"에서 G-LOC. "dropping from over 17,000 feet to less than 8,000 feet in altitude in less than 10 seconds". Auto-GCAS("an RTA system integrated on the jets less than two years earlier in the Fall of 2014")가 "commanded a roll to wings level and pull up maneuver, and recovered the aircraft less than 3,000 feet above the ground." — [arXiv 2110.03506](https://arxiv.org/abs/2110.03506)
- [학술/공식] **요구사항 우선순위**(원문-직접추출): "in the development of Auto GCAS, the high-level requirements in order of precedence were to do no harm, do not interfere, and prevent collisions ... This requirement ordering might seem counter-intuitive ... However, this order of requirements proved critical in acceptance of the system". 발췌 요구사항:
  - Do No Harm: "The pilot shall be able to interrupt a maneuver." / "Subsystem monitors shall determine if a failure exists and be provided to Auto GCAS." / "Auto GCAS shall not activate an automatic recovery maneuver if a failure of a subsystem supporting Auto GCAS exists."
  - Do Not Interfere: "The pilot shall be able to turn the system off." / "The pilot shall be able to select the protection level." / "Auto GCAS shall notify the pilot when the automatic recovery maneuver initiates and terminates." / "The system shall record data about each automatic recovery maneuver activation."
  - Prevent Collisions: "The system shall conduct an automatic recovery maneuver when the projected recovery trajectory intersects the terrain profile contour with buffers." / "The system shall terminate an automatic recovery maneuver as soon as it is determined that the aircraft will clear the terrain threat."
- [학술/공식] 방해 없음(nuisance-free) 정량 기준(원문-직접추출): 1995년 조종사 연구로 "a 1.5 second time available design criteria was identified, and collision avoidance maneuvers that activated with less than 1.5 seconds time available were considered nuisance-free". 사전검증된 단순 기동: "In F-16 Auto GCAS, a single roll to wings level and 5g pull maneuver is conducted". Auto ACAS(공중충돌회피)는 "nine different maneuvers".
- [학술/공식] 신뢰 형성(원문-직접추출): "the ability to turn the system off was an important feature that engendered pilot trust"; 위험허용도 조절 "a “norm” mode ... and a “min” mode which minimizes buffer size"; "Knowledge of Auto GCAS’s 98% reliability increased test pilot trust of the system"; 투명성은 "pilot training before operations and through visual indicators on the aircraft’s head-up-display (HUD)".
- [학술/공식] RTA 자체 무결성 감시(원문-직접추출): "Possible software checks include monitoring for missing “heartbeat” signals from components and “reasonableness checks” that ensure incoming data are within a reasonable range of values ... a failure of the inertial navigation system should not allow Auto GCAS to roll inverted and pull down into the ground instead of pulling up". (→ 입력 데이터가 틀리면 안전장치도 틀린다는 점을 지적. "데이터 불신 기체 격리" 근거)
- **구조 실적(출처별 상충, 날짜 병기)**:
  - [공식] NASA Armstrong 2019-04-16: "The Auto GCAS has saved the lives of eight pilots in the 4 and a half years since it was fielded in the F-16 fleet." (원문) — [NASA 19-02](https://www.nasa.gov/centers/armstrong/news/newsreleases/2019/19-02.html)
  - [기업] Lockheed Martin 제품 페이지: "has already been credited with 12 saves—13 pilots, 12 F-16s" since entering service "with the U.S. Air Force in late 2014." (원문, 페이지 날짜 없음) — [Lockheed Auto GCAS](https://www.lockheedmartin.com/en-us/products/autogcas.html). 같은 수치의 Lockheed X 게시물(게시 ID 디코딩상 2024-01-31): "12 saves — 13 pilots, 12 F-16s" (검색발췌) — [X/LockheedMartin](https://x.com/LockheedMartin/status/1752712683802280303)
  - [언론, 공군 인용] Air Force Times 2024-11-20: "The Air Force installed Auto-GCAS on its F-16 and F-22 fighter jets, and credits the system with saving the lives of 16 aviators since 2014." (원문, 공군 내 담당 부서 미명시) — [Air Force Times](https://www.airforcetimes.com/news/your-air-force/2024/11/20/could-a-fighter-jet-software-upgrade-have-saved-this-pilots-life/)
  - [공식] ACC(2016) 기사는 당시 "four pilots" 구조. (검색발췌, 페이지 403) — [ACC](https://www.acc.af.mil/News/Article/1026196/point-of-recovery-ground-collision-avoidance-system-saving-pilots-lives/)
  - → 심사위원용 권장 인용: "Air Force credits Auto-GCAS with saving 16 aviators since 2014 (F-16/F-22, reported Nov 2024)". 제조사 수치(13명)는 F-16만, 2024-01 기준.
- [기업] 개발 주체: Lockheed Skunk Works·AFRL·NASA 공동, 2009년 NASA Armstrong에서 비행시험 시작, 연구 기간 "nearly three decades". F-35 적용은 2018 통합·시험 완료, 2019-06 배치 시작 계획, "will ultimately protect more than 3,200 F-35s". (원문) — [Lockheed](https://www.lockheedmartin.com/en-us/products/autogcas.html). F-35 함대 수명 동안 지상충돌 "more than 26" 방지 추정(예측치, 실적 아님). (검색발췌) — [Lockheed 2019-07-24 보도자료](https://news.lockheedmartin.com/2019-07-24-Life-Saving-Anti-Collision-Software-Integrated-into-First-F-35s-Seven-Years-Ahead-of-Schedule)
- [언론] 대조군: 해군 F/A-18E/F Super Hornet에는 Auto-GCAS 미설치. 해군은 2022-06 Trona 인근 Lt. Richard Bullock 사망사고와의 관련성 언급 거부. (원문) — [Air Force Times](https://www.airforcetimes.com/news/your-air-force/2024/11/20/could-a-fighter-jet-software-upgrade-have-saved-this-pilots-life/)

**NASA 계열: EVAA, ICAROUS, Safeguard**
- [공식] EVAA(Expandable Variable Autonomy Architecture, NASA Armstrong): "deterministic systems with higher authority to protect against catastrophic piloting faults" / "allow a lower level certification for the machine learning sub-systems" / "restricts commands of higher level critical decision makers not certified to level A software" (원문) — [data.nasa.gov EVAA](https://data.nasa.gov/dataset/expandable-variable-autonomy-architecture-project). 다중 모니터 RTA(MM-RTA) 샌드박스이며 ASTM 작업그룹 WK53403(F3269의 전신)에 연구결과를 제공했다는 서술. AFRL은 주관기관이 아니라 협력기관으로 등장. (검색발췌, NTRS 문서 특정 불확실) — [NTRS 20160000872](https://ntrs.nasa.gov/citations/20160000872), [NTRS 20170006090 PDF](https://ntrs.nasa.gov/api/citations/20170006090/downloads/20170006090.pdf)
- [학술/공식] ICAROUS (Consiglio, Muñoz, Hagen, Narkawicz, Balachandran, 2016 IEEE/AIAA DASC): "ICAROUS is a software architecture comprised of highly assured algorithms"; "well-established formal methods to guarantee higher levels of safety assurance"; 핵심 기능 "constraint conformance monitoring and contingency control functions". (원문) — [NTRS 20170001936](https://ntrs.nasa.gov/citations/20170001936). DAIDALUS(DAA 알고리즘)가 기반이며 RTCA DAA MOPS 참조 구현, 핵심 알고리즘 다수가 정리증명기로 검증됨. (검색발췌) — 같은 출처; Monitoring ICAROUS 프로젝트는 FRET로 요구사항을 쓰고 Copilot으로 실행 가능한 런타임 모니터를 생성. (검색발췌) — [arXiv 2012.03745](https://arxiv.org/pdf/2012.03745)
- [공식] Safeguard (Young, Dill, Hayhurst, Gilabert, NASA Langley, 2017 DASC): "Unlike typical geofencing or geo-limitation functions, Safeguard operates independently of the off-the-shelf UAS autopilot"; "completion of software verification and validation in accordance with NASA standards for spacecraft systems (to Class B)"; "flight testing on multiple air vehicles". (원문) — [NTRS 20170009617](https://ntrs.nasa.gov/citations/20170009617). 비행시험에서 무인기를 no-fly zone으로 보내 약 100 ft에서 비행 종료(terminate)시킨 시연. (검색발췌) — [NASA Langley feature](https://www.nasa.gov/feature/langley/crashing-into-safe-autonomous-flight)

**최신 사례: X-62A VISTA (AI 조종 F-16 개조기)**
- [언론/공식] 2022-12-01~16, AI 에이전트가 X-62A를 조종한 비행시험 12회. 안전조종사 상시 탑승. 에이전트는 "while maintaining real-world airspace boundaries" 전술 기동 수행. (검색발췌) — [DefenseScoop 2023-02-14](https://defensescoop.com/2023/02/14/ai-agents-take-control-of-modified-f-16-fighter-jet/)
- [언론] 업그레이드 후에도 핵심 "safety trips" 체계는 그대로 유지했다는 보도. 시험 포인트는 "low risk"로 평가. (검색발췌, 유료기사) — [The Air Current](https://theaircurrent.com/technology/special-report-aviation-industry-certify-ai/)
- [언론, 2026-04] HAVE HOLIDAYS: "Engineers installed a third-party autonomous agent in the X-62’s Enterprise Open Mission System Architecture computer" and "evaluated safety rules intended to prevent autonomous aircraft from exceeding limits established by operators". 같은 기간 HAVE HEAT으로 "27 AI-controlled intercepts during eight flights at Edwards Air Force Base in April". (원문) — [AvWeb](https://avweb.com/aviation-news/military-aviation/ai-flies-x-62-vista-live-target-intercepts/)

**다중 에이전트 적용 ① 제어장벽함수(CBF) 안전 필터**
- [학술] Wang, Ames, Egerstedt, "Safety Barrier Certificates for Collisions-Free Multirobot Systems", IEEE T-RO 33(3):661–674, 2017, DOI 10.1109/TRO.2017.2659727. 기존 제어기를 안전에 필요한 만큼만 최소 수정(QP), 실시간 해법, 분산화(각 로봇은 근처 로봇만 고려), 보수성·해 존재성·교착(deadlock)은 relaxed CBF·하이브리드 제동·일관된 섭동으로 처리. 하드웨어 실험에서는 **일부러 충돌하도록 만든 제어기**를 넣고도 충돌을 막음. (검색발췌) — [Caltech record](https://resolver.caltech.edu/CaltechAUTHORS:20170215-165434009)
- [학술] 이종(가속도 한계가 다른) 로봇 확장판 수식 (원문, ar5iv 추출) — [arXiv 1609.00651](https://arxiv.org/abs/1609.00651):
  - 쌍별 안전 장벽함수: `h_ij = sqrt(2(α_i+α_j)(‖Δp_ij‖ − D_s)) + (Δp_ijᵀ/‖Δp_ij‖) Δv_ij ≥ 0`, `Δp_ij = p_i − p_j`, `Δv_ij = v_i − v_j` (D_s = 안전거리, α = 최대 가속도)
  - 장벽 제약: `L_f h_ij + L_g h_ij u + γ h_ij³ ≥ 0, ∀ i≠j`
  - 중앙 QP: `u* = argmin_u Σ_i ‖u_i − û_i‖²  s.t.  A_ij u ≤ b_ij ∀ i≠j,  ‖u_i‖_∞ ≤ α_i`
  - 분산 분할(Strategy B): `−Δp_ijᵀ u_i ≤ (α_i/(α_i+α_j)) b_ij`, `Δp_ijᵀ u_j ≤ (α_j/(α_i+α_j)) b_ij` → 가속력이 큰 기체가 회피 책임을 더 많이 짐(이종 함대에 바로 적용 가능).
  - 하드웨어: Magellan Pro 1대 + Khepera III 3대. 쿼드로터 5대로 검증한 ICRA 2017 후속도 있음. (검색발췌)
- [학술] **Robotarium 실운용 사례**(Hobbs 사이드바, 원문-직접추출): 원격 접속 군집로봇 시험장에서 "user submitted algorithms are treated as black box functions that can be probed at run time. Specifically, control barrier function based quadratic programs (explicit ASIF) are used to prevent collisions between the various robots involved in an experiment. An explicit ASIF-based approach is attractive in this case as it is minimally invasive to the desired inputs and provides a smooth overriding behavior." — [arXiv 2110.03506](https://arxiv.org/abs/2110.03506)
  - → "신뢰할 수 없는 명령원(사용자 코드)을 블랙박스로 보고 런타임에 안전 필터를 씌운다"는 구조가 우리 문제(AI/LLM/운용자 명령)와 같다.

**다중 에이전트 적용 ② RL 실드**
- [학술] Alshiekh et al., "Safe Reinforcement Learning via Shielding", AAAI-18 (DOI 10.1609/AAAI.V32I1.11797, arXiv 1708.08611). 시간논리 명세에서 반응형 "shield"를 합성. "The shield monitors the actions from the learner and corrects them only if the chosen action causes a violation of the specification." 배치 방식 2종: 학습자에게 허용 행동 목록을 미리 주는 방식(preemptive), 학습자 출력을 사후에 거르는 방식(post-posed). 학습 중과 실행 중 모두 명세 준수 보장 주장. (검색발췌) — [AAAI OJS](https://ojs.aaai.org/index.php/AAAI/article/view/11797), [arXiv 1708.08611](https://arxiv.org/abs/1708.08611v1)

### Inferences
- **ASTM F3269 용어에 그대로 대응시키면 심사위원 설득력이 높다**: AI 할당기, LLM, 운용자 = *Complex Function*(F3269 1.3이 사람도 이 역할을 할 수 있다고 명시) / 명령 게이트웨이 = *Input Manager* / 정책·안전 검사기 = *Safety Monitor* / 차단·대체 결정 = *RTA Switch* / 기체별 Hold·RTL·Loiter = *Recovery Function*. "과부하 운용자의 실수도 같은 필터를 통과한다"는 주장을 표준 문구로 뒷받침할 수 있다.
- **24시간 구현 권장 조합**: (a) 이산 명령(임무 할당, 웨이포인트, 모드 변경)에는 0차 Simplex식 "허용/거부/대체" 게이트(구현 쉬움, 설명 쉬움), (b) 연속 속도 명령에는 1차 CBF-QP(2D 단일적분기 모델이면 제약 1~2개는 닫힌 해로도 계산 가능, `cvxpy`/`quadprog`로도 수십 줄). Hobbs가 지적한 chatter 문제는 히스테리시스로 처리한다.
- **Auto-GCAS 원칙을 데모 UX 규칙으로 옮기기**: ① 개입은 최소로(nuisance-free, 거부 대신 가장 가까운 안전 명령으로 수정) ② 개입 시작·종료를 운용자에게 알리기 ③ 모든 개입 기록 남기기 ④ 운용자가 보호수준을 고를 수 있게 하기(norm/min) ⑤ 끄기는 가능하되 2단계 확인. 이 다섯 개가 공군 시스템에서 수용성을 만든 요구사항이라는 점을 말할 수 있다.
- "RTA의 입력 데이터가 틀리면 RTA도 틀린다"(INS 고장 예시)는 Q4의 **기체 데이터 무결성 감시 → 격리**가 RTA의 필수 전제임을 보여준다. 데모 내러티브에서 두 기능을 한 줄로 이어 설명할 수 있다.

### Gaps
- 미 공군 안전센터(AFSEC)의 공식 Auto-GCAS 누적 구조 수치 페이지는 찾지 못함. 수치가 출처·시점별로 다름(NASA 2019: 8명 / Lockheed 2024-01: 13명·F-16만 / AFT 2024-11: 16명·F-22 포함). F-35 구조 사례는 공식 확인 안 됨.
- ASTM F3269-21 본문(구성요소 정의·요구사항)은 유료라 미열람.
- Sha(2001) 원문 미열람. 게재지(IEEE Software로 알려짐)는 검색 결과로 확인 못 함.
- X-62A "safety trips"·HAVE HOLIDAYS 안전규칙의 구현·발동 조건은 공개 자료 없음.
- AFRL 명의의 EVAA 문서는 찾지 못함(NASA Armstrong 주관).

---

## Q2. 정책 요구사항 — DoDD 3000.09(2023), DoD AI 윤리원칙, NATO, 정치선언, REAIM(서울 2024), 한국

### Takeaway
**DoDD 3000.09(2023-01-25)**는 자율·반자율 무기체계에 대해 다음을 글자 그대로 요구한다: "appropriate levels of human judgment", **시간·지리 경계 안에서 교전을 끝내고 그러지 못하면 "terminate the engagement or obtain additional operator input"**, "anti-tamper mechanisms, and cybersecurity", HMI가 "clearly indicating what actions operators need to perform and which actions the system will perform", "transparent feedback", 활성/비활성 절차. 또 "failure"의 정의에 **통신 저하, 사이버 공격, 재밍, 스푸핑, 기만**을 명시한다. NATO(2021)와 미국 주도 정치선언(2023)은 모두 **"disengage or deactivate"** 능력을 요구한다. 한국은 2024 REAIM 서울 "Blueprint for Action" 주최국이자 지지국이고, 국방AI법안(2026-01 발의)이 국회 심사 중이다. 국방부 명의의 공식 "국방 AI 윤리원칙" 문서는 확인하지 못했다.

### Cited Findings

**DoDD 3000.09 "Autonomy in Weapon Systems" (원문-직접추출)**
- [공식] "Effective: January 25, 2023", Originating Component: OUSD(Policy). — [esd.whs.mil 공식 PDF](https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodd/300009p.pdf) (자동 접근 403) / [Wayback 사본](https://web.archive.org/web/2024id_/https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodd/300009p.pdf)
- **1.2.a**: "Autonomous and semi-autonomous weapon systems will be designed to allow commanders and operators to exercise appropriate levels of human judgment over the use of force."
- **1.2.a.(1)**: "Systems will go through rigorous hardware and software verification and validation (V&V) and realistic system developmental and operational test and evaluation (T&E) ... These measures will provide sufficient confidence that autonomous and semi-autonomous weapon systems:
  (a) Function as anticipated in realistic operational environments against adaptive adversaries taking realistic and practicable countermeasures.
  (b) **Complete engagements within a timeframe and geographic area, as well as other relevant environmental and operational constraints, consistent with commander and operator intentions. If unable to do so, the systems will terminate the engagement or obtain additional operator input before continuing the engagement.**
  (c) Are sufficiently robust to minimize the probability and consequences of failures."
- **1.2.a.(2)**: "Consistent with the potential consequences of an unintended engagement or unauthorized parties interfering with the operation of the system, physical hardware and software will be designed with appropriate: (a) System safety, **anti-tamper mechanisms, and cybersecurity** in accordance with DoD Instruction (DoDI) 8500.01 and Military Standard 882E. (b) Human-machine interfaces and controls. (c) Technologies and data sources that are transparent to, auditable by, and explainable by relevant personnel."
- **1.2.a.(3)** HMI: "(a) Be readily understandable to trained operators, such as by **clearly indicating what actions operators need to perform and which actions the system will perform**. (b) Provide transparent feedback on system status. (c) Provide clear procedures for trained operators to activate and deactivate system functions."
- **1.2.f** DoD AI 윤리원칙 5개(Responsible, Equitable, Traceable, Reliable, Governable). Governable: "The DoD will design and engineer AI capabilities to fulfill their intended functions while possessing the ability to detect and avoid unintended consequences, and the ability to disengage or deactivate deployed systems that demonstrate unintended behavior." Reliable: "explicit, well-defined uses, and the safety, security, and effectiveness of such capabilities will be subject to testing and assurance within those defined uses across their entire life cycles."
- **Section 3 (V&V·T&E)**: "including analysis of unanticipated emergent behavior"; "(1) Hardware and software V&V will include iterative cyber T&E in accordance with DoDI 5000.89, to verify that the weapon system is resilient and survivable in contested cyberspace."; 변경 후 "System software will be tested using best-available DoD means and methods to validate that critical safety features have not been degraded. Automated testing tools, such as modeling and simulation, will be used whenever feasible."; "Changes to the state transition matrix may require whole system follow-on operational T&E."
- **Section 4 (고위급 검토)**: 개발 착수 전 USD(P)·USD(R&E)·VCJCS 검증, 배치 전 USD(P)·USD(A&S)·VCJCS 검증. 배치 전 항목 중 "(2) System safety, anti-tamper mechanisms, cyber survivability, operational resilience, and cybersecurity capabilities have been implemented ... A monitoring regime is in place to identify and address changes in operational environment, data inputs, and use that could contribute to such failures." / "(3)(b) Have demonstrated that the system can be reprogrammed with sufficient rapidity to enable timely correction of any unintended system behaviors" / "(5) System design and human-machine interfaces are readily understandable to trained operators, provide transparent feedback on system status, and provide clear procedures for trained operators to activate and deactivate system functions."
- **Glossary "failure"** (데모 위협모델 근거로 그대로 인용 가능): "An actual or perceived degradation or loss of intended functionality or inability of the system to perform as intended or designed. Failure can result from a number of causes, including, but not limited to, human error, faulty human-machine interaction, malfunctions, **communications degradation, software coding errors, enemy cyber-attacks or infiltration into the industrial supply chain, jamming, spoofing, decoys**, other enemy countermeasures or actions, or unanticipated situations on the battlefield. For the purposes of this issuance, minimizing the probability and consequences of failure means reducing the probability and consequences of unintended engagements to acceptable levels while meeting mission objectives and **does not mean achieving the lowest possible level of risk by never engaging targets**."
- **Glossary "operator-supervised autonomous weapon system"**: "An autonomous weapon system that is designed to provide operators with the ability to intervene and terminate engagements, including in the event of a weapon system failure, before unacceptable levels of damage occur."
- [분석] CNAS(Scharre): 핵심 "appropriate levels of human judgment" 문구는 2012판에서 바뀌지 않았고 미 정부의 UN 논의 입장의 중심. (검색발췌) — [CNAS 2023-02-06](https://www.cnas.org/press/press-note/noteworthy-dod-autonomous-weapons-policy). 2018 미국 CCW 작업문서: "appropriate"는 "not a fixed, one-size-fits-all level of human judgment". (검색발췌) — [OGC OSD PDF](https://ogc.osd.mil/Portals/99/Law%20of%20War%202023/US%20Working%20Paper%20-%20Human-Machine%20Interaction%20in%20the%20Development%20Deployment%20and%20Use%20of%20Emerging%20Technologies%20in%20the%20Area%20of%20LAWS%20-%20CCW_GGE.2_2018_WP.4_E.pdf)

**NATO (2021-10-22) 책임 있는 국방 AI 원칙 6개**
- [공식] Lawfulness / Responsibility and Accountability("clear human responsibility shall apply in order to ensure accountability") / Explainability and Traceability("appropriately understandable and transparent") / Reliability("explicit, well-defined use cases"; "safety, security, and robustness" "subject to testing and assurance") / **Governability**("the ability to take steps, such as disengagement or deactivation of systems," "when such systems demonstrate unintended behaviour") / Bias Mitigation. (원문) — [NATO AI Strategy summary](https://www.nato.int/cps/en/natohq/official_texts_187617.htm)

**미국 주도 "Political Declaration on Responsible Military Use of AI and Autonomy" (2023-02 REAIM에서 공개, 비구속)**
- [공식 인용] "States should design and engineer military AI capabilities so that they possess the ability to detect and avoid unintended consequences and the ability to disengage or deactivate deployed systems that demonstrate unintended behavior." / "States should also implement other appropriate safeguards to mitigate risks of serious failures." (검색발췌, 국무부 원문 미열람) — [Inside Unmanned Systems](https://insideunmannedsystems.com/state-department-issues-declaration-on-military-use-of-ai-and-autonomy/), [ETO AGORA](https://agora.eto.tech/instrument/1380)

**REAIM 2024 서울 "Blueprint for Action" (한국 주최)**
- [언론/공식 인용] 2024-09-09~10 서울, 96개국 1,952명 참가(외교부). 61개국 지지(한국·미국·일본·프랑스·영국·우크라이나 등), 중국 불참. 20개 조항, 3개 장. 법적 구속력 없음. 핵무기 관련 "maintain human control and involvement for all actions critical to informing and executing sovereign decisions concerning nuclear weapons employment". (검색발췌; 지지국 수는 보도마다 ~60/61로 차이) — [Asia News Network/Korea Herald](https://asianews.network/seoul-summit-charts-framework-on-responsible-ai-military-use/), [Vision IAS 요약](https://visionias.in/current-affairs/news-today/2024-09-11/security/blueprint-for-action-issued-by-responsible-ai-in-the-military-domain-summit), [Fortune 2024-09-10](https://www.fortune.com/2024/09/10/china-ai-ban-nuclear-weapons)

**한국 (2024–2026)**
- [언론] 국방부, 2024-09 "'안전하고 신뢰할 수 있는 AI 활용 국방 가이드라인 연구' 용역사업을 최근 발주했다." "AI 활용 과정에서 야기될 수 있는 부작용을 최소화하고 안전한 AI 활용이 가능하도록 가이드라인을 마련해 배포할 계획이다." (원문, 발행 2024-09-09) — [전자신문](https://www.etnews.com/20240909000194)
- [언론] 2023-04: 군이 2021년부터 '국방 AI 추진전략'에 AI 윤리기준 정립을 넣었으나 AI 무기체계 민간 공모에 '윤리성 평가' 기준을 적용하지 않았다는 보도. (검색발췌) — [한국일보 2023-04-14](https://www.hankookilbo.com/news/article/A2023041415360001972)
- [의안/시민단체] **국방인공지능법안**(유용원·부승찬 의원 등 33인, 의안번호 2216355), 2026-01 발의, 국방위원회 소관. 안전성·신뢰성·책임성 확보와 국방부장관의 3년 주기 국방 AI 기본계획 포함. 시민단체는 인간 통제 원칙·금지 대상 정의 부재를 비판. (검색발췌, 법안 원문 미열람) — [참여연대 2026 정기국회 입법과제](https://peoplepower21.org/peace/2028472), [참여연대 입법의견서](https://peoplepower21.org/publiclaw/2022744)
- [언론] 2026-09-02 국방부 '국방 AI 전략 포럼': "현재 국회 국방위원회에서는 국방인공지능법안을 검토 중이며, 법안에는 국방 AI 기술의 신속한 군 적용 절차와 신뢰성·안전성 보장 방안 등이 담겼다고 국방부는 설명했다." / "인공지능의 신뢰성·안전성 보장을 위한 제도적 기반 마련이 병행돼야 한다" / 쟁점: "인간 지휘관의 최종 통제권을 어떻게 보장할지" (원문) — [뉴스핌 2026-09-02](https://www.newspim.com/news/view/20260902000951)
- [언론] 2026-01-22 AI 기본법 전면 시행. 국방·국가안보 목적 AI는 적용 제외. (검색발췌) — [참여연대](https://peoplepower21.org/peace/2028472). 2026-08 관계부처 합동 '대한민국 인공지능 윤리원칙' 확정(7대 원칙: 인간중심성·프라이버시 보호·공정성·포용성·책임성·**안전성**·**신뢰성**·투명성). (검색발췌) — [다음/뉴스 2026-08-24](https://v.daum.net/v/20260824185707259?f=p)

### Inferences
- 미군 심사위원의 "how do you know it's safe?"에는 **DoDD 3000.09 1.2.a.(1)(b) 문장을 그대로 기능으로 구현했다**고 답하는 것이 가장 강하다: "명령이 시간·지리 경계(지오펜스/ROE 박스) 밖으로 나가면 시스템이 자동으로 교전/임무를 중단(Hold/RTL)하거나 운용자 추가 승인을 받는다." 이것이 '하방 차단'의 정책상 근거다.
- Glossary의 "failure" 정의에 재밍·스푸핑·사이버 공격·통신 저하가 들어 있으므로, **기체 데이터 불신 → 자동 격리** 기능은 3000.09의 "minimize the probability and consequences of failures"를 직접 겨냥한다고 주장할 수 있다.
- "does not mean ... never engaging targets" 문구는 **'모두 막으면 안전'이 정답이 아니다**라는 뜻이다. 데모 지표에 *차단 수*만이 아니라 *임무 성공률 유지*를 함께 보여야 한다(Q7).
- HMI 요구사항("which actions operators need to perform and which actions the system will perform")은 차단 사유 설명 UI의 설계 기준으로 그대로 쓸 수 있다(Q5).
- 한국 측 근거는 "REAIM 2024 서울 Blueprint(한국 주최·지지)" + "국방AI법안 심사 중(신뢰성·안전성 보장 조항)" + "범정부 AI 윤리원칙의 안전성·신뢰성" 정도가 공개 자료로 확인된다.

### Gaps
- 국방부 명의의 공식 "국방 AI 윤리원칙/신뢰성 지침" 문서(2024–2026)는 찾지 못함. 2024-09 발주 용역 결과물 공개 여부 미확인.
- 국방인공지능법안의 인간 통제 관련 조문 원문 미확인(의안정보시스템 열람 필요). 2026-10 현재 처리 단계 미확인.
- 한국의 미국 정치선언(2023) 지지 여부는 이번 조사에서 1차 출처로 확인하지 못함.
- 정치선언 원문(국무부 페이지) 미열람. 인용문은 2차 보도 기반.

---

## Q3. 링크 상실(lost-link)·페일세이프 표준 — STANAG 4586, ArduPilot/PX4 파라미터, FAA/DoD 정의

### Takeaway
FAA 정의상 lost link가 나면 무인기는 **"predictable or planned maneuver"**를 하고, 링크를 회복하지 못하면 **"flight termination must be implemented"**. ArduPilot/PX4는 이를 파라미터로 구현한다. GCS 하트비트 끊김 기본 5초(ArduPilot `FS_GCS_TIMEOUT`, 2~120 s) 후 RTL/Land/SmartRTL/Brake. EKF 분산 2개 이상이 임계값(기본 0.8)을 1초 넘으면 Land. 지오펜스 위반 시 `FENCE_ACTION`(RTL/Land/Brake 등). 단, **PX4 지오펜스는 "이미 위반한 뒤"에야 발동**하므로 사전 예측 필터(RTA)가 따로 필요하다. STANAG 4586의 lost-link 세부 절차(AEP-84)는 공개 자료로 확인하지 못했다.

### Cited Findings

**FAA Pilot/Controller Glossary (원문-직접추출)** — [FAA P/CG "L"](https://www.faa.gov/air_traffic/publications/atpubs/pcg_html/glossary-l.html)
- "LOST LINK (LL) - An interruption or loss of the control link, or when the pilot is unable to effect control of the aircraft and, as a result, the UA will perform a predictable or planned maneuver. Loss of command and control link between the Control Station and the aircraft. There are two types of links: An uplink which transmits command instructions to the aircraft, and A downlink which transmits the status of the aircraft and provides situational awareness to the pilot."
- "LOST LINK PROCEDURE - Preprogrammed or predetermined mitigations to ensure the continued safe operation of the UA in the event of a lost link (LL). In the event positive link cannot be established, flight termination must be implemented."
- FLIGHT TERMINATION: "The intentional and deliberate process of terminating the flight of a UA in the event of an unrecoverable lost link, loss of control, or other failure that compromises the safety of flight." (검색발췌, 미러 사이트) — [angleofattack 미러](https://www.angleofattack.com/far/glossary/flight-termination/)
- [공식] FAA HITL 연구: 관제사에게 lost-link 정보를 2분 이내 제공하고 lost-link 경로는 최소 4분간 선회 없이 유지할 것을 제안. (검색발췌, 4분의 기준 시점 미확인) — [FAA TC-19/25](https://hf.tc.faa.gov/publications/2019-z-25-validation-unmanned-enroute/tc19-25.pdf)

**ArduPilot Copter (원문 / 파라미터 표는 원문-직접추출)**
- 공통: Radio·Battery·GCS·Terrain 페일세이프로 모드가 바뀌면 "the vehicle stays in that mode until the pilot changes it manually". 목록: Radio, Battery, GCS, EKF, Dead Reckoning, Vibration, Terrain Data Loss, Crash Check, Parachute, Independent Watchdog. (원문) — [Failsafe landing page](https://ardupilot.org/copter/docs/failsafe-landing-page.html)
- **GCS 페일세이프**: 하트비트를 `FS_GCS_TIMEOUT`초(기본 5초) 동안 못 받으면 발동. "if no GCS is ever connected, the GCS failsafe will remain inactive regardless of parameter settings." `FS_GCS_ENABLE`: 0 Disabled, 1 Always RTL(GPS 불가 시 Land), 3 SmartRTL or RTL, 4 SmartRTL or Land, 5 Always Land, 6 DO_LAND_START or RTL, 7 BRAKE or LAND. 착지 상태면 즉시 disarm. 재연결 후에도 페일세이프 모드 유지. (원문) — [GCS Failsafe](https://ardupilot.org/copter/docs/gcs-failsafe.html). 파라미터 표: "FS_GCS_TIMEOUT: ... Timeout before triggering the GCS failsafe ... Range 2 to 120 seconds" (원문-직접추출) — [Copter parameters](https://ardupilot.org/copter/docs/parameters.html)
- **EKF 페일세이프**: "The EKF failsafe will trigger when any two of the EKF “variances” for compass, position or velocity" are "higher than the FS_EKF_THRESH parameter value for 1 second." 분산은 0(신뢰)~1(불신). `FS_EKF_ACTION` 기본 1 = Land. GPS 글리치는 `EK3_POS_I_GATE`/`EK3_VEL_I_GATE` 게이트 밖이면 측정 거부, 지속 시 "usually about 7 seconds" 후 GPS로 재설정. (원문) — [EKF failsafe](https://ardupilot.org/copter/docs/common-ekf-inav-failsafe.html). 파라미터 표: "FS_EKF_THRESH ... Values 0 Disabled, 0.6 Strict, 0.8 Default, 1.0 Relaxed" (원문-직접추출) — [Copter parameters](https://ardupilot.org/copter/docs/parameters.html)
- **지오펜스**(원문-직접추출, 파라미터 표): "FENCE_ACTION: ... What action should be taken when fence is breached — 0 Report Only, 1 RTL or Land, 2 Always Land, 3 SmartRTL or RTL or Land, 4 Brake or Land, 5 SmartRTL or Land"; "FENCE_MARGIN: Distance that autopilot's should maintain from the fence to avoid a breach — 1 to 10 meters"; "FENCE_RADIUS ... 30 to 10000 meters"; "FENCE_ALT_MAX ... 10 to 1000 meters". — [Copter parameters](https://ardupilot.org/copter/docs/parameters.html)
- 지오펜스 동작(원문): 위반 후 백업 펜스는 "created 20m out from the previous breached fence" (기체 위치 기준이 아님). 펜스를 무시하려면 "you should be ready to switch the flight mode twice". 최소 권장 반경 30 m, GPS 품질 필수(GPS arming check·EKF failsafe를 끄지 말 것). — [Cylindrical fence](https://ardupilot.org/copter/docs/common-ac2_simple_geofence.html)

**PX4 (원문)** — [PX4 Safety Configuration](https://docs.px4.io/main/en/config/safety.html)
- "the default behavior (for most failsafes) is to enter Hold for [COM_FAIL_ACT_T] seconds before performing an associated failsafe action." (→ 운용자에게 개입할 유예시간을 줌)
- Data link loss: `COM_DL_LOSS_T` "Amount of time after losing the data connection before the failsafe will trigger"; `NAV_DLL_ACT` = Disabled, Hold, Return, Land, Disarm, Terminate.
- RC loss: `NAV_RCL_ACT` = Disabled, Loiter, Return, Land, Disarm, Terminate, Hold.
- **Geofence**: "Note that the failsafe action will only trigger once the vehicle has already breached the geofence." `GF_ACTION` = None, Warning, Hold, Return, Terminate, Land.
- Position loss: `COM_POS_FS_ACT` 기본 = 가능하면 하강. Flight termination: "Turns off all controllers and sets all PWM outputs to their failsafe values."
- (기본 타임아웃 값은 이번 발췌에 포함되지 않음 → Gaps)

**STANAG 4586 / AEP-84**
- [기업] STANAG 4586에서 GCS(CUCS)는 Vehicle Specific Module(VSM)을 통해 기체와 통신. VSM은 CUCS 쪽이나 기체 탑재 모두 가능. (검색발췌) — [Lockheed mGCS Capabilities Guide 2013](https://www.lockheedmartin.com/content/dam/lockheed-martin/rms/documents/cdl/mGCSCapabilitiesGuide-2013.pdf)
- [기업] 벤더 매핑 예: 로이터 중심 좌표, 항법명령 유효성 플래그, "bingo energy"(귀환 강제 에너지 임계) 변수. (검색발췌) — [Embention STANAG 4586 manual](https://manuals.embention.com/1x-pdi-builder/en/8.2⧸1.3/1x%20configuration/stanag/index.md)
- [표준] AEP-84.1(2017-04-05, 548쪽): STANAG 4586 구현 지침(VSM, CCISM 등). 본문 비공개. (검색발췌) — [GlobalSpec AEP-84.1](https://standards.globalspec.com/std/10266881/aep-84-1)

### Inferences
- **이종 기체 통합 페일세이프 표**를 데모에 넣으면 설득력이 크다(값은 시연 설정 예시): 공중(쿼드) GCS 끊김 5 s → Hold → 15 s → RTL; 지상(UGV) → 정지(Hold); 해상(USV) → Loiter/정박점 복귀. ArduPilot의 Copter/Rover/Boat 계열이 같은 MAVLink 파라미터 체계를 공유하므로 SITL에서 세 종류를 한 GCS로 시연할 수 있다(Rover·Boat 파라미터는 이번에 확인하지 않음 → Gaps).
- **PX4 지오펜스는 "위반 후 발동"**, ArduPilot `FENCE_MARGIN`도 1~10 m 여유일 뿐이다. 그래서 상위 C2 계층에서 *명령 단계*의 사전 검사(웨이포인트·경로가 펜스를 넘는지)와 *예측* 검사(현재 속도로 t초 뒤 위치)를 하면 기체 펜스와 겹치는 **이중 펜스**(defense-in-depth)가 된다. "기체 자체 펜스 + C2 안전 커널 펜스 = 독립된 두 층"은 NASA Safeguard의 "autopilot과 독립" 원칙과 같은 논리다.
- "재연결 후에도 페일세이프 모드 유지"(ArduPilot)는 래치형 RTA(Hobbs)와 같다. 격리된 기체를 **운용자 명시 확인 없이 자동 복귀시키지 않는** 정책의 선례로 쓸 수 있다.

### Gaps
- STANAG 4586/AEP-84의 lost-link 타이머·순서(loiter→return→autoland 등) 원문은 공개 웹에서 확인 불가.
- PX4 `COM_DL_LOSS_T`, `COM_RC_LOSS_T`, `COM_FAIL_ACT_T`의 기본값은 이번 발췌에 없음(PX4 파라미터 레퍼런스 확인 필요).
- ArduPilot Rover/ArduSub/Boat의 페일세이프 파라미터는 조사하지 않음.
- DoD 자체의 UAS lost-link 정책 문서(예: 군 UAS 운용 규정)는 찾지 못함.

---

## Q4. 함대 신뢰·무결성 감시 — 기체 간 교차검증, RAIM형 무결성, 신뢰점수, 비잔틴 내성(W-MSR) — 몇 시간 안에 구현 가능한 것

### Takeaway
몇 시간 안에 구현할 수 있고 인용 가능한 기법은 네 가지다. ① **잔차(residual) 검사**: GPS로 계산한 기체 간 거리와 독립 측정(UWB/레이더/카메라) 거리의 차가 임계값을 넘으면 스푸핑 판정(Mykytyn 2023). ② **RAIM식 다수결**: 측정 5개면 이상 *탐지*, 6개면 *배제* 가능. ③ **W-MSR**: 이웃 값 중 위·아래 극단 F개를 버리고 평균하면, 그래프가 (2F+1)-robust일 때 악성 이웃이 F개 이하인 정상 노드들이 합의에 도달함이 증명됨. ④ **신뢰점수 기반 할당**(평판 모델). 중요한 한계: 상대거리만 보는 검사는 **함대 전체를 똑같이 옮기는 공통 스푸핑을 못 잡는다**(2026-08 프리프린트). 따라서 독립 절대 기준(anchor) 1개 이상이 필요하다.

### Cited Findings

**RTA 관점: 입력 데이터 무결성은 안전장치의 전제**
- [학술/공식] "Recognizing and accommodating failures that could impact an RTA system is a critical element of RTA design. The failures could come from inside the RTA system or from externally provided information that the RTA uses to make a response decision." (원문-직접추출) — [Hobbs et al., arXiv 2110.03506](https://arxiv.org/abs/2110.03506)

**GNSS 무결성: RAIM / FDE**
- [공식] FAA 자료(2009 ICAO 브리핑): "Need 5 satellites for fault detection (or 4 satellites and baro-aiding). Need 6 satellites for fault detection and exclusion (or 5 satellites and baro aiding)." (검색발췌) — [ICAO SAM RAIM presentation](https://www.icao.int/sites/default/files/sp-files/SAM/Documents/2009/SAMIG4/presentation%20ICAO_SAM_IG_RAIM_Volchansky_v4.pdf); NBAA도 같은 수치(5개 탐지, 6개 배제). (검색발췌) — [NBAA RAIM](https://nbaa.org/aircraft-operations/communications-navigation-surveillance-cns/global-positioning-system-gps/)
- [표준] ArduPilot EKF는 새 GPS 측정을 IMU 기반 예측 위치와 비교해 통계 게이트(`EK3_POS_I_GATE`, `EK3_VEL_I_GATE`) 밖이면 사용하지 않음(혁신량 일관성 검사). (원문) — [ArduPilot EKF failsafe](https://ardupilot.org/copter/docs/common-ekf-inav-failsafe.html)

**기체 간 교차검증 (스푸핑 탐지)**
- [학술] Mykytyn, Brzozowski, Dyka, Langendoerfer (2023, MECO; arXiv 2301.12766): "civil GPS signals are unencrypted and unauthenticated"; 방법은 "comparing the distance between each two swarm members calculated from their GPS coordinates" with UWB 측정 거리; "If the difference in distances is larger than a chosen threshold the GPS spoofing attack is declared detected." 단일·다중 송신기 스푸핑 모두 대상. (원문) — [arXiv 2301.12766](https://arxiv.org/abs/2301.12766)
- [프리프린트] "Drones in Distress"(arXiv 1904.11568): 협력 측위로 2D 위치를 이웃 3대로 구하되, 이웃 자체가 공격받았을 수 있으므로 **이웃 4대**를 써서 오염된 1대를 식별·배제(한 번에 1대 공격 가정). (검색발췌) — [arXiv 1904.11568](https://arxiv.org/pdf/1904.11568)
- [프리프린트, 2026-08-07] Park & Yoo, "Rigid-Covert GNSS Spoofing of UAV Swarms": "Cooperative UAV-swarm defenses commonly cross-check GNSS positions against measured inter-drone geometry." 그러나 공통·완만한 평행이동(RigidShift)은 "preserves all pairwise distances"이므로 상대거리만 보는 탐지기로는 관측 불가. 신뢰 앵커 드론에 정렬해 절대위치 복원, GNSS 표류 약 10.1 m에서 중앙값 오차 0.39 m(20 seeds). **시뮬레이션만, 미심사.** (원문) — [arXiv 2608.06885](https://arxiv.org/abs/2608.06885)
- [프리프린트, 2026] 잔차 기반 탐지 + 신뢰 이웃을 앵커로 SDP 위치 추정 + 게임이론 대응. (검색발췌) — [arXiv 2605.26876](https://arxiv.org/pdf/2605.26876)

**Sybil·사칭 방어 (물리계층 서명)**
- [학술] Gil, Kumar, Mazumder, Katabi, Rus, "Guaranteeing Spoof-Resilient Multi-Robot Networks", RSS 2015 / Autonomous Robots 41(6):1383–1400, 2017. 손상된 로봇 1대가 다수의 가짜 ID를 만드는 Sybil 공격을 Wi-Fi 신호의 물리적 특성으로 탐지. 키 교환 없이 동작. AscTec 쿼드로터 + iRobot Create 실험에서 **스푸퍼 탐지율 96% 초과**. (검색발췌) — [RSS 2015 p20](https://www.roboticsproceedings.org/rss11/p20.html), [MIT LL](https://www.ll.mit.edu/r-d/publications/guaranteeing-spoof-resilient-multi-robot-networks)
- [프리프린트] Mallmann-Trenn, Cavorsi, Gil, "Crowd Vetting" (arXiv 2012.06291, 2020): "We characterize the advantage of using a robot's neighborhood to find and eliminate adversarial robots." 이웃들의 신뢰 의견을 모아 적대 로봇을 **유한 시간** 안에 탐지·배제. "particularly well-suited for problems with a time critical nature". 적대 로봇이 섞인 군집 추적에 적용. (원문) — [arXiv 2012.06291](https://arxiv.org/abs/2012.06291)

**비잔틴 내성 합의: W-MSR (원문-직접추출)** — LeBlanc, Zhang, Koutsoukos, Sundaram, "Resilient Asymptotic Consensus in Robust Networks", IEEE JSAC 31(4), 2013-04 — [저자 PDF (Purdue)](https://engineering.purdue.edu/%7Esundara2/papers/journals/JSAC_robust_consensus.pdf)
- 위협 정의: "Definition 1: A node i ∈ A is said to be Byzantine if it does not send the same value to all of its neighbors at some time-step, or if it applies some other function f′_i(·) at some time-step." / "Definition 2: A node i ∈ A is said to be malicious if it sends x_i[t] to all of its neighbors at each time-step, but applies some other function f′_i(·) at some time-step." 범위: F-total(전체 최대 F개), F-local(각 정상 노드의 이웃 중 최대 F개).
- 알고리즘(그대로): "1) At each time-step t, each normal node i obtains the values of its neighbors, and forms a sorted list. 2) If there are less than F values strictly larger than its own value, x_i[t], then normal node i removes all values that are strictly larger than its own. Otherwise, it removes precisely the largest F values in the sorted list (breaking ties arbitrarily). Likewise, if there are less than F values strictly smaller than its own value, then node i removes all values that are strictly smaller than its own. Otherwise, it removes precisely the smallest F values. 3) Let R_i[t] denote the set of nodes whose values were removed ... Each normal node i applies the update x_i[t+1] = Σ_{j∈J_i[t]∖R_i[t]} w_ij[t] x^i_j[t]"
- 그래프 조건: "Definition 8 (r-reachable set): ... S is an r-reachable set if ∃i ∈ S such that |V_i \ S| ≥ r" / "Definition 10 (r-robustness): A nonempty, nontrivial digraph D = (V, E) on n nodes (n ≥ 2) is r-robust ... if for every pair of nonempty, disjoint subsets of V, at least one of the subsets is r-reachable."
- 정리: "Theorem 1: ... Under the F-total malicious model, resilient asymptotic consensus is achieved if and only if the network topology is (F + 1, F + 1)-robust." / "Theorem 2: ... Under the F-local malicious model, resilient asymptotic consensus is achieved if the topology of the network is (2F+1)-robust. Furthermore, a necessary condition is for the topology of the network to be (F + 1)-robust." / "Theorem 4 ([28]): ... Under the F-total Byzantine model, resilient asymptotic consensus is achieved if and only if the topology of the normal network is (F + 1)-robust."
- 주의: 2022년 Coq 형식검증 연구가 원 논문 증명의 정량자 표현 부정확성 등을 지적. (검색발췌) — [arXiv 2202.13833](https://arxiv.org/pdf/2202.13833)
- **로봇 적용**: Saulnier, Saldaña, Prorok, Pappas, Kumar, "Resilient Flocking for Mobile Robot Teams", IEEE RA-L 2(2):1039–1046, 2017. 초록(원문-직접추출): "We present a method that enables resilient formation control for mobile robot teams in the presence of non-cooperative (defective or malicious) robots ... our connectivity management strategy ensures that the network lies above a critical resilience threshold, guaranteeing that the consensus algorithm always converges to a value within the range of the cooperative agents’ initial values." 서론: "A single non-cooperative (defective or malicious) robot can potentially manipulate the whole network ... (e.g., a robot sharing an incorrect location due to a defective GPS sensor)". W-MSR 사용 명시. — [저자 PDF (Lehigh)](https://www.lehigh.edu/~das819/pdf/ral17-resilient-flocking.pdf)

**신뢰·평판 기반 임무 할당**
- [학술] Shi et al. (2010): 이종 다중로봇 협업용 평판 기반 할당 모델(직접·전체·그룹 평판 3층). 평판 높은 로봇에 작업 우선 배정. (검색발췌) — [TU/e wiki PDF](https://dsdwiki.wtb.tue.nl/images/Zhiguo_Shi_et_al._-_2010_-_The_task_allocation_model_based_on_reputation_for_the_heterogeneous_multi-robot_collaboration_system.pdf); 2014 후속은 시간 감쇠·그룹 보정 추가 (검색발췌) — [PMC3932263](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3932263/)
- [학술] Georgia Tech 2013 학위논문: 임무 중 동료의 역량·신뢰도를 평가해 팀 구조 조정. 일부 구성원이 성능 저하·불신 상태일 때 이득이 가장 큼. (검색발췌) — [Georgia Tech repository](https://repository.gatech.edu/entities/publication/933c8064-2ed5-4f9c-8167-84f31839380f)
- [학술] 적대적 다중에이전트용 trust-aware task allocation(양자 영감 최적화). 전문은 2026-11-12 공개 예정. (검색발췌) — [NSF PAR 10674552](https://par.nsf.gov/biblio/10674552-trust-aware-task-allocation-quantum-optimization-adversarial-multi-agent-systems)

### Inferences
- **24시간 구현안 (가장 단순 → 복잡 순)**:
  1. *자기 일관성 검사*(기체 1대): 보고 위치의 변화량과 보고 속도×Δt의 차이, 물리 한계(최대 속도·가속) 위반, 하트비트 지연·순서 역전 → "reasonableness check"(Hobbs). 수십 줄.
  2. *교차 관측 잔차*(기체 2대 이상): 시뮬레이터에서 "기체 A의 센서가 본 기체 B의 위치(또는 거리)"를 생성하고, B의 자기보고 위치와 비교해 `|d_GPS − d_measured| > τ`이면 B의 신뢰점수를 깎음(Mykytyn 방식). 공중 드론이 지상·해상 기체를 관측하는 이종 시나리오와 잘 맞음.
  3. *다수결/배제*: 관측자가 3명 이상이면 RAIM처럼 "누가 이상치인지" 배제 가능(5개 탐지/6개 배제 비유). Drones in Distress의 "이웃 4대" 논리.
  4. *W-MSR*: 함대 공통 추정값(예: 표적 위치, 풍속, 집결점)에 대해 F=1로 위·아래 극단 1개씩 버리고 평균. 3~5대 데모에서는 완전그래프를 쓰면 (2F+1)=3-robust 조건 충족이 쉬움(완전그래프 K_n의 robustness는 ⌈n/2⌉, 일반 그래프 지식이며 이번에 원문 확인 안 함).
  5. *신뢰점수 → 격리 상태기계*: TRUSTED → SUSPECT(점수<θ1: 고위험 임무 할당 제외, 운용자 경고) → ISOLATED(점수<θ2 또는 서명 실패: 명령 수신 차단·안전 모드(Hold/RTL) 강제·함대 합의에서 제외). 복귀는 래치형으로 운용자 확인 필요.
- **공통 스푸핑 한계는 정직하게 밝히는 편이 낫다**: 상대거리 검사는 함대 전체 평행이동을 못 잡는다(2026 프리프린트). 데모에서는 "지상국(GCS) 위치·고정 랜드마크·UGV의 휠 오도메트리 같은 독립 앵커 1개 이상"을 둔다고 말하면 질문에 대응할 수 있다.
- 비잔틴 모델 구분(malicious = 모두에게 같은 거짓말, Byzantine = 이웃마다 다른 거짓말)은 **방송형 C2(모든 기체가 같은 메시지를 봄)**에서는 malicious 모델이 현실적이라는 설명에 쓸 수 있다(추론).

### Gaps
- 이종(공·지·해) 플랫폼 간 교차관측 무결성의 실전/군 사례는 찾지 못함. 위 논문들은 대부분 동종 드론·지상로봇.
- Saulnier 논문의 정량 결과(악성 로봇 수, 수렴 오차)는 이번에 추출하지 않음.
- "Byzantine-resilient task allocation"의 형식 보장 알고리즘은 찾지 못함(평판 모델은 대부분 휴리스틱).
- K_n robustness 수치는 원문 미확인(일반 지식).

---

## Q5. 명령 인가 패턴 — 2인 규칙, 서명 명령, 정책-as-코드(OPA), 능력 토큰, 고위험 행동의 human-on-the-loop 승인, 차단 사유 설명

### Takeaway
군에서 이미 쓰는 패턴은 **2인 개념(two-person concept)**이다. 핵무기에서 "한 사람에 의한 우발적·악의적 발사"를 막는다. 소프트웨어로는 다음을 조합한다. ① **MAVLink 2 메시지 서명**(SHA-256 48비트, 32바이트 키, 타임스탬프로 재전송 방지, 기체 쪽에서 바로 쓸 수 있음) ② **OPA식 정책-결정/집행 분리**(정책은 Rego, 결정은 구조화 JSON으로 사유 포함) ③ **Macaroons식 감쇠 가능한 능력 토큰**(기체·시간·구역 제한) ④ **고위험 명령은 2차 승인**(DoDD 3000.09의 "obtain additional operator input", OWASP LLM06의 "human approval for high-impact actions"). 차단 설명은 DoDD 3000.09 HMI 요구와 Auto-GCAS의 "개입 시작·종료 알림, 기록"을 기준으로 삼는다.

### Cited Findings

**2인 규칙 (Two-person concept / no-lone zone)**
- [공식 인용] AFI 91-104: "the two-person concept" is designed to prevent accidental or malicious launch of nuclear weapons by a single individual. No-lone zone은 "an area that, when staffed, must be staffed by two or more qualified or cleared individuals". (검색발췌, Wikipedia가 AFI 인용) — [Wikipedia: Two-person rule](https://en.wikipedia.org/wiki/Two-person_rule), [AFI 91-104 PDF](https://presidentandthebomb.org/files/afi91-104.pdf)
- [공식] DOE 정의 "Two-Person Concept (TPC)": "A concept of operations implemented to ensure no lone individual has unrestricted access to a nuclear explosive or other crucial asset". 구현 방식은 zone coverage와 더 엄격한 person-to-person coverage. (검색발췌) — [DOE Directives TPC](https://www.directives.doe.gov/terms_definitions/two-person-concept-tpc)

**서명된 명령: MAVLink 2 Message Signing** (원문) — [mavlink.io Message Signing](https://mavlink.io/en/guide/message_signing.html)
- 목적: "allows a MAVLink system to verify that messages originate from a trusted source." (인증만 제공, 암호화 아님)
- `signature = sha256_48(secret_key + header + payload + CRC + link-ID + timestamp)`, 13바이트 서명 부가, 비밀키 32바이트(링크 양 끝 저장).
- 타임스탬프: 48비트, "10 microsecond units since 1st January 2015 GMT time", 같은 (SystemID, ComponentID, LinkID) 스트림에서 단조 증가.
- 거부 규칙: 이전보다 오래된 타임스탬프, 서명 불일치, 로컬 시각보다 6,000,000 단위(1분) 넘게 과거.
- `RADIO_STATUS`는 항상 서명 없이 수용. 서명 실패 패킷으로 링크 타임스탬프를 갱신하면 안 되고, `SETUP_SIGNING`은 브로드캐스트·포워딩 금지, 키를 파라미터·로그에 노출 금지.

**정책-as-코드: Open Policy Agent** (원문) — [OPA docs](https://www.openpolicyagent.org/docs/latest/)
- OPA "decouples policy decision-making from policy enforcement." 정책 언어는 "a high-level declarative language called Rego". 입력은 구조화 데이터(JSON), 결정은 allow/deny에 한정되지 않는 임의의 구조화 출력(→ 차단 사유·위반 규칙 ID 반환 가능). OPA는 "a graduated Cloud Native Computing Foundation (CNCF) project".

**능력 토큰: Macaroons (Google, NDSS 2014)**
- [학술] "macaroons embed caveats that attenuate and contextually confine when, where, by who, and for what purpose a target service should authorize requests"; 체인 HMAC 구성으로 쿠키 수준의 효율. 공개키 기반 SPKI/SDSI에 견줄 만한 위임 표현력. (검색발췌) — [Google Research](https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/), [NDSS PDF](https://www.ndss-symposium.org/wp-content/uploads/2017/09/04_3_1.pdf)

**LLM/AI 명령원에 대한 가드레일: OWASP LLM06:2025 Excessive Agency** (원문) — [OWASP GenAI](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
- 정의: 취약점은 "enables damaging actions to be performed in response to unexpected, ambiguous or manipulated outputs from an LLM". 원인: "excessive functionality," "excessive permissions," "excessive autonomy."
- 대책: "Utilise human-in-the-loop control to require a human to approve high-impact actions before they are taken"; "Implement authorization in downstream systems rather than relying on an LLM to decide if an action is allowed or not"; complete mediation, 즉 "all requests made to downstream systems via extensions are validated against security policies."

**인간 승인·설명 요구의 군 정책 근거**
- [공식] DoDD 3000.09 1.2.a.(1)(b): 경계 밖이면 "terminate the engagement or obtain additional operator input before continuing the engagement." / 1.2.a.(3)(a): HMI는 "clearly indicating what actions operators need to perform and which actions the system will perform" / (b) "Provide transparent feedback on system status." (원문-직접추출) — [DoDD 3000.09 (Wayback)](https://web.archive.org/web/2024id_/https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodd/300009p.pdf)
- [공식] DoD ZT Strategy: "Never Trust, Always Verify Explicitly. Treat every user, device, and application as untrusted and unauthenticated. Authenticate and explicitly authorize to the least privilege using dynamic security policies." (원문-직접추출) — [DoD Zero Trust Strategy 2022 (Wayback)](https://web.archive.org/web/2024id_/https://dodcio.defense.gov/Portals/0/Documents/Library/DoD-ZTStrategy.pdf)
- [학술/공식] Auto-GCAS: "Auto GCAS shall notify the pilot when the automatic recovery maneuver initiates and terminates." / "The system shall record data about each automatic recovery maneuver activation." / 사람이 단순 기동을 더 신뢰: "humans trust an easily understood maneuver consistent with human training, expectations, and preferences". (원문-직접추출) — [Hobbs et al.](https://arxiv.org/abs/2110.03506)

### Inferences
- **명령 경로 설계(1 액션 = 1 검사)**: `명령원(운용자/AI 할당기/LLM)` → `서명·ID 확인`(MAVLink 서명 또는 HMAC) → `정책 검사`(지오펜스·고도·속도·배터리 여유·ROE 박스·기체 신뢰 상태·명령 빈도) → `위험등급 분류` → 저위험: 자동 통과 / 중위험: 가장 가까운 안전 명령으로 수정 후 통과(+알림) / 고위험(예: 무기·페이로드 해제, 펜스 해제, 격리 해제, 다수 기체 동시 RTL 취소): **2차 승인(운용자 재확인 또는 두 번째 역할)** / 금지: 거부. OWASP의 "authorization in downstream systems rather than relying on an LLM"을 그대로 구현한 형태다.
- **24시간 기준 OPA 대신 순수 Python 규칙 테이블**도 충분하다. 다만 "정책은 데이터(YAML/Rego), 집행기는 작고 고정"이라는 구조를 보여주면 OPA 선례로 설명할 수 있다. 결정 출력은 `{allow, modified_cmd, rule_id, reason_ko, reason_en, evidence}` 형태가 좋다.
- **차단 사유 설명 UX**(DoDD 3000.09 1.2.a.(3) + Auto-GCAS 기준): (1) 무엇이 막혔나(원 명령), (2) 어떤 규칙 때문인가(규칙 ID·한 줄 설명), (3) 시스템이 대신 무엇을 하나("which actions the system will perform"), (4) 운용자가 할 수 있는 것("which actions operators need to perform", 예: 2차 승인 요청 버튼), (5) 기록 ID. 시작·종료 알림과 로그는 필수.
- **2인 규칙의 해커톤식 축소판**: 1인 운용자 과제이므로 사람 2명 대신 "운용자 + 독립 안전 커널" 또는 "운용자 + 지휘관 역할 토큰"으로 구현하고, 고위험 명령만 2-of-2를 요구하면 인지부하를 늘리지 않으면서 선례를 가져올 수 있다.
- **능력 토큰**: AI 할당기·LLM에게는 "기체 X, 구역 Y, T분, 이동 명령만" 같은 감쇠된 토큰만 발급하면, 프롬프트 인젝션을 당해도 피해 범위(blast radius)가 토큰 범위로 제한된다(ZT "Presume Breach"와 같은 논리).

### Gaps
- 군 C2/무인체계에서 "서명 명령 + 2인 승인"을 결합한 공개 구현 사례(예: 특정 GCS 제품)는 찾지 못함.
- JP 1-02 사전의 "two-person concept" 공식 문구는 직접 확인 못 함(AFI·DOE 2차 인용).
- MAVLink 서명의 ArduPilot/PX4 실제 설정 절차·SITL 지원 여부는 이번에 확인하지 않음.
- Macaroons 논문 원문 미열람(초록 기반).

---

## Q6. 무기체계·전술 엣지에 대한 Zero Trust — 2022 전략과 2024–2026 지침

### Takeaway
DoD Zero Trust Strategy(2022-10)는 **"never trust, always verify"**, **"Presume Breach … limit the blast radius"**, 최소 권한, 행위 상시 분석을 원칙으로 하고 **FY2027 말까지 Target Level(91개 활동)**을 목표로 한다. 무기체계는 IT → OT → 무기체계 순서에서 **마지막**이다. 2025-11 OT 지침(105개 활동)은 무기체계의 **경계까지만**(예: 무기 전원은 포함, 내부 표적·발사 체계는 제외) 다룬다. 무기체계 ZT 목표는 "FY2035 and beyond"로 제시됐고("very green in the thinking"), 전략 2.0은 2026년 초 발표 예정이었으나 이번 조사에서 발간을 확인하지 못했다. → 무인체계 C2에 ZT를 적용하는 표준 지침은 아직 없다. 팀이 "Presume Breach를 기체 단위로 적용"하면 선도적 해석으로 내세울 수 있다.

### Cited Findings
- [공식] DoD ZT Strategy(2022) 원문(원문-직접추출) — [DoD CIO PDF](https://dodcio.defense.gov/Portals/0/Documents/Library/DoD-ZTStrategy.pdf) (자동 접근 403) / [Wayback 사본](https://web.archive.org/web/2024id_/https://dodcio.defense.gov/Portals/0/Documents/Library/DoD-ZTStrategy.pdf):
  - "This “never trust, always verify” mindset requires us to take responsibility for the security of our devices, applications, assets, and services; users are granted access to only the data they need and when needed."
  - "At its core, ZT assumes no implicit trust is granted to assets or users based solely on their physical or network location ... or asset ownership"
  - "Presume Breach. Limit the "blast radius" – the extent and reach of potential damage incurred by a breach – by segmenting access, reducing the attack surface, and monitoring risks in real-time within DoD's risk tolerance levels and thresholds." 각주: "Consciously operate and defend resources with the assumption that an adversary has presence within your environment."
  - "Least Privilege. "Subject/entity should be given only those privileges needed for it to complete its task”."
  - "Scrutinize and Analyze Behavior. All events within our IE must be continuously monitored, collected, stored, and analyzed based on risk profiles and generated in near-real time for both user and device behaviors."
  - ZT RA v2.0 원칙 5개: "1) Assume a Hostile Environment; 2) Presume Breach; 3) Never Trust, Aways [sic] Verify; 4) Scrutinize Explicitly; and 5) Apply Unified Analytics."
  - 전술 환경: "ZT enables information dominance across the communications spectrum in the tactical environment by ensuring the security of data, applications, assets and services (DAAS). Execution plans must account for the potential ramifications of ZT in the tactical environment."
  - 일정: "projected roadmap for achieving the ZT Target Level by the end of FY2027."
- [언론] Target Level 91개 활동, Advanced는 61개 추가로 총 152개, 기한 2027-09-30. (검색발췌) — [DefenseScoop 2024-04-04](https://defensescoop.com/2024/04/04/dod-zero-trust-implementations-phase-2027/)
- [언론, 2025-04-02] Breaking Defense(Resnick, DoD ZT 포트폴리오 관리실장): 무기체계 ZT 목표 FY2035(비구속). "We're talking about stuff that potentially is inside the skin of this, of the weapon system." / "We are far away. I'm suggesting fiscal [year 20]35 and beyond." / "It's very green in the thinking." / "maybe not just for weapon systems, that ZT [zero trust] doesn't end with IT." FY2022 NDAA가 무기체계 ZT를 요구하며, 무기체계는 IT·OT 다음 마지막 영역. 모든 무기체계에 ZT가 맞지는 않을 수 있다는 발언도 있음. (원문) — [Breaking Defense](https://breakingdefense.com/2025/04/dod-floats-2035-as-goal-for-zero-trust-in-weapons-systems/)
- [언론, 2025-12-01] OT용 ZT 지침("Zero Trust for Operational Technology Activities and Outcomes", 2025-11-18자, 28쪽): "105 zero-trust activities and capability outcomes"(target 84, advanced 21), 7개 기둥(users; devices; applications and workloads; data; networks and environments; automation and orchestration; visibility and analytics). 범위는 "some elements of a weapon system or defense critical infrastructure component"이며 "a power source for a specific weapon, but not that system's internal targeting or firing systems". OT에는 구체적 기한 없음. (원문) — [DefenseScoop](https://defensescoop.com/2025/12/01/dod-guidance-implementing-zero-trust-for-operational-technology-ot/)
- [언론] DTM 25-003(2025-07): 통제시스템·OT를 포함한 모든 비밀·비비밀 시스템에 최소 Target Level ZT 요구. (검색발췌) — [MeriTalk](https://www.meritalk.com/articles/dod-issues-zero-trust-ot-guidance/); OT target FY2030, advanced FY2033 언급(가변). (검색발췌) — [runZero](https://www.runzero.com/blog/dod-zero-trust-guidance-ot-systems/)
- [언론, 2025-12-09] ZT 전략 2.0은 2026년 초(3월경) 발표 예정이며 OT·IoT·방위핵심기반시설·무기체계 프레임워크를 다룰 예정. (검색발췌) — [DefenseScoop](https://defensescoop.com/2025/12/09/dod-zero-trust-strategy-2-0-expected-early-2026/)
- [분석, 2026-05] Federal News Network 기고: 국방 OT ZT 구현 현실(엣지 장치와 UAV까지 확장된다는 해석). (검색발췌, 해석이 DefenseScoop보다 넓음 → 상충) — [Federal News Network](https://federalnewsnetwork.com/commentary/2026/05/the-reality-of-implementing-zero-trust-for-defense-operational-technology/)

### Inferences
- 무인체계 C2에 바로 옮길 수 있는 ZT 원칙은 다섯 가지다. ① **기체=디바이스, 명령원=사용자/워크로드**로 보고 모든 명령에 인증·인가(위치나 "우리 링크"라서 믿지 않음) ② **Presume Breach** = 기체 1대 또는 명령원 1개가 이미 장악됐다고 가정하고 피해 범위를 제한(격리, 능력 토큰, 기체별 키) ③ **Least Privilege** = AI 할당기는 이동 명령만, 무장·펜스 해제 권한 없음 ④ **Scrutinize Behavior** = 텔레메트리 상시 분석으로 신뢰점수 산출(Q4) ⑤ **Dynamic policy** = 신뢰점수·상황에 따라 정책이 동적으로 바뀜.
- 공식 지침이 무기체계 "내부"는 아직 다루지 않으므로(OT 지침은 경계까지), 해커톤 결과물은 "**전술 엣지 C2 계층의 ZT 시제**"로 내세우는 것이 정확하다. 공식 표준을 따랐다고 과장하지 않는다.
- DDIL(단절·간헐·저대역) 환경에서는 중앙 인가 서버에 매번 물을 수 없다. 그래서 **사전 발급 능력 토큰 + 기체 측 서명 검증 + 링크 상실 시 안전 기본동작**의 조합이 ZT와 lost-link 요구를 동시에 만족시키는 설계가 된다(추론).

### Gaps
- ZT 전략 2.0(2026)의 실제 발간 여부·내용 미확인.
- 무기체계·전술 엣지 ZT에 대한 공개 공식 지침(2024–2026)은 찾지 못함. Breaking Defense 발언과 OT 지침 범위 정도만 확인.
- OT 지침 원문(28쪽) 미열람. FY2030/2033 기한은 2차 출처.

---

## Q7. "하방이 막혔다"를 증명하는 데모 지표 — 선례와 정량 근거

### Takeaway
선례가 있는 지표는 다음과 같다. AFRL RTA 튜토리얼의 **개입 횟수·제어 변경량·침습성·안전집합 크기**, Auto-GCAS의 **nuisance-free 1.5초 기준**, **신뢰도 98%가 신뢰를 만들었다**는 보고, 스푸핑 탐지율(Gil: 96% 초과), 시드 수를 밝힌 몬테카를로(Park & Yoo: 20 seeds). 통계적으로 "N회 실행에서 위반 0건"은 **"위반률 95% 상한 ≈ 3/N"**(rule of three)으로 표현해야 정직하다(1,000회 무위반 → 95% 신뢰로 위반률 < 0.3%). DoDD 3000.09는 "절대 교전하지 않음"이 최소 위험의 의미가 아니라고 명시하므로, **임무 성공률 유지**를 반드시 함께 보여야 한다.

### Cited Findings
- [학술/공식] RTA 비교 지표(원문-직접추출): "the number of RTA activations, magnitude of the response, activation timing, and size of the safe set can be use[d] to compare nuisance criteria across different RTAs." — "An RTA activations metric tracks the number of seconds or discrete time steps that a recovery maneuver is in control ... it provides a measure of relative conservatism of various RTA solutions in the presence of the same, possibly faulty primary controller." / "control magnitude metric" / "An RTA invasiveness metric describes whether the RTA activates appropriately when near the safety constraint boundary, while refraining from activating when far from the allowable boundary." / "An RTA safe set size measures of the volume of the safe set CS. The larger the volume, the more space the primary controller has to operate optimally, and the less invasive the RTA is." — [Hobbs et al., arXiv 2110.03506](https://arxiv.org/abs/2110.03506)
- [학술/공식] Auto-GCAS: 1.5초 time-available 기준(nuisance-free), 98% 신뢰도가 시험조종사의 신뢰를 높임, 운용자 위험허용도 모드(norm/min). (원문-직접추출) — 같은 출처
- [학술] 오탐·미탐 고려: Hobbs는 RTA-인간 상호작용 항목에 "missed detection/false alarm considerations"를 포함. (원문-직접추출) — 같은 출처
- [공식] DoDD 3000.09: "minimizing the probability and consequences of failure means reducing the probability and consequences of unintended engagements to acceptable levels while meeting mission objectives and does not mean achieving the lowest possible level of risk by never engaging targets." / 변경 후 "validate that critical safety features have not been degraded. Automated testing tools, such as modeling and simulation, will be used whenever feasible." / 배치 전 "reprogrammed with sufficient rapidity to enable timely correction of any unintended system behaviors". (원문-직접추출) — [DoDD 3000.09 (Wayback)](https://web.archive.org/web/2024id_/https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodd/300009p.pdf)
- [학술] Sybil 스푸퍼 탐지율 96% 초과(실기 쿼드로터+지상로봇). (검색발췌) — [Gil et al., RSS 2015](https://www.roboticsproceedings.org/rss11/p20.html)
- [프리프린트] 공통 스푸핑 하에서 절대위치 복원 중앙값 오차 0.39 m(표류 10.1 m, 20 seeds, 시뮬레이션). (원문) — [arXiv 2608.06885](https://arxiv.org/abs/2608.06885)
- [학술] CBF 하드웨어 시연은 "일부러 충돌하게 만든" 명목 제어기에서도 충돌을 막는 방식으로 안전성을 보였다(적대적 명목 입력 시험의 선례). (검색발췌) — [Wang, Ames, Egerstedt 2017](https://resolver.caltech.edu/CaltechAUTHORS:20170215-165434009)
- [학술] W-MSR 보장 문구: 정상 기체의 합의값이 "within the range of the cooperative agents’ initial values"(→ 측정 가능한 불변식). (원문-직접추출) — [Saulnier et al. 2017](https://www.lehigh.edu/~das819/pdf/ral17-resilient-flocking.pdf)
- [통계] Rule of three: "the interval from 0 to 3/n is a 95% confidence interval for the rate of occurrences in the population." 예: 1,500명 무이상 → "fewer than 1 person in 500 (or 3/1500)". (원문) — [Wikipedia: Rule of three (statistics)](https://en.wikipedia.org/wiki/Rule_of_three_(statistics))
- [표준] 격리/전환 시간 참고값: ArduPilot EKF 페일세이프 1초 지속 조건, GCS 페일세이프 기본 5초, GPS 글리치 재설정 약 7초, MAVLink 서명 재전송 허용창 1분. (원문) — [ArduPilot EKF](https://ardupilot.org/copter/docs/common-ekf-inav-failsafe.html), [ArduPilot GCS](https://ardupilot.org/copter/docs/gcs-failsafe.html), [MAVLink signing](https://mavlink.io/en/guide/message_signing.html)

### Inferences
- **데모 대시보드 권장 지표 세트(선례 매핑)**:
  1. *불변식 위반 0건 / N 시드* — 지오펜스 이탈, 기체 간 최소거리(D_s) 침범, 배터리 귀환 여유 위반. "1,000 시드 0건 → 95% 신뢰 상한 0.3%"로 표기(rule of three). 위반 0건을 "증명"이라고 부르지 말고 "통계적 상한"이라고 말한다.
  2. *차단/수정된 위험 명령 수(명령원별)* — 운용자·AI 할당기·LLM·주입 공격으로 나눠 표시. 수정(minimal modification)과 거부를 구분(Hobbs의 control magnitude).
  3. *개입률·침습성* — 전체 명령 중 개입 비율, 경계에서 먼 상황의 불필요 개입 수(Auto-GCAS의 nuisance 관점). 낮을수록 "방해하지 않는 안전장치".
  4. *임무 성공률: 기준선 vs 공격 하 vs 안전커널 켬* — DoDD 3000.09의 "while meeting mission objectives". 안전커널이 성공률을 크게 떨어뜨리지 않음을 보여야 한다.
  5. *격리까지 걸린 시간(time-to-isolate)과 오탐/미탐* — 스푸핑·명령 탈취 주입 시점부터 SUSPECT·ISOLATED 전환까지(초). 정상 기체 오격리 수(false alarm). 비교 기준으로 ArduPilot EKF 1초·GCS 5초.
  6. *운용자 부담* — 운용자가 직접 승인해야 했던 고위험 명령 수/분(T1-1의 인지부하 요구와 연결).
- **"적대적 명목 입력" 시험 설계**: Wang 등이 일부러 충돌하는 제어기를 넣은 것처럼, 데모에서도 (a) 무작위 위험 명령 생성기(퍼저), (b) 프롬프트 인젝션된 LLM 명령, (c) 스푸핑된 기체 텔레메트리를 몬테카를로로 주입하고 1)~5) 지표를 표로 보여주면, "어떻게 안전한지 아느냐"에 대한 정량 답이 된다.
- **회귀 시험 = DoDD 3000.09 Section 3**: "critical safety features have not been degraded"를 pytest + 시뮬레이션 시드 세트로 구현해 `ship` 때마다 돌린다고 말하면, 해커톤 저장소 구조(1 액션 = 1 테스트)가 정책 요구와 연결된다.

### Gaps
- 다중 UxV C2에서 "차단된 위험 명령 수", "격리 소요 시간" 같은 지표를 공개 보고한 군·산업 사례는 찾지 못함(위 매핑은 추론).
- ASTM F3269이 요구하는 검증 커버리지·시험 지표는 유료 본문이라 미확인.
- Auto-GCAS "98% reliability"의 정의(무엇의 98%인지)는 Hobbs 원문에서 더 확인하지 않음(참고문헌 [92] 추적 필요).
