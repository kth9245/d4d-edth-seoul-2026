# 무인체계 군집·지상통제(GCS)에 대한 사이버·전자전(EW) 위협 — 1인 다수 통제 관점 사실 기반

> 작성일·접속일: 2026-10-08 (아래 모든 URL 접속일 동일, 별도 표기 없으면 "접속 2026-10-08").
> 출처 구분 태그: **[공식]** 정부·군·국제기구 발표/정부 제출자료, **[의원실]** 국회의원이 부처 자료를 받아 공개, **[언론]** 언론 보도, **[주장]** 당사자 일방 주장(미검증), **[학술]** 논문, **[CVE]** NVD/CISA 등록 취약점, **[업계]** 기업·벤더·분석업체 자료.
> 원문 인용은 원어 그대로 둔다. 일부 인용은 WebFetch/검색 요약 도구가 뽑아 준 문장이라 원문 대조가 필요할 수 있다. 그런 경우 "(요약도구 추출)"로 표시했다.

---

## Q1. 북한의 대남 GPS 교란·기만: 회차별 날짜·수치, 공식 발표, 무인체계 영향, 2025~2026 현황

### Takeaway
과기정통부 자료를 바탕으로 한 의원실 공개 집계에 따르면 2010년 8월부터 2024년 11월 13일까지 북한 GPS 교란으로 기지국·항공기·선박 **7,270건**의 장애가 있었다(2016년 1회에만 3,516건, 2024년 선박 1,157건은 역대 최다). 무인기에는 **2012년 5월 10일 인천 Schiebel S-100 무인헬기 추락 사망사고**가 있다. GPS 상실 뒤 운용자 대응이 잘못되어 지상통제 차량을 들이받았다. 2024년 11월 합참은 북한 교란이 "무인기 출현에 대비한 훈련" 목적이라고 평가했다. 2025년에도 교란은 이어졌다(7월 백령도 인근, 2024~2025.9 항공기 복행 46회). 2026년 7월 기준 중앙전파관리소는 "올해 백령도 인근 교란 미탐지"라고 밝혔다.

### Cited Findings

