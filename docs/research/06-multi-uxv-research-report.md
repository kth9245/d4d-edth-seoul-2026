# 조종 대신 역할을 맡기고, 바닥을 막아라

증거는 팀 방향의 핵심 구조를 강하게 받쳐 준다. 운용자는 기체를 조종하지 않고 미리 정의된 '플레이'로 역할만 맡긴다. 시스템은 그 역할을 기체에 연결하고, 기체가 빠지면 다른 기체에 다시 연결한다. 공개 기록상 1인이 3대를 넘겨 운용한 검증 사례는 모두 이 방식을 썼다. AFRL IMPACT(시뮬레이션 12대), DARPA OFFSET(이종 100대 이상), 영국 Dstl 2025 시험(이종 3대)이 그 예다. "숙련 운용자도 직접 통제는 3대까지"라는 연구(Porat 2016)를 보면 T1-1이 말하는 '3대 이상'은 사람이 직접 조종할 수 있는 한계를 넘는 지점이다. 수요도 같은 방향을 가리킨다. 미 육군은 2026년 8월 플랫폼마다 따로 노는("stove-piped") 조종기를 대신할 "policy-based" 공통 통제기를 공모했다. DIU와 DAWG는 지휘관 의도를 플랫폼별 "playbook"에 연결하는, 특정 업체에 묶이지 않는 오케스트레이터에 1억 달러 상금을 걸었다. 한국 육군 유무인 분대는 아직 운용요원 4명이 플랫폼 4종을 맡는, 1:1에 가까운 단계다.

빈자리는 두 곳이다. 첫째, 이번 조사에서 운용자 인지부하를 정량 측정해 공개한 업체는 하나도 찾지 못했다. 둘째, 여러 기체를 한 콘솔로 지휘할 때의 공격면과 사고 경로가 실제로 존재한다. MAVLink는 기본 설정에서 인증이 없어 PX4에서 CVSS 9.8 원격 셸 취약점(CVE-2026-1579)이 나왔다. 북한 GPS 교란은 2010~2024년 7,270건의 장애를 냈다. 2012년 인천에서는 GPS를 잃은 뒤 운용자가 잘못 대응해 무인헬기가 지상통제소 차량을 들이받았고 1명이 숨졌다.

그래서 **"측정되는 부하"와 "사람을 포함한 모든 명령원에 똑같이 걸리는 안전 바닥"**이 미군·업계·대드론·해양 심사위원 모두 앞에서 방어할 수 있는 차별점이다. 이 조합은 SUPPORTY와도 '연출 대 계산·측정·보장'으로 확실히 갈린다. SUPPORTY는 실물 하드웨어와 스토리로 상을 받았지만, 코드를 보면 임무 배정은 랜덤이었고 인지부하 경고는 `pend>=4` 스크립트였으며 Starlink 전환 코드는 한 줄도 없었다.

다만 증거는 세 곳을 고치라고 요구한다.
- **플레이 수를 줄인다.** 유연한 위임 인터페이스의 이점은 로봇 8대에서 사라졌다. 플레이 수와 파라미터를 작게 묶어야 한다.
- **재연결 대상을 바꾼다.** GPS 교란은 한 구역의 모든 기체를 동시에 친다. 같은 구역 기체로 역할을 넘기면 함께 실패한다. 교란에 강한 다른 도메인 기체로 넘기고, 동시에 쏟아지는 경보를 한 건으로 묶어야 한다.
- **2인 승인을 축소한다.** 2인 승인은 '운용자 1명'이라는 전제와 충돌한다. 드물게 쓰는 고위험 플레이에만 지휘관 토큰이나 독립 안전 커널을 두 번째 키로 쓰는 형태로 줄여야 한다.

*근거와 표기: 원 노트는 `knowledge/inbox/2026-10-08-multi-uxv-research/`의 7개 파일(products-market, military-programs, cognitive-load-science, field-operations, cyber-ew-threats, safety-floor-mechanisms, supporty-and-oss)이다. 모든 URL 접근일은 2026-10-08이다. 본문의 (회사 주장)·(교전국 주장)·(검색 스니펫)·(미검증)·(원문 미확인) 표기는 원 노트의 신뢰도 표시를 그대로 옮긴 것이다. 지난 대회 수상작 공통점은 `03-d4d-showcase-winners.md`, 대회 요구사항과 심사 배점은 `05-t1-1-brief.md`에 있다. 이 문서는 그 둘을 반복하지 않고 T1-1 증거만 종합한다.*

## 1인이 3대를 넘긴 검증 사례는 모두 '플레이 호출'이었다

