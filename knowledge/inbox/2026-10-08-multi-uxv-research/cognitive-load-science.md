# 단일 운용자 다중 UxV 감독의 인지부하 과학 (모델 · 실험 수치 · 측정 · 설계 패턴)

> 작성 2026-10-08. 모든 인용문의 **접근일은 2026-10-08**. 직접 인용(verbatim)과 수식은 원문 그대로 두었다.
> 표기: [원문확인] = PDF 원문을 직접 내려받아 읽음 / [초록·요약] = 초록·저장소 메타데이터·2차 요약만 확인 / [스니펫] = 검색 결과 요약에만 근거(원문 미확인, 인용 전 재확인 필요).
> 범위: 인지부하·감독제어 과학. SUPPORTY·오픈소스·현장 운용·군 사업 상세는 같은 폴더의 다른 노트(`supporty-and-oss.md`, `field-operations.md`, `military-programs.md`)가 다룬다.

## Q1. 감독제어 모델(Sheridan, Fan-out, Neglect/Interaction time, Wait time, Utilization)과 실험에서 나온 운용자:비히클 비율

### Takeaway
"한 명이 몇 대를 운용할 수 있나"는 상수가 아니라 **NT(방치 가능 시간)·IT(상호작용 시간)·WT(대기 시간)의 비율**로 정해진다: `FO = NT/(IT+WT) + 1`. 실험실 수치는 직접 조종형 과업에서 대략 4–6대(정점), 탐색 과업 8–12대(직접 제어 한계), 고자율·플레이 기반 감독에서 12대(IMPACT)~100대 이상(DARPA OFFSET 스웜)까지 넓게 퍼지며, 운용자 점유율(utilization) 약 70%가 성능 저하의 경험적 문턱이다.

### Cited Findings