**(a) 회차별 공식 집계 (과기정통부 → 정희용 의원실, 2024-11-17 공개)** [의원실/공식자료]
- 2010.8.23~26: 기지국 181, 항공기 14, 선박 1 (합 196) / 2011.3.4~14: 기지국 145, 항공기 106, 선박 10 (합 261) / 2012.4.28~5.13: 기지국 109, 항공기 1,016, 선박 254 (합 1,379) / 2016.3.31~4.5: 기지국 1,794, 항공기 1,007, 선박 715 (총 3,516건) / 2024.3.5~11.13: 기지국 1, 항공기 805, 선박 1,157 — [안전신문 2024-11-18](https://www.safetynews.co.kr/news/articleView.html?idxno=233748)
  - 원문: "2010년 8월 23~26일간 기지국 181국, 항공기 14대, 선박 1척" / "2012년 4월 28일~5월 13일간 기지국 109국, 항공기 1016대, 선박 254척" / "2016년 3월 31일~4월 5일간 기지국 1794국, 항공기 1007대, 선박 715척으로 총 3516건" / "올해 3월 5일~11월 13일간 기지국 1국, 항공기 805건, 선박 1157건" / "교란 영향으로 장애가 생긴 기지국, 항공기, 선박은 총 7270건으로 나타났다." (요약도구 추출)
- 같은 자료의 누적 세부: 기지국 2,230 / 항공기 2,948 / 선박 2,137, 총 7,270건 — [세계일보 2024-11-17](https://www.segye.com/newsView/20241117507200)
  - 원문: "선박은 올해 1157건이 발생해 2016년 715건에 비해 1.6배 늘어났다." / 정희용 의원: "GPS 전파 교란은 단순한 도발을 넘어 명백한 국제법 위반이며 우리 국민의 생명과 안전을 직접적으로 위협하는 테러 행위"
  - **불일치 주의**: 회차별 합(196+261+1,379+3,516+1,963=7,315)이 발표 총계 7,270과 45건 다르다(필자 계산). 공식 원자료로 확인하지 못했다.
- 2016년 진행 중 중간집계(2016-04-05 기준): 항공기 962대, 어선 약 700척, 이동통신 기지국 1,786곳 노출, 교란신호 100회, 최대 출력 45dB 초과 — [Korea Times 2016-04-05](https://www.koreatimes.co.kr/foreignaffairs/northkorea/20160405/n-koreas-gps-jamming-targets-aircraft-navigation-system) [언론, 정보소식통 인용]
  - 같은 기사는 2010~2012년 3차례 공격이 여객기 약 1,000대와 "as well as of the military's unmanned aerial vehicles"의 GPS 항법을 교란했다고 서술(요약도구 추출). 군 무인기 피해를 언급한 드문 공개 서술이다.
- 2012년 영향 항공기 수 보도는 엇갈린다: "553 civilian airliners"(2012.4.28~5.6) 또는 "618 Korean passenger planes, 48 foreign … and one U.S. military aircraft" — 검색 결과 스니펫에서 확인했고 공식 원자료로는 검증하지 못했다 ([AIN 2012-06-01](https://www.ainonline.com/aviation-news/defense/2012-06-01/uav-crash-korea-linked-gps-jamming), [The Aviationist 2012-05-12](https://theaviationist.com/2012/05/12/north-korean-electronic-warfare/)).

**(b) 2024년 회차별 상세**
- 2024년 1~8월: 항공기 533대, 선박 1,055척, 총 1,588건 신고. 월별로는 3월 40건, 4월 69건, 5월 말~6월 초 1,479건(급증). 발신지는 해주·옹진·평강·강화·청단 방향 — [RFA 2024-09-06, 박충권 의원실·과기정통부 자료](https://www.rfa.org/korean/in_focus/nk_nuclear_talks/gps_attack-09062024091432.html) [의원실/공식자료]
  - 원문: "이로 인해 전파 수신 장애를 겪은 한국의 항공기는 533대, 선박은 1천55척으로 총 1천588건의 신고가 접수됐습니다." / "한국 과기부는 북한의 GPS 전파 교란 영향을 받은 항공기와 선박이 모두 대체항법 적용 등을 통해 실제 피해 발생은 없었다고 밝혔습니다."
- 2024년 5월 말~6월 초: Lloyd's List가 AIS를 분석한 결과 일주일가량 상선 약 60척이 영향을 받았고, 5월 28일 9척이 NLL 부근에 잘못 표시됐다(검색 요약 기반). 인천시는 5.29~31 교란으로 "어선 조업손실과 선박 조난 피해"가 있었다며 교란방지장치 실험에 착수했다 — [Kuehne+Nagel 2024-06-13](https://mykn.kuehne-nagel.com/news/article/south-koreas-west-coast-targeted-with-gps-jam-13-Jun-2024) [언론/업계, 미검증]
- 2024년 6월: 한국 정부가 북한 교란 문제를 ITU·ICAO·IMO에 제기했고, ICAO는 북한을 처음으로 국명을 들어 우려를 표명했다 — [Korea JoongAng Daily 2024-11](https://www.koreajoongangdaily.com/korea/north-korea-jams-gps-signals-affecting-ships-civilian-aircraft-jcs/11215469) [언론, 검색 스니펫 기반]
- 2024년 11월 8~9일 해주·개성 일대 교란. 합참 발표: 선박 수 척과 민항기 수십 대 운항에 일부 장애, 군 작전·장비 영향 없음. 5~6월보다 신호가 약했다 — [Korea Times 2024-11](https://mobile.koreatimes.co.kr/www/nation/2024/11/103_385974.html), [SBS 2024-11-09](https://news.sbs.co.kr/news/endPage.do?news_id=N1007866765) [공식(합참)]
  - 합참(AP 인용): "We urge North Korea to stop GPS interference provocations immediately and strongly warn…" / 피해: "disrupted dozens of civilian aircraft and several vessels" — [AP via NBC News 2024-11-09](https://www.nbcnews.com/news/world/north-korean-gps-manipulation-disrupted-dozens-planes-vessels-rcna179444)
  - 여객선 신고 4건. 백령~인천 코리아프린세스호의 GPS 장애가 1시간 45분 지속됐고, 다른 선사는 "배의 위치가 실제와 다르게 표시"(기만 정황)됐다고 보고 — [YTN 2024-11-09](https://www.ytn.co.kr/_ln/0101_202411092256080011) [언론, 검색 요약 기반]
- 2024년 11월 1~10일 과기정통부 집계: 총 331건(항공기 279, 선박 52). 발신 방향 개풍·해주 — [RFA 2024-11-11](https://www.rfa.org/korean/in_focus/nk_nuclear_talks/north-west-sea-gps-signal-jamming-11112024095539.html) [공식]
  - 원문: "전파혼신으로 인한 운항사고 등 실제 피해는 발생하지 않았다고 덧붙였습니다."
- **무인기 연계 (핵심)**: 합참 공보실장은 11월 교란을 대드론 훈련으로 평가했다 — [이투데이 2024-11-12](https://www.etoday.co.kr/news/view/2418609) [공식(합참 브리핑)]
  - 원문: "지금 11월에 이뤄지고 있는 것들은 주로 무인기 출현에 대비한 훈련 목적이 많이 있다고 본다" / "북한은 8일부터 GPS 전파 교란을 시도해 닷새째 지속하고 있다." / "GPS 교란은 있다가도 없고 없다가도 있다"
  - 이후 교란은 경기·강원 북부로 넓어졌다 — [Korea Times 2024-11](https://m.koreatimes.co.kr/pages/article.asp?newsIdx=386475) [언론]
- 맥락: 2024-10 북한은 한국 무인기가 평양에 침투했다고 주장했고(10-11), 잔해를 회수했다고 주장했다(10-19). 한국 국방부: "North Korea's one-sided claims are not worth verifying, nor do they merit a response" — [Reuters via Arab News 2024-10-19](https://www.arabnews.com/node/2575886/world) [주장(북한) / 공식(국방부 무대응)]

**(c) 무인체계에 대한 직접 영향 — 2012 S-100 추락 사망사고**
- 2012-05-10 인천에서 군 평가 중이던 Schiebel S-100 Camcopter 무인헬기가 추락해 지상통제소(차량)를 들이받았다. Schiebel 엔지니어 1명이 숨지고 한국인 원격조종사 2명이 다쳤다 — [Shephard 2012-05-23](https://shephardmedia.com/news/uv-online/heli-pacific-2012-schiebel-s-100-crash-due-loss-gp) [언론/업계]
  - 원문: "The 10 May crash of a Schiebel S-100 UAV in the South Korean port city of Incheon … was caused by a loss of GPS, the company has confirmed." / Schiebel MD Neil Hunter "confirmed it was a loss of GPS that helped create the conditions for the crash." / "The engineer was killed and two others injured."
  - 사진 캡션 원문: "Jamming of its GPS receiver may have contributed to the crash of a Schiebel S-100 Camcopter UAV in Korea." — [AIN 2012-06-01](https://www.ainonline.com/aviation-news/defense/2012-06-01/uav-crash-korea-linked-gps-jamming)
  - 검색 스니펫상 AIN 본문: Schiebel은 "an incorrect response by the operators after the Camcopter lost its GPS signal led to the crash, some minutes later"라고 밝혔다. 기체에는 다중 IMU가 있어 "allow safe operation and recovery in the absence of GPS signals"라고 주장했다. 기체와 지상국의 기록장치는 화재로 소실됐다(요약도구 추출, 원문 대조 필요).
  - 같은 시기(4.28~) 개성발 교란이 김포·인천 공항 여객기를 교란했다. 2013년 국방부는 군의 S-100이 GPS 교란에 취약하다고 밝혔다(Yonhap 인용, [Altair](https://www.altair.com.pl/wiadomosci/pdf/8891) 2차 출처) [언론]

**(d) 2025~2026 현황**
- 2025-07(화요일, 기사 7-25): 백령도 인근 북한 GPS 교란. 과기정통부가 확인했고 민간 선박에 경고했다 — [NK News 2025-07-25](https://www.nknews.org/2025/07/north-korea-jams-gps-signals-near-maritime-border-leading-rok-to-warn-ships/) [공식(과기정통부 대변인)]
  - 원문: "We can confirm that there was an attempt from the North,"
- 2025-10-14: 박정훈 의원실이 국토부 비행자료와 과기정통부 교란 보고를 근거로 공개한 바에 따르면, GPS 교란으로 인한 **복행(go-around) 2024년 32회, 2025년 1~9월 14회, 합 46회** — [NK News 2025-10-14](https://www.nknews.org/?p=962298) [의원실/공식자료]
  - 원문: "North Korea's GPS jamming is a clear provocation against South Korea and poses a serious threat to flight safety,"
- 2025-10-09: ICAO 제42차 총회(2025.9.23~10.3, 몬트리올)가 북한·러시아의 GNSS 간섭을 시카고협약 위반으로 본 2025년 6월 이사회 결정을 지지했다 — [NK News 2025-10-09](https://www.nknews.org/?p=962026) [공식(ICAO)]
  - 원문: "infractions of the 1944 Convention on International Civil Aviation"
- 2026-07-03: 과기정통부 중앙전파관리소는 2026년 들어 백령도 인근에서 북한 GPS 교란을 탐지하지 않았다 — [NK News 2026-07-03](https://www.nknews.org/2026/07/no-reports-of-north-korean-gps-jamming-near-maritime-border-seoul-says/) [공식(관계자 발언)]
  - 원문: "observed no North Korean GPS jamming near Baengnyeong Island"
- 나무위키에는 2025-12-05~2026-01-13 87건 추가 확인이라는 서술이 있으나 원자료를 확인하지 못했다 — [나무위키](https://namu.wiki/w/%EB%B6%81%ED%95%9C%EC%9D%98%20%EB%8C%80%EB%82%A8%20GPS%20%EA%B5%90%EB%9E%80%20%EB%8F%84%EB%B0%9C) [미검증]
- OPSGROUP은 2024년 새 스푸핑 지역으로 "North/South Korea border areas"를 명시했다 — [OPSGROUP GPS Spoofing Technical Guide 2024-09](https://ops.group/dashboard/wp-content/uploads/2024/09/GPS-Spoofing-Technical-Guide-WG2024-OG2.pdf) [업계]

### Inferences
- 한반도 교란은 일회성이 아니라 14년 넘게 반복된 상시 위협이다. 1회 영향 범위는 수백~수천 대에 이른다. 한 지역의 **모든 비행체·선박이 동시에** 영향을 받는 공통모드(common-mode) 장애라는 점이 중요하다. 1인이 3대 이상 이종 무인체를 운용하는 콘솔이라면 GPS 장애 경보가 여러 대에서 동시에 뜨는 상황을 전제로 설계해야 한다.
- S-100 사례의 원인 구도는 'GPS 상실 → 운용자 오대응 → 몇 분 뒤 지상통제소 충돌 사망'이다(제조사 설명). EW 사건이 **운용자 인지부하와 절차 오류를 거쳐** 치명적 결과로 이어진 한국 내 실례다. "과부하 운용자가 치명적 결과를 내지 못하게 막는다"는 팀 목표의 직접 근거로 쓸 수 있다.
- 합참이 교란 목적을 "무인기 대비 훈련"으로 본 것은 북한 GPS 교란이 **한국 무인기를 겨냥한 대드론 수단**으로 운용된다는 공식 평가로 읽힌다.
- 정부가 매번 "실제 피해 없음"이라고 한 근거는 유인기·선박의 대체항법(관성·지상항법·육안)이다. 사람이 탑승하지 않고 GPS 의존도가 높은 소형 무인체는 같은 조건에서 더 취약하다고 추정된다.

### Gaps
- 2024년 5.29~6.2 회차만 따로 낸 과기정통부 공식 수치는 찾지 못했다. RFA의 "5월 말~6월 초 1,479건"이 가장 가까운 공식 계열 수치다. "약 500대 항공기·수백 척"(AP 계열)은 원문을 특정하지 못했다.
- 2024년 집계 기준이 출처마다 다르다(박충권: 1~8월 항공기 533·선박 1,055 / 정희용: 3.5~11.13 항공기 805·선박 1,157 / 11.1~10 331건). 국토부 "2024년 1~8월 항공기 교란 578건 중 북한발 533건"은 검색 스니펫으로만 봤다.
- 군 무인기(송골매, RQ-4, 소형 정찰드론 등)가 교란으로 손실·임무 실패했다는 공식 공개 자료는 찾지 못했다(합참은 매번 "군 피해 없음").
- 2025년 연간 총계, 2026년 서해 외 지역(경기·강원 북부) 교란 여부는 확인하지 못했다.
- 2012 S-100 사고의 공식 조사 보고서는 공개 자료로 찾지 못했다(기록장치 소실).

---

## Q2. 우크라이나·러시아, 발트해, 중동의 GNSS 교란·기만과 드론 영향 (수치)

### Takeaway
GNSS 교란은 이제 전 세계 상시 위협이다. 발트해 6개국이 ICAO에 낸 자료에 따르면 2025년 1~4월 **122,607편**이 간섭을 받았고, 4월에는 해당 공역 항공편의 27.4%(일부 지역 42% 초과)가 영향을 받았다. 2026년 이란 전쟁 국면에서 걸프 해역 간섭 이벤트는 1분기 약 **978,000건**이었다(업계 집계). 우크라이나에서는 RUSI(2023)가 월 **1만 대** 드론 손실, 즉 대부분 러시아 EW 탓이라고 추정했다. 러시아가 칼리닌그라드 송신기로 우크라이나 드론을 NATO 영공 쪽으로 돌린다는 보도(2026-05)도 있다.

### Cited Findings

**발트해·북유럽 (2024~2026)**
- 2025년 1~4월 365개 항공사 **122,607편**이 GNSS 간섭을 겪었다. 스웨덴·에스토니아·핀란드·라트비아·리투아니아·폴란드 공동으로 ICAO 이사회에 보고했다. 2025년 4월 평균 **27.4%**, 일부 지역 **42% 초과**. 발신원은 칼리닌그라드·상트페테르부르크·스몰렌스크·로스토프로 지오로케이션됨 — [Anadolu 2025](https://www.aa.com.tr/en/europe/report-says-russian-gps-jamming-disrupted-123-000-flights-over-baltic-airspace/3680588), [GPS World](https://www.gpsworld.com/123000-flights-disrupted-by-gnss-jamming/) [공식(정부 공동보고) via 언론]
  - 원문(요약도구 추출): "Between January and April 2025, a total of 122,607 flights operated by 365 airlines experienced interference" / "In April alone, an average of 27.4% of flights within the affected airspace encountered disruption; in some areas the proportion exceeded 42%."
- 리투아니아 월별 간섭 건수: 2024-03 556 → 2024-10 890 → 2025-01 1,185. 에스토니아 2024-10 1,150, 2025-01 1,085. "Since August 2024, a dramatic increase in jamming and spoofing of GNSS signals for aircrafts has been recorded" — [EU 이사회 문서 ST-9188-2025 (2025-05, 리투아니아·에스토니아·핀란드 제출)](https://data.consilium.europa.eu/doc/document/ST-9188-2025-INIT/en/pdf) [공식]
- 라트비아 항행서비스: 2022년 연간 26건 → 2025년 8월 한 달 195건. 스웨덴: 2023년 55건 → 2025년 733건(무엇을 센 건수인지 스니펫에 명시 없음) — [Al Arabiya 2025-09-04](https://english.alarabiya.net/News/world/2025/09/04/sharp-rise-in-gps-jamming-in-aviation-over-baltic-sea-sweden-), [Moscow Times 2025-09-04](https://www.themoscowtimes.com/2025/09/04/sweden-accuses-russia-of-widespread-gps-jamming-over-baltic-sea-a90427) [공식 via 언론, 검색 스니펫. 라트비아 수치는 원 기사를 특정하지 못함]
- 2025-10-03 ICAO 총회에서 핀란드·에스토니아가 러시아를 지목했고, 핀란드 해경은 2025-10-31 "4월 이후 발트해 위성항법 상시 교란"을 보고했다 — 검색 요약 기반 ([GPS World: 13 EU member states](https://www.gpsworld.com/13-eu-member-states-demand-action-on-gnss-interference/))
- 2026: 스웨덴 교통청 접수 GNSS 간섭은 2026-05-28까지 142건(2025년 같은 기간 약 336건). "no clear signs of a decline since late winter". 리투아니아는 칼리닌그라드 스푸핑 안테나가 2025년 초 수 개에서 수십 개로 늘었다고 함 — [NordiskPost 2026-07-19](https://www.nordiskpost.com/2026/07/19/baltic-sea-gnss-interference-russia/) [공식 via 언론]
- 폴란드 2026: 5~6월 약 70%의 날에 전 GNSS 대역 장기 교란(무간섭일은 5월 10%, 6월 13%). 8월 1~19일 63%의 날 전면 교란. 기만 가능 거리는 최대 450km로 보도됨. "Recreational and commercial drone flights are also becoming more difficult" — [Euronews 2026-08-25](https://www.euronews.com/my-europe/2026/08/25/phones-drones-and-ships-running-blind-as-gps-malfunctions-across-poland) [언론(측정소 자료 인용)]
- 2026-09-17~18 스웨덴 상공 여객기 2편이 GPS 교란·기만을 겪었다 — [avi-go 2026](https://avi-go.com/news/articles/8fb0aeaf7980ab95b074561de288ea5f) [언론, 제목 기준]

**러시아의 우크라이나 드론 '탈취·유도' 주장 (2026)**
- Telegraph 보도(Yle 2026-05-25 재인용): 러시아가 칼리닌그라드 송신기로 우크라이나 드론을 공중에서 "hijacking"해 핀란드 등 NATO 영공 쪽으로 돌린다는 주장. 영국 항법학회 Ramsay Faragher는 시간코드 혼란이 비행 중 재부팅·셧다운과 추락을 부를 수 있다고 설명했다 — [Yle 2026-05-25](https://yle.fi/a/74-20227778) [언론 보도, 미검증]
  - Keir Giles 원문: "There is no reason for Russia to stop, because there will be no costs or consequences imposed on Moscow"

**우크라이나 전장 (드론 대상 EW)**
- RUSI 『Meatgrinder: Russian Tactics in the Second Year of Its Invasion of Ukraine』(2023-05): 우크라이나 UAV 손실 월 약 10,000대, 전선 약 10km마다 주요 EW 체계 1개 — [Task & Purpose 2023-05-20](https://taskandpurpose.com/news/ukraine-10000-drone-losses/), 원보고서 [RUSI PDF](https://static.rusi.org/403-SR-Russian-Tactics-web-final.pdf) [학술/싱크탱크]
  - 원문: "Ukraine is using enough aerial drones that it is losing 10,000 UAVs per month and has not yet run out." / RUSI 인용: "These systems are heavily weighted towards the defeat of UAVs and tend not to try and deconflict their effects." ([Business Insider 재인용](https://www.businessinsider.nl/ukraine-is-losing-10000-drones-a-month-to-russian-electronic-warfare-systems-that-send-fake-signals-and-screw-with-their-navigation-researchers-say))
  - 반론: 우크라이나 특수통신청장 Yuri Shchyhol은 정찰드론 하루 40~45대 손실이라고 말했다(월 약 1,200~1,350대, 필자 계산). 전문가 James Patton Rogers는 RUSI 수치가 "likely" 과대평가라고 봤다(같은 BI 기사).
  - 러시아군이 우크라이나 Motorola 256-bit 암호 무전을 해독해 공중 드론 타격에 활용했다는 서술(같은 T&P 기사, RUSI 인용).
- 우크라이나는 Shahed에 거짓 GPS 좌표를 주입해 경로를 돌린다. "one recent attack saw 45 percent of the drones intercepted or redirected" — [SOFREP](https://sofrep.com/news/ukraine-spoof-russian-drones-electronic-warfare/) [언론 2차, 미검증]. 관련 보도: Euronews 2024-12-04 「Perdidos y engañados: cómo Ucrania redirige drones rusos a Bielorrusia」 ([링크](https://es.euronews.com/2024/12/04/perdidos-y-enganados-como-ucrania-redirige-drones-rusos-a-bielorrusia), 제목 기준)
- EW를 피하려는 광섬유 FPV 확산. 우크라이나 제조사 발언: "Longer range spools in particular are only 30% successful at 15km compared to 80% for Russian flights up to 20km" — [The War Zone, Inside Ukraine's Fiber-Optic Drone War](https://www.twz.com/news-features/inside-ukraines-fiber-optic-drone-war) [업계 인터뷰, 검색 스니펫]

**중동 (이스라엘·이란 전쟁)**
- OPSGROUP(2024-09): 2024년 스푸핑 영향 항공편이 상반기 하루 약 300편에서 **하루 평균 1,500편**으로 늘었다 — [AIN 2024-09-09](https://backend.ainonline.com/aviation-news/air-transport/2024-09-09/opsgroup-releases-gps-spoofing-workgroup-report) [업계]
  - 2023-11까지 OPSGROUP에 50건 보고. 동지중해(카이로·텔아비브·베이루트 중심). 한 항공기는 벤구리온 상공으로 표시됐지만 실제로는 최대 212nm 떨어져 있었다 — [OPSGROUP Technical Guide](https://ops.group/dashboard/wp-content/uploads/2024/09/GPS-Spoofing-Technical-Guide-WG2024-OG2.pdf), [AIN 2023-11-08](https://ainonline.com/aviation-news/air-transport/2023-11-08/gps-spoofing-incidents-increase-middle-east)
- Windward(해운 분석): 2025년 하반기 전 세계 GPS 교란 영향 선박 **18,300척 초과**(3분기 약 11,600, 4분기 약 6,700). 2026년 1분기 전 세계 약 **978,000 이벤트**, 그중 **98%가 중동 걸프**, 걸프 내 직접 영향 선박 1,100척 초과. 개전(2026-02-28, "Operation Epic Fury") 첫 2주 1,650척 초과(페이지 안 수치끼리 불일치 있음). 2025-10 초 카타르 교통부가 GPS 장애로 이틀간 해상 항행을 "temporarily halted" — [Windward 2026](https://windward.ai/blog/gps-jamming-is-mainstream-changes-between-2025-and-2026/) [업계]
- CNN(2026-03-06) 「Ships and planes are vulnerable to GPS jamming. The Iran war is revealing just how bad the problem is」 — [CNN](https://www.cnn.com/2026/03/06/science/gps-jamming-ships-planes-iran-war) (본문 접근 불가, HTTP 451, 제목만 확인)

**고전적 시연·사례**
- 2012-06-19 미 화이트샌즈(DHS GYPSY 시험): UT Austin Todd Humphreys 팀이 1,000달러 미만 장비로 GPS 스푸핑해 소형 무인헬기 고도를 속여 하강시켰다. "the first known unequivocal demonstration that commandeering a UAV via GPS spoofing is technically feasible" — [UT Austin](https://ae.utexas.edu/?p=8578), [GPS World](https://www.gpsworld.com/drone-hack/) [학술 시연]
- 2011-12 RQ-170 이란 포획: 익명의 이란 엔지니어는 통신 재밍으로 자동비행 모드를 유도한 뒤 GPS 스푸핑으로 칸다하르 기지에 착륙하는 것처럼 속였다고 **주장**했다("By putting noise jamming on the communications, you force the bird into autopilot"). 미 당국자는 "ludicrous"라고 일축했다 — [CSM 2011-12-15](https://proof.csmonitor.com/World/Middle-East/2011/1215/Exclusive-Iran-hijacked-US-drone-says-Iranian-engineer), [Fox News](https://www.foxnews.com/tech/iran-hijacked-spy-drone-with-gps-hack-ridiculous-official-says) [주장, 미검증]. UT 팀도 이 주장을 "implausible"로 봤다(위 UT 자료).

### Inferences
- 발트해의 27~42%, 폴란드의 70%-of-days 같은 수치는 GNSS 간섭이 '사건'이 아니라 '작전 환경 상수'라는 뜻이다. 다수 무인체 운용 콘솔은 GNSS 무결성 상실을 기본 시나리오로 놓고 설계해야 한다(대체항법, 자동 귀환·정지 정책, 운용자 경보 묶기).
- 기만(spoofing)은 교란(jamming)보다 위험하다. 조용히 위치를 틀어 다수 기체를 **동시에, 같은 방향으로** 끌고 갈 수 있다(칼리닌그라드 유도 주장, Shahed 유도 사례). 1인 다수 통제 시스템에서는 개별 기체 이상 탐지와 함께 **군집 단위의 상관된 위치 편이 탐지**가 필요하다.

### Gaps
- 2025~2026 발트해 연간 총 항공편 수치, 국가별 항공편 단위 수치는 찾지 못했다.
- 이스라엘 발 스푸핑의 2025~2026 정량 수치는 찾지 못했다(OPSGROUP 2025 업데이트 미확인).
- 러시아의 '우크라이나 드론 NATO 쪽 유도' 주장은 Telegraph 단일 보도이고 대수 등 정량 정보가 없다.
- RUSI 원문 PDF는 크기 제한으로 직접 열람하지 못했다(2차 보도로 인용).

---

## Q3. 지휘통제 링크·GCS 침해: MAVLink 무인증, 서명(signing) 채택·약점, CVE(2020~2026), 학술 공격, 실제 사례, 함대 전체 위험

### Takeaway
MAVLink는 기본값이 무인증이다. CISA는 2026-03-31 PX4 CVE-2026-1579(CVSS **9.8**)를 공지했다. 서명이 꺼져 있으면 누구나 SERIAL_CONTROL로 **셸 명령을 실행**할 수 있다는 내용이다. MAVLink 2 서명은 인증만 하고 암호화는 하지 않는다. 미서명 패킷 수용 규칙은 구현에 맡겨져 있고, **모든 장치가 같은 대칭키를 공유**하는 구조라 기기 하나만 털려도 함대 전체 인증이 무너진다(CVE-2020-10282 서술). 실제 사례로는 SkyGrabber(2009), Creech GCS 키로거 감염(2011), Spiderweb(2025, 117대를 적국 LTE로 조종), Ghost Robotics 4족 UGV 탈취 취약점(CVE-2025-41108, MAVLink 기반)이 있다.

### Cited Findings

**MAVLink 프로토콜 자체**
- [CVE] **CVE-2020-10282** (CVSS 9.8, 2020-07-03): "The Micro Air Vehicle Link (MAVLink) protocol presents no authentication mechanism on its version 1.0 (nor authorization) whichs leads to a variety of attacks including identity spoofing, unauthorized access, PITM attacks and more. … MAVLink 2.0 only provides a simple authentication system based on HMAC. This implies that the flying system overall should add the same symmetric key into all devices of network. If not the case, this may cause a security issue, that if one of the devices and its symmetric key are compromised, the whole authentication system is not reliable." — [NVD CVE-2020-10282](https://nvd.nist.gov/vuln/detail/CVE-2020-10282)
- [CVE] **CVE-2020-10283** (CVSS 9.8, 2020-08-20): 버전 협상(AUTOPILOT_VERSION)을 이용한 **MAVLink 1.0 다운그레이드로 인증 우회**. "attackers may use this method to bypass authentication capabilities and interact with the autopilot directly." — [NVD CVE-2020-10283](https://nvd.nist.gov/vuln/detail/CVE-2020-10283)
- [공식 문서] MAVLink 서명 명세 — [mavlink.io Message Signing](https://mavlink.io/en/guide/message_signing.html)
  - "MAVLink 2 adds support for message signing, which allows a MAVLink system to verify that messages originate from a trusted source."
  - "The 48 bit (6 byte) signature is the first 48 bits of a SHA-256 hash of the complete packet"
  - 미서명 수용: "MAVLink libraries should provide a mechanism that allows a system to conditionally accept unsigned packets." / "The rules for accepting these packets will be implementation specific" / 예시 규칙: "RADIO_STATUS packets are always accepted without signing" / "Accept all unsigned packets until a signed packet is received (unconditionally)"
  - 재전송 허용창: 새 스트림은 "accepted if it not more than 6 million (one minute) behind the current timestamp"
  - 키 관리: "The SETUP_SIGNING message should never be broadcast" / "The mavgen C and Python libraries support only one key per link."
- [공식 문서] ArduPilot 서명 — [ArduPilot MAVLink2 Signing](https://ardupilot.org/copter/docs/common-MAVLink2-signing.html)
  - "This does NOT encrypt the data, just merely controls if the autopilot will respond to MAVLink commands or not."
  - "USB connections are unaffected, allowing full connection to an autopilot using an unknown passkey."
  - "Communication with any serial port using MAVLink 1 is not protected."
  - 문서상 설정 절차는 Mission Planner(SETUP > Advanced > Mavlink Signing)만 설명한다.
- [CVE/공식] **CVE-2026-1579, CISA ICSA-26-090-02 (2026-03-31)**: PX4, CVSS v3.1 **9.8**, CWE-306. 영향 섹터는 "Transportation Systems, Emergency Services, Defense Industrial Base", 배포 범위는 "Worldwide". 보고자는 Dolev Aviv(Cyviation) — [CISA](https://www.cisa.gov/news-events/ics-advisories/icsa-26-090-02)
  - 원문: "The MAVLink communication protocol does not require cryptographic authentication by default." / "When MAVLink 2.0 message signing is not enabled, any message -- including SERIAL_CONTROL, which provides interactive shell access -- can be sent by an unauthenticated party with access to the MAVLink interface." / "Successful exploitation of this vulnerability could allow an attacker with access to the MAVLink interface to execute arbitrary shell commands without cryptographic authentication."
  - 완화책: "PX4 recommends enabling MAVLink 2.0 message signing as the authentication mechanism for all non-USB communication links."
- [업계] Ignitec(비동료심사): 서명은 인증만 하고 암호화는 하지 않는다. 링크가 털리면 과거 서명 패킷을 타임스탬프 허용창 안에서 재전송할 수 있다 — [Ignitec](https://www.ignitec.com/insights/mavlink-integration-in-defence-uavs-architecture-security-and-deployment-considerations/). KPMG(2025-10)가 MAVLink v2의 도청·스푸핑·DoS 내성을 시험했다(결론부는 확인하지 못함) — [KPMG NL](https://kpmg.com/nl/en/home/insights/2025/10/secure-drone-communication-an-absolute-must-for-a-reliable-uav-deployment.html)
- [학술] MAVSec(2019)은 MAVLink 2 서명 방식이 "highly vulnerable"하며 GPS 기반 타임스탬프 조작으로 키 없이 공격할 수 있다고 주장한다(스니펫만 확인) — [ResearchGate MAVSec](https://www.researchgate.net/publication/334629745_MAVSec_Securing_the_MAVLink_Protocol_for_ArdupilotPX4_Unmanned_Aerial_Systems)

**주요 CVE (NVD API 조회, 2026-10-08)**
- PX4
  - CVE-2026-32709 (2026-03-16, 5.4): MAVLink FTP 무인증 경로탐색. "allows any MAVLink peer to read, write, create, delete, and rename arbitrary files on the flight controller filesystem without authentication" — [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-32709)
  - CVE-2026-32743 (2026-03-19, 6.5): MavlinkLogHandler 스택 오버플로(MAVLink 로그 요청으로 유발) — [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-32743)
  - CVE-2026-26741 / 26742 (2026-03-10, 각 8.1): 모드 전환 로직 결함. Auto→Manual 전환 시 "rapid uncontrolled ascent (flyaway)" 가능 — [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-26741)
  - CVE-2024-38951 (2024-06-25, 6.5): "crafted MavLink message"로 DoS — [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-38951)
  - CVE-2024-24255 (2024-02-06, 4.2): 지오펜스 경쟁상태. "allows attackers to send drones on unintended missions" — [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-24255)
  - CVE-2024-30800 (5.6): 지오펜스 우회로 비행금지구역 진입 — [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-30800)
  - 그 밖에 CVE-2025-9020(MAVLink 셸 UAF), CVE-2025-15150(로그 핸들러), CVE-2021-46896(msgid 332 오버플로) 등. NVD 키워드 "PX4"에 2026-09까지 자동조종 관련 다수 등록됨.
- ArduPilot
  - **CVE-2026-38971** (2026-07-02, CVSS 9.1, CWE-125): "ardupilot through Plane-4.6.3 was found to contain an out-of-bounds read issue in libraries/GCS_MAVLink/GCS_serial_control.cpp in GCS_MAVLINK::handle_serial_control()". CISA ADP SSVC 평가: Exploitation=poc, Automatable=yes — [MITRE CVE API](https://cveawg.mitre.org/api/cve/CVE-2026-38971), 참조 이슈 [ArduPilot #32524](https://github.com/ArduPilot/ardupilot/issues/32524)
  - CVE-2024-48519 / 51394 / 51395: 로컬 버퍼 오버플로 DoS(Rover ADIS1647x, AP_MSP, AP_SmartAudio) — [Feedly CVE-2024-48519](https://feedly.com/cve/CVE-2024-48519)
  - CVE-2022-28711 (9.8): APWeb CGI 메모리 손상 — [NVD](https://nvd.nist.gov/vuln/detail/CVE-2022-28711)
- QGroundControl / Mission Planner: NVD 키워드 검색 결과 **0건**(2026-10-08 조회). GCS 쪽 CVE 공백이 '안전'을 뜻하는지 '연구 부족'을 뜻하는지는 판단할 근거가 없다.
- 이종 무인체(UGV) 관련
  - **CVE-2025-41108** (2025-10-22, CVSS v4 9.2): Ghost Robotics Vision 60(군용 4족 로봇). "could allow an attacker to send commands to the robot from an external attack station, impersonating the control station (tablet) and gaining unauthorised full control of the robot. … The communication protocol used in this interface is based on MAVLink … There are two methods for connecting to the robot remotely: Wi-Fi and 4G/LTE." — [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-41108)
  - CVE-2024-33844 (7.5): Parrot ANAFI USA. 잘못된 MAV_MISSION_TYPE의 MISSION_COUNT 한 번으로 "cut off the connection between a controller and the drone" — [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-33844)

**학술 공격 연구**
- Rodday·Schmidt·Pras (Univ. Twente, IEEE NOMS 2016 / Black Hat Asia 2016): 경찰용 전문 드론의 XBee 텔레메트리 링크가 무암호화라 MITM과 명령 주입이 가능했다. 거리 최대 약 2km — [Univ. Twente](https://research.utwente.nl/en/publications/exploring-security-vulnerabilities-of-unmanned-aerial-vehicles/), [The Hacker News 2016-04](https://thehackernews.com/2016/04/hacking-drone.html)
  - 원문: "Xbee chips do have built-in encryption capabilities, but for avoiding latency between the drone and the user's commands, the chips doesn't implement encryption." / "The most important one is to use proper encryption"
- Davanian·Massacci·Allodi (PECCS 2017): "The protocol neither incorporates authentication nor encryption." 2013년 SiK 라디오 분석에서는 "an attacker can take over if she can establish the Radio connection to the drone." — [SciTePress](https://www.scitepress.org/PublishedPapers/2017/64085/64085.pdf)
- MAVLink 서베이(arXiv 1906.10641): "messages are sent in plain text" / "the MAVLink protocol is vulnerable to replay attacks." — [arXiv](https://arxiv.org/pdf/1906.10641)
- DSN 2016 발표: MAVLink는 "unencrypted and uses System IDs to distinguish UAVs". System ID를 포착해 MAVLink 패킷을 스푸핑하는 은닉 공격 시연 — [DSN16 슬라이드](https://web.eecs.umich.edu/~weimerw/p/DSN16-Industrial%20Attack%20and%20Arch.pdf)
- PGFuzz (NDSS 2021, Purdue): ArduPilot·PX4·Paparazzi에서 **156개 신규 버그**를 찾았고 개발자가 106개를 인정했다(56개 정책) — [NDSS](https://www.ndss-symposium.org/ndss-paper/pgfuzz-policy-guided-fuzzing-for-robotic-vehicles/), [PDF](https://www.cs.purdue.edu/homes/dxu/pubs/NDSS21_PGFuzz.pdf)
- ArduPilot 역공학·제어인지 보안분석(arXiv 2512.01164, ICSE 2026 SERP4IoT): 인증·서명이 꺼져 있으면 거짓 MAVLink 메시지를 여전히 주입할 수 있다 — [arXiv](https://arxiv.org/html/2512.01164v1)
- 한국 방산연구소 논문(2020, 한국어): PX4·SiK 라디오 기반 군용 드론의 **텔레메트리 하이재킹** 공격 시나리오 — [KoreaScience](https://www.koreascience.or.kr/article/JAKO202009651163133.pdf)

**실제 사례**
- **SkyGrabber (2009)**: WSJ 2009-12-17 보도와 국방부 확인. 이라크 무장세력이 약 26달러짜리 러시아산 소프트웨어 SkyGrabber로 **무암호화 Predator 영상 피드**를 가로챘다. 2008-12 체포된 무장대원 노트북에서 영상 파일이 나왔다 — [Defense One/GCN 2009-12](https://www.defenseone.com/defense-systems/2009/12/military-predator-video-intercepted-by-iraqis/188556/), [CSM 2009-12-17](https://www.csmonitor.com/Technology/Horizons/2009/1217/SkyGrabber-Is-hacking-military-drones-too-easy) [공식 확인 + 언론]
  - 반론(전 소장 Dale Meyerrose): "nothing hacked. It was the intercept of a broadcast signal" (요약도구 추출)
- **Creech AFB GCS 키로거 감염 (2011)**: Predator·Reaper 조종석(GCS) 컴퓨터가 키로거에 감염됐다. 기밀·비기밀 망 모두 감염됐고 여러 차례 삭제에도 재발했으며 비행은 계속됐다 — [Wired Danger Room 2011-10-07 재게시](https://vizcenter.sdsu.edu/exclusive-computer-virus-hits-u-s-drone-fleet/), [The Register 2011-10-10](https://www.theregister.com/2011/10/10/keylogging_bug_infects_predator_drones/) [언론, 이후 공군 감염 인정(AP)]
  - 원문: "We keep wiping it off, and it keeps coming back."
- **RQ-170 (2011)**: Q2 참조 [주장].
- **Operation Spiderweb (2025-06-01)**: 우크라이나 SBU, 18개월 준비. 트럭 컨테이너로 117대를 운반했다. **러시아 국내 4G/LTE망과 사전 장착 SIM**으로 우크라이나에서 원격 조종했고 ArduPilot 기반이었다. Janes는 공개 영상에 Mission Planner가 보인다고 분석했다. 젤렌스키는 기체마다 조종사가 따로 있었다고 말했다. 우크라이나는 러시아 항공기 40대 이상, 70억 달러 이상 피해를 **주장**한다 — [CEPA](https://cepa.org/article/ukraine-attack-the-spiders-web-still-needs-humans/), [Janes](https://www.janes.com/osint-insights/defence-and-national-security-analysis/operation-spiderweb-ukraine-covert-drone-strike-inside-russia), [Wikipedia](https://en.wikipedia.org/wiki/Operation_Spiderweb)
  - CEPA 원문: "FPV drones were remotely piloted from Ukraine via Russia's domestic 4G/LTE mobile networks using pre-installed sim cards." / "embedding control signals amidst civilian data traffic"
  - Unmanned Airspace: "There was no AI coordinated drone swarm attacks nor autonomous flight control." — [Unmanned Airspace](https://www.unmannedairspace.info/counter-uas-systems-and-policies/operation-spiderweb-why-telecom-networks-are-the-new-trojan-horse/)
- **우크라이나↔러시아 드론 C2 해킹**: Kyiv Post는 HUR 해커가 러시아 드론 통제 프로그램을 뚫어 피아식별(IFF) 서버가 멈췄다고 보도했다(날짜 불명) — [Kyiv Post](https://fu.kyivpost.com/post/27795) [주장]. 2025-07-14 BO Team이 러시아군 드론 공급사 Gaskar Group을 공격해 47TB(백업 10TB 포함) 파괴를 주장했고 HUR가 확인했다고 보도됨 — [Tom's Hardware](https://tomshardware.com/tech-industry/cyber-security/ukrainian-hackers-say-they-compromised-a-major-russian-drone-company-destroying-data-backups-and-systems) [주장/언론]
- **한국 드론 업계 표적화 (2025-03-17, 국정원)**: Q4 참조.

**함대 단위(1→N) 위험 분석**
- [학술] UAV 보안 서베이(arXiv 2109.14442): "Whether in a centralized or decentralized architecture, the GCS is constantly threatened by adversaries. In both architectures, the GCS represents a single point of failure" / 공격자가 정상 UAV 수를 임무 최소치 밑으로 떨어뜨리면 "the adversary causes the flight mission to fail by disrupting the entire UAV network." — [arXiv 2109.14442](https://arxiv.org/pdf/2109.14442)
- [학술] 군집 대상 GNSS 스푸핑 서베이(2025): "An attack's impact is exacerbated by the swarm's control logic, resulting in cascading failures." / "A critical mitigation gap persists, namely the interval between attack detection and the implementation of effective real-time countermeasures." — [Univ. of Bedfordshire 연구포털](https://researchportal.beds.ac.uk/p/en/research-outputs/a-survey-ongnss-spoofing-attacks-onuav-swarms-challenges-current-)
- 공유 대칭키 문제: 위 CVE-2020-10282 서술("same symmetric key into all devices … if one of the devices and its symmetric key are compromised, the whole authentication system is not reliable").

### Inferences
- **1인 다수 통제에서 바뀌는 점(종합 추론)**:
  1. **GCS 하나 = 함대 전체의 키·권한 집합.** MAVLink 서명은 링크당 키 1개에 공유 대칭키 구조다. GCS(또는 기체 1대)가 털리면 서명된 정상 명령으로 함대 전체를 조종할 수 있다. 서명이 '외부자'는 막아도 '내부자가 된 공격자'는 막지 못한다.
  2. **명령 증폭.** 콘솔에 "전 기체 RTL/임무 재할당" 같은 일괄 명령이 있으면 탈취된 콘솔이나 오조작 한 번이 N대에 동시에 퍼진다. 그래서 일괄 명령에는 정책 가드(지오펜스·민간지역·무장 여부 확인, 2인 승인, 단계적 적용)가 필요하다.
  3. **공통모드 EW.** 같은 공역의 기체는 교란·기만을 동시에 받는다(Q1·Q2). 운용자 화면에 경보가 N배로 쏟아지는 순간이 바로 S-100식 오대응 위험이 가장 큰 순간이다.
  4. **제3자망 의존.** Spiderweb은 상용 LTE가 C2 링크가 될 수 있음을 보여 줬다. 반대로 C2를 상용망·클라우드에 두면 그 망이 함대의 단일 장애점이 된다. CVE-2025-41108 UGV도 Wi-Fi/LTE로 원격 연결되었다.
  5. **SkyGrabber 교훈.** 다운링크(영상·텔레메트리)가 평문이면 함대 전체의 감시 대상·의도가 노출된다. MAVLink 서명은 암호화를 하지 않으므로 이 문제는 여전히 남는다.
- 팀의 기존 자산(LightGBM 게이트 + LSTM 전문가 IDS: GPS 스푸핑·DoS·MAVLink 퍼징, replay 연구)은 위 CVE 계열(SERIAL_CONTROL 셸, FTP 경로탐색, 조작된 MAVLink로 인한 DoS, 다운그레이드)과 직접 대응한다. 기체별 IDS 경보를 콘솔 단위에서 "격리 → 안전모드 → 운용자 확인" 정책으로 묶으면 1:N 상황의 하방 차단 논리가 된다(추론).

### Gaps
- MAVLink 2 서명이 실제 현장(군·공공·상용)에서 얼마나 켜져 있는지 측정한 조사는 찾지 못했다.
- QGroundControl과 Mission Planner는 NVD에 CVE가 0건이다. GitHub Security Advisories(mavlink/qgroundcontrol, ArduPilot/MissionPlanner)는 직접 확인하지 못했다. QGC의 서명 지원 현황도 미확인.
- ArduPilot GHSA-8g74-gp28-fgqv(CVE-2026-38971)는 GitHub 페이지를 직접 열람하지 못했다. 패치 상태는 서드파티 피드마다 다르다.
- 'GCS 1대 침해로 다수 기체를 실제로 탈취한' 공개 실전 사례는 찾지 못했다(Creech는 감염이지 탈취가 아님).
- RQ-170 스푸핑 주장은 독립 검증 자료가 없다.

---

## Q4. 한국 드론 보안 정책: KISA/과기정통부 인증, 국방 드론 보안 요구사항, 국정원 지침, 2025~2026 발표

### Takeaway
한국에는 '드론 전용 독립 인증제'가 없다. 정보통신망법 기반 **IoT 보안인증의 '드론' 분야**와 2024-06-10 KISA·과기정통부의 「정보통신망연결기기등 정보보호인증기준 상세 해설서(드론)」가 있을 뿐이다. 2025-03 국정원은 북한 등 국가배후 조직의 **드론 개발업체 해킹 시도 증가**를 경고했고, 2024-12 방사청 등과의 합동점검에서 다수 취약점을 확인했다. 2026-06-26 국방부 「국방 드론·대드론 발전 정책」은 공급망·품질·**보안을 사전 검증하는 한국형 상용드론 군용인증체계**와 부품 100% 국산화를 계획했다.

### Cited Findings
- **KISA 드론 해설서 (2024-06-10)** [공식 via 언론]: "한국인터넷진흥원(KISA)은 과학기술정보통신부와 함께 '정보통신망연결기기등 정보보호인증기준 상세 해설서(드론)'를 배포한다고 10일 밝혔다." 김정희 KISA 디지털안전지원본부장: "산업, 국방, 공공 분야에서 활용되는 드론에 대해 보안이 내재화될 수 있도록 지원할 것" — [디지털데일리 2024-06-10](https://m.ddaily.co.kr/page/view/2024061011014676790)
  - 해설서가 따로 필요했던 이유: 드론은 이동통신·위성통신·소출력 통신 등 제어·운용 방식이 일반 IoT와 달라 기존 IoT 해설서를 그대로 적용하기 어렵다(부제: "기존 IoT 보안 해설서로는 관리 어려워…제조기업·공인시험 기관서 참고") — [뉴스1 2024-06-10](https://www.news1.kr/it-science/security-hacking/5442579)
  - 정보통신망법 제48조의6 기반 IoT 보안인증의 8개 분야 중 '교통(드론)'에 해당. KISA는 **국군방첩사령부와 해설서를 공동 개발**했고, "군에 도입되는 드론 보안인증이 제도화되면" 협력을 강화할 계획 — [KISA 보도자료(검색 스니펫, 직접 접속은 인증서 오류)](https://www.kisa.or.kr/402/form?postSeq=2412), [에이티엔뉴스](https://www.atnnews.co.kr/news/articleView.html?idxno=88240)
  - 선행: 2020-12 과기정통부·국토부 「민간분야 드론 사이버보안 가이드」 — [이데일리](https://edaily.co.kr/News/Read?mediaCodeNo=257&newsId=02899526625994256) [공식 via 언론]
- **국정원 (2025-03-17)** [공식 via 언론] — [보안뉴스 2025-03-17](http://www.boannews.com/news/articleView.html?idxno=136514)
  - 원문: "국내 드론 개발업체에 대한 북한 등 국제·국가 배후 해킹조직의 공격 시도가 증가하고 있다."
  - 수법: 거래처를 사칭한 피싱 메일, 기업 메일·문서관리 시스템 취약점으로 내부망에 침투해 드론 기술 탈취 시도. 아직 "직접적인 피해로 이어지진 않았지만"
  - 2024-12 국정원·방위사업청·국가보안기술연구소 합동점검: "보안시스템 미비·관리부실 등 다수의 보안 취약점을 확인했다."
  - 2025-03-13~14 항공안전기술원(인천)에서 국토부와 설명회를 열고 「사이버 보안 관리 매뉴얼」(보안규정, 방화벽, 취약점 점검, 보안설정, 점검 체크리스트)을 배포
- **국방부 「국방 드론·대드론 발전 정책」 (2026-06-26)** [공식] — [정책브리핑 korea.kr](https://www.korea.kr/briefing/policyBriefingView.do?newsId=156768313), [국방부 보도자료](https://www.mnd.go.kr/mnd/167/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGbW5kJTJGMTMwMDAwMDUlMkZEUElNXzExNjUwNCUyRmFydGNsVmlldy5kbyUzRnBhc3N3b3JkJTNEJTI2cmdzQmduZGVTdHIlM0QlMjZmaW5kT3Bud3JkJTNEJTI2ZmluZFdvcmQlM0QlMjZyZ3NFbmRkZVN0ciUzRCUyNmZpbmRUeXBlJTNEJTI2ZmluZENsU2VxJTNEJTI2X0NTUkYlM0RiZTlmZjYxMjkzZTc0ODEzYjU2NTE5YjZiZjg3N2EwZiUyNnBhZ2UlM0QxJTI2)
  - 원문: "공급망과 품질·보안 등을 사전에 검증하는 한국형 상용 드론 군용인증체계를 구축하겠습니다."
  - 장관 답변: "중국산이 아닌 국산의 드론 부품과 이런 것들을 더 강화시켜서 100% 다 국산으로 지금 하려고 계획을 잡고 있다는 말씀드립니다."
  - 규모: "50만 드론전사 양성", "근거리 정찰드론, 소형 자폭드론 등 소모성·저비용 드론을 2만 대 이상 신속히 확보", "국산 교육용 상용드론 6만여 대를 도입". 장관은 2029년까지 약 6만여 대(분대당 1대 수준)를 언급했다(일부 답변은 국방부 요청으로 수정됨).
  - 시험 인프라: "드론·대드론 제조업체가 전파 교란, 요격 등 고난도 실증을 수행할 수 있도록 군 훈련장을 개방"
  - 입법: "첨단 전력을 신속하게 확보하기 위한 법 제정을 추진하겠습니다."
- 공공기관 중국산 드론 비중(2020-10): 국토부 산하기관 드론 약 56.5%가 중국산, 국방부·관세청은 100% 국산 — [쿠키뉴스 2020-10-27](https://www.kukinews.com/article/view/kuk202010270306) [언론/국감 자료, 오래된 수치]
- 학술·전문가 의견: 「국방 드론 도입현황 분석을 통한 사이버보안 발전방안 제시」(KCI) — [KCI](https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003094830). 보안뉴스 국방보안 칼럼(2025-12)은 2026년 위협으로 드론 대량생산이 만드는 공급망·업데이트 공격면을 꼽고 SBOM·서명 기반 업데이트를 권고했다 — [보안뉴스](https://www.boannews.com/media/view.asp?idx=141216&page=1&mkind=3&kind=) [전문가 의견]
- 해외 비교(참고): 미 OMB M-26-02 「Ensuring Government Use of Secure Unmanned Aircraft Systems…」(2025-11) — [White House PDF](https://www.whitehouse.gov/wp-content/uploads/2025/11/M-26-02-Ensuring-Government-Use-of-Secure-Unmanned-Aircraft-Systems-and-Supporting-United-States-Producers.pdf). 2025-12 FCC의 중국산(DJI·Autel 등) 신규 드론 제한 보도 — [트위그 2025-12-23](https://www.twig24.com/news/2025/12/23/20251223500204) [언론]

### Inferences
- 한국 정책은 '제조사 기기 인증(IoT 보안인증 드론 분야)'과 '업체 사이버보안 관리(국정원)'에 맞춰져 있다. **운용 단계 보안(다수 기체 C2 링크 인증, GCS 침해 시 피해 한정, EW 하 운용 정책)**은 공개 기준에서 거의 다뤄지지 않는다. 팀 데모가 채울 수 있는 공백이다.
- 국방부가 2029년까지 수만 대 규모의 상용·소모성 드론을 도입하면 드론 1대당 운용자 비율이 떨어질 수밖에 없다(1인 다수 통제). 동시에 공급망·보안 사전검증을 하겠다고 했으므로 심사위원에게 "보안이 내재된 다수 통제"는 정책 방향과 맞는 메시지다.

### Gaps
- 국정원이 공공기관의 중국산 드론·부품 사용을 제한한다는 공식 지침(2024~2026)은 찾지 못했다.
- 국군방첩사령부의 '국방 드론 보안 요구사항' 문서, 군용 드론 보안인증의 시행 시점과 세부 기준은 공개 자료에서 확인하지 못했다.
- '한국형 상용드론 군용인증체계'의 구체 항목(통신 암호화·인증, 펌웨어 서명 등)은 2026-06 발표 시점에 공개되지 않았다.
- KISA 원문 보도자료 페이지는 인증서 오류로 직접 열람하지 못했다(스니펫 기반 인용).

---

## Q5. 무인자산이 EW로 손실되는 비율 vs 물리적(kinetic) 손실 통계

### Takeaway
공식 원인별 손실 통계는 없다. 공개 추정치는 우크라이나 FPV의 **50% 이상**(CTC 2025, 상당수는 아군 재밍)부터 **75%**(프랑스 육군총장 2024 발언 보도)까지 EW 손실로 본다. 2023년 RUSI는 월 1만 대 손실 대부분을 EW·대드론 탓으로 추정했다. 반대 방향으로 소형 드론은 러시아군 장비 피해·파괴의 **60~70%**를 차지한다(RUSI 2025). 드론이 지배적 타격 수단이 됐고, 그 드론을 가장 많이 잡는 것이 EW라는 구도다.

### Cited Findings
- CTC Sentinel (West Point, 2025-07, David Hambling): "Reportedly something over 50 percent of FPV drones are downed by jamming, many by friendly fire." / RUSI(Watling & Reynolds, 2025-02) 인용: 소형 드론이 "currently account for 60-70% of damaged and destroyed Russian systems" / Shahed 요격률은 "intercepting over 90 percent of the Shaheds"(우크라이나 공군, 2025-03 기준)였으나 대량 공격 때는 떨어졌다 — [CTC Sentinel 2025-07](https://ctc.westpoint.edu/moving-targets-implications-of-the-russo-ukrainian-war-for-drone-terrorism/) [학술/싱크탱크]
- Forbes(Hambling, 2025-01-14): "In June, French Army Chief of Staff Gen. Schill suggested that 75% of FPVs were being brought down by electronic warfare" — [Forbes 2025-01-14](https://www.forbes.com/sites/davidhambling/2025/01/14/why-fpv-drones-are-still-ukraines-biggest-tank-killers/) [언론, 고위 장성 발언 재인용]. Forbes 2025-06은 재밍 손실이 최대 75%이며 상당수는 '아군 오인 재밍'이라고 서술 — [Forbes 2025-06-06](https://www.forbes.com/sites/davidhambling/2025/06/06/fiber-optic-birds-nest-heralds-a-fiber-drone-summer-in-ukraine/) (검색 스니펫)
- RUSI(2023-05): 월 약 10,000대 손실(우크라이나 장교 3명 인터뷰 기반, EW·대드론 무기 탓). 우크라이나 특수통신청은 정찰드론 하루 40~45대라고 반박성 수치를 냈다 — [Task & Purpose](https://taskandpurpose.com/news/ukraine-10000-drone-losses/), [Business Insider](https://www.businessinsider.nl/ukraine-is-losing-10000-drones-a-month-to-russian-electronic-warfare-systems-that-send-fake-signals-and-screw-with-their-navigation-researchers-say) [싱크탱크/공식 반론]
- Breaking Defense(2023-06): "Ukraine losing up to 10,000 drones a month, mostly to Russian electronic warfare" — [Breaking Defense 2023-06](https://breakingdefense.com/2023/06/dumb-and-cheap-when-facing-electronic-warfare-in-ukraine-small-drones-quantity-is-quality/) [언론]
- 명중률 저하(신뢰도 낮은 2차 출처): 2023년 양호 조건 40~60% → 2024년 중반 강한 재밍 구역 20~30% 이하 — [Military Machine](https://militarymachine.com/russia-electronic-warfare-ukraine-drones) [저신뢰]
- 광섬유 FPV: 무선 방사가 없어 EW 탐지·재밍 대상이 아니다. 대신 사거리 약 5~10km, 속도 약 60~70km/h로 제한된다 — [Military Machine](https://militarymachine.com/fiber-optic-drones-unjammable-weapons) [저신뢰]. 장거리 성공률은 Q2의 TWZ 인용 참조.

### Inferences
- 원인 구분이 불완전하지만, 여러 독립 출처가 소형 드론 손실의 **절반 이상을 EW**로 본다. 무인체계 생존성 설계에서 EW 대응은 키네틱 방호보다 우선순위가 높다.
- "상당수가 아군 재밍"이라는 지적은 **우군 EW와 우군 드론 간 탈충돌(deconfliction)**, 즉 다수 자산의 주파수·공역 통합 관리를 운용 콘솔이 맡아야 하는 근거다. RUSI도 러시아 EW가 "tend not to try and deconflict their effects"라고 지적했다.

### Gaps
- 우크라이나·러시아 어느 쪽에서도 원인별(EW/키네틱/고장/아군 재밍) 손실 공식 통계는 공개되지 않았다.
- 한국군 무인기 손실의 원인별 통계는 공개 자료가 없다.
- 해상·지상 무인체(USV·UGV)의 EW 손실 비율 수치는 찾지 못했다.
- 2025~2026년 최신 RUSI 원문 수치는 2차 인용으로만 확인했다.