군 연구의 흐름을 따라가 보면 1인 다수 운용이 어떤 조건에서 성립했는지가 분명하다.
- **DARPA CODE(2019):** RQ-23 6대가 통신과 GPS 없이 임무를 수행했다. PM은 "one operator can command multiple aircraft"라고 말했지만, 실제로 몇 명이 운용했는지는 공개되지 않았다([DARPA](https://www.darpa.mil/news/2019/code-success)).
- **AFRL IMPACT:** 운용자는 **"plays"라는 고수준 명령**으로 지휘하고, 자율 기능이 자산 할당·경로 계획·방책(COA) 추천을 맡았다. 이 구조로 **시뮬레이션 차량 12대**의 기지방호를 관리했다([Draper et al. 2017](https://corescholar.libraries.wright.edu/isap_2017/85)).
- **DARPA OFFSET(2021-11, Fort Campbell 최종 실험):** 스웜 지휘관이 VR 인터페이스로 **UAV 최대 139대, UGV 44대, 가상 차량 최대 100대**의 이종 스웜을 운용했다. 과부하로 판정된 비율은 12,181개 추정치 중 **3.2%**였다([Adams et al., arXiv 2308.00102](https://ar5iv.labs.arxiv.org/html/2308.00102)). 지휘 수단은 개별 조종이 아니라 "digital library"에 담긴 전술의 호출이었다. 전술을 부르면 디스패처가 "can automatically select and assign vehicles with the necessary capabilities that are proximally close"([army.mil](https://www.army.mil/article/252556), [arXiv](https://arxiv.org/abs/2308.00102)). 이것이 팀이 말하는 '역할 결합'의 직계 선례다.
- **영국 Dstl(2025):** 유인 차량 안의 운용자 1명이 자동표적인식(ATR)의 도움을 받아 **UAV 1대와 UGV 2대**를 지휘한 시험을 "UK first"로 발표했다. T1-1 문제 정의와 거의 같은 형태다([GOV.UK](https://www.gov.uk/government/news/successful-trial-paves-the-way-for-improved-reconnaissance-on-army-operations)).

OFFSET 수치를 인용할 때는 주의할 점이 두 가지 있다. 첫째, 같은 army.mil 기사는 운용 형태를 "a single operator working alongside a swarm commander"라고 묘사했다. 실제로는 2인 팀이었다. 둘째, 논문 초록은 부하가 "did cross the overload threshold frequently"라고도 썼다. 3.2%는 시간 비율이라 '빈번히 넘었다'와 측정 단위가 다르다. IEEE Spectrum의 요약 수치(드론 110대, 지상 차량 30대, 가상 50대)도 논문 수치와 다르다([IEEE Spectrum](https://spectrum.ieee.org/darpa-robot)). 미군 장교 앞에서는 "목표는 250대, 실증은 2인 팀으로 100대 이상, 과부하는 시간의 3.2%"라고 나눠 말해야 신뢰를 잃지 않는다.

| 사례 | 형상 | 운용자 : 기체 | 성격 | 출처 |
|---|---|---|---|---|
| Porat et al. 2016 | 이스라엘 UAS 숙련자 연구 종합 | 직접 통제 최대 3, 감독 최대 15 | 학술 리뷰 | [PMC4878290](https://pmc.ncbi.nlm.nih.gov/articles/PMC4878290/) |
| 미 육군 SCORCH | 아파치 사수의 UAS 통제 | 1 : 최대 3 | 설계 목표 | [Warrior Maven](https://warriormaven.com/land/army-technology-accelerates-helicopter-drone-attacks) |
| DARPA CODE (2019) | RQ-23 실기 6 + 가상 14 | 운용 인원 미공개 | 시연 | [DARPA](https://www.darpa.mil/news/2019/code-success) |
| AFRL IMPACT (2017) | 이종 UxV 기지방호, play 명령 | 1 : 12 (시뮬) | 연구 | [CORE Scholar](https://corescholar.libraries.wright.edu/isap_2017/85) |
| DARPA OFFSET FX-6 (2021) | UAV·UGV 이종 스웜, 전술 라이브러리 | 지휘관+보조 : 100+ | 실외 실험 | [arXiv 2308.00102](https://arxiv.org/abs/2308.00102) |
| 영국 Dstl (2025) | UAV 1 + UGV 2, ATR | 1 : 3 | 공식 시험 | [GOV.UK](https://www.gov.uk/government/news/successful-trial-paves-the-way-for-improved-reconnaissance-on-army-operations) |
| 호주 MQ-28 + E-7A (2025) | 실기 2 + 가상 1 | 1 : 3 | 공식 시험 | [The War Zone](https://twz.com/air/mq-28-ghost-bats-controlled-from-e-7-wedgetail-in-loyal-wingman-test) |
| Auterion Nemyx (2026-01) | FPV 3대, 표적 3개 실사격 | 1 : 3 | 시연(회사 해석 "1:N") | [Inside Unmanned Systems](https://insideunmannedsystems.com/auterion-demonstrates-one-operator-drone-swarm-strike-in-u-s-live-fire-test/) |
| Swarmer (우크라이나, 2025) | 정찰 1 + 폭격 2, 최대 8 | 3명 : 3~8 (기존 9명) | 실전(회사·익명 장교) | [Ukrainska Pravda/WSJ](https://www.pravda.com.ua/eng/news/2025/09/03/7529154/) |
| Skydio (FAA 승인) | 공공안전 X10 도크 | PIC 1 : 최대 4 | 민간 규제 승인 | [DroneXL](https://dronexl.co/2026/03/28/skydio-faa-multi-drone-bvlos-approval/) |
| 한국 육군 유무인 분대 (2026) | 드론·로봇개·무인차량·자율차 | 운용요원 4 : 플랫폼 4종 | 실증 편성 | [뉴스스페이스](https://www.newsspace.kr/news/article.html?no=15018) |

### 3대가 벽인 이유는 명령보다 '알아차리기'에 있다

Porat 등은 이스라엘 UAS 연구를 종합해 두 가지 결론을 냈다. 숙련 운용자는 "can supervise up to 15 UASs efficiently using moderate levels of automation"하지만, 임무·탑재체 관리 수준의 통제는 "up to three systems"까지라는 것이다. 여러 대를 맡으려면 운용자가 "interact primarily at the outermost loop via a mission and payload manager"해야 한다고도 정리했다([Porat et al. 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC4878290/)). 실험실 수치도 비슷한 범위에 모인다. 시뮬 로봇은 6대에서 효과가 정체됐다([Crandall & Cummings 2007](https://faculty.cs.byu.edu/~crandall/papers/CrandallCummingsTRO2007_Final.pdf)). 수색 과업에서 직접 통제의 한계는 8~12대였다([Wang et al. 2009](https://www.ri.cmu.edu/?p=10283), 초록). 로봇이 4대에서 8대로 늘자 표적 탐지와 상황인식이 유의하게 나빠졌다([Chen et al. 2010](https://stars.library.ucf.edu/scopus2010/1143), 초록).

왜 이런 벽이 생기는지는 Fan-out 모델이 설명한다. 1인이 감당할 수 있는 대수는 다음 식으로 정해진다.

`FO = NT/(IT+WT) + 1`

여기서 NT는 기체를 방치해도 되는 시간, IT는 운용자가 한 대와 상호작용하는 시간, WT는 대기시간이다. Cummings와 Mitchell은 이 대기시간을 모델에 넣자 1인 상한이 **36~67% 떨어진다**는 것을 보였다. 대기시간 중 가장 큰 부분은 상황인식 상실 대기(WTSA)였다. WTSA는 기체에 문제가 생겼는데 운용자가 알아차리지 못하고 아무것도 하지 않는 시간이다. 이것이 전체 대기의 **63~72%**를 차지했고, 저자들은 "operators clearly struggled with the multiple vehicle management task, driven primarily by WTSA"라고 썼다([Cummings & Mitchell 2008](https://dspace.mit.edu/handle/1721.1/90280)).

이 결과는 팀 설계에 직접 연결된다. 1인 다수 운용에서 가장 큰 손실은 명령을 입력하는 시간이 아니다. 아무도 문제를 보지 못한 채 흘러가는 시간이다. 기체가 빠지면 역할을 자동으로 다시 연결하는 기능과 경보 예산은 정확히 이 항을 줄인다. 같은 이유로 Olsen과 Wood는 IT를 로그로 측정해 UI 개선 전후를 비교했다. 화면 해상도를 낮춰 스크롤이 생기자 상호작용 노력이 25~46% 늘었다([Olsen & Wood 2004](https://hci.rwth-aachen.de/materials/conferences/CHI2004/1p231.pdf)).

### 70% 점유율 문턱은 쓸 만하지만, 과소부하도 함께 보여야 한다

팀이 쓰려는 '운용자 busy-time 70%' 문턱의 출처는 Cummings와 Guerlain(2007)이다. 이 논문은 "a 70% utilization (percentage busy time) score is a valid threshold for predicting significant performance decay"라고 제안했다. 다만 이번 조사에서는 원문을 열지 못했고 제3자 요약으로만 확인했다([paperguide 요약](https://paperguide.ai/papers/09b4e035-e943-4ea4-ac20-c3d30f2b43ff/)). 대신 원문을 확인한 두 논문이 이 문턱을 재인용한다. 하나는 Cummings와 Mitchell 2008의 "operators working beyond 70% utilization experience significantly degraded performance"다. 다른 하나는 Donmez 등 2010의 실측이다.

Donmez 등은 74명이 RESCHU 시뮬레이터에서 이종 차량 5대를 운용하게 했다. 점유율 **60~70% 구간에서 점수가 가장 높았고** 80~90% 구간은 70~80%보다 낮았다. 그런데 30~40%의 과소부하 구간도 60~70%보다 유의하게 낮았다([Donmez et al. 2010](https://dspace.mit.edu/handle/1721.1/87059)). 같은 논문은 두 가지 한계를 스스로 밝혔다. 점유율에는 수동적 모니터링 시간이 들어가지 않는다. 또 보고된 값은 사후 집계라 "not accurate as an instantaneous measure of workload"다.

그래서 데모의 busy-time은 이렇게 정의해야 방어할 수 있다.
- **분자는 지시된 과업 시간이다.** 경보 확인, 승인, 명령 작성처럼 외부 이벤트가 요구한 과업에 쓴 시간만 센다.
- **슬라이딩 창으로 계산한다.** 최근 60~300초 창에서 계산한다.
- **두 기준선을 함께 그린다.** 과부하 기준인 70% 선과, 여력이 있어 기체를 더 맡길 수 있다는 40% 미만 밴드를 같이 표시한다.

### 플레이는 작게, 실행은 기본적으로 '동의'를 받는다

위임과 플레이북 연구는 팀 방향을 지지하지만 동시에 한계도 그어 준다. Miller와 Parasuraman은 사람 사이의 위임을 모델로 한 플레이북식 인터페이스를 제안했다. 자동화 수준(LOA)을 고정된 단계가 아니라 '과업별 역할·권한의 구성'으로 다시 정의했다([Miller & Parasuraman 2007](https://swov.nl/en/publicatie/designing-flexible-interaction-between-humans-and-automation-delegation-interfaces), 초록). 그러나 RoboFlag 실험에서는 "Performance was superior with flexible interfaces for four robots, but this benefit was eliminated when eight robots had to be supervised"였다. 연구진은 그 원인을 "the greater workload demand imposed by full flexibility"로 봤다([Furukawa 2005](https://www.scitepress.org/Papers/2005/11907/11907.pdf)). 플레이 라이브러리와 파라미터 공간이 커질수록 운용자가 고르는 일 자체가 부하가 된다는 뜻이다. 팀의 '허용 목록 플레이와 범위가 제한된 파라미터'는 보안 장치이면서 인지부하 장치이기도 하다.

실행 방식에 대해서는 Ruff 등(2002)의 결과가 있다. 운용자가 실행 전에 승인하는 management-by-consent가, 일정 시간 안에 거부하지 않으면 실행되는 management-by-exception보다 우수했다. 최대 4대를 다룰 때는 자동화 수준을 올리면 오히려 성능이 나빠질 수 있었다([Porat et al. 재인용](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2016.00568/epub)). 이 결과는 팀의 "탐지는 보고 단계를 거치고 대응은 운용자가 고른다"는 설계를 정당화한다. 동시에 이벤트가 몰릴 때는 적응형 자동화가 필요하다는 점도 보여 준다. Parasuraman 등은 운용자 수행이 문턱 아래로 떨어질 때만 보조를 켜는 적응형 자동화로 변화 탐지와 상황인식을 높이고 부하를 낮췄다([GMU HAI Lab](https://humanfactors.gmu.edu/archives/defunct-labs/research), 초록).

다만 자동화 편향은 연습으로 사라지지 않는다. "Automation complacency is found in both naive and expert participants and cannot be overcome with simple practice"([Parasuraman & Manzey 2010](https://depositonce.tu-berlin.de/items/0c787d91-6021-480b-a333-009e0d1d0092/full), 초록). 예외 모드를 켤 때는 자동 승인된 건 중 틀린 건의 비율을 함께 보여 주는 편이 정직하다.

'결정 수 대 수동 명령 수' 지표에는 정량 근거가 있다. 유무인 협업 IMPRINT 모델에서 조종사 과업의 부하 합(VACP)은 고수준 명령 6.6, 중수준 7.0, 저수준 7.3이었다. 부하 60 이상은 포화 근처로 봤다([Andrews et al., WSC 2020](https://informs-sim.org/wsc20papers/014.pdf)).

### 이종성 자체보다 유형별 방치·상호작용 시간이 중요하다

'이종 편대는 부하를 높인다'는 통념도 실험 결과와 맞지 않는다. Donmez 실험에서는 이종성이 높아질수록 방치 시간이 길어지고 상호작용이 짧아졌다. 점수는 중간 이종도 구성이 가장 높았다([Donmez et al. 2010](https://dspace.mit.edu/handle/1721.1/87059)). Nehme 등은 남는 인지 자원이 있었는데도 주의를 잘못 배분한 운용자가 성능이 나빴다는 결과를 보고했다. 그래서 "directed decision support that makes it clear to the operator what tasks are the most critical"이 필요하다고 결론지었다([Nehme et al. 2008](https://dspace.mit.edu/handle/1721.1/90279)). 시스템이 '지금 가장 중요한 결정 1건'을 앞에 띄우는 것이 기체 수를 늘리는 것보다 더 중요하다는 뜻이다.

2026년 연구도 주목할 만하다. 스웜 크기가 조금 줄면 부하가 높은 상태로 남는 '부하 잔류'가 관찰됐다([Hunt et al. 2026](https://arxiv.org/abs/2604.21707), AHFE 채택 preprint). 기체가 이탈하는 순간 운용자 부하가 바로 내려가지 않는다는 뜻이고, 자동 재연결의 가치를 하나 더 보탠다.

경보 예산에는 산업 표준을 끌어올 수 있다. EEMUA 191은 "less than one alarm per 10 minutes"를 "very likely to be acceptable"로, 이상 발생 직후 "less than ten alarms in 10 minutes"를 "should be manageable, but may be difficult"로 본다([Control Global](https://www.controlglobal.com/protect/safety-instrumented-systems/article/11382017/alarm-management-asm-alarm-management-guidelines-and-isa-182-how-do-they-stack-up-control-global)). 10분에 10건을 넘으면 경보 홍수로 분류하는 관행도 있다([Emerson](https://d1-live.emerson.com/documents/automation/article-alarm-management-by-numbers-deltav-en-38292.pdf), 검색 스니펫). 원 표준은 유료라 직접 보지 못했으므로, 발표에서는 "산업 경보관리 벤치마크"라고 표현하는 편이 안전하다.

## 미 육군과 DIU는 지금 벤더 중립 '정책 기반 지휘층'을 사려 한다

미군의 2024~2026년 공통 문제의식은 T1-1 문제 정의와 거의 같은 문장으로 쓰여 있다. 육군 RCCTO 국장 Rasch 중장은 **"Today, everything has its own controller."**라고 말했다. 그는 HMIF(인간-기계 통합 편성)를 2027년에 처음 배치하겠다고 했다. 1단계에서는 지상·공중 드론 공통 통제기를 만들되 원격조종 인력이 오히려 늘고, 2단계에서 그 인원을 줄인다는 계획을 밝혔다. 같은 자리에서 "We don't want a robot wandering off the battlefield."라고도 했다([Breaking Defense, 2025-04](https://breakingdefense.com/2025/04/army-eyeing-first-human-machine-integrated-formations-in-2027-common-controller-for-robotics/)).

2026년 8월 13일 육군 공모는 더 직접적이다. 기체가 아니라 "controllers and human-machine interfaces for Group 1-3 UAS, Launched Effects and Unmanned Ground Vehicles"를 구한다. 문제는 **"disparate, stove-piped control systems prevents soldiers from operating multiple robotic and autonomous systems as an integrated team"**으로 정의됐다. 요구하는 통제 특성은 "asymmetric, distributed, intelligent, intermodal, **policy-based** and resilient control"이고, MOSA(모듈형 개방 시스템 접근) 준수가 필수다([Inside Unmanned Systems, 2026-08](https://insideunmannedsystems.com/army-seeks-commercial-controllers-for-drones-and-ground-robots-under-new-c2-architecture/)). 이 공고에 'cognitive load'나 'workload'라는 단어는 없다. 육군이 사려는 것과 측정 방법 사이에 빈칸이 있다는 뜻이다. 공군도 사정이 비슷하다. 2023년 ACC 사령관은 전투기 1대당 CCA 1대부터 시작하겠다고 했다([Air & Space Forces](https://www.airandspaceforces.com/acc-boss-fighters-should-start-with-one-cca-then-see-where-it-takes-us/)). 2026년 7월에도 "Whether a single fighter pilot can meaningfully supervise multiple CCAs"는 열린 질문이었다([Breaking Defense, 2026-07](https://breakingdefense.com/2026/07/the-autonomous-cca-wingmen-of-2030-may-look-nothing-like-todays-assumptions/)).

조달 신호 중 가장 강한 것은 2026년 1월 DIU·DAWG·해군의 **1억 달러 Autonomous Vehicle Orchestrator 상금 챌린지**다. 목표는 "translate a battlefield commander's intent from voice, text, and haptic input into machine execution"과 "vehicle-agnostic capability for understanding, tasking and coordinating autonomous systems"다. DAWG 국장 Donovan 중장은 "We want orchestrator technologies that allow humans to work the way they already command"라고 했고, "the human - the ethical decision maker - always maintains a clear understanding of what the system is doing"을 조건으로 걸었다([DIU](https://www.diu.mil/latest/diu-and-dawg-launch-autonomous-vehicle-orchestrator-prize-challenge)). 검색 요약 기준 세부 요구는 세 가지다. 의도를 플랫폼 "playbook" 옵션에 연결할 것, 플랫폼이 이미 내보내는 데이터로 함대 상황을 파악할 것, 기존 기체 자율 스택을 수정하지 않을 것이다. Donovan은 지휘관이 "clicking through menus or programming behaviors"를 하지 않게 하겠다고도 말했다([ExecutiveGov](https://www.executivegov.com/articles/diu-dawg-navy-challenge-av-orchestrator)). 챌린지는 여러 팀이 상금을 받는 구조다. NODA AI의 '1억 달러 수주' 주장은 연방 공고와 맞지 않는다([RuntimeWire](https://runtimewire.com/article/noda-ai-100m-autonomous-military-command-contract)).

CDAO Swarm Forge도 같은 방향이다. "heterogeneous swarming implies multi-vendor UAS command, control and autonomy"라고 정의했고, "The United States currently lacks the inventory and the doctrine to deploy massed, coordinated, low-cost robotic systems"라고 인정했다. 분기별 Crucible 행사로 90일 안에 부대에 전달하는 구조다([DefenseScoop, 2026-03-31](https://defensescoop.com/2026/03/31/pentagon-preparing-drone-swarm-crucible/)). DAWG의 FY2027 요청액은 약 546억 달러다. 다만 그중 536억 달러는 조정법안 통과를 조건으로 한 요청이다([Defense One](https://www.defenseone.com/ideas/2026/05/pentagons-54-billion-bet-autonomous-warfare/413735/)). Replicator는 2025년 8월까지 '수천 대'를 배치한다는 목표를 놓쳤다([MeriTalk](https://www.meritalk.com/articles/replicator-drone-initiative-earns-good-grades-two-years-in/)).

이 증거는 팀 설계와 정확히 겹치지만, 경고도 하나 담고 있다. 팀의 '플레이'는 Orchestrator의 "playbook"에, '범위가 제한된 허용 목록 플레이'는 육군의 "policy-based control"에 대응한다. 그런데 Donovan이 지휘관에게 "programming behaviors"를 시키지 않겠다고 한 점을 보면, 노코드 플레이 작성 기능은 **운용자가 아니라 계획 참모가 임무 전에 하는 일**로 분명히 선을 그어야 한다. 그래야 이 요구와 충돌하지 않는다.

### 업체들은 같은 분업을 팔지만, 부하는 아무도 재지 않았다

상용 제품은 거의 모두 같은 분업을 내세운다. 사람은 목표·우선순위·교전 승인을 맡고, 자율은 항법·편대·충돌 회피를 맡는다. 기체를 잃으면 자동으로 재할당한다.
- **Anduril Lattice:** "automatically breaks down operator intent into discrete tasks"를 표방한다([Maginative](https://www.maginative.com/article/anduril-announces-lattice-for-mission-autonomy-an-ai-powered-platform-to-manage-drone-swarms/), 검색 스니펫). 2024년 IBP 24.1에서는 공중·수상·수중의 무인 체계와 데이터 피드 "more than a dozen"을 연동했다([Unmanned Systems Technology](https://www.unmannedsystemstechnology.com/2024/04/unmanned-and-autonomous-systems-simultaneously-coordinated-with-command-and-control-software/), 검색 스니펫). '1명이 수백 대'는 2023년 회사 주장이다([Breaking Defense, 2023](https://breakingdefense.com/2023/05/andurils-new-tech-could-allow-single-operator-to-control-hundreds-of-autonomous-systems/)).
- **Auterion:** 2026년 1월 운용자 1명이 FPV 3대에 목표를 주고 효과를 승인한 실사격 시연에서 Lorenz Meier가 "The one-pilot, one-drone model is obsolete."라고 말했다([Inside Unmanned Systems](https://insideunmannedsystems.com/auterion-demonstrates-one-operator-drone-swarm-strike-in-u-s-live-fire-test/)). 1대를 잃으면 다른 기체가 그 표적을 넘겨받는다([Interesting Engineering](https://interestingengineering.com/military/pentagon-operator-three-targets-drone-swarm)).
- **Saronic Echelon:** "autonomy-aware alerts"와 "surfacing only the most relevant data"를 내세운다. 동시에 CTO는 Echelon이 "purpose-built to unlock the full potential of Saronic's autonomy stack"이라며 수직 통합을 옹호했다([Seapower](https://seapowermagazine.org/saronic-unveils-echelon-a-unified-platform-for-mission-planning-simulation-and-command-and-control-of-autonomous-surface-vessels/)).
- **Skydio:** FAA 승인으로 원격 조종자 1명이 X10을 최대 4대 운용한다. 두 번째 호출이 오면 두 번째 드론을 보내고, 첫 드론의 복귀는 자율에 맡긴다([DroneXL](https://dronexl.co/2026/03/28/skydio-faa-multi-drone-bvlos-approval/)).
- **Shield AI(LUCAS):** "Humans remain in control of strike decisions while autonomy manages navigation, coordination, and execution."이라고 썼다([Shield AI](https://shield.ai/?p=15350)).

이번 조사가 확인한 빈칸은 두 가지다. 하나는 **상용 제품 쪽에 운용자 인지부하의 정량 평가(NASA-TLX, 2차 과업 등)를 공개한 자료가 없다**는 점이다. 업체 주장은 "reducing cognitive load", "reduces workload" 같은 정성적 문구에 그친다(products-market 노트 6절). 다른 하나는 **접근통제와 감사**다. 2025년 10월 육군 CTO 메모는 Anduril이 주도하는 NGC2 프로토타입을 "very high risk"로 평가했다. 메모는 "We cannot control who sees what, we cannot see what users are doing, and we cannot verify that the software itself is secure."라고 적었다. Anduril은 "outdated snapshot"이라고 반박했다([The Defense Post](https://thedefensepost.com/2025/10/09/us-army-security-platform-prototype/amp/)). 측정되는 부하와 명령 감사 로그는 1위 업체들도 비워 둔 자리다.

시장 규모는 정의마다 편차가 커서 하나만 출처와 함께 쓰는 것이 안전하다. MarketsandMarkets는 무인 C2/C3 시장을 2025년 약 42억 달러에서 2035년 약 168억 달러(CAGR 15%)로 본다. 같은 보고서는 "Dedicated ground stations built around one vehicle are being replaced by software-led command layers"라고 서술한다([MarketsandMarkets](https://www.marketsandmarkets.com/Market-Reports/unmanned-c2-c3-market-74094713.html), 유료 보고서 요약·검색 스니펫, 보고서끼리 편차가 최대 100배). 자본도 이 계층으로 몰린다. Anduril은 2026년 5월 기업가치 610억 달러([Crunchbase News](https://news.crunchbase.com/defense-tech/anduril-5b-valuation-vc-funding-record-data/)), Helsing은 2026년 7월 180억 달러([CNBC](https://www.cnbc.com/2026/07/13/helsing-fund-raise-defense-18-billion.html)), Saronic은 92.5억 달러([techbuzz.ai](https://www.techbuzz.ai/articles/defense-tech-startup-saronic-raises-1-75b-for-autonomous-warships), 2차 출처)다.

### 한국은 인력 절벽과 '공통 아키텍처' 요구가 함께 커지고 있다

한국 쪽 근거는 인구 구조에서 출발한다.
- **20세 남성 인구:** 병무청 자료(임종득 의원실)에 따르면 2025년 약 22.4만 명에서 **2040년 약 14.3만 명**으로 준다. 상비병력은 2022년 약 50만 명에서 2025년 7월 약 45만 명으로 줄었다([중앙일보 via Daum, 2025-10-06](https://v.daum.net/v/20251006170145067), 원문 확인).
- **KIDA 2026년 7월 분석:** 현 추세가 이어지면 2045년 상비병력이 약 19.7만 명이 된다([Korea Daily](https://www.koreadaily.com/article/20260708200709936), 검색 요약, 원 기사 URL은 410).
- **국방부 구상:** 드론·무인기 전력을 약 **30배** 늘리고, 병사 비중을 현재 60%에서 **2040년 37%**로 낮춘다([아이뉴스24, 2026-09-03](https://www.inews24.com/view/2001302), 원문 확인).

그런데 2026년 육군 유무인 분대는 **전투원 4명과 무인체계 운용요원 4명, 총 8명**으로 편성됐고, 드론·로봇개·다목적 무인차량·자율주행차량 **4종**을 운용한다. 2027년 중대급, 2028년 대대급으로 실증을 넓힐 계획이다([뉴스스페이스, 2026-07-29](https://www.newsspace.kr/news/article.html?no=15018)). 운용자 1명이 플랫폼 1종을 맡는 지금 비율로는 병력 감소와 무인체계 30배 증강을 동시에 감당할 수 없다. 이 연결은 추론이다. 공식 문서가 '1인당 몇 대'를 제시한 적은 없다.

해군 쪽 요구는 더 구체적이다. 해군참모총장은 Navy Sea GHOST의 4대 과제 중 하나로 **"공통 아키텍처 구축"**을 꼽았다([파이낸셜뉴스, 2026-09-08](https://www.fnnews.com/news/202609080904320627)). LIG넥스원은 USV 통합제어체계에 정부 주관 "해양무인체계 공통아키텍처"를 먼저 적용해 다수·다종 USV의 상호운용성을 확보한다고 밝혔다([뉴데일리 비즈](https://biz.newdaily.co.kr/site/data/html/2025/05/22/2025052200169.html), 검색 요약). 한화시스템은 2026년 8월 부산에서 AUV와 무인수상정 2종을 OneWeb 저궤도 위성통신으로 동시에 통제하는 대기뢰전을 시연했다([한화시스템](https://www.hanwhasystems.com/kr/prcenter/newsView.do?bbidx=812)). 국방부의 AI 사업에는 "드론 공용조종체계"가 포함됐다는 보도가 있다([헤럴드경제, 2026-06-25](https://www.heraldk.com/article/2026062516554180507), [세계일보, 2026-04-30](https://www.segye.com/newsView/20260430516740); 여러 기사에 걸친 서술이라 정확한 귀속은 원문 확인 필요).

국내 대기업은 대부분 해외 자율 소프트웨어와 손잡고 있다. KAI–Shield AI([Airforce Technology](https://www.airforce-technology.com/news/shield-ai-kai/)), HD현대–Anduril([한국경제](https://www.hankyung.com/article/202508077552i)), 한화–HavocAI([Maritime Executive](https://maritime-executive.com/article/hanwha-teams-up-with-american-swarming-boat-ai-startup-havoc)), 현대로템–Shield AI가 그 예다. 현대로템 MOU의 3단계인 "integrated command and control of various types of MUM-T weapon systems"는 아직 미래 과제다([Shield AI](https://shield.ai/?p=14965)). 각 사의 자율 위에 얹는 국산 벤더 중립 운용자 계층은 주권·수출통제 측면에서도 논리가 선다. 다만 이를 뒷받침하는 문서는 찾지 못했으므로 추정으로 표시한다.

2차 심사의 글로벌 확장(25%)에 쓸 도입 경로는 미국·한국 양쪽에 모두 실재한다.
- **미국 경로:** 육군 UAS Marketplace CSO, DIU Orchestrator와 Swarm Forge가 있다(위 출처). Oregon UAS Accelerator는 2026년 TRL 3부터 받는 'pioneer' 트랙을 새로 만들었고, 5,000~9,000달러의 보조금과 Pendleton 시험장의 "14,000 sq miles of controlled airspace"를 제공한다([Unmanned Airspace](https://www.unmannedairspace.info/uncategorized/oregon-uas-accelerator-launches-2026-challenge/)).
- **한국 경로:** 방사청 신속시범사업은 성숙 기술의 연구개발 기간을 12개월 이내로 줄인다([파이낸셜뉴스, 2026-09-18](https://www.fnnews.com/news/202609180858361306)). 방산 챌린지는 과제당 최대 1억 원을 지원한다([MTN](https://news.mtn.co.kr/news-detail/2026040816371870009)). 드론·로봇·AI 분야에는 '공모형 획득' 제도가 추진 중이다([뉴시스](https://www.newsis.com/view/NISX20260223_0003522678)).
- **NATO 경로:** REPMUS 2025에는 22개국의 260개 체계가 참가해 "integrated multi-domain command and control"을 시험했다([Baird Maritime](https://www.bairdmaritime.com/security/naval/unmanned-naval-systems/nato-completes-unmanned-systems-exercise-in-portugal), 검색 요약).

## 전장의 병목은 사람 수, 링크, 그리고 한꺼번에 오는 교란이다

우크라이나는 무인체계 운용이 결국 사람 수와 통신에 막힌다는 것을 보여 준다.
- **물량:** 2025년 군이 확보한 FPV는 약 **300만 대**로 전년의 약 2.5배였다([Ukrainska Pravda, 2025-12-24](https://www.pravda.com.ua/eng/news/2025/12/24/8013217)).
- **인력 대비 효과:** 무인체계군(USF)은 전체 국방 인력의 **2.2%**로 검증된 표적 타격의 **36.3%**(2025년 7월)를 맡았다고 보고했다. 목표는 5%다([Euromaidan Press](https://euromaidanpress.com/2025/09/19/ukraines-drone-forces-aim-to-reach-5-of-total-military-for-full-front-coverage/), 교전국 주장).
- **운용 비율:** 여전히 드론 1대에 사람 1명 이상이 붙는다. Spiderweb 작전은 드론 117대에 운용자 117명이었다([Wikipedia](https://en.wikipedia.org/wiki/Operation_Spiderweb)). 러시아 Rubicon의 FPV 팀도 3~4명이다([FPRI](https://www.fpri.org/article/2026/06/inside-rubicon-the-structure-of-russias-elite-drone-center/)).
- **줄인 사례:** Swarmer는 "instead of nine operators in a conventional setup, only three are needed – a planner, a navigator and an operator"라고 했다. 통상 3대, 최대 8대를 운용한다([Ukrainska Pravda/WSJ](https://www.pravda.com.ua/eng/news/2025/09/03/7529154/), 회사·익명 장교 출처).
- **Lasar's Group:** 경로계획 소프트웨어로 조종사 1명에게 폭격 드론을 최대 5대 묶는다. 조종사는 25분 이상 걸리는 편도 비행 중 타격 정렬에 "a few minutes"만 접속한다([Euromaidan Press, 2026-08-22](https://euromaidanpress.com/2026/08/22/one-pilot-five-bombers-ukraines-lasars-group-ties-whole-raid-to-single-operator-to-save-manpower/), 광고성 기사 표기).

Lasar's 사례는 Fan-out 모델의 'NT는 길게, IT는 짧게'를 그대로 구현한 것이다. 이 구조에서 실제 한계는 여러 기체의 정렬 시점이 겹칠 때 생기는 대기열(WTQ)이다. 데모에 '도착 시각 충돌 → 큐 대기 → 시간차 제안' 장면을 넣으면 실전과 모델이 맞물린다.

### 이종 협동은 이미 사람이 손으로 하고 있다

팀의 '한 기체의 탐지가 다른 기체의 역할을 만든다'는 아이디어는 전장에서 이미 사람이 수작업으로 하는 일이다.
- **UGV 임무 급증:** 2026년 1월 **7,511건**에서 8월 **25,143건**으로 늘었고, 사용 부대는 117개에서 230개가 됐다. 대부분이 군수와 후송이다. 국방부 통계는 "disabling a single robot can deprive a brigade of an entire logistics or evacuation route"라고 경고했고, 러시아 FPV가 UGV를 노린다고 했다([UNITED24, 2026-09-09](https://united24media.com/war-in-ukraine/ukraines-ground-robots-just-passed-25000-missions-a-month-as-front-line-logistics-go-unmanned-22395)).
- **혼합 링크와 아군 간섭:** West Point MWI 분석에 따르면 우크라이나는 UGV를 Starlink·가시선 무선·광섬유·공중 중계로 섞어 통제한다. 그래도 러시아 재밍과 아군끼리의 "electronic fratricide" 때문에 링크 유지에 애를 먹는다. Starlink 대역폭은 "as little as 10 megabits per second"까지 떨어진다. 분석은 UGV를 독립 플랫폼이 아니라 "nodes within a larger system"으로 쓰고, 위에서 쿼드콥터가 감시(overwatch)하라고 권했다([MWI, 2026-03-09](https://mwi.westpoint.edu/networked-for-war-lessons-from-ukraines-ground-robots/)).
- **공중 탐지 → 지상 유도:** 공중 드론이 (주로 야간에) 적을 찾으면 원격 운용자가 UGV를 유도한다([IEEE Spectrum](https://spectrum.ieee.org/ukraine-ground-drones), 검색 스니펫).
- **해상 모선:** Magura 해상드론은 2026년 FPV를 실어 나르는 모선이 되어 크림반도 내륙 레이더를 타격했다고 주장된다([UNITED24](https://united24media.com/war-in-ukraine/magura-sea-drones-goes-from-hunter-to-fpv-mothership-striking-russian-radars-in-crimea-21274), 교전국 주장). 미 DIU는 공중드론을 최소 2대 통합하는 USV에 1억 달러 SWAP-USV 상금을 걸었다(같은 출처, 검색 스니펫).

현장의 디컨플릭션 도구는 여전히 원시적이다. USF 운용자는 "we have a group chat of coordinating small aviation in that specific sector"라고 했다. 피아를 구분할 수 없어 겁에 질린 병사들이 "click all of the frequencies to be jammed"한다며 "It's a mess."라고 증언했다([Business Insider via Yahoo](https://www.yahoo.com/news/soldiers-ukraine-panic-jam-everything-090501576.html)). 공중·지상·해상 기체를 묶어 탐지가 곧 다른 기체의 역할 제안으로 이어지게 하는 일은 이 그룹채팅을 시스템으로 대체하는 일이다.

### EW와 링크 상실은 '사건'이 아니라 기본 조건이다

EW 손실 수치는 출처마다 다르지만 방향은 하나다.
- **명중률과 사거리:** Azov 무인체계대대장에 따르면 러시아 EW 때문에 무선 FPV는 접촉선에서 5~8km로 묶이고, 명중률은 "can decrease to 30%"까지 떨어진다. 광섬유 드론은 함대의 5% 미만이다([TWZ, 2025-05-28](https://www.twz.com/news-features/inside-ukraines-fiber-optic-drone-war)).
- **격추 비율:** CTC Sentinel은 "Reportedly something over 50 percent of FPV drones are downed by jamming, many by friendly fire"라고 썼다([CTC Sentinel, 2025-07](https://ctc.westpoint.edu/moving-targets-implications-of-the-russo-ukrainian-war-for-drone-terrorism/)). 프랑스 육군총장의 75% 발언 보도도 있다([Forbes](https://www.forbes.com/sites/davidhambling/2025/01/14/why-fpv-drones-are-still-ukraines-biggest-tank-killers/)). 2023년 RUSI의 '월 1만 대 손실'은 우크라이나 측이 '하루 40~45대'라고 반박한 수치다([Task & Purpose](https://taskandpurpose.com/news/ukraine-10000-drone-losses/)).
- **단일 링크 의존:** 2026년 2월 Starlink 화이트리스트로 러시아 단말이 차단되자 "in some areas, assault operations have actually stopped"라는 보고가 나왔다([NV](https://english.nv.ua/amp/russian-field-operations-crippled-after-starlink-cut-50581450.html), 우크라이나 당국 발언).

여기서 나오는 설계 요구는 두 가지다. 운용자 화면에 각 자산의 링크 상태, 대체 링크, 링크를 잃었을 때 예정된 행동이 보여야 한다. 그리고 모든 플레이에 링크 상실 시 행동이 미리 정의돼 있어야 한다.

### 한반도에서는 GPS 교란이 14년째 반복되는 위협이다

한국 고유의 근거는 더 날카롭다.
- **2022년 북한 무인기 침투:** 2022년 12월 26일 북한 무인기 5대가 들어왔을 때 한 대도 격추하지 못했다. "Some of them disappeared from radar screens as they were being tracked"라는 보도가 나왔다. 날개폭 3m 미만 소형 무인기의 탐지·타격 능력이 부족하다는 지적도 함께였다([AP via KTVU](https://www.ktvu.com/news/south-korean-military-north-korea-drones), 검색 스니펫).
- **누적 장애 7,270건:** 과기정통부 자료를 정희용 의원실이 공개한 집계에 따르면, 2010년 8월부터 2024년 11월 13일까지 북한 GPS 교란으로 기지국·항공기·선박에 **7,270건**의 장애가 났다. 2016년 1회 교란으로만 3,516건이었다. 2024년 선박 피해는 **1,157건**으로 2016년의 1.6배였다([세계일보](https://www.segye.com/newsView/20241117507200), [안전신문](https://www.safetynews.co.kr/news/articleView.html?idxno=233748)). 회차별 합계(7,315건)가 발표 총계와 45건 다르다.
- **합참 평가:** 합참은 2024년 11월 교란을 "주로 무인기 출현에 대비한 훈련 목적"으로 봤다([이투데이](https://www.etoday.co.kr/news/view/2418609)). 2010~2012년 교란이 군 무인기의 GPS 항법까지 방해했다는 보도도 있다([Korea Times, 2016](https://www.koreatimes.co.kr/foreignaffairs/northkorea/20160405/n-koreas-gps-jamming-targets-aircraft-navigation-system)).
- **복행:** 2024년부터 2025년 9월까지 GPS 교란 때문에 항공기가 46회 복행했다([NK News](https://www.nknews.org/?p=962298)).
- **간헐성:** 2026년 7월 중앙전파관리소는 올해 백령도 인근에서 교란을 탐지하지 못했다고 밝혔다([NK News](https://www.nknews.org/2026/07/no-reports-of-north-korean-gps-jamming-near-maritime-border-seoul-says/)). 합참 표현대로 교란은 "있다가도 없고 없다가도 있다".

가장 무거운 사례는 2012년 5월 10일 인천의 Schiebel S-100 추락이다. 제조사는 GPS 상실이 사고 조건을 만들었다고 확인했다. 기체는 지상통제소 차량을 들이받았고 엔지니어 1명이 숨지고 2명이 다쳤다([Shephard](https://shephardmedia.com/news/uv-online/heli-pacific-2012-schiebel-s-100-crash-due-loss-gp)). AIN 보도(검색 스니펫)에 따르면 Schiebel은 "an incorrect response by the operators after the Camcopter lost its GPS signal led to the crash, some minutes later"라고 설명했다([AIN](https://www.ainonline.com/aviation-news/defense/2012-06-01/uav-crash-korea-linked-gps-jamming)). 기록장치는 화재로 소실됐고 공식 조사 보고서는 공개 자료에서 찾지 못했다. **전자전 사건이 운용자의 판단 오류를 거쳐 사망으로 이어진 한국 내 실례**이고, 팀의 '과부하 운용자도 바닥을 뚫지 못한다'는 주장의 가장 직접적인 근거다.

해외 수치는 교란이 일상이 됐음을 보여 준다. 발트해 6개국 공동 보고에 따르면 2025년 1~4월에 **122,607편**이 GNSS 간섭을 겪었고, 4월에는 해당 공역 항공편의 27.4%가 영향을 받았다([GPS World](https://www.gpsworld.com/123000-flights-disrupted-by-gnss-jamming/)). 걸프 해역에서는 2026년 1분기에 약 978,000건의 간섭 이벤트가 집계됐다([Windward](https://windward.ai/blog/gps-jamming-is-mainstream-changes-between-2025-and-2026/), 업계 집계).

이 증거는 팀의 재연결 설계를 고치라고 요구한다. 교란은 **공통모드**다. 한 구역의 GPS 의존 기체가 **동시에** 영향을 받는다. 그래서 'GPS가 교란된 드론의 역할을 같은 구역의 다른 드론에 넘기는' 재연결은 함께 실패한다. 재연결은 교란에 덜 의존하는 다른 도메인 기체를 우선해야 한다. 예를 들어 휠 오도메트리가 있는 UGV나 위성 링크를 쓰는 USV다(추론). 동시에 시스템은 퇴화 모드 플레이(정지·관성 귀환)로 내려가야 한다. 더 중요한 점도 있다. 경보 N개가 한꺼번에 뜨는 순간이 곧 S-100식 오대응 위험이 가장 큰 순간이다. 그래서 공통 원인 경보를 **한 건의 사건으로 묶고 권장 플레이 하나를 붙여** 보여 주는 기능이 필요하다. 이 장면은 한국 심사위원에게 바로 통하는 데모가 된다. 서해 GPS 교란이 오고, 경보 3건이 1건으로 묶이고, 역할이 다른 도메인으로 재연결되고, 그 와중에 운용자가 서둘러 낸 위험 명령을 안전 바닥이 수정한다.

## MAVLink 무인증과 운용자 오대응이 안전 바닥을 필수로 만든다

1인이 다수 기체를 지휘하면 공격면도 함께 곱해진다.
- **기본 무인증:** MAVLink 1.0에는 인증이 없다. MAVLink 2.0의 서명은 HMAC 기반이라 함대의 모든 장치에 같은 대칭키를 넣어야 한다. 그래서 "if one of the devices and its symmetric key are compromised, the whole authentication system is not reliable"([NVD CVE-2020-10282](https://nvd.nist.gov/vuln/detail/CVE-2020-10282)).
- **원격 셸:** 2026년 3월 31일 CISA는 PX4의 **CVE-2026-1579(CVSS 9.8)**를 공지했다. 서명이 꺼져 있으면 대화형 셸을 여는 SERIAL_CONTROL을 포함해 어떤 메시지든 인증 없이 보낼 수 있다. 결과는 "execute arbitrary shell commands without cryptographic authentication"이다. 영향 섹터에는 "Defense Industrial Base"가 포함됐다([CISA ICSA-26-090-02](https://www.cisa.gov/news-events/ics-advisories/icsa-26-090-02)).
- **서명의 한계:** ArduPilot 문서에 따르면 서명은 "This does NOT encrypt the data"이고 USB 연결에는 적용되지 않는다([ArduPilot](https://ardupilot.org/copter/docs/common-MAVLink2-signing.html)).
- **지상로봇 탈취:** MAVLink 기반 군용 4족 로봇 Ghost Robotics Vision 60은 공격자가 제어 태블릿을 사칭해 "gaining unauthorised full control of the robot"할 수 있었다. 원격 연결 경로는 Wi-Fi와 4G/LTE였다([NVD CVE-2025-41108](https://nvd.nist.gov/vuln/detail/CVE-2025-41108)).
- **실제 사례:** 2009년 이라크 무장세력은 약 26달러짜리 SkyGrabber로 암호화되지 않은 Predator 영상을 가로챘다([Defense One](https://www.defenseone.com/defense-systems/2009/12/military-predator-video-intercepted-by-iraqis/188556/)). 2011년 Creech 기지의 GCS는 키로거에 감염돼 "We keep wiping it off, and it keeps coming back."이라는 말이 나왔다([The Register](https://www.theregister.com/2011/10/10/keylogging_bug_infects_predator_drones/)).
- **단일 장애점:** UAV 보안 서베이는 중앙집중이든 분산이든 "the GCS represents a single point of failure"라고 정리했다([arXiv 2109.14442](https://arxiv.org/pdf/2109.14442)).

1:N 콘솔에는 고유한 위험이 하나 더 있다. '전 기체 귀환'이나 '임무 재할당' 같은 일괄 명령이 있으면, 탈취된 콘솔이나 운용자의 오조작 한 번이 N대에 동시에 퍼진다. 노트는 이것을 '명령 증폭'으로 정리했다(추론).

한국 정책은 기기와 업체 단에 머물러 있다.
- **기기 인증:** KISA와 과기정통부는 2024년 6월 국군방첩사령부와 함께 만든 드론 분야 IoT 보안인증 해설서를 배포했다([디지털데일리](https://m.ddaily.co.kr/page/view/2024061011014676790)).
- **업체 해킹 경고:** 국정원은 2025년 3월 북한 등의 "국내 드론 개발업체에 대한 … 공격 시도가 증가하고 있다"고 경고했다. 2024년 12월 합동점검에서는 다수의 보안 취약점을 확인했다([보안뉴스](http://www.boannews.com/news/articleView.html?idxno=136514)).
- **군용 인증:** 국방부는 2026년 6월 "공급망과 품질·보안 등을 사전에 검증하는 한국형 상용 드론 군용인증체계"를 예고했다([정책브리핑](https://www.korea.kr/briefing/policyBriefingView.do?newsId=156768313)).

모두 기기 인증과 업체 관리에 초점이 있다. 운용 단계 보안, 즉 다수 기체 C2 링크의 인증과 GCS가 침해됐을 때의 피해 한정은 공개 기준에서 거의 다뤄지지 않는다. 사이버 방어 학생 팀이 메울 수 있는 공백이다.

### 사람도 '검증되지 않은 주 제어기'로 거르는 선례가 있다

팀이 가장 강하게 기댈 수 있는 개념은 런타임 보증(RTA)이다. AFRL 튜토리얼은 RTA를 "online verification mechanisms that filter an unverified primary controller output to ensure system safety"로 정의한다. 여기서 주 제어기는 "may come from a human operator, an advanced control approach, or an autonomous control approach"이고, 보증 장치는 "entirely agnostic to the underlying structure of the primary controller"하게 만든다([Hobbs et al., arXiv 2110.03506](https://arxiv.org/abs/2110.03506)). 표준인 ASTM F3269-21은 "This practice was developed with UAS in mind"라고 밝히고, "a human may perform the role of either the Complex Function or a Recovery Function"이라고 명시한다. 구성요소는 Input Manager, Safety Monitor, RTA Switch, Recovery Function이다([ASTM](https://store.astm.org/f3269-21.html)). **"런타임 가드가 사람의 명령에도 똑같이 적용된다"는 팀 설계는 표준 문구로 그대로 뒷받침된다.** 원격 군집로봇 시험장 Robotarium은 실제 운영에서 사용자가 제출한 알고리즘을 "black box functions"로 보고 CBF 기반 QP 필터로 충돌을 막는다(Hobbs 같은 출처). NASA Safeguard는 "operates independently of the off-the-shelf UAS autopilot"하다([NASA NTRS](https://ntrs.nasa.gov/citations/20170009617)).

실전 실적과 수용성 설계에서는 F-16 Auto-GCAS가 대표 선례다.
- **구조 실적:** Air Force Times(2024-11)는 공군이 이 시스템으로 2014년 이후 F-16·F-22 조종사 **16명**을 구했다고 집계한다고 보도했다([Air Force Times](https://www.airforcetimes.com/news/your-air-force/2024/11/20/could-a-fighter-jet-software-upgrade-have-saved-this-pilots-life/)). 수치는 출처마다 다르다. NASA는 2019년에 8명([NASA](https://www.nasa.gov/centers/armstrong/news/newsreleases/2019/19-02.html)), Lockheed는 F-16만 13명이라고 밝혔다([Lockheed Martin](https://www.lockheedmartin.com/en-us/products/autogcas.html)).
- **요구사항 순서:** 개발 요구사항의 우선순위는 **"do no harm, do not interfere, and prevent collisions"**였다. 이 순서가 "critical in acceptance of the system"이었다고 한다.
- **방해하지 않는 기준:** 조종사가 기동을 중단하거나 시스템을 끌 수 있었다. 개입이 시작되고 끝날 때 알렸고, 개입마다 기록을 남겼다. 남은 시간 1.5초 미만에서만 개입하도록 해 불필요한 개입을 없앴다. "Knowledge of Auto GCAS's 98% reliability increased test pilot trust"(이상 [Hobbs et al.](https://arxiv.org/abs/2110.03506)).

같은 문서는 입력 데이터가 틀리면 안전장치도 틀린다고 경고한다. INS가 고장 나면 Auto-GCAS가 뒤집힌 채 땅으로 당길 수도 있다는 것이다. 그래서 기체 데이터의 무결성을 감시하고 믿을 수 없는 기체를 격리하는 기능이 RTA의 전제가 된다.

기체 자체의 페일세이프만으로는 부족하다. FAA는 lost link가 나면 무인기가 "a predictable or planned maneuver"를 하고, 링크를 회복하지 못하면 "flight termination must be implemented"라고 정의한다([FAA P/CG](https://www.faa.gov/air_traffic/publications/atpubs/pcg_html/glossary-l.html)). ArduPilot은 GCS 하트비트가 기본 5초 끊기면 RTL·Land 등을 실행한다([ArduPilot](https://ardupilot.org/copter/docs/gcs-failsafe.html)). 하지만 PX4 지오펜스는 "will only trigger once the vehicle has already breached the geofence"다([PX4](https://docs.px4.io/main/en/config/safety.html)). 그래서 C2 계층이 명령 단계에서 경로를 미리 검사하는 '두 번째 펜스'가 따로 필요하다.

### 정책 문구가 안전 바닥의 기능 명세가 된다

DoDD 3000.09(2023-01-25)는 다음 내용을 글자 그대로 요구한다([DoDD 3000.09, Wayback 사본](https://web.archive.org/web/2024id_/https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodd/300009p.pdf)).
- **경계 안에서 끝내기:** 체계는 "Complete engagements within a timeframe and geographic area … If unable to do so, the systems will **terminate the engagement or obtain additional operator input** before continuing the engagement."
- **변조 방지와 사이버 보안:** "anti-tamper mechanisms, and cybersecurity"를 갖춘다.
- **HMI:** "clearly indicating what actions operators need to perform and which actions the system will perform", "transparent feedback on system status", 활성·비활성 절차를 제공한다.
- **'failure'의 정의:** 원인에 "communications degradation, … enemy cyber-attacks …, jamming, spoofing, decoys"를 명시한다.
- **최소 위험의 의미:** "does not mean achieving the lowest possible level of risk by never engaging targets"라고 못 박는다.
- **변경 후 재검증:** 변경 뒤에는 "validate that critical safety features have not been degraded"하고, 가능하면 M&S 자동 시험을 쓴다.

비무장 플랫폼은 적용 대상이 아니다([Wikipedia](https://en.wikipedia.org/wiki/Department_of_Defense_Directive_3000.09), 검색 요약). 그래도 미군 심사위원의 "how do you know it's safe?"에 이 문장들을 기능으로 구현했다고 답하는 것이 가장 강하다. 국제 규범도 같은 방향이다. NATO 원칙은 "disengagement or deactivation"을 요구한다([NATO](https://www.nato.int/cps/en/natohq/official_texts_187617.htm)). 2024년 REAIM 서울 Blueprint는 한국이 주최하고 지지했다([Asia News Network](https://asianews.network/seoul-summit-charts-framework-on-responsible-ai-military-use/)). 국회에서 심사 중인 국방인공지능법안의 쟁점도 "인간 지휘관의 최종 통제권을 어떻게 보장할지"다([뉴스핌, 2026-09-02](https://www.newspim.com/news/view/20260902000951)).

명령면 축소에는 보안 선례를 그대로 가져올 수 있다.
- **Zero Trust:** DoD Zero Trust 전략은 "Presume Breach. Limit the "blast radius""와 최소 권한을 원칙으로 한다([DoD ZT Strategy, Wayback](https://web.archive.org/web/2024id_/https://dodcio.defense.gov/Portals/0/Documents/Library/DoD-ZTStrategy.pdf)). 다만 무기체계에 ZT를 적용하는 목표 시점은 "fiscal [year 20]35 and beyond"이고 "very green in the thinking" 단계다([Breaking Defense, 2025-04](https://breakingdefense.com/2025/04/dod-floats-2035-as-goal-for-zero-trust-in-weapons-systems/)). 그래서 해커톤 결과물은 공식 표준 준수가 아니라 **"전술 엣지 C2 계층의 ZT 시제"**로 내세우는 것이 정확하다.
- **LLM 명령원:** OWASP는 "Implement authorization in downstream systems rather than relying on an LLM to decide if an action is allowed"와 "human approval for high-impact actions"를 권한다([OWASP LLM06:2025](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)).
- **2인 개념:** 핵무기 운용의 '2인 개념'은 "accidental or malicious launch … by a single individual"을 막기 위한 장치다([Wikipedia, AFI 91-104 인용](https://en.wikipedia.org/wiki/Two-person_rule)).

데이터 무결성 쪽에도 구현할 수 있는 기법이 있다. GPS로 계산한 기체 간 거리를 UWB 같은 독립 측정 거리와 비교하는 잔차 검사가 대표적이다([Mykytyn et al. 2023](https://arxiv.org/abs/2301.12766)). 다만 함대 전체를 똑같이 평행이동시키는 공통 스푸핑은 상대거리 검사로 잡을 수 없다. 독립된 절대 기준이 최소 1개 필요하다([Park & Yoo, arXiv 2608.06885](https://arxiv.org/abs/2608.06885), 미심사 시뮬레이션). 원 노트에는 팀의 기존 자산으로 LightGBM 게이트와 LSTM 전문가 모델로 된 IDS(GPS 스푸핑, DoS, MAVLink 퍼징, replay 탐지)가 기록돼 있다. 대회 FAQ는 기존 코드 활용을 허용하므로, 해커톤 중 새로 만든 부분과 구분해 `demo/BUILT_HERE.md`에 적으면 된다(05 브리프, 04 문서).

## 팀 방향 점검: 증거는 뼈대를 받치고 세 곳의 수정을 요구한다

아래 표는 팀 방향의 구성 요소를 하나씩 증거와 맞대 본 결과다. 판정 근거의 출처는 앞 절에 인용했다.

| 구성 요소 | 판정 | 핵심 근거 | 수정·보강 |
|---|---|---|---|
| 운용자는 조종하지 않고 역할을 맡긴다 | 강한 지지 | IMPACT plays, OFFSET 전술 라이브러리, Porat '바깥 루프', DIU "playbook" | 피치 첫 문장으로 쓴다 |
| 노코드 조합형 플레이(SOP 디지털화) | 조건부 | OFFSET은 전술을 "composing collective behaviors"로 만들었다([DARPA](https://www.darpa.mil/research/programs/offensive-swarm-enabled-tactics)). 위임 인터페이스(Miller & Parasuraman). | **작성은 계획 참모의 사전 업무로 한정한다**(Donovan: 지휘관이 "programming behaviors" 하지 않게). 플레이 수와 파라미터를 작게 둔다(8대에서 유연성 이점 소멸). 시연에서 작성 장면은 20초 안팎으로 줄인다. |
| 역할을 가능한 기체에 결합하고 이탈 시 재결합 | 지지, 보강 필요 | OFFSET 디스패처, Auterion 표적 재할당, Skydio 자동 인계, 부하 잔류(Hunt 2026) | **공통모드 교란을 반영해 다른 도메인 기체로 재결합한다.** 링크가 끊긴 기체는 마지막 의도를 유지하거나 퇴화 플레이로 전환한다. |
| 기체 협동(탐지가 다른 기체의 역할을 낳음) | 지지 | 공중 탐지 → UGV 유도, MWI overwatch, Magura 모선, SWAP-USV | 새로 생긴 역할은 '제안'으로 운용자 큐에 올리고 경보 예산에 포함한다 |
| 탐지 → 보고 → 운용자가 대응 선택 | 강한 지지 | DoDD 반자율 정의, Ruff의 consent 우위, 업체들의 "humans remain in control of strike decisions" | 이벤트가 몰리면 저위험 플레이만 적응형 예외로 돌린다. 자동화 편향(자동 승인 오류율)을 측정한다. |
| 실시간 계획 변경과 미리보기 | 지지 | DoDD HMI "which actions the system will perform", Saronic "plan, simulate, and execute" | 미리보기에 바뀌는 역할·기체·안전 바닥 판정을 함께 보여 준다 |
| 1층: 배치 전 플레이 검증 | 지지 | DoDD 3000.09 3절(M&S 자동 시험, 안전 기능 비퇴화 확인) | "위반 0건"을 증명이 아니라 통계적 상한으로 표기한다(1,000 시드 무위반이면 95% 신뢰로 위반률 0.3% 미만, [rule of three](https://en.wikipedia.org/wiki/Rule_of_three_(statistics))) |
| 2층: 모든 명령원(사람 포함)에 런타임 가드 | 강한 지지 | RTA 정의, ASTM F3269 1.3, Robotarium, S-100 사고, OWASP LLM06 | 거부보다 '가장 가까운 안전 명령으로 수정'을 먼저 한다(do not interfere). 개입의 시작·종료를 알리고 기록한다. 불필요한 개입 수도 센다. |
| 3층: 기체별 키, 허용 목록 플레이, 범위 제한 파라미터 | 지지 | 공유 대칭키 문제(CVE-2020-10282), ZT Presume Breach, OWASP 과잉 권한 | AI 할당기와 LLM에는 기체·구역·시간이 제한된 감쇠 토큰만 준다([Macaroons](https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/)) |
| 3층: 위험 플레이 2인 승인 | 조건부 | 2인 개념(AFI 91-104), DoDD "obtain additional operator input" | **'1인 운용' 전제와 충돌한다.** 두 번째 키를 지휘관 역할 토큰이나 독립 안전 커널로 두고, 드문 고위험 플레이에만 요구한다. 그로 인한 추가 지연을 측정한다. |

### 다섯 개 실시간 지표는 대부분 버티고, 정의를 다듬으면 더 강해진다

Pina 등은 인간-자동화 팀을 평가할 때 "At a minimum, one metric from each class should be used"라고 권한다. 클래스는 임무 효과, 자율체 행동 효율, 인간 행동 효율, 인간 상태 선행지표, 협업 지표다([MIT HAL2008-04](https://dspace.mit.edu/handle/1721.1/46743), 초록). 팀의 다섯 지표는 이 틀에 잘 맞는다. 다만 임무 효과 지표가 빠져 있다. DoDD 3000.09가 "never engaging"을 최소 위험으로 보지 않는다고 명시한 만큼, **안전 바닥을 켠 상태에서 임무 성공률이 유지된다**는 것을 반드시 함께 보여야 한다.

| 지표 | 외부 기준 | 판정 | 다듬을 점 |
|---|---|---|---|
| 운용자 busy-time (70%) | Cummings & Guerlain 2007(원문 미확인, 재인용 2건), Donmez 2010 60~70% 최적 | 지지 | 분자를 '지시된 과업 시간'으로 정의하고 60~300초 창으로 계산한다. 40% 미만 과소부하 밴드도 표시하고, 모니터링 시간 제외를 명시한다. |
| 10분당 경보 수 | EEMUA 191: 10분당 1건 미만이면 허용, 10건 초과면 홍수 | 지지 | 공통 원인 경보는 묶은 뒤 센다. 우선순위 분포도 함께 보여 준다. |
| 운용자 결정 수 대 수동 명령 수 | IMPRINT: 고수준 명령 6.6 대 저수준 7.3 | 지지 | 같은 시드로 '기체별 수동 명령' 기준선을 돌려 비교한다 |
| 역할 공백 시간 | 직접적인 문헌 기준 없음. WTSA가 대기의 63~72% | 신규 지표(강점) | 역할이 비는 순간부터 재결합된 기체가 임무 위치에 도착할 때까지로 정의한다. 수동 재할당(알아차림 + 결정 + 명령)과 비교한다. |
| 차단된 위험 명령 수 | Hobbs: 개입 수·개입 크기·침습성 | 조건부 | 명령원별(사람/AI/LLM/주입 공격)로 나누고, 수정과 거부를 구분한다. 불필요한 개입 수와 임무 성공률을 반드시 함께 보여 준다. |
| (추가 권장) 1인당 감당 대수 | `FO_hat = NT/(IT+WT)+1` | 추가 | "같은 성공률에서 필요한 운용자 수 = ceil(N/FO_hat)"을 헤드라인 숫자로 쓴다 |

비교 실험은 같은 시나리오 시드와 같은 이벤트 도착률로 '수동 모드 대 역할 모드'를 돌려야 공정하다. Olsen과 Wood는 보상이 없는 피험자가 대충 해서 fan-out이 낮게 나왔다고 보고했다. 시연 운용자에게도 점수 경쟁 같은 동기를 주는 편이 측정을 덜 왜곡한다([Olsen & Wood 2004](https://hci.rwth-aachen.de/materials/conferences/CHI2004/1p231.pdf)).

### 증거가 요구하지만 아직 방향에 없는 다섯 가지

**1. 자산별 링크 상태와 링크 상실 시 예정 행동.** 이것을 보여 주는 패널과 플레이별 lost-link 정의가 필요하다. MWI의 혼합 링크 분석과 FAA의 lost link 정의가 근거다.

**2. 공통 원인 경보 묶음.** GPS 교란처럼 여러 기체에 동시에 오는 경보를 한 건으로 묶어야 한다. S-100 사고와 7,270건 교란이 근거다.

**3. 기체 신뢰 상태와 자동 격리.** 상태는 TRUSTED → SUSPECT → ISOLATED로 바뀐다. 격리를 풀 때는 운용자의 확인을 받는다. 이 기능에 팀의 IDS가 들어간다. 이런 래치형 복귀에는 ArduPilot이라는 선례가 있다. ArduPilot은 재연결 뒤에도 페일세이프 모드를 유지한다.

**4. 기존 전술망과의 연동.** ArduPilot SITL은 Copter·Rover·motorboat를 내장 물리모델로 지원한다([ArduPilot SITL](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html), [SITL_cmdline.cpp](https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_HAL_SITL/SITL_cmdline.cpp)). pytak로 만든 CoT를 `239.2.3.1:6969` 멀티캐스트로 보내면 TAK 서버 없이 ATAK에 표시된다([pytak](https://github.com/snstac/pytak), [AryaOS](https://aryaos.readthedocs.io/en/latest/airtak_cuas_getting_started/), 벤더 문서이고 우리 환경에서는 미검증). 이 둘로 '실제 오토파일럿 펌웨어'와 '기존 전술망 연결'을 보여 줄 수 있다. 다만 24시간 안에는 리스크가 있으므로, 순수 Python 시뮬레이터를 기본 경로로 두는 이중화가 안전하다(supporty-and-oss 노트 B1·B3).

**5. 발진·회수와 배터리 교체 대기.** 현장의 병목은 소프트웨어가 아니라 물자라는 지적이 반복된다. Swarmer CEO는 "Each drone requires a team that will carry it, prepare it, check it. This is what limits the scale."이라고 말했다([To Vima/WSJ](https://www.tovima.com/wsj/ai-powered-drone-swarms-have-now-entered-the-battlefield)). 이 상태를 역할 결합에 반영해 보여 주면 현장감이 생긴다.

한 문장 재정의 후보는 둘이다. 첫째, "1인 다중 통제의 병목은 조종이 아니라 주의와 신뢰다. 운용자는 역할만 맡기고, 과부하 운용자든 AI든 공격자든 누구의 명령도 같은 안전 바닥을 뚫지 못한다." 둘째, 짧은 버전으로 "조종사 1명이 아니라 지휘관 1명: 역할을 맡기고, 바닥은 시스템이 지킨다."

## SUPPORTY와는 '연출 대 계산·측정·보장'으로 갈린다

SUPPORTY의 실체는 원 저장소가 아니라 팀원 미러로 확인했다. 원 저장소는 2026-10-08 기준 404다. 쇼케이스 기록상 상은 T1 본상이 아니라 "OREGON"이다([D4D showcase API](https://d4d.tech/api/showcase)). 저장소는 **커밋 1개, 13개 파일, 약 2,000줄**이고 테스트는 없다([커밋 cad1fca](https://github.com/jang961111-hash/SKYFLEET-C2/commit/cad1fca6799deb5ef24c84721d889f2aec164816)). 데모 서버는 응답하지 않았다.

실제로 구동된 것은 실물 UGV 1대와 VTOL 1대다. 게이트웨이로 RC PWM 값을 보내는 방식이었다. 나머지 3대(공중 1, 해상 1, 지상 1)는 등속 직선 이동 시뮬이다([assets.py](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/assets.py#L97-L111), [sim.py](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/sim.py#L34-L69)). 주장한 기능과 코드는 다음처럼 어긋난다.
- **Mission Queue:** 콘솔의 큐는 하드코딩된 임무 10개를 `Math.random()`으로 7~13초마다 만들어 내고, 자산 배정도 랜덤이다([console.html#L614-L631](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L614-L631)).
- **백엔드 배정:** 능력·도메인·거리로 1건씩 탐욕적으로 고른다. `urgency`는 점수에 쓰이지 않는다([missions.py#L41-L64](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/missions.py#L41-L64)).
- **인지부하:** 대기 요청 수 `pend>=4`라는 임계값 하나다. 수동 모드에서는 요청이 아예 진행되지 않게(`maxSt = 0`) 돼 있어, 경고가 반드시 세션당 1회 뜨는 스크립트다([console.html#L660-L675](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L660-L675)).
- **Starlink 전환:** 코드에 0건이다. 상단의 `LINK 4G · 92%` 칩은 정적 HTML이다([console.html#L321-L325](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L321-L325)).
- **지도와 의존성:** 지도에는 선택한 자산 1대만 표시된다([console.html#L548](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L548)). 타일은 온라인이다([console.html#L573-L577](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L573-L577)). 음성 경로는 클라우드 LLM(Haiku)과 TTS에 의존하고, "전진·정지" 같은 스틱 수준 명령까지 다룬다([asset_control.py](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/jarvis_ext/asset_control.py#L107-L125)).

시연 당일 콘솔이 다른 버전이었는지는 확인할 수 없다. 강점도 분명하다. 실물 하드웨어와 조종석 리그, 우크라이나 군인 인터뷰에서 출발한 스토리, 문제 시트 요구 5개에 하나씩 대응한 구성이다(03 문서). 같은 심사위원층이 다시 볼 가능성이 크므로, 공격하기보다 "SUPPORTY가 '한 사람이 여러 대를 만질 수 있다'를 보여 줬다면, 우리는 '한 사람이 여러 대를 맡겨도 안전하다'를 숫자로 보여 준다"처럼 이어받는 틀이 낫다.

| 항목 | SUPPORTY (코드 근거) | 우리 방향 | 현장에서 증명하는 방법 |
|---|---|---|---|
| 운용자 행위 | 음성으로 자산을 1대씩 제어(스틱 수준 포함) | 역할·플레이 호출, 결정만 | 결정 수 대 수동 명령 수 |
| 배정 | 랜덤(콘솔), 1건씩 탐욕(백엔드), 재배정 없음 | 능력 기반 결합·재결합, 근거 표시 | 역할 공백 시간, 기체 이탈 장면 |
| 인지부하 | `pend>=4` 세션당 1회 | busy-time·경보·역할 공백 실측, 수동 모드와 A/B | 같은 시드 전후 비교 곡선 |
| 통신 | 정적 칩, Starlink 0줄 | 링크 상태, lost-link 플레이, 교란 시나리오 | 서해 GPS 교란 주입 |
| 안전 | E-STOP, 수동 override | 모든 명령원에 런타임 가드, 명령면 축소, 개입 로그 | 명령원별 차단·수정 수, 성공률 유지 |
| 표준·연동 | RC PWM over HTTP | MAVLink(SITL), CoT/ATAK, STANAG 4586식 어댑터 설명 | 폰 ATAK에 같은 자산 표시 |
| COP | 선택한 1대만 지도에 표시 | 전 자산·역할·경로를 동시에 표시 | 화면 자체 |
| 시험 | 0개 | 1 액션 1 테스트, 시드 회귀 | 저장소 |
| 하드웨어 | 실물 2대(강점) | 없음 → SITL의 실제 오토파일럿 펌웨어로 대응 | 시뮬임을 명시하고 무엇을 검증했는지 구분 |

03 문서가 지적한 대로 지난 대회에서 'LLM 코파일럿 + 지도 대시보드' 형태는 거의 상을 받지 못했다. 이번에도 LLM은 보조로 두고, 핵심 판단 로직(역할 결합, 안전 판정, 부하 계산)을 따로 보여 주는 편이 맞다. 현재 저장소 정책 1(오프라인 시연)을 따르면 클라우드에 의존하지 않는 구조 자체가 단절·간헐·저대역(DDIL) 환경 대응의 증거가 된다. 시연 중 인터넷 허용 여부(`decisions/log/0001`)는 아직 제안 상태다.

## 3분 피치에 박을 숫자 15개

| # | 사실 | 숫자 | 출처 | 신뢰도·주의 |
|---|---|---|---|---|
| 1 | 숙련 운용자의 직접 통제 한계 | 통제 3대, 감독 15대 | [Porat et al. 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC4878290/) | 동료심사 리뷰, 원문 확인 |
| 2 | 대기시간을 넣으면 1인 상한이 줄고, 손실 대부분은 '못 알아챈 시간' | 상한 36~67% 감소, WTSA가 대기의 63~72% | [Cummings & Mitchell 2008](https://dspace.mit.edu/handle/1721.1/90280) | 원문 확인. 동종 UAV 4대, 피험자 12명. |
| 3 | 점유율 문턱 | 70% 초과 시 성능 저하, 60~70%에서 점수 최고 | [Cummings & Mitchell 2008](https://dspace.mit.edu/handle/1721.1/90280), [Donmez et al. 2010](https://dspace.mit.edu/handle/1721.1/87059) | 70% 원전(2007)은 원문 미확인, 재인용 2건으로 교차 확인 |
| 4 | DARPA OFFSET 최종 실험 | 이종 100대 이상(UAV ≤139, UGV 44), 과부하 3.2% | [arXiv 2308.00102](https://arxiv.org/abs/2308.00102), [army.mil](https://www.army.mil/article/252556) | 실제는 지휘관+보조 2인. "빈번히 넘음"과 측정 단위가 다름. |
| 5 | 영국 Dstl 2025 | 운용자 1명이 이종 3대(UAV 1 + UGV 2), "UK first" | [GOV.UK](https://www.gov.uk/government/news/successful-trial-paves-the-way-for-improved-reconnaissance-on-army-operations) | 정부 공식, 원문 확인 |
| 6 | 미 육군 문제 정의 | "Today, everything has its own controller." / 2026-08 공모 "stove-piped control systems", "policy-based" | [Breaking Defense](https://breakingdefense.com/2025/04/army-eyeing-first-human-machine-integrated-formations-in-2027-common-controller-for-robotics/), [Inside Unmanned Systems](https://insideunmannedsystems.com/army-seeks-commercial-controllers-for-drones-and-ground-robots-under-new-c2-architecture/) | 원문 확인 |
| 7 | DIU·DAWG Orchestrator | 상금 1억 달러, "vehicle-agnostic" | [DIU](https://www.diu.mil/latest/diu-and-dawg-launch-autonomous-vehicle-orchestrator-prize-challenge) | 1차 출처. 여러 팀 수상 구조. |
| 8 | 한국 육군 유무인 분대 | 8명 = 전투원 4 + 운용요원 4, 플랫폼 4종 | [뉴스스페이스](https://www.newsspace.kr/news/article.html?no=15018) | 원문 확인. 1인당 대수는 미언급. |
| 9 | 한국 인력 절벽 | 20세 남성 22.4만(2025) → 14.3만(2040). 병사 비중 60% → 37%(2040), 드론 30배. | [중앙일보 via Daum](https://v.daum.net/v/20251006170145067), [아이뉴스24](https://www.inews24.com/view/2001302) | 원문 확인. "1인당 대수 증가"는 추론. |
| 10 | 북한 GPS 교란 | 2010~2024년 장애 7,270건, 2024년 선박 1,157건(역대 최다) | [세계일보](https://www.segye.com/newsView/20241117507200), [안전신문](https://www.safetynews.co.kr/news/articleView.html?idxno=233748) | 의원실 공개 정부 자료. 회차 합계와 45건 불일치. |
| 11 | 2012 인천 S-100 추락 | GPS 상실 → 운용자 오대응 → 지상통제소 충돌, 사망 1, 부상 2 | [Shephard](https://shephardmedia.com/news/uv-online/heli-pacific-2012-schiebel-s-100-crash-due-loss-gp), [AIN](https://www.ainonline.com/aviation-news/defense/2012-06-01/uav-crash-korea-linked-gps-jamming) | 제조사 설명. '오대응' 문구는 검색 스니펫. 공식 보고서 미공개. |
| 12 | MAVLink 무인증 원격 셸 | PX4 CVE-2026-1579, CVSS 9.8 | [CISA](https://www.cisa.gov/news-events/ics-advisories/icsa-26-090-02) | 정부 공식 |
| 13 | 우크라이나 FPV 물량과 EW 손실 | 2025년 약 300만 대, 절반 이상이 재밍으로 격추되고 상당수는 아군 재밍 | [Ukrainska Pravda](https://www.pravda.com.ua/eng/news/2025/12/24/8013217), [CTC Sentinel](https://ctc.westpoint.edu/moving-targets-implications-of-the-russo-ukrainian-war-for-drone-terrorism/) | 물량은 정부 발표. EW 비율은 "reportedly". |
| 14 | 소프트웨어로 줄인 운용 인원 | 드론 3대 기준 9명 → 3명 | [Ukrainska Pravda/WSJ](https://www.pravda.com.ua/eng/news/2025/09/03/7529154/) | 회사·익명 장교 출처, 독립 검증 없음 |
| 15 | 안전 필터의 실전 실적과 수용성 원칙 | Auto-GCAS 2014년 이후 16명 구조. 우선순위 "do no harm → do not interfere → prevent collisions" | [Air Force Times](https://www.airforcetimes.com/news/your-air-force/2024/11/20/could-a-fighter-jet-software-upgrade-have-saved-this-pilots-life/), [Hobbs et al.](https://arxiv.org/abs/2110.03506) | 구조 수가 출처마다 다름(8/13/16). 16명은 공군 집계 보도. |

3분 피치에서는 1·2·8·10·11·12번이 문제 제기를 맡고, 5·6·7번이 군 적용 가능성을, 15번이 '어떻게 안전한지 아느냐'의 답을 맡는 순서가 자연스럽다(팀 판단). 시장 규모는 정의마다 편차가 커서 2차 발표에서 하나만 출처와 함께 쓴다.

## 심사위원이 물을 13가지와 근거 있는 답

### 미군 장교가 물을 질문

**"한 사람이 정말 몇 대를 감당하나? 그 숫자의 근거는?"** 숫자는 상수가 아니라 기체의 방치 가능 시간, 상호작용 시간, 대기시간의 비율로 정해진다. 우리는 그 값을 로그로 직접 재서 `FO_hat`으로 보여 준다. 기준선은 학계 수치다. 숙련 운용자의 직접 통제는 3대, 감독은 15대([Porat et al. 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC4878290/))이고, 플레이 기반 감독으로 IMPACT는 시뮬 12대([Draper et al. 2017](https://corescholar.libraries.wright.edu/isap_2017/85))를 관리했다. OFFSET의 100대 이상은 2인 팀의 결과라고 먼저 밝힌다([army.mil](https://www.army.mil/article/252556)). 우리 데모의 수치는 시뮬레이션에서 소수 운용자로 잰 값이며 일반화된 비율이 아니라고 정직하게 말한다.

**"교전·무장 결정은 누가 하나? DoDD 3000.09와 맞나?"** 탐지는 보고 단계를 거치고 대응은 운용자가 고른다. 이 구조는 지침이 정의한 반자율 체계, 즉 "only engage individual targets or specific target groups that have been selected by a human operator"와 같다([Wikipedia: DoDD 3000.09](https://en.wikipedia.org/wiki/Department_of_Defense_Directive_3000.09)). 안전 바닥은 지침 1.2.a.(1)(b)를 기능으로 구현했다. 시간·지리 경계 밖에서는 "terminate the engagement or obtain additional operator input"한다. HMI는 "which actions the system will perform"을 표시한다([DoDD 3000.09](https://web.archive.org/web/2024id_/https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodd/300009p.pdf)). 정찰 중심 데모는 비무장 플랫폼이라 지침 적용 대상이 아니라는 점도 알고 있다고 밝힌다.

**"GPS 재밍이나 링크 상실이 오면?"** 모든 플레이에 링크 상실 시 행동이 정의돼 있다. FAA 정의대로 "predictable or planned maneuver"를 한다([FAA P/CG](https://www.faa.gov/air_traffic/publications/atpubs/pcg_html/glossary-l.html)). 기체 쪽에는 ArduPilot의 GCS 하트비트 5초 페일세이프가 그대로 남는다([ArduPilot](https://ardupilot.org/copter/docs/gcs-failsafe.html)). 교란은 한 구역을 통째로 치기 때문에, 역할은 다른 도메인 기체로 재연결하고 경보 N개는 사건 1건으로 묶는다. 이것은 2012년 인천 S-100 사고에서 얻은 교훈이다([Shephard](https://shephardmedia.com/news/uv-online/heli-pacific-2012-schiebel-s-100-crash-due-loss-gp)). 2026년 2월 Starlink 차단으로 일부 전선에서 공세가 멈춘 사례([NV](https://english.nv.ua/amp/russian-field-operations-crippled-after-starlink-cut-50581450.html))도 단일 링크 전환만으로는 부족하다는 근거다.

**"기존 체계(TAK, MAVLink, STANAG 4586)와 붙나?"** 기체 쪽은 MAVLink다. ArduPilot SITL로 실제 오토파일럿 펌웨어가 도는 공중·지상·해상 기체를 붙인다([ArduPilot SITL](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html)). 상황도는 CoT로 ATAK에 내보낸다([pytak](https://github.com/snstac/pytak)). 구조는 STANAG 4586의 VSM(Vehicle Specific Module) 개념처럼 기체별 어댑터 위에 공통 코어를 얹었다고 설명한다([NATO STO](https://www.sto.nato.int/publications/STO%20Educational%20Notes/STO-EN-SCI-271/EN-SCI-271-03.pdf), 검색 요약). STANAG 메시지 자체를 구현하지는 않았다고 구분한다. 미 육군 2026-08 공모가 MOSA를 필수로 요구한다는 점과도 연결된다([Inside Unmanned Systems](https://insideunmannedsystems.com/army-seeks-commercial-controllers-for-drones-and-ground-robots-under-new-c2-architecture/)).

### 업계 CEO가 물을 질문

**"Lattice나 Hivemind가 이미 하는 것 아닌가?"** Shield AI는 기체 쪽 'AI 파일럿'을 다른 회사 기체에 넣는 사업이다. Saronic은 Echelon이 자사 자율 스택을 위해 만들어졌다며 수직 통합을 택했다([Seapower](https://seapowermagazine.org/saronic-unveils-echelon-a-unified-platform-for-mission-planning-simulation-and-command-and-control-of-autonomous-surface-vessels/)). 국방부가 기존 자율 스택을 고치지 않는 벤더 중립 오케스트레이터에 1억 달러 상금을 따로 건 것 자체가, 이 계층이 아직 풀리지 않았다는 신호다([DIU](https://www.diu.mil/latest/diu-and-dawg-launch-autonomous-vehicle-orchestrator-prize-challenge)). 그리고 이번 조사에서 운용자 부하를 정량 공개한 업체는 찾지 못했다. 1위 업체의 NGC2도 접근통제·감사 문제로 "very high risk" 평가를 받았다([The Defense Post](https://thedefensepost.com/2025/10/09/us-army-security-platform-prototype/amp/)). 우리는 각 사의 자율 위에 얹는 계층이며, 부하 측정과 명령 감사로 차별화한다.

**"누가 사고, 어떻게 들어가나?"** 미국에서는 육군 UAS Marketplace 공모, DIU Orchestrator 스프린트, 90일 주기의 Swarm Forge Crucible이 진입로다([DefenseScoop](https://defensescoop.com/2026/03/31/pentagon-preparing-drone-swarm-crucible/)). Oregon UAS Accelerator는 TRL 3부터 받아 준다([Unmanned Airspace](https://www.unmannedairspace.info/uncategorized/oregon-uas-accelerator-launches-2026-challenge/)). 한국에서는 성숙 기술 12개월 신속시범사업([파이낸셜뉴스](https://www.fnnews.com/news/202609180858361306))과 방산 챌린지([MTN](https://news.mtn.co.kr/news-detail/2026040816371870009))가 있다. 수요의 근거는 육군 유무인 분대의 단계적 확대(2027 중대급, 2028 대대급)([뉴스스페이스](https://www.newsspace.kr/news/article.html?no=15018))와 해군의 '공통 아키텍처' 과제([파이낸셜뉴스](https://www.fnnews.com/news/202609080904320627))다. 국내 대기업이 해외 자율 SW와 손잡는 흐름 속에서 국산 중립 계층이 주권 측면의 논리를 갖는다는 주장은 추정이므로 그렇게 표시한다.

**"플레이는 누가 만들고, 현장 SOP가 바뀌면?"** 플레이 작성은 운용자가 아니라 계획 참모가 임무 전에 한다. DAWG 국장도 지휘관이 "programming behaviors"를 하지 않게 하겠다고 했다([ExecutiveGov](https://www.executivegov.com/articles/diu-dawg-navy-challenge-av-orchestrator)). 새 플레이나 수정된 플레이는 배치 전에 시뮬레이션 시드 세트로 회귀 시험을 통과해야 한다. 이것은 DoDD 3000.09의 "validate that critical safety features have not been degraded"와 "reprogrammed with sufficient rapidity"를 구현한 것이다([DoDD 3000.09](https://web.archive.org/web/2024id_/https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodd/300009p.pdf)). 러시아 Rubicon이 대응책 학습 주기를 약 6주로 줄였다는 분석([drone-warfare.com](https://drone-warfare.com/research/russia-unmanned-forces/), 신뢰도 낮음)은 플레이를 빨리 갱신하는 능력이 곧 전투력이라는 점을 보여 준다.

### 한국대드론산업협회가 물을 질문

**"대드론 임무에 어떻게 쓰나?"** 2022년 북한 무인기 5대 침투 때 한 대도 격추하지 못했고, 일부는 추적 중 레이더에서 사라졌다([AP via KTVU](https://www.ktvu.com/news/south-korean-military-north-korea-drones)). 대드론은 바로 '탐지가 다른 기체의 역할을 낳는' 임무다. 레이더나 공중 기체가 탐지하면 보고 단계를 거치고, 운용자가 '식별'이나 '추적 인계' 플레이를 고르면 시스템이 가능한 기체에 역할을 묶는다. 트랙을 잃으면 마지막 위치와 예상 위치로 재획득 역할을 만든다. 미국도 Replicator 2를 소형무인기 대응에 배정했다([Defense News](https://www.defensenews.com/pentagon/2024/09/30/small-drone-defense-is-next-in-pentagons-replicator-buying-push/)). 아군 재밍이 아군 드론을 떨어뜨리는 문제([CTC Sentinel](https://ctc.westpoint.edu/moving-targets-implications-of-the-russo-ukrainian-war-for-drone-terrorism/))도 있다. 같은 구역 아군 자산을 한 화면에 묶는 디컨플릭션이 대드론 현장의 실제 요구다.

**"한 대가 해킹당하면 함대 전체가 넘어가지 않나?"** 그 위험이 실제로 있어서 기체별 키를 쓴다. MAVLink 2 서명은 공유 대칭키라 한 기체만 털려도 함대 전체 인증이 무너진다([NVD CVE-2020-10282](https://nvd.nist.gov/vuln/detail/CVE-2020-10282)). 서명이 꺼진 PX4는 무인증 원격 셸을 허용했다([CISA](https://www.cisa.gov/news-events/ics-advisories/icsa-26-090-02)). 우리는 Zero Trust의 "Presume Breach"([DoD ZT Strategy](https://web.archive.org/web/2024id_/https://dodcio.defense.gov/Portals/0/Documents/Library/DoD-ZTStrategy.pdf))에 따라 기체를 하나씩 격리할 수 있게 했다. 이상한 기체는 신뢰 점수를 깎아 고위험 역할에서 빼고, 안전 모드로 돌린 뒤 운용자 확인 없이는 복귀시키지 않는다. 한국 정책은 아직 기기 인증과 업체 관리에 머물러 있다([정책브리핑](https://www.korea.kr/briefing/policyBriefingView.do?newsId=156768313), [보안뉴스](http://www.boannews.com/news/articleView.html?idxno=136514)). 운용 단계의 피해 한정이 우리가 메우는 공백이다.

### 해양대 교수가 물을 질문 (2차)

**"해상 무인체계는 운용이 무엇이 다른가?"** 해상 기체는 방치 가능 시간이 길고 원거리 위성 링크에 의존한다. 미 해군 중형 USV는 대부분 자율 모드로 항해하고, 육상 운용센터가 "supervised autonomy"로 임무를 바꾸는 모델을 쓴다([USNI News](https://news.usni.org/2024/01/16/navy-wraps-first-unmanned-surface-deployment-to-westpac), 검색 요약). TF59는 AI가 이상을 탐지하면 사람이 결정하는 구조다([USNI News](https://news.usni.org/2022/10/11/navy-wants-100-unmanned-ships-monitoring-middle-east-waters-by-next-year), 검색 요약). 한국 쪽에서는 한화시스템이 LEO 위성통신으로 AUV와 무인수상정을 동시에 통제했다([한화시스템](https://www.hanwhasystems.com/kr/prcenter/newsView.do?bbidx=812)). 해군은 Navy Sea GHOST의 과제로 '공통 아키텍처'를 꼽았다([파이낸셜뉴스](https://www.fnnews.com/news/202609080904320627)). 서해에서는 2024년 선박 GPS 장애가 1,157건이었다([세계일보](https://www.segye.com/newsView/20241117507200)). 그래서 해상 역할은 예외 기반 경보, 정박점이나 배회 위치로 가는 lost-link 플레이, 교란 시 다른 도메인으로의 재연결을 기본으로 둔다. 우크라이나 Magura가 FPV 모선으로 쓰인 사례([UNITED24](https://united24media.com/war-in-ukraine/magura-sea-drones-goes-from-hunter-to-fpv-mothership-striking-russian-radars-in-crimea-21274), 교전국 주장)는 해상-공중 협동 역할의 실전 근거다.

### 누구든 물을 질문

**"SUPPORTY와 무엇이 다른가?"** SUPPORTY는 한 사람이 음성으로 여러 대를 만질 수 있다는 것을 실물로 보여 줬다. 우리는 한 사람이 여러 대를 맡겨도 안전하다는 것을 숫자로 보여 준다. 구체적으로는 임무 배정이 실제로 계산되고, 역할이 자동으로 다시 연결되며, 부하가 측정되고, 사람을 포함한 모든 명령이 같은 안전 바닥을 지난다. 근거는 SUPPORTY 코드의 랜덤 큐와 `pend>=4` 규칙이다([console.html](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L660-L675)). 다만 발표에서는 상대 코드를 지적하기보다 우리 측정치를 보여 주는 쪽으로 답한다.

**"인지부하가 줄었다는 것을 어떻게 증명했나?"** 같은 시나리오 시드와 같은 이벤트 도착률로 '기체별 수동 명령 모드'와 '역할 모드'를 돌려 비교했다. busy-time(70% 선과 40% 과소부하 밴드), 10분당 경보 수, 결정 수 대 명령 수, 역할 공백 시간, 임무 성공률을 함께 보여 준다. 각 지표의 기준은 Cummings와 Donmez의 점유율 연구([Donmez et al. 2010](https://dspace.mit.edu/handle/1721.1/87059)), EEMUA 191 경보 벤치마크([Control Global](https://www.controlglobal.com/protect/safety-instrumented-systems/article/11382017/alarm-management-asm-alarm-management-guidelines-and-isa-182-how-do-they-stack-up-control-global)), IMPRINT의 명령 수준별 부하([Andrews et al. 2020](https://informs-sim.org/wsc20papers/014.pdf))다. 피험자는 팀원 소수이고 시뮬레이션이므로, 효과의 방향을 보인 것이지 일반화한 것은 아니라고 밝힌다.

**"안전 바닥이 임무를 방해하지 않나? 2인 승인은 1인 운용과 모순 아닌가?"** 우리 가드는 Auto-GCAS의 우선순위인 "do no harm, do not interfere"를 따른다([Hobbs et al.](https://arxiv.org/abs/2110.03506)). 그래서 거부보다 가장 가까운 안전 명령으로 수정하는 것을 먼저 한다. 개입이 시작되고 끝날 때 알리고, 불필요한 개입 수와 가드를 켠 상태의 임무 성공률을 함께 공개한다. DoDD 3000.09도 "never engaging"을 최소 위험으로 보지 않는다. 2인 승인은 핵무기의 2인 개념([Wikipedia](https://en.wikipedia.org/wiki/Two-person_rule))에서 가져왔지만, 1인 운용 전제를 지키려고 두 번째 키를 지휘관 역할 토큰이나 독립 안전 커널로 두고 드문 고위험 플레이에만 요구한다. 그로 인한 추가 지연도 지표로 보여 준다.

## 결론

이번 종합으로 생각이 가장 크게 바뀐 지점은 경쟁 축이다. 2026년의 심사위원은 "1명이 N대"를 모든 업체에게서 듣는다. Auterion은 "The one-pilot, one-drone model is obsolete"라고 하고, Anduril은 '수백 대'를 말한다. 그러나 아무도 보여 주지 않은 것은 '측정된 부하'와 '최악의 결과가 어디서 멈추는가'다. 증거를 보면 이 둘은 따로가 아니라 같은 문제의 두 면이다. 1인 다수 운용의 가장 큰 손실은 아무도 알아차리지 못한 시간(WTSA)이었다. 한국에서 실제로 사람이 죽은 경로는 GPS를 잃은 순간 과부하 운용자가 잘못 대응한 것이었다. 그래서 '인지부하 감소'를 편의 기능이 아니라 **안전 기능**으로 다시 정의할 수 있다. 런타임 가드가 사람에게도 걸린다는 설계는 사이버 방어 팀의 정체성, 북한 교란과 해킹이라는 한국 위협, DoDD 3000.09와 ASTM F3269의 문구, 그리고 1위 업체들이 비워 둔 접근통제·감사 공백이 한 점에서 만나는 위치다.

두 번째 시사점은 2차 심사용이다. 미 육군의 2026년 8월 공모에는 부하라는 단어가 없다. Orchestrator는 반복 스프린트로 평가한다. 즉 구매자는 기능을 사려 하지만 그것을 평가할 계측 도구는 비어 있다. 팀이 만드는 busy-time, 역할 공백 시간, 명령원별 차단·수정 기록과 rule-of-three 통계는 데모의 장식이 아니다. 여러 업체의 오케스트레이터를 같은 시나리오로 비교하는 **평가 하네스**로 확장될 수 있다. 이것이 해외로 가져갈 수 있는 제품 가설이다. 다만 이 마지막 가설은 근거 문서가 없는 추론이므로, 멘토링 시간에 미군·업계 심사위원에게 직접 확인할 질문으로 남겨 둔다.