**(a) Fan-out 원형: Olsen & Wood (CHI 2004) [원문확인]**
- 원문 수식과 정의: "We hypothesize that the following fan-out equation holds, `FO = AT / IT` … FO=fan-out or the number of robots a human can control simultaneously, AT=activity time or the time that a robot is actively effective after receiving commands from a user, IT=interaction time or the time that it takes for a human to interact with a given robot." — [Olsen & Wood 2004, CHI](https://hci.rwth-aachen.de/materials/conferences/CHI2004/1p231.pdf)
- AT와 NT의 관계(겹침 비율 O): `AT = O*IT + NT` ("Overlap is the percentage of the interaction time where the robot is also active.") — 같은 출처.
- IT는 단일 덩어리가 아니라 4개 성분이라는 가설(과업 전환 비용의 근거로 자주 인용): "1. Robot Monitoring and Selection … 2. Context Switching – when switching attention between robots the user must spend time reaquiring the goals and problems of the new robot. 3. Problem Solving … 4. Command Expression" 그리고 "it seems that IT should increase with FO. This is because the more robots there are to control, the greater the monitoring and robot selection time." — 같은 출처.
- 실험 맥락: "robo-races" — 8명이 8번 경주, 로봇 18대 가용·목표 10개, 장애물 밀도 35%. 측정된 평균 fan-out: Simple 1.46 / Bounce 2.94 / Plan 5.11. 장애물 22%로 낮추면 1.84 / 3.36 / 9.09. 계산된 interaction effort는 로봇 지능과 무관하게 ~2.7–3.4로 비슷("no statistical difference in the interaction times across the three robot types"). — 같은 출처.
- 인터페이스 품질 측정 사례: 해상도를 1600x1200→800x600으로 낮춰 스크롤이 필요해지자 interaction effort가 +46%(Simple), +25%(Bounce), +26%(Plan) 증가 → "inferior interfaces produce higher interaction effort". — 같은 출처. (해커톤 시사점: **IT를 로그로 재서 UI 개선 전후를 비교**하는 것이 학계에서 쓰인 방식)
- 동기 문제: 무보상 피험자는 대충 해서 fan-out이 낮게 나와 상금 경주로 바꿈 — "unmotivated subjects distorted the results". — 같은 출처.
- "fan-out plateau" 측정법: 로봇을 늘려도 과업 효과가 더 오르지 않는 지점. "We might hypothesize that for a given HRI team, the fan-out plateau would be between 4 and 12 robots." (단, 측정 비용이 매우 크다고 지적) — 같은 출처.

**(b) RAD / Free time / Fan-out: Olsen & Goodrich (PERMIS 2003) [원문확인]**
- `RAD = IE / (IE + NT)` ("RAD is a unitless quantity that represents the fraction of a human's time that is consumed by interacting with a robot."), `FT = 1.0 − RAD`, `FO = 1.0 / RAD = (NT + IE) / IE`. — [Olsen & Goodrich 2003](https://faculty.cs.byu.edu/~mike/mikeg/papers/OlsenGoodrichPERMIS2003.pdf)
- 자유시간(FT)은 2차 과업으로 측정 가능: "One way to measure free time is to give the user a robotic task and some other secondary task … Finding more bullfinches without increasing the time to target would mean that RAD had been reduced." (2차 과업 예: 암산, 가짜 통화, 물체 분류, 이메일 읽기) — 같은 출처.
- FO 한계의 두 번째 원인으로 작업기억을 지목: "The second constraint that limits fan-out is caused by limitations of human cognition, primarily memory." — 같은 출처.

**(c) Neglect tolerance와 이종 편대 실현가능성: Crandall, Goodrich, Olsen & Nielsen (IEEE SMC-A 2005) [원문확인]**
- 정의: "Formally, neglect time is the expected amount of time that a robot can be ignored before its performance drops below a threshold." / "Formally, interaction time is the expected amount of time that a human must interact with a robot to bring it to peak performance." — [Crandall et al. 2005, DOI 10.1109/TSMCA.2005.850587](https://students.cs.byu.edu/~crandall/papers/CGON_SMCa_05.pdf)
- "Roughly speaking, fanout is one plus the ratio of neglect time to interaction time." → `FO = NT/IT + 1`. 예시: NT 안에 IT가 3번 들어가면 "the human can only manage four total robots." — 같은 출처.
- 이종 편대: 로봇 i마다 (NT_i, IT_i)가 다르며, 식 (1)로 "whether the neglect time for each robot is sufficiently long to allow the human to interact with every robot in the team"을 검사해 실현 가능/불가를 판정. (식 자체는 PDF에서 이미지라 텍스트 추출 불가 — 의미상 "각 로봇의 NT_i ≥ 나머지 로봇 IT의 합" 형태로 읽힘, **이 형태는 노트 작성자의 재구성**) — 같은 출처.
- NT/IT는 단일 로봇 + 2차 과업 실험으로 얻는 방법을 제안("a measurement methodology, based on a secondary task paradigm"), 3대 팀 예측에서 "the model seems to identify situations of operator overload." — 같은 출처.

**(d) 대기시간(Wait Time) 포함 Fan-out: Cummings & Mitchell (IEEE SMC-A 38(2):451–460, 2008) [원문확인]**
- 수식: 원 Fan-out `FO = (NT + IT)/IT = NT/IT + 1` (Eqn 1), 대기시간 `WT = Σ_{i=1..X} WTQ_i + Σ_{j=1..Y} WTSA_j` (Eqn 2), 수정 Fan-out `FO = NT / (IT + WT) + 1` (Eqn 3). WTI(상호작용 중 의사결정 대기)는 IT에 포함. "X = Number of human-automation interaction queues that build, Y = Number of time periods in which a loss of SA causes wait time". — [Cummings & Mitchell 2008](https://dspace.mit.edu/handle/1721.1/90280)
- 3가지 대기: "1) wait time in the human decision-making queue (WTQ), 2) interaction wait time (WTI), and 3) wait time due to loss of situation awareness (WTSA)." — 같은 출처.
- 해석: "the modified Fan-out (Eqn. 3) is not intended to make an accurate prediction of exactly how many vehicles a person could control, but merely set an upper limit given human and system limitations." — 같은 출처.
- 실험 맥락: MAUVE 시뮬레이터, 동종·독립 UAV 4대 고정(SEAD 임무), 피험자 12명(ROTC/현역 9명 포함), 자동화 4단계(Manual/Passive/Active/Super Active) × 재계획 빈도 2수준. 실측 평균: WTI 81.5 s (SD 57.6), WTQ 35.0 s (SD 43.4), WTSA 263.7 s (SD 239.7). WTSA가 전체 대기시간의 63%(저 재계획) / 72%(고 재계획). — 같은 출처.
- 핵심 수치: "By including wait times in the prediction model, the upper bound of the number of homogeneous independent unmanned vehicles a single controller can manage drops 36-67% based on the effectiveness of the decision support." 관리-예외(management-by-exception) 최고 자동화에서도 SA 상실 대기 때문에 36% 감소. — 같은 출처.
- WTSA의 조작적 정의(구현 가능): "Situation awareness wait time was recorded when at least one vehicle required attention, but the operator did not realize it … This time interval was marked by operator inactivity, i.e., if a problem was present, and the operator did not attend to it and was not engaged in any other task." — 같은 출처.
- 배경 문헌 요약(같은 논문): "operators can control anywhere from one to twelve unmanned air vehicles [2-4] and one to eight ground vehicles [5, 6]". — 같은 출처.

**(e) 70% 점유율(utilization) 문턱 [초록·요약 + 원문 내 재인용]**
- Cummings & Guerlain (Human Factors 49(1), 2007): 고자율 비행 중 미사일을 시간민감 표적에 재할당하며 난이도가 다른 2차 과업 수행. "The results suggest that a 70% utilization (percentage busy time) score is a valid threshold for predicting significant performance decay and could be a generalizable metric that can aid in manning predictions." — [paperguide 요약(3자, 원문 미확인)](https://paperguide.ai/papers/09b4e035-e943-4ea4-ac20-c3d30f2b43ff/)
- 같은 문턱을 Cummings & Mitchell 2008 원문이 재인용: "UT is the ratio of time an operator is actively engaged in a task (including the three major elements of information processing: perception, cognition, and action) to the overall operating time of a system … operators working beyond 70% utilization experience significantly degraded performance [2, 11, 12]." — [Cummings & Mitchell 2008](https://dspace.mit.edu/handle/1721.1/90280) [원문확인]
- 반론/보완: Whetten, Goodrich & Guo (2010) 에이전트 기반 시뮬레이션 — "operators may be more effective when they operate at less than maximum capacity." — [BYU SMC2010](https://faculty.cs.byu.edu/~mike/mikeg/papers/SMC2010.pdf) [스니펫]
- "Fan-Out Revisited": NT가 인간·로봇 능력을 섞는다며 "the time a robot can operate self-sufficiently, and the time a human estimates the robot can do so"로 분리 제안, "Previous research indicates fan-out is often overestimated." — [UWF IR Commons](https://ircommons.uwf.edu/esploro/outputs/conferenceProceeding/Fan-Out-Revisited/99381474081806600) [초록·요약]

**(f) 점유율–성능의 역U자 관계: Donmez, Nehme & Cummings (IEEE SMC-A 40(6):1180–1190, 2010) [원문확인]**
- 실험: 74명, RESCHU 시뮬레이터, 5대(UAV/UUV) 이종도 3수준. 점유율 구간별 점수: "60-70% utilization corresponded to significantly higher scores than most other utilization values (30-40%: p=.02, 50-60%: p=.02, 70-80%: p=.02, 80-90%: p<.0001). In addition, 80-90% utilization resulted in lower scores than both 70-80% (p=.03) and 40-50%, p=.04) utilization." — [Donmez et al. 2010](https://dspace.mit.edu/handle/1721.1/87059)
- 점유율의 정의와 장점: "'percent busy time' of an operator … this is generally meant as the time an operator is directed by external events to complete a task … Compared to more common measures of workload (e.g., pupil dilation, NASA TLX), utilization provides the means to assess workload in real-time, non-intrusively. What is not included in this measurement is the time spent monitoring the system". — 같은 출처.
- 높은 점유율 → 주의 비효율로 인한 대기(WTAI) 증가: "WTAI is significantly associated with operator utilization (UT), such that high UT levels correspond to higher wait times." — 같은 출처.
- 저자 스스로의 한계: "All utilization metrics reported here were post-hoc aggregate measures, which are not accurate as an instantaneous measure of workload … does a person need to work at or above 70% utilization for some period of time before the negative effects are seen". — 같은 출처.

**(g) 실험별 운용자:비히클 비율 수치 모음**
| 연구 | 과업/맥락 | 결과 | 출처 |
|---|---|---|---|
| Crandall & Cummings 2007 (IEEE T-RO 23(5)) | 시뮬 로봇 2/4/6/8대, 8분 세션, 12명 | "number of objects collected steadily increases … up to six robots, at which point effectiveness plateaus"; 관측 FO 4–6대 | [원문확인](https://faculty.cs.byu.edu/~crandall/papers/CrandallCummingsTRO2007_Final.pdf) |
| Wang, Lewis et al. 2009 (HRI'09) | USAR 시뮬, 로봇 4/8/12대 | full-task에서 4→8 성능↑, 8→12 성능↓; "Workload increased monotonically with number of robots"; "consistent with earlier studies suggesting a limit of between 8-12 robots for direct human control" | [CMU RI 초록](https://www.ri.cmu.edu/?p=10283) [초록·요약] |
| Chen, Barnes et al. 2010 (RoboLeader, HRI'10 / ARL-TR-5239) | 지상 로봇 4 vs 8대 | "Participants detected significantly less targets and had significantly worse situation awareness when there were 8 robots compared to the 4-robot condition"; RoboLeader로 임무 시간 ~13% 단축 | [UCF STARS](https://stars.library.ucf.edu/scopus2010/1143), [DTIC](https://apps.dtic.mil/sti/pdfs/ADA528104.pdf) [초록·요약] |
| Parasuraman et al. 2005 / Furukawa 2005 | RoboFlag, Playbook, 로봇 4 vs 8대 | "Performance was superior with flexible interfaces for four robots, but this benefit was eliminated when eight robots had to be supervised." | [Furukawa 2005 원문확인](https://www.scitepress.org/Papers/2005/11907/11907.pdf) |
| Ruff, Narayanan & Draper 2002 (Presence 11(4)) | 시뮬 UAV 최대 4대 | management-by-consent가 exception·manual보다 우수 | [Frontiers 리뷰 재인용](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2016.00568/epub) [초록·요약] |
| Porat et al. 2016 (Frontiers in Psychology) | 이스라엘 SME 대상 일련의 연구 | "an experienced operator can supervise up to 15 UASs efficiently using moderate levels of automation, and control (mission and payload management) up to three systems." 팀 vs 단독 비교에서 대체로 팀 우세 | [원문확인](https://doi.org/10.3389/fpsyg.2016.00568) |
| 같은 논문의 배경 인용 | — | "one operator could control 4–5 vehicles (Cummings et al., 2007a) and apply supervisory control for up to 12 vehicles (Cummings and Guerlain, 2007)" | 같은 출처 |
| Nehme et al. 2008 (Int. C2 Journal) | DES 예측, 이종 팀 2/4/6/8대 | "For teams of six and eight UVs, operator utilization is saturated in the heterogeneous case for all three switching strategies" | [MIT DSpace 원문확인](https://dspace.mit.edu/handle/1721.1/90279) |
| Draper et al. 2017 (IMPACT, ISAP) | AFRL, 기지방어, play 기반 | 1명이 "a dozen simulated vehicles"(12대) 관리 지원 | [CORE Scholar](https://corescholar.libraries.wright.edu/isap_2017/85) [초록·요약] |
| Adams, Hamell & Walker (DARPA OFFSET FX-6, 2021 실시) | 실제 도시 훈련장, UAV+UGV 이종 스웜 | "a single human can deploy a swarm of 100 heterogeneous robots to conduct real-world missions"; 과부하 판정 3.2% | [arXiv 2308.00102 원문확인](https://arxiv.org/abs/2308.00102) |
| Rey-Becerra & Wischniewski 2024 (리뷰, 35편) | SHMR 문헌 종합 | "Wang et al. (2009b) and Velagapudi et al. (2008) proposed a fan-out of 9 robots, while Crandall and Cummings (2007) explained that there seems to be a plateau at 6 robots." | [AHFE 2024 원문확인](https://doi.org/10.54941/ahfe1005460) |

### Inferences
- 시뮬레이터에서 **NT, IT, WTQ, WTSA를 이벤트 로그로 실측**하면 `FO_hat = mean(NT) / (mean(IT) + mean(WT)) + 1`을 실시간 숫자로 띄울 수 있다(예: NT=120 s, IT=20 s면 FO=7; 같은 조건에 WT=15 s가 붙으면 FO≈4.4). "이 운용자는 지금 약 N대까지 감당 가능" + "필요 운용자 수 = ceil(비히클 수 / FO_hat)"이 **인력 절감**을 보여주는 가장 학술적으로 방어 가능한 데모 숫자다.
- SUPPORTY의 "대기 요청 4건 이상 = 과부하" 규칙은 큐 길이(X)만 본다. 위 모델들은 큐 길이보다 **서비스 시간(IT)·방치 가능 시간(NT)·대기 시간(WT)**과 **점유율 70%**를 쓰므로, 같은 4건이라도 각 건의 IT가 5초인지 60초인지에 따라 판정이 달라져야 한다는 것이 과학적 반론이 된다.
- Donmez 결과는 **과소부하(30–40%)도 성능을 떨어뜨린다**는 근거이므로, 경보는 "과부하"만이 아니라 "여력 있음 → 비히클 더 할당 가능" 방향(인력 절감 근거)도 표시할 수 있다.

### Gaps
- Cummings & Guerlain 2007 원문(미사일 수, 2차 과업, 70% 근거 데이터)은 직접 확인하지 못했다(유료). 70% 문턱은 원문 재인용 2건(Cummings & Mitchell 2008, Donmez 2010)으로만 교차 확인.
- 검색 요약에 "In practice, fan-out ranges from one robot being controlled by two to three operators to 12-16 robots being controlled by a single operator" 및 "Goodrich et al. extended Olsen's model to include switch costs and heterogeneous robots"라는 문장이 있었으나 어떤 문헌의 문장인지 URL을 특정하지 못해 인용하지 않음.
- Sheridan의 감독제어 원전(Telerobotics, Automation, and Human Supervisory Control, 1992)과 Sheridan & Verplank(1978) 10단계 원문은 이번에 직접 열지 못했다(아래 Q3의 Parasuraman–Sheridan–Wickens 2000으로 대체).
- 큐잉 이론 기반 주의 모델(예: Schmidt 1978 ATC, Rouse 1980)은 조사하지 못했다.

## Q2. 이종 vs 동종 편대, 과업 전환 비용, 주의 배분 실패, 변화맹, 자동화 편향·안주(complacency)

### Takeaway
"이종 편대가 항상 부하를 높인다"는 통념은 **실험적으로 단순하지 않다**: 이종성이 NT를 늘리고 IT를 줄이면 오히려 점유율이 내려가고(Donmez 2010), 중간 이종도에서 점수가 가장 높았다. 진짜 위험은 이종성 그 자체보다 **전환 시 맥락 재획득 비용, SA 상실로 인한 대기(WTSA), 우선순위 판단 실패, 자동화 편향**이다.

### Cited Findings
- **이종성이 점유율을 낮춘 실험**: Donmez et al. 2010 — 5대 구성: 이종 없음(n=26: MALE UAV 5대), 중간(n=25: MALE 3 + UUV 2), 높음(n=23: MALE 2 + UUV 2 + HALE 1). "as the level of heterogeneity increased, operators interacted less frequently with the vehicles due to longer neglect times and shorter interaction periods." 그런데 점수는 "the medium heterogeneity configuration resulted in significantly higher score than both the no and high heterogeneity team structures." 저자 해석: "the use of higher levels of autonomy can also lead to degraded performance." — [Donmez et al. 2010](https://dspace.mit.edu/handle/1721.1/87059) [원문확인]
- **이종 팀 DES 예측**: Nehme, Mekdeci, Crandall & Cummings 2008 — NDS(결정지원 없음, 레거시)와 FDS(완전 결정지원) UV 혼합 팀은 성능이 두 동종 팀 사이에 위치; "heterogeneous operators have a higher task load due to the inclusion of NDS vehicles in the teams, which require more regular operator attention." 또한 레거시 차량 재계획에 집중한 운용자는 점유율이 가장 낮았는데도 성능이 나빴다: "they had spare cognitive resources but performed at a degraded level because they did not efficiently allocate their attention. These results illustrate the need to provide decision support, regardless of the team composition, as well as directed decision support that makes it clear to the operator what tasks are the most critical." 팀 크기가 전환 전략보다 성능에 더 큰 영향. — [Nehme et al. 2008, Int. C2 J.](https://dspace.mit.edu/handle/1721.1/90279) [원문확인; PDF 글꼴 인코딩을 복호화해 읽음, 약어 NDS/FDS는 복호화 추정]
- **이종성이 왜 어려운가(이론)**: 같은 논문은 기존 모델이 "fail to account for the different demands that heterogeneous vehicles/tasks could require"라고 지적하고, 전환 비용을 "switching between different combinations of heterogeneous vehicles can lead to different switch costs"로 모델링. — 같은 출처.
- **과업 전환(맥락 재획득) 비용**: Olsen & Wood의 IT 4성분 중 "Context Switching – when switching attention between robots the user must spend time reaquiring the goals and problems of the new robot." 및 "the more diverse situations the robots find themselves in the greater the context-switching time." — [Olsen & Wood 2004](https://hci.rwth-aachen.de/materials/conferences/CHI2004/1p231.pdf) [원문확인]
- Crandall et al. 2005: 재방문 시 "switching interval" 동안 로봇 성능이 계속 하락 — "it takes a human a little time to 'come up to speed' when they turn their attention back to the robot. During this switching interval, the robot performance may continue to decline so the switch back to the robot must begin soon enough". — [Crandall et al. 2005](https://students.cs.byu.edu/~crandall/papers/CGON_SMCa_05.pdf) [원문확인]
- Crandall & Cummings 2007의 주의배분효율(AAE) 지표: "SA of the entire HRT (… global SA …), wait times due to loss of SA (WTSA) … and switching times (STs) (the amount of time it takes for the operator to decide which robot to interact with)". — [Crandall & Cummings 2007](https://faculty.cs.byu.edu/~crandall/papers/CrandallCummingsTRO2007_Final.pdf) [원문확인]
- **주의 배분 실패가 가장 큰 손실원**: Cummings & Mitchell 2008 — WTSA가 전체 대기의 63–72%, "operators clearly struggled with the multiple vehicle management task, driven primarily by WTSA". — [Cummings & Mitchell 2008](https://dspace.mit.edu/handle/1721.1/90280) [원문확인]
- **비히클 수 증가 → 부하 단조 증가**: "Workload increased monotonically with number of robots." / "Performance per robot decreased with increases in team size." / 병목은 탐색(내비게이션) — "robot navigation is the best candidate for automation". — [Wang et al. 2009](https://www.ri.cmu.edu/?p=10283) [초록·요약]
- **스웜 크기 변화의 '부하 잔류(workload residue)'** (2026, N=34, 드론 4–20대 모니터링 과업): "Small increases preserve lower workload, whereas small decreases leave workload elevated, indicating workload residue; large changes in either direction attenuate these effects, suggesting a reset response." 객관 성능은 작은 변화에 거의 영향 없음. — [Hunt et al. 2026, AHFE 채택 preprint](https://arxiv.org/abs/2604.21707) [원문확인(초록·방법)]
- **변화맹/변화 탐지**: Parasuraman, Cosenzo & de Visser 2009 — 정찰 임무 4중 과업(UAV 표적식별, UGV 경로계획, SA 탐침이 섞인 통신, 상황지도 변화 탐지). 적응형 자동화 조건에서 "Change detection accuracy and situation awareness were higher and workload was lower for adaptive compared to static automation." — [GMU HAI Lab](https://humanfactors.gmu.edu/archives/defunct-labs/research) [초록·요약], DOI 10.1080/08995600902768800
- 변화맹 전용 다중 UAV 연구는 드묾. 2026 arXiv 원고(Sasangohar 그룹)는 다중 화면 지휘관이 변화맹에 취약하다며 시선추적으로 놓친 변화를 하이라이트하는 도구를 제안 — [arXiv 2601.18015](https://arxiv.org/pdf/2601.18015) [스니펫]. 촉각 변화맹은 확인, 시각-촉각 교차 변화맹은 미확인(UAV 제어 맥락) — [Salu dissertation](https://deepblue.lib.umich.edu/bitstream/2027.42/108870/1/salu_1.pdf) [스니펫]
- **자동화 편향·안주**: Parasuraman & Manzey 2010 (Human Factors 52(3):381–410) — "Complacency and automation bias represent different manifestations of overlapping automation-induced phenomena, with attention playing a central role." / "Automation complacency is found in both naive and expert participants and cannot be overcome with simple practice." / "Automation bias results in making both omission and commission errors when decision aids are imperfect." / 훈련·지시로 막을 수 없고 팀 의사결정에도 영향. — [TU Berlin 저장소](https://depositonce.tu-berlin.de/items/0c787d91-6021-480b-a333-009e0d1d0092/full), DOI 10.1177/0018720810376055 [초록·요약]
- 다중 UAV 맥락의 자동화 편향: Cummings & Mitchell(Aerospace Science and Technology, 2007) — 관리-예외 결정지원을 받은 운용자에게 자동화 편향 증거. — [MIT DSpace](https://dspace.mit.edu/handle/1721.1/90289) [스니펫]
- 자율성 증가의 양면: "the number of vehicles one operator can control increases with autonomy, but increasing system autonomy can introduce negative consequences for operator situation awareness and complacency" (Cummings, Bruni, Mercier & Mitchell 2007, Int. C2 J. 1(2)). — [MIT DSpace](https://dspace.mit.edu/handle/1721.1/90285), [DTIC ADA478338](https://apps.dtic.mil/sti/pdfs/ADA478338.pdf) [초록·요약]
- 개인차: 공간능력·주의통제·게임 경험이 다중 로봇 성과를 조절(Chen, Barnes & Harper-Sciarini 2011, IEEE SMC-C 41(4):435–454 리뷰); RoboLeader 실험에서 "Those participants with higher spatial ability detected more targets". — [dblp](https://dblp.uni-trier.de/pid/09/1577.html), [UCF STARS](https://stars.library.ucf.edu/scopus2010/1143) [초록·요약]

### Inferences
- 데모에서 "이종(UAV+UGV+USV) 3종 이상"을 보여줄 때, 이종성 자체를 부하 증가 요인으로 가정하기보다 **비히클 유형별 NT/IT 프로파일**(예: USV는 NT 길고, UAV 영상 식별은 IT 길다)을 정의하고 점유율에 반영하는 편이 Donmez/Nehme 결과와 일치한다.
- 전환 비용을 줄이는 UI: (1) 다음에 볼 비히클을 시스템이 제안(“which robot next” = Olsen의 monitoring & selection 성분 감소), (2) 비히클 재방문 시 직전 맥락 요약 카드(context switching 감소), (3) 같은 유형·인접 지역 과업을 묶어 처리(Lewis 등 공간적 근접성 효과 — [스니펫](https://ah.lib.nccu.edu.tw/bitstream/140.119/118863/1/3044.pdf)).
- WTSA(문제가 있는데 운용자가 아무것도 안 하는 시간)는 로그만으로 자동 계산할 수 있으므로, "놓친 이벤트/알아차리기까지 걸린 시간"을 before/after 핵심 지표로 쓰는 것이 변화맹·주의 실패를 정량화하는 현실적 방법이다.

### Gaps
- Squire & Parasuraman 2010 (Ergonomics 53(8), 자동화·과업부하가 다중 반자율 로봇 감독 중 과업 전환에 미치는 영향)과 Goodrich, Quigley & Cosenzo 2005("Task Switching and Multi-Robot Teams")의 수치 결과는 원문 접근 실패로 확보하지 못함.
- 순수 "이종 vs 동종"에서 이종이 부하를 증가시킨다는 직접 실험 수치는 찾지 못함(오히려 반대 방향 결과만 확보). NT/IT를 통제한 상태에서 '유형 수'만 바꾼 실험이 있는지 불명.
- 다중 UAV 표준 변화맹 패러다임(flicker 등) 실험은 찾지 못함.

## Q3. 인터페이스 설계 패턴: 위임/Playbook, 적응형 자동화, 자동화 수준(LOA), 임무 수준 추상화, 다중감각 경보, 경보 관리(ISA-18.2/EEMUA 191)

### Takeaway
학계·군 연구가 수렴하는 패턴은 **(1) 임무/플레이 수준 위임(Playbook) + 필요 시 하위 수준 개입 허용, (2) 부하·성능 기반으로 켜지는 적응형 자동화, (3) 실행은 '동의(consent)' 기본·과부하 시에만 '예외(exception)'로, (4) 경보는 시간당 개수 예산과 우선순위 분포로 관리**다. 산업 경보관리 표준의 "운용자당 10분에 1건 이하"는 그대로 데모의 경보 예산으로 쓸 수 있다.

### Cited Findings
- **Playbook/위임 인터페이스**: Miller & Parasuraman 2007 (Human Factors 49(1):57–75) "Designing for Flexible Interaction Between Humans and Automation: Delegation Interfaces for Supervisory Control" — 정적·적응형 자동화를 비판하고 인간 간 위임을 모델로 제시, 공유된 계층적 과업 모델로 다수준 위임, LOA를 "과업별 역할·권한의 구성"으로 재정의, 스포츠 플레이북 은유, UAV 임무계획 프로토타입. — [SWOV 서지](https://swov.nl/en/publicatie/designing-flexible-interaction-between-humans-and-automation-delegation-interfaces) [초록·요약]
- 위임의 5가지 기본 방식(Miller 2005 워크숍 초안): goals, plans, negative constraints, positive constraints, priorities/policies. — [Miller 2005 draft](https://www.cs.rochester.edu/research/mipas2005/final-drafts/miller.pdf) [스니펫]
- Playbook 유연성의 한계: RoboFlag(로봇 4 vs 8대, 8종 인터페이스) — 4대에서는 유연한 인터페이스가 우세, 8대에서는 이점 소멸; "participants reported significantly higher mental workload when supervising eight robots compared to four robots … the benefit of the flexible interfaces may have been reduced due to the greater workload demand imposed by full flexibility." — [Furukawa 2005](https://www.scitepress.org/Papers/2005/11907/11907.pdf) [원문확인], 원 실험 Parasuraman, Galster, Squire, Furukawa & Miller 2005 (IEEE SMC-A 35(4):481–493) — [scinapse](https://scinapse.io/papers/2305255894) [초록·요약]
- **IMPACT(AFRL) = play 기반 다중 UxV**: "The human-autonomy team controls multiple UxVs by utilizing high level commands called plays." 자율 측은 자산 할당, 경로 계획, 행동방책(COA) 추천. — [IMPACT 1차 평가 목록](https://independent.academia.edu/DougLange), [Draper et al. 2017](https://corescholar.libraries.wright.edu/isap_2017/85) [초록·요약]
- **DARPA OFFSET의 플레이식 지휘**: I3 VR 샌드테이블; 전술(tactic)을 부르면 디스패처가 "can automatically select and assign vehicles with the necessary capabilities that are proximally close"; 텍스트-음성 알림 사용. — [Adams et al., arXiv 2308.00102](https://arxiv.org/abs/2308.00102) [원문확인]
- **적응형 자동화와 트리거**: GMU 연구실 정리 — 적응형 자동화는 "is initiated by the system based on critical mission events, operator performance, or physiological state." Parasuraman et al. 2009에서는 자동 표적인식 보조가 "invoked only if individual operator change detection performance was below a threshold, but not otherwise" → 변화탐지·SA↑, 부하↓. — [GMU HAI Lab](https://humanfactors.gmu.edu/archives/defunct-labs/research) [초록·요약]
- HFM-217 워크숍(2012) 결론: "flexible, adjustable, trustworthy automation being operated under user sovereignty" 필요, 다중 무인체에 제어과업을 나누는 "adequate models" 필요. — [NATO STO MP-HFM-217](https://www.sto.nato.int/publications/STO%20Meeting%20Proceedings/STO-MP-HFM-217/$MP-HFM-217-ES.pdf) [스니펫]
- **LOA 모델**: Parasuraman, Sheridan & Wickens 2000 (IEEE SMC-A 30(3):286–297) — 4가지 기능 유형(정보 획득, 정보 분석, 결정·행동 선택, 행동 실행) × 각 유형별 저→고 수준; 수준 선택의 1차 기준은 운용자 영향(정신부하, SA, 안주, 기술 퇴화). — [DOI 10.1109/3468.844354](https://doi.org/10.1109/3468.844354) [초록·요약]
- **동의(consent) vs 예외(exception)**: Ruff et al. 2002 — "Management-by-consent (in which the operator must approve an automated solution before execution) was superior to management-by-exception (where automation gives the operator a period of time to reject the solution)." 및 "higher LoAs can actually degrade operator performance when operators attempted to control up to four UA." — [Porat et al. 2016 재인용](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2016.00568/epub), [van Dijk & de Reus, ICAS 2010](https://icas.org/ICAS_ARCHIVE/ICAS2010/PAPERS/211.PDF) [초록·요약]
- **임무 수준 추상화(계층 루프)**: 내부 루프(자세·안정) → 내비게이션 → 임무·탑재체 관리. "in order for one operator to be able to control multiple systems, operators will need to interact primarily at the outermost loop via a mission and payload manager while relegating routine navigation and motion control tasks to the automation." — [Porat et al. 2016](https://doi.org/10.3389/fpsyg.2016.00568) [원문확인] (원 모델: Cummings et al. 2007)
- 무엇을 자동화할지: "The results support the choice of task-centered architectures in which the control and coordination of robotic platforms is automated, leaving search and identification of targets to human operators." — [Wang et al. 2009](https://www.ri.cmu.edu/?p=10283) [초록·요약]
- **결정지원은 '무엇이 가장 중요한지' 명시해야**: "directed decision support that makes it clear to the operator what tasks are the most critical" — [Nehme et al. 2008](https://dspace.mit.edu/handle/1721.1/90279) [원문확인]
- **다중감각/다중모드**: SSC Pacific MOCU 개선(영상+그래픽 통합, 합성음성 출력, 게임패드 입력)으로 다중 USV 단독 운용 시 "Significant gains in performance times and error reduction" (시뮬레이터 평가). — [DTIC ADA586656](https://apps.dtic.mil/sti/pdfs/ADA586656.pdf) [스니펫]. AFIT 다중기 RPA 연구: "frequent, unpredictable, and oftentimes overwhelming, volumes of communication events can produce unmanageable levels of system induced workload", 시각·텍스트 응답이 다른 시각 과업과 경쟁. — [AFIT facpub 83](https://scholar.afit.edu/facpub/83) [스니펫]
- 스웜 인터페이스 메타분석: Hocraffer & Nam 2017 (Applied Ergonomics 58:66–80, 27편) — 사용자·임무 맞춤 인터페이스와 스웜 자동화 수준↑이 부하·SA에 긍정적; 과도한 과업 전환은 SA 위협. — [서지](https://katalog.hcu-hamburg.de/vufind/Search2Record/ELV030756014), DOI 10.1016/j.apergo.2016.05.011 [2차 요약]
- **경보 관리 수치(산업 표준 → 전이 가능)**
  - EEMUA 191: "less than one alarm per 10 minutes" = "very likely to be acceptable"; 이상 발생 후 "less than ten alarms in 10 minutes following an upset" = "should be manageable, but may be difficult". — [Control Global](https://www.controlglobal.com/protect/safety-instrumented-systems/article/11382017/alarm-management-asm-alarm-management-guidelines-and-isa-182-how-do-they-stack-up-control-global) [원문(기사) 확인]
  - ISA-18.2 해설: ~150 alarms/day/operator = 허용 가능, ~300/day = 최대 관리 가능 — [Yokogawa(Control Engineering 기사)](https://www.yokogawa.com/tw/library/resources/media-publications/implementing-alarm-management-per-the-ansi-isa-182-standard-control-engineering) [스니펫]. MAC Solutions 백서(2018): 150/day KPI는 2009판에 있었고 "ISA 18.2 (2016) omitted this KPI completely", IEC 62682:2014는 "around 144 alarms per day" — [BINDT 뉴스](https://www.bindt.org/News/August-2018/new-white-paper-from-mac-solutions-on-how-to-make-sense-of-alarm-system-performance-kpis/) [스니펫]
  - 경보 홍수(flood): 운용자 자리당 10분에 10건 초과로 시작, 10분 창이 5건 미만이면 종료; 홍수 상태 시간 <1% 목표 — [Emerson DeltaV "Alarm management by numbers"](https://d1-live.emerson.com/documents/automation/article-alarm-management-by-numbers-deltav-en-38292.pdf) 등 [스니펫]
  - 우선순위 분포 목표 약 80% 낮음 / 15% 중간 / 5% 높음 — [IChemE 실무 가이드](https://www.icheme.org/media/16019/icheme-alarm-management-practical-guide-06_05_2021.pdf), Emerson 표 [스니펫]

### Inferences
- 데모 UI 설계안(근거 연결): (1) 임무를 "플레이"(예: `정찰-구역`, `경계-선`, `호송`, `추적-인계`)로 부여하고 자율이 자산 할당 → 운용자는 승인만(consent), (2) 점유율 >70% 또는 2차 과업 반응시간 급증 시에만 저위험 플레이를 자동 승인(exception)으로 전환 = 적응형 자동화, (3) 경보는 우선순위 3단계 + "10분 1건" 예산 바(bar) 표시, 예산 초과 시 저우선 경보를 묶음(digest) 처리.
- 경보 예산은 SUPPORTY의 "4건 대기" 규칙보다 **산업 표준이라는 외부 권위**가 있어 심사에서 설명하기 쉽다. 단, 표준 원문은 유료이고 판(edition)마다 KPI가 달라 "업계 벤치마크(EEMUA 191, ISA-18.2)"라고 표현하는 편이 안전하다.
- 동의 vs 예외 선택은 자동화 편향과 연결된다: 예외 모드를 쓰면 처리량은 오르지만 잘못된 자동 제안 통과(commission error) 위험 → 데모에서 "자동 승인된 건 중 오답 비율"을 함께 보여주면 균형 잡힌 주장이 된다.

### Gaps
- ISA-18.2/EEMUA 191 원문(유료)을 직접 확인하지 못함 — 수치는 기사·벤더·학회 자료 경유.
- Miller & Parasuraman 2007, Parasuraman et al. 2005·2009의 정량 결과(정확도 %, 시간 단축 %)는 원문 미확보.
- 다중 UxV에서 청각·촉각 경보의 정량 효과(예: Calhoun/Draper 계열 연구, Dixon & Wickens)는 이번에 확보하지 못함.

## Q4. 측정: NASA-TLX, 2차 과업, 시선·동공·HRV·EEG, 24시간 해커톤 실현 가능성, 과업 큐 기반 실시간 계산적 부하 추정(VACP/IMPRINT) 공식

### Takeaway
24시간·센서 없음 조건에서 가장 방어 가능한 조합은 **(1) 로그 기반 실시간 점유율(utilization)과 대기시간 분해(WTQ/WTSA), (2) 과업별 VACP 값을 합산하는 IMPRINT식 계산 부하(채널>7·총합≥60 경고), (3) 브라우저 내 탐지반응과업(DRT) 2차 과업으로 여유용량 측정, (4) 사후 Raw TLX**다. 웹캠 시선추적은 오차 ~4°로 '어느 패널을 보나' 수준만 가능하고, 생리 지표는 단일 지표로 부하를 확실히 판별하지 못한다는 체계적 리뷰가 있다.

### Cited Findings
**(a) 과업 기반 계산적 부하: VACP / IMPRINT**
- VACP 척도표(McCracken & Aldrich 1984 계열, Bierbaum et al.) — Keller 2002 WSC 튜토리얼 표 [원문확인]: — [Keller 2002](https://www.informs-sim.org/wsc02papers/019.pdf)
  - Visual: 0.0 없음 / 1.0 "Visually Register/Detect" / 3.7 "Visually Discriminate" / 4.0 "Visually Inspect/Check" / 5.0 "Visually Locate/Align" / 5.4 "Visually Track/Follow" / 5.9 "Visually Read (symbol)" / 7.0 "Visually Scan/Search/Monitor (continuous/serial inspection, multiple conditions)"
  - Auditory: 0.0 / 1.0 "Detect/Register Sound" / 2.0 "Orient to Sound (general…)" / 4.2 "Orient to Sound (selective…)" / 4.3 "Verify Auditory Feedback" / 4.9 "Interpret Semantic Content (speech)" / 6.6 "Discriminate Sound Characteristics" / 7.0 "Interpret Sound Patterns (pulse rates, etc.)"
  - Cognitive: 0.0 / 1.0 "Automatic (simple association)" / 1.2 "Alternative Selection" / 3.7 "Sign/Signal Recognition" / 4.6 "Evaluation/Judgment (consider single aspect)" / 5.3 "Encoding/Decoding, Recall" / 6.8 "Evaluation/Judgment (consider several aspects)" / 7.0 "Estimation, Calculation, Conversion"
  - Psychomotor: 0.0 / 1.0 "Speech" / 2.2 "Discrete Actuation (button, toggle, trigger)" / 2.6 "Continuous Adjustive (flight control, sensor control)" / 4.6 "Manipulative" / 5.8 "Discrete Adjustive" / 6.5 "Symbolic Production (writing)" / 7.0 "Serial Discrete Manipulation (keyboard entries)"
- 합산 규칙(원문): "The workload level is increased at the beginning of each task and decreased at the end by the values assigned to the task … a total workload is calculated by summing the totals of all four channels." 코드 예: `Visual := Visual + 6; … TotalWorkload := Visual + Auditory + Cognitive + Psychomotor;` — 같은 출처.
- 채널 과부하 문턱: "In one analysis (Bierbaum, et al 1987), the analysts decided that any cumulative workload value greater than the highest value on the component scale tables represented excess workload. Any cumulative workload value of 8 or more was defined as an unacceptable workload level. This represents a conservative approach". — 같은 출처.
- 총합 문턱은 합의가 없다: ARL 모델러들은 과거 "a single overall workload value of 60 (Mitchell, Samms, Henthorn & Wojciechowski, 2003) or 40 (Mitchell, 2005) or 7 (McCracken & Aldrich, 1984)"을 썼고, 단일 문턱은 방어가 어려워 운용자·구간별 문턱으로 바꿈; "Despite the many years of research, there is, however, no consensus among researchers on a workload threshold." SWAT 문턱 제안치 40–50. — [Mitchell & Samms, NASA NTRS](https://ntrs.nasa.gov/api/citations/20110012092/downloads/20110012092.pdf) [원문확인]
- IMPRINT Pro: "uses a linear workload model incorporating the workload components to classify a predicted overall workload, where ≥60 as overload. IMRPINT Pro does not provide an underload threshold." — [Adams et al., arXiv 2308.00102](https://arxiv.org/abs/2308.00102) [원문확인]
- 유인-무인 협업(MUM-T) IMPRINT 모델(AFIT/AFRL, 2020): 조종사 과업별 총 부하 예 — "Plan UAV Strategy for 1 UAV 10.8 / for 2 UAVs 11.2 / for 3 UAVs 11.8", "Check UAV Status 9", "High Level Command (TBM) 6.6 / Medium Level Command (PDE) 7.0 / Low Level Command (VS) 7.3", "Confirm Command 4.2"; "Events that were above a workload level of 60 were considered to be near or above the saturation threshold". — [Andrews, Rusnock, Miller & Meador, WSC 2020](https://informs-sim.org/wsc20papers/014.pdf) [원문확인] (고수준 명령일수록 VACP 합이 낮다는 점이 플레이 기반 지휘의 정량 근거로 쓸 만함)
- 이론적 기반: IMPRINT의 부하 예측은 다중자원이론(MRT, Wickens 2008) 기반 — "According to MRT, the capacity of human mental resources is limited … The point where the individual's resources are overloaded is the workload threshold." — [Mitchell & Samms](https://ntrs.nasa.gov/api/citations/20110012092/downloads/20110012092.pdf) [원문확인]

**(b) 실시간 다차원 부하 알고리즘(현장 검증): Heard & Adams / DARPA OFFSET**
- 5개 성분(인지·청각·음성·신체·시각), 성분별 신경망, 인지·청각·신체는 5초마다, 음성은 1초마다 추정 후 5초로 재표본; 시각은 IMPRINT Pro 모델값; "An overall workload model is generated by uniformly aggregating the workload component models." 학습·검증은 IMPRINT Pro 모델 기준. 결과: "The SC's estimated overall workload was only classified as an overload state for 3.2% of the 12,181 usable workload estimates". — [Adams, Hamell & Walker, arXiv 2308.00102](https://arxiv.org/abs/2308.00102) [원문확인]
- 언론 보도에 따르면 같은 프로그램에서 10분마다 자기보고 부하·스트레스·피로를 받고, 최종 연습에서 HRV·자세·발화 속도 센서를 사용. — [Oregon State 보도](https://engineering.oregonstate.edu/all-stories/one-person-can-supervise-swarm-100-robots-study-finds) [스니펫]

**(c) 점유율(utilization)을 실시간 지표로**
- Donmez et al. 2010: 점유율 = 외부 이벤트로 지시된 과업 수행 시간 비율, 수동적 모니터링 시간 제외, 실시간·비침습, 비율척도라 모델에 쓰기 좋음(위 Q1-(f) 인용). — [Donmez et al. 2010](https://dspace.mit.edu/handle/1721.1/87059) [원문확인]

**(d) 주관 척도: NASA-TLX**
- Hart 2006 "NASA-Task Load Index (NASA-TLX); 20 Years Later" (Proc. HFES 50(9):904–908) — 550편 사용 연구 검토. — [Hart 2006 PDF](https://humansystems.arc.nasa.gov/publications/HFES_2006_Paper.pdf) [초록·요약]
- 계산: 가중 TLX = Σ(쌍비교 가중치 × 6개 하위척도 점수) / 15 → 0–100; Raw TLX(RTLX)는 가중 단계 생략(6개 평균), 민감도 비교 결과는 혼재. — [Wikipedia NASA-TLX](https://en.wikipedia.org/wiki/NASA-TLX), [MeasuringU](https://measuringu.com/nasa-tlx/) [2차 요약]
- 해석 기준: Grier 2015/2016 "How High is High? A Meta-Analysis of NASA-TLX Global Workload Scores"(HFES Proc.)가 과업 유형별 백분위 기준을 제공 — [ScienceOpen](https://scienceopen.com/document/vid/561bc725-b469-4a12-9045-edf6407d350b) [서지만]
- SHMR 연구 대부분이 TLX에 의존하나 "questionnaires that seem to show less sensitivity to task changes" — [Rey-Becerra & Wischniewski 2024](https://doi.org/10.54941/ahfe1005460) [원문확인]
- 2026 신규 동향: LLM 에이전트가 과업을 시뮬레이션해 TLX를 사전 예측하는 "Synthetic TLX" — "Synthetic TLX uses AI agents to simulate a human executing the task and forecast the workload before a person even attempts it." — [Kuo et al. 2026, arXiv 2609.12273](https://arxiv.org/abs/2609.12273) [원문확인(초록)]

**(e) 2차 과업: 탐지반응과업(DRT, ISO 17488:2016)**
- 표준 범위: "a detection-response task … mainly intended for assessing the attentional effects of cognitive load", 3가지 변형, 프로토콜·통계는 규정하지 않음; 2022년 재확인(현행). — [ISO 17488:2016](https://www.iso.org/standard/59887.html) [초록·요약]
- 측정법(2차 문헌): 3–5초마다 자극, 손가락 버튼 응답; 반응시간 + 적중률(자극 후 100–2500 ms 내 응답 비율); 2차 과업 없이/있이 비교. — [PMC5855461](https://pmc.ncbi.nlm.nih.gov/articles/PMC5855461) [스니펫 — 수치는 원문 재확인 필요]
- 주의: 초당 1회 이상 수동 입력이 있는 과업에서는 버튼 경쟁 때문에 RT 증가가 인지부하가 아닐 수 있음(표준의 경고, 검색 요약). — [ISO 17488](https://www.iso.org/standard/59887.html) [스니펫]
- 2차 과업으로 자유시간(FT)을 대리측정하는 HRI 전통: Olsen & Goodrich 2003(위 Q1-(b)), Crandall et al. 2005("a measurement methodology, based on a secondary task paradigm"). [원문확인]

**(f) 생리·시선 지표와 실현 가능성**
- Charles & Nixon 2019 (Applied Ergonomics 74:221–232, 58편 체계적 리뷰): "there is no single measure that clearly discriminates mental workload but there is a growing empirical basis"; 과업 유형·부하·(일부) 난이도 구분 가능, 급/완만 변화 민감도는 지표마다 다름. — [Cranfield 저장소](https://dspace.lib.cranfield.ac.uk/handle/1826/14683) [초록·요약]
- Tao et al. 2019 (IJERPH, 91편): 심혈관·안구운동·EEG 지표가 부하와 유의하게 관련된 비율 76% / 66% / 71% — "not universally valid in all task scenarios". — [PMC6696017](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6696017/) [초록·요약]
- 웹캠 시선추적: WebGazer 원 논문 평균 오차 4.17°(재인용), 실험실 웹캠 ~4°(~172 px) vs 적외선 0.5–1°; 학부 연구 3.65°(SD 0.77°), 드리프트 보정 실패; 샘플링 12–15 Hz 보고(약한 근거). — [WebQAmGaze, arXiv 2303.17876](https://arxiv.org/abs/2303.17876), [Utrecht 학위논문](https://studenttheses.uu.nl/handle/20.500.12932/40709), [WebGazer IJCAI16](https://jeffhuang.com/papers/WebGazer_IJCAI16.pdf) [스니펫/초록]

### Inferences
- **해커톤용 실시간 부하 지수 설계(근거 결합)** — 모두 시뮬레이터 이벤트 로그만으로 계산 가능, 센서 불필요:
  1. `U(t) = (최근 W초 중 운용자가 '지시된 과업'(대화창 열림·명령 작성·경보 확인)에 쓴 시간) / W` (W=60–300 s). 경고: U>0.70 과부하, U<0.40 여력(추가 할당 가능) — Cummings/Guerlain, Donmez.
  2. `VACP(t) = Σ_{진행 중 과업} (V+A+C+P)`; 채널별 합 ≥8 또는 총합 ≥60 경고 — Keller/Bierbaum, IMPRINT. 과업 유형(예: 영상 식별 = V 7.0(scan) + C 6.8 + P 2.2, 경보 확인 = V 1.0 + A 1.0 + C 3.7 + P 2.2)을 표에서 골라 상수로 둔다(**값 배정은 팀의 판단, 문헌 값 자체는 위 표**).
  3. `WT` 분해: WTQ(큐 대기), WTSA(문제 존재 + 운용자 무활동) → `FO_hat = NT/(IT+WT)+1`.
  4. 검증용: DRT(브라우저 화면 가장자리 점등 3–5 s 간격, Space키, 100–2500 ms 적중) 반응시간 증가 = 여유용량 감소; 실행 후 RTLX 6문항(2분).
- 위 1–3은 "모델 기반 추정", 4는 "행동 측정"이므로, 데모에서 두 곡선이 같이 움직이는 것을 보여주면 SUPPORTY의 단순 규칙 대비 **타당성(validity) 주장**이 생긴다.
- 웹캠 시선은 오차 4°면 약 60 cm 거리에서 화면상 ~4 cm 수준(작성자 계산)이라 비히클 아이콘 단위 응시 판정은 불가, 화면 사분면/패널 단위 "어디를 오래 안 봤나"(방치 영역) 정도만 현실적이다. 시간 대비 효용이 낮아 우선순위 낮음.

### Gaps
- Grier(2015) TLX 백분위 기준값 자체는 확보 못함. 인터넷에 도는 "0–9 낮음…80–100 매우 높음" 5구간은 출처 불명이라 인용하지 않음.
- 웹캠 기반 동공 측정·rPPG(원격 광용적맥파) HRV의 정확도는 조사하지 못함.
- ISO 17488 원문(유료)의 정확한 적중 창(100–2500 ms)과 자극 간격은 2차 문헌으로만 확인.
- VACP 척도 값은 판본마다 descriptor 표기가 다름(예: 3.7을 "Identify"로 표기하는 판). 원 McCracken & Aldrich(1984) 보고서는 직접 확인 못함.

## Q5. 군 특화 연구: AFRL IMPACT, 미 육군 ARL, 해군 다중 USV, CCA 조종사 부하, DARPA OFFSET, 우크라이나 "드론 1대당 운용자 1명" 병목

### Takeaway
군 연구는 공통적으로 **플레이/의도 기반 고수준 지휘 + 자율 자산할당**으로 1:N을 달성하려 하며(IMPACT 1:12 시뮬, OFFSET 1:100+ 실외), 동시에 과부하는 '빈도'로 관리(OFFSET 3.2%)한다. 우크라이나에서는 학술 문헌보다 보도·업계 발언이 대부분이며, 장거리 비행 구간을 자율에 맡겨 "조종사 1명–폭격 드론 최대 5대" 같은 실전 사례가 보고된다.

### Cited Findings
- **AFRL IMPACT**: 1차년도 평가 — 7명이 기지방어 임무에서 UxV 6대 관리, 전체 시스템과 play calling·자율·피드백·테스트베드 모두 긍정 평가, 입력 모달리티(마우스/키보드, 터치, 음성) 객관 자료 수집. — [IMPACT initial evaluation 목록](https://independent.academia.edu/DougLange) [초록·요약]. Draper et al. 2017: 단일 운용자 + 이종 UV, "a dozen simulated vehicles performing base defense tasks". — [CORE Scholar](https://corescholar.libraries.wright.edu/isap_2017/85) [초록·요약]. 박사논문(Wright State, 2017): 12대 합성 환경, 8명 × 1시간 4회, IMPACT HAI vs 기준선 — "participants both preferred and performed better with the IMPACT HAI as compared to the Baseline HAI." — [CORE Scholar etd 1722](https://corescholar.libraries.wright.edu/etd_all/1722) [초록·요약]
- **NATO HFM-170 (2008–2011, 보고서 2012)** "Supervisory Control of Multiple Uninhabited Systems – Methodologies and Enabling Human-Robot Interface Technologies": 8개국 15개 기술시연; 주제에 "Flexible (adaptive) level of automation. Optimization of human/vehicle ratio. Heterogeneous systems." 서론: "Given the possibility that future operators may control multiple UVs simultaneously, additional human factors challenges will be to maintain situation awareness, a reasonable workload level, and high system performance and safety across several managed assets." — [DTIC ADA591805](https://apps.dtic.mil/sti/pdfs/ADA591805.pdf), [서론 장(Draper & van Breda)](https://publications.tno.nl/publication/101099/V0HB49/draper-2012-introduction.pdf) [서론 원문확인]
- **미 육군 ARL**: RoboLeader(4 vs 8 로봇) 결과(Q1 표), Chen·Barnes 계열 리뷰(Q2), ARL 인간성능모델링(IMPRINT) 부하 문턱 실무와 "운용자·구간별 문턱" 방식(Q4, [Mitchell & Samms](https://ntrs.nasa.gov/api/citations/20110012092/downloads/20110012092.pdf)).
- **해군/해양**: SSC Pacific의 MOCU 개선으로 1인 다중 USV 동시 운용 지원, 시뮬레이터 사용성 평가에서 수행 시간·오류 유의 감소, 그러나 "improvements in on-board sensor capabilities and obstacle avoidance systems may still be necessary". — [DTIC ADA586656](https://apps.dtic.mil/sti/pdfs/ADA586656.pdf) [스니펫]. 미 해군 시연 발언: "When a single operator can command air, surface, and subsurface autonomous vehicles simultaneously, we create a force multiplier that dramatically expands our operational footprint without expanding our personnel requirements" — [DVIDS](https://www.dvidshub.net/news/500074/naval-engineers-control-unmanned-vessels-across-countries-mission-operation-center) [스니펫]. Cummings & Guerlain 2007의 비행 중 미사일 재표적화 과업(해군 맥락으로 보이나 토마호크 명시는 미확인).
- **CCA(협동전투기) 조종사 부하**: 고충실 MUM-T 시뮬레이터에서 조종사가 자기 전투기를 몰며 CCA 4대 팀을 감독, CCA 유사성(similarity)에 따라 자기보고 정신부하가 변하지 않음; 숙련 피험자 부족으로 베이지안 분석. — [SAGE, DOI 10.1177/10711813251366297](https://doi.org/10.1177/10711813251366297) [스니펫]. Eglin의 F-15E·F-16 + XQ-58 2대 시험 목적이 "pilot workload and situational awareness" 이해 — [Aerospace America](https://aerospaceamerica.aiaa.org/institute/air-force-pushes-collaborative-combat-aircraft-from-concept-to-combat-readiness/) [스니펫, 결과 미공개]. 조종사당 드론 최대 5대 구상 — [TWZ](https://www.twz.com/how-fighter-jet-pilots-could-stop-worrying-and-learn-to-love-the-drone) [스니펫]
- **DARPA OFFSET (CCAST 팀)**: 최대 ~200 하드웨어 UAV/UGV + 250 시뮬 비히클 지원, 최종 FX-6(2021-11, Fort Campbell)에서 스웜 지휘관 2명 평가; "While the swarm commander's workload estimates did cross the overload threshold frequently, the swarm commander was able to successfully complete the missions". 과부하 판정 3.2%(12,181 추정치 중). — [Adams et al. arXiv 2308.00102](https://arxiv.org/abs/2308.00102) [원문확인] (게재: Field Robotics 2023 채택 / IEEE T-FR 2024 표기 혼재)
- **우크라이나**: Lasar's Group은 경로계획 소프트웨어로 "up to five bombers"를 조종사 1명에 묶고, 조종사는 타격 정렬에 "a few minutes"만 접속; 표적 35–60 km, 편도 25분 이상; 이유는 인력 부족. Sine Engineering CEO: "70 to 80% of the need for autonomy right now is reconnaissance." (기사에 advertorial 표기) — [Euromaidan Press 2026-08-22](https://euromaidanpress.com/2026/08/22/one-pilot-five-bombers-ukraines-lasars-group-ties-whole-raid-to-single-operator-to-save-manpower/) [원문(기사) 확인]. 요격드론은 하루 최대 1,000대 생산 가능하나 운용자 부족(젤렌스키 발언) — [LIGA.net](https://news.liga.net/en/amp/politics/news/ukraine-produces-up-to-1000-interceptors-per-day-but-there-are-not-enough-operators-zelensky) [스니펫]. 한 운용자가 동시에 다룰 수 있는 드론 수는 경험에 달려 있다는 논평 — [Strategypage 2025-05](https://www.strategypage.com/htmw/htlead/2025050112031.aspx) [스니펫]. 여단 UAV 대대: "Right now, we still have crews or individuals controlling one drone." — [Kyiv Post](https://www.kyivpost.com/post/38057) [스니펫]

### Inferences
- 우크라이나 사례(장거리 비행은 자율, 사람은 '타격 정렬 몇 분'만)는 정확히 Fan-out 모델의 "NT를 늘리고 IT를 짧게"와 같은 구조다: 편도 25분(NT 큼) / 정렬 수 분(IT) → 이론상 FO가 5를 넘을 수 있으며, 실제 한계는 **동시에 몰리는 정렬 시점(WTQ)** 이다. 데모 시나리오에 "도착 시각이 겹치는 이벤트 → 큐 대기 발생 → 자동 시간차(TOT 지연) 제안"을 넣으면 실전 맥락과 모델이 맞물린다(MAUVE의 TOT 지연 요청 기능과 같은 발상, Cummings & Mitchell 2008).
- IMPACT·OFFSET 모두 "플레이 + 자율 자산할당 + 예외 시 개입"이라는 같은 패턴이므로, 해커톤 데모가 이 패턴을 따르면 "검증된 군 연구 방향과 정합"이라고 말할 수 있다.

### Gaps
- IMPACT의 정량 부하·성능 수치(TLX 값, 과업 시간)와 AFRL 기술보고서 원문은 확보하지 못함.
- 최근(2022–2026) 미 해군 다중 USV 감독 피어리뷰 연구는 찾지 못함.
- CCA 부하의 정량 결과(공개 논문 수치), 우크라이나 운용 경험을 다룬 **학술**(피어리뷰) 문헌은 찾지 못함 — 대부분 보도·업계 발언.
- NATO HFM-170 본문(15개 시연별 결과, 감독제어 프레임워크), HFM-247 관련 보고서는 다운로드 실패(STO 사이트 HTML 응답)로 본문 미확인.

## Q6. 심사위원이 받아들일 "임무 성공 + 인력 절감" 지표

### Takeaway
학계 표준은 단일 점수가 아니라 **지표 클래스 묶음**이다: 임무 효과(성공률·시간), 자율체 행동 효율(NT), 인간 행동 효율(IT·점유율), 주의 배분 효율(WTSA·전환 시간), 인간 상태 선행지표(부하·SA·신뢰). 인력 절감은 **"같은 임무 성공률에서 운용자 1명당 비히클 수(또는 필요한 운용자 수)"**로 표현하는 것이 Fan-out 문헌과 일치한다.

### Cited Findings
- Pina, Donmez & Cummings (MIT HAL2008-04) 5개 지표 클래스: "mission effectiveness, autonomous platform behavior efficiency, human behavior efficiency, human behavior precursors, and collaborative metrics"; 권고 "At a minimum, one metric from each class should be used to provide a multi-dimensional assessment of the human-automation team." — [MIT DSpace 1721.1/46743](https://dspace.mit.edu/handle/1721.1/46743) [초록·요약]
- 결과 지표만으로는 부족: "mission effectiveness fails to provide insights into the process that leads to the final mission-related output, and a suboptimal process can still lead to a successful completion of a mission." (Donmez, Pina & Cummings) — [MIT DSpace 1721.1/90286](https://dspace.mit.edu/handle/1721.1/90286) [스니펫]
- Crandall & Cummings 2007: 좋은 지표 집합의 조건 — "First, it should contain the key performance parameters of the system. Second, it should identify the limitations of the agents in the system. Third, it should have predictive power." 클래스: Interaction Efficiency(IE: IT 등), Neglect Efficiency(NE: NT 등), Attention Allocation Efficiency(AAE: 전역 SA, WTSA, 전환 시간). FO 예측 4가지 방법을 실측 FO(4–6대)와 비교. — [Crandall & Cummings 2007](https://faculty.cs.byu.edu/~crandall/papers/CrandallCummingsTRO2007_Final.pdf) [원문확인]
- 인력 절감의 문제 정의(원문): "Current UV platforms require multiple operators to control a single UV. However, this need for significant manpower is expensive and often ineffective. As a result, it is desirable to invert this ratio so that a few operators can effectively control many UVs in order to (a) reduce costs, (b) extend human capabilities, and (c) improve human-UV system (HUVS) effectiveness." — [Crandall & Cummings 2008, HAL2008-05](https://dspace.mit.edu/handle/1721.1/46744) [원문확인]
- Fan-out plateau = "adding more robots will not increase task effectiveness"인 지점이 1명당 최대 운용 수의 실증 정의. — [Olsen & Wood 2004](https://hci.rwth-aachen.de/materials/conferences/CHI2004/1p231.pdf) [원문확인]
- 임무 성과 지표 예(실험에서 실제 쓰인 것): Cummings & Mitchell — 목표 TOT 준수, 무장/발사 창, 위협 구역 회피, 대기시간(WTI/WTQ/WTSA) [원문확인]; Donmez — 점수, 탐색과업 대기시간, 점유율 (세 변수 간 상관: utilization/score ρ=−.25, utilization/wait ρ=.50, score/wait ρ=−.58) — [Donmez et al. 2010](https://dspace.mit.edu/handle/1721.1/87059) [원문확인]; Crandall & Cummings 2007 — 수집 물체 수, 잃은 로봇 수 [원문확인]; Wang 2009 — 발견 피해자 수 [초록]; Andrews 2020 — 생존 적 표적 수 + 시간가중 VACP [원문확인]
- 팀 vs 단독 비교 설계: Porat et al. 2016은 같은 대수를 1명 vs 팀이 운용하는 조건을 비교 — "In MOMU settings, when the tasks are similar or when areas of interest overlap, one operator seems to have an advantage over a team … However, in all other cases, a team was advantageous over a single operator." — [Porat et al. 2016](https://doi.org/10.3389/fpsyg.2016.00568) [원문확인]
- OFFSET은 "과부하 시간 비율"(3.2%)과 "임무 완수"를 함께 보고 — [Adams et al.](https://arxiv.org/abs/2308.00102) [원문확인]
- 2026 시뮬레이션 연구(3인 팀, 반자율 UAV 3–30대): 90% 완수 기준으로 동종 할당 최대 9대, 이종 할당 11대 — "heterogeneous"는 비히클 종류가 아닌 할당 전략 의미. — [ScienceDirect S0169814126001046](https://www.sciencedirect.com/science/article/abs/pii/S0169814126001046) [스니펫, 403으로 원문 미확인]

### Inferences
- **24시간 데모용 지표 세트(각 클래스에서 1개 이상, Pina et al. 권고 충족)**:
  | 클래스 | 지표 | 데모 표시 |
  |---|---|---|
  | 임무 효과 | 마감 내 처리된 임무 이벤트 비율(%) · 치명 이벤트 대응시간(중앙값 s) · 놓친 이벤트 수 | before/after 막대 |
  | 자율체 효율 | 평균 NT(유형별) | 표 |
  | 인간 행동 효율 | 평균 IT, 점유율 U(t) 곡선, 클릭/명령 수 | 실시간 게이지(70% 선) |
  | 주의 배분 효율 | WTQ, WTSA(초), 경보/10분 | 실시간 + 합계 |
  | 선행지표 | VACP 합, DRT 반응시간, 사후 RTLX | 실시간 + 사후 |
  | 인력 절감 | `FO_hat = NT/(IT+WT)+1`, 필요 운용자 수 = ceil(N/FO_hat), 같은 성공률(예: ≥90%)에서 1인당 비히클 수 | 헤드라인 숫자 |
- 헤드라인 문장 형태 예: "같은 시나리오(시드 고정)에서 임무 성공률 ≥90%를 유지하며, 기준선 UI는 1인당 2대(FO_hat≈2)였고 제안 UI는 1인당 6대(FO_hat≈6) → 6대 편대 기준 필요 인원 3명→1명". (**숫자는 예시일 뿐 실측 필요**) 실험 시 Olsen & Wood의 교훈대로 피험자 동기(점수·경쟁)를 부여해야 fan-out이 과소측정되지 않는다.
- 공정 비교를 위해 기준선과 제안안에 **같은 시나리오 시드·같은 이벤트 도착률**을 쓰고, 운용자 수를 늘려가며(1명/2명) 성공률 곡선을 그리면 "같은 성공률에서 필요 인원"을 곡선 교차점으로 보일 수 있다(작성자 제안).

### Gaps
- 심사위원(D4D × EDTH)이 실제로 어떤 지표를 선호하는지에 대한 공개 자료는 이 조사 범위에서 찾지 못함(다른 노트 `supporty-and-oss.md` 등 참고 필요).
- Pina et al. HAL2008-04 원문의 클래스별 세부 지표 목록은 직접 확인하지 못함(초록 수준).
- "같은 성공률에서 인력 절감"을 공식 지표로 쓴 군 평가 보고서(예: 운용자/비히클 비율 요구조건 문서)는 찾지 못함.
