# SUPPORTY(SKYFLEET-C2) 실제 구현 분석 + 24시간용 다중 UxV 오픈소스 도구 조사

> 조사일(접근일): 2026-10-08 (모든 URL 접근일 동일). 조사자: AI 연구 에이전트.
> 원 저장소 `https://github.com/UXUIJASON/SKYFLEET-C2`는 2026-10-08 기준 **404(비공개 또는 삭제)**. 같은 커밋을 담은 팀원 미러 `https://github.com/jang961111-hash/SKYFLEET-C2`(커밋 `cad1fca6799deb5ef24c84721d889f2aec164816`)를 스크래치패드에 읽기 전용으로 clone하여 전 파일을 읽었다(코드는 실행하지 않음).
> 아래에서 `M` = `https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816`
> 직접 인용·코드 식별자·수식은 원문 그대로 둔다.

## A1. SUPPORTY가 공개한 결과물의 실체 (저장소·커밋·데모 URL)

### Takeaway
SUPPORTY 결과물은 **커밋 1개(2026-07-05 09:45 KST), 13개 파일, 약 2,000줄**의 작은 저장소다: 단일 HTML 콘솔 + FastAPI C2 백엔드 + 외부 JARVIS 음성봇 연동 모듈 + 시나리오 문서. 데모 서버(AWS EC2)는 현재 응답하지 않는다.

### Cited Findings
- D4D 쇼케이스 API 상 항목: `"title": " SUPPORTY — Multi-UxV C2"`, `"track": "T1 · 자율·무인 & 대드론"`, `"repoUrl": "https://github.com/UXUIJASON/SKYFLEET-C2"`, `"demoUrl": "http://54.180.123.161:8300/console"`, `"submittedAt": "2026-07-05T00:52:33Z"`, `"award": "OREGON"`, 스크린샷 3장 — [D4D showcase API](https://d4d.tech/api/showcase)
- 원 저장소 URL은 HTTP 404, 소유자 `UXUIJASON`의 공개 저장소 7개 목록에 SKYFLEET-C2 없음(2026-10-08) — [github.com/UXUIJASON/SKYFLEET-C2](https://github.com/UXUIJASON/SKYFLEET-C2), [GitHub API users/UXUIJASON/repos](https://api.github.com/users/UXUIJASON/repos)
- 미러 저장소 설명: `"SKYFLEET — AI-copilot command & control system for UGV·VTOL unmanned assets. Team SUPPORTY @ D4D APAC Seoul (72h) · 🏆 Oregon UAS Accelerator Award"`, 생성 2026-07-06, pushed_at 2026-07-05T00:46:32Z — [jang961111-hash/SKYFLEET-C2](https://github.com/jang961111-hash/SKYFLEET-C2)
  - 참고: 미러 설명은 "72h"라 하지만, 쇼케이스 원문 수집본은 대회 기간을 2026-07-04~05로 기록 — [D4D showcase API](https://d4d.tech/api/showcase) (팀 내부 inbox `2026-10-08-d4d-showcase-winners.md`) → 상충, 미확인.
- 커밋 이력: 단 1개 `cad1fca 2026-07-05 09:45:26 +0900 UXUIJASON | SKYFLEET Multi-UxV C2 (D4D T1): console, C2 backend, JARVIS integration, mission scenarios`, 커밋 메시지 말미에 `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` (AI 코딩 도구 사용 흔적) — [커밋 cad1fca](https://github.com/jang961111-hash/SKYFLEET-C2/commit/cad1fca6799deb5ef24c84721d889f2aec164816)
- 파일 트리(줄 수): `console.html` 695, `c2/control_service.py` 491, `c2/missions_nav.py` 155, `jarvis_ext/asset_control.py` 125, `c2/assets.py` 124, `c2/missions.py` 99, `c2/volt_bridge.py` 95, `c2/sim.py` 70, `README.md` 54, `jarvis_ext/INTEGRATE.md` 49, `scenarios/SKYFLEET_missions.md` 29, `.gitignore` 18, `c2/requirements.txt` 4 — 합계 2,008줄 — [커밋 cad1fca](https://github.com/jang961111-hash/SKYFLEET-C2/commit/cad1fca6799deb5ef24c84721d889f2aec164816)
- README 원문(목적): `"지상(UGV)·항공(VTOL)·해상(USV) 무인체계를 **하나의 콘솔·하나의 통신 모듈**로 통제하는 C2 시스템. 4G/5G 셀룰러 ↔ Starlink 위성 자동 전환으로 음영지역·해상에서도 제어권을 유지하며, 음성 AI 코파일럿(JARVIS)으로 1인 다중통제를 구현합니다."` — [M/README.md#L5](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/README.md#L5)
- README 원문(범위 한정): `"> 본 저장소는 팀 결과물(콘솔·C2·연동·시나리오)만 포함합니다."` → JARVIS 본체·WheelDrive 게이트웨이 코드는 저장소에 없음 — [M/README.md#L54](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/README.md#L54)
- 테스트 파일 없음(13개 파일 중 test 없음), `requirements.txt`는 `fastapi, uvicorn[standard], httpx, pydantic` 4개뿐이며 `volt_bridge.py`가 import하는 `paho.mqtt`는 누락 — [M/c2/requirements.txt](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/requirements.txt), [M/c2/volt_bridge.py#L12](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/volt_bridge.py#L12)
- 데모 URL 접근 결과(2026-10-08 04:06·04:08 UTC 경, curl 10~15초 타임아웃): `http://54.180.123.161:8300/console`, `/api/assets`, JARVIS `https://54-180-123-161.sslip.io:8340/` 모두 응답 없음(HTTP 000) — [데모 URL](http://54.180.123.161:8300/console)
- 쇼케이스 제출 텍스트의 기술 스택 표기: `Python & Java / WebRTC / AWS EC2`; 사업 주장: `"요르단과, UAE에 샘플 수출이력이 있으며, 현재 우크라이나에서 실증을 준비하고 있습니다."` (검증 불가 주장) — [D4D showcase API](https://d4d.tech/api/showcase)

### Inferences
- 저장소에 Java 코드는 없다. "Java"는 저장소 밖 구성요소(게이트웨이/앱 등)일 가능성(추정).
- 단일 커밋·AI 공동저자 표기·테스트 부재 → 대회 종료 직전 일괄 업로드한 해커톤 코드. 심사위원이 코드를 열면 "콘솔 대부분이 스크립트된 연출"임을 바로 확인할 수 있는 수준(A2·A4 참조).

### Gaps
- 원 저장소가 비공개 전환됐는지 삭제됐는지 확인 불가. 미러가 원본과 완전히 동일한지는 커밋 저자·시각 일치로만 추정.
- 데모 영상 없음(`video None`), 라이브 데모 오프라인 → 실제 시연 흐름(어떤 순서로 무엇을 보여줬는지)은 확인 불가.

## A2. 무엇이 실제이고 무엇이 목업인가 (시뮬레이터·실기체 링크)

### Takeaway
**실기체 2대(UGV 1, VTOL 1)는 실제 링크**가 있었다: EC2의 "WheelDrive" HTTP 게이트웨이에 RC PWM 값(1000~2000)을 100 ms 하트비트로 전송, 영상은 WebRTC/HLS/RTSP. **나머지 3대(air-2, sea-1, ugv-2)는 등속 직선 이동 시뮬**이다. 표준 시뮬레이터(PX4/ArduPilot SITL, Gazebo)나 MAVLink는 전혀 쓰지 않았다.

### Cited Findings
- 자산 시드: 실물 `ugv-1 "MULE-UGV"`(gateway `http://54.180.123.161:8090`), 실물 `air-1 "T2-CRUZA"`(`:8091`), 시뮬 `air-2 "CCA-ISR"`, `sea-1 "USV-01"`, `ugv-2 "MULE-02"`; 주석 `# sim assets to fill the multi-domain picture (air CCA + sea USV + a 2nd ground)` — [M/c2/assets.py#L97-L111](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/assets.py#L97-L111)
- 제어 모델은 RC 채널 PWM: `# UGV:   ch1=steer  ch2=throttle  ch3=gear` / `# Drone: ch1=yaw    ch2=throttle  ch3=roll  ch4=pitch  ch5=gimbal  (APK-recovered)` → 벤더 앱(APK)을 역분석해 채널 매핑을 얻은 것으로 보임 — [M/c2/assets.py#L11-L16](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/assets.py#L11-L16)
- 실물 송신: `await _http.get(f"{a.gateway}/control", params={"steer": s.steer, "throttle": s.throttle, "gear": s.gear, "ds4": s.ds4, "ds5": s.ds5}, timeout=1.0)`, `KEEPALIVE_MS = 100` — [M/c2/control_service.py#L30](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/control_service.py#L30), [#L94-L103](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/control_service.py#L94-L103)
- 백엔드 docstring: `"실물 UGV/드론: 제어 상태유지 + keep-alive로 wintop 게이트웨이(WheelDrive /control) 송신"`, `"시뮬 자산: sim.tick 으로 목표 이동 (콘솔 다중자산 그림)"` — [M/c2/control_service.py#L1-L11](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/control_service.py#L1-L11)
- 시뮬 엔진: `SPEED = {"air": 18.0, "ground": 4.0, "sea": 6.0}`, `ARRIVE_M = 8.0`; 목표 방위로 등속 이동(`_step_latlon`), 배터리는 `drain = (0.02 if a.pose.speed > 0 else 0.005) * dt`; 지형·장애물·통신 모델 없음 — [M/c2/sim.py#L34-L69](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/sim.py#L34-L69)
- 영상: `{"webrtc": f"http://{host}:8889/{path}", "hls": f"http://{host}:8888/{path}", "rtsp": f"rtsp://{host}:8554/{path}"}` (8889/8888/8554 조합은 MediaMTX 기본 포트와 일치 — 추정) — [M/c2/assets.py#L93-L95](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/assets.py#L93-L95)
- 실물 텔레메트리: LTE 모듈 AT 명령 기반 GPS·신호 push(`"모듈이 실물 자산의 GPS fix를 주기적으로 push (AT+QGPSLOC → 여기)"`, `"모듈이 4G 신호품질을 push (AT+QCSQ → RSRP/SINR/RSRQ)"`) — [M/c2/control_service.py#L235-L248](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/control_service.py#L235-L248)
- 배터리 전압은 벤더 MQTT 브리지: `"벤더 브로커(mqtt.ks.epplink.com)에서 우리 차량(flashid)의 배터리 전압을 구독해 C2의 /api/asset/{ASSET}/telem 로 push"`, 토픽 `realfly/{flashid}/report` — [M/c2/volt_bridge.py#L3-L10](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/volt_bridge.py#L3-L10)
- 자율 복귀: GPS 브레드크럼 역주행(`STEER_GAIN = 4.0`, `GPS_TIMEOUT_S = 4.0` 페일세이프) + GPS 없을 때 `"GPS-denied 복귀 — 명령 로그 시간역전(dead reckoning). 센서 불필요."` (`(steer, 2 * NEUTRAL - thr)`로 명령 로그를 역재생해 후진) — [M/c2/missions_nav.py#L15-L20](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/missions_nav.py#L15-L20), [#L106-L138](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/missions_nav.py#L106-L138)
- 실물은 자율 임무 수행 미완: `# real asset: no autonomous nav yet (GPS breadcrumb loop = missions_nav TODO)` / `# -> mark assigned; operator drives it (manual/voice) = human-on-the-loop` — [M/c2/missions.py#L82-L86](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/missions.py#L82-L86)
- 수동 조종 입력: 방향키 + Logitech G29 레이싱 휠(Gamepad API, 20 Hz 송신 `setInterval(g29tick,50)`) — [M/console.html](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html)
- 제출 스크린샷 3장은 콘솔 화면이 아니라 **곡면 모니터·HOTAS 조이스틱·좌석으로 된 조종석 리그**에서 VTOL 기체 영상(속도 "0.0 km/h", "7.9 km/h" OSD)과 위성 산악 지도+비행 텔레메트리(고도·속도·거리 수치)를 띄운 사진 — [screenshot 1](https://hlwjyighifwvhqloaixd.supabase.co/storage/v1/object/public/event-covers/screenshots/1783212395101-ab149ec1f53fd05e.png), [2](https://hlwjyighifwvhqloaixd.supabase.co/storage/v1/object/public/event-covers/screenshots/1783212398919-1d468446641db468.png), [3](https://hlwjyighifwvhqloaixd.supabase.co/storage/v1/object/public/event-covers/screenshots/1783212402559-5566006f852b9c81.png)

### Inferences
- 스크린샷 속 지도·텔레메트리 UI는 저장소의 `console.html`(Leaflet, 위 HUD)과 형태가 다름 → 벤더 GCS 앱 또는 별도 비행 시뮬레이터 화면일 가능성(추정). 즉 심사 현장의 "와우" 요소는 **실물 하드웨어·조종석 리그**였을 가능성이 높다.
- 해상(USV)은 100% 시뮬, 항공 실기체도 RC 채널 수준의 직접 조종 → "임무 단위 자율 통제"는 시뮬 자산에서만 성립.

### Gaps
- WheelDrive/wintop 게이트웨이, 벤더 기체(T2-CRUZA, REMOTY-4WD)의 실제 사양·통신 경로(LTE 라우터 등)는 저장소 밖이라 확인 불가.
- 스크린샷의 비행 화면이 실기체 영상인지 시뮬레이터인지 확정 불가.

## A3. 임무 할당 방식 (규칙? LLM?)

### Takeaway
두 갈래가 따로 논다. (1) 백엔드 `missions.allocate()`는 **규칙 기반 탐욕(greedy) 1건씩 배정**: 능력(capability) 필터 → 도메인 선호 순위 → 평면 거리. (2) 콘솔의 Mission Queue는 백엔드와 **연결되지 않은 클라이언트 측 랜덤 연출**이며, "AI 자동처리"의 자산 배정은 `Math.random()`으로 풀에서 고른다. LLM(Claude Haiku)은 음성 명령을 태그로 바꾸는 데만 쓰이고 배정 계산에는 관여하지 않는다.

### Cited Findings
- 배정 규칙 표: `MISSION_SPEC = {"recon": {"cap": "recon", "domains": ["air", "ground", "sea"]}, "isr": {...["air"]}, "resupply": {...["ground", "air"]}, "patrol": {...["sea", "ground", "air"]}, "relay": ..., "ew": ..., "decoy": ...}` — [M/c2/missions.py#L15-L23](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/missions.py#L15-L23)
- 배정 함수 핵심: `cands = [a for a in ASSETS.values() if spec["cap"] in a.capabilities and a.mission is None and a.mode in ("idle", "manual")]` … `# score: domain preference (lower=better) then proximity` … `return (dom, _dist(a, location))` … `cands.sort(key=score); return cands[0].id`; 거리 `dlat*111000`, `dlon*88000`의 평면 근사 — [M/c2/missions.py#L41-L64](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/missions.py#L41-L64)
- `urgency` 필드는 저장만 되고(`urgency: str = "normal"  # normal | priority | urgent`) 배정 점수에 쓰이지 않음; 가용 자산 없으면 `"reason": "no available asset"`로 끝(대기열·재배정 없음) — [M/c2/missions.py#L25-L33](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/missions.py#L25-L33), [M/c2/control_service.py#L294-L298](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/control_service.py#L294-L298)
- 콘솔 Mission Queue는 하드코딩 10개 임무에서 랜덤 생성: `const MISSIONS=[{p:'p1',n:'그날의 6분',d:'지상·구출',a:'UGV'}, ...]`, `const R=n=>Math.floor(Math.random()*n);`, `(function loop(){newRequest(true);setTimeout(loop,7000+Math.random()*6000);})();` — [M/console.html#L614-L631](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L614-L631), [#L693-L694](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L693-L694)
- 콘솔 "배정": `const ASSETPOOL={UGV:['UGV-1','UGV-2'],VTOL:['AIR-1'],USV:['SEA-1']};` … `if(r.st===2 && !r.asset){const pool=ASSETPOOL[r.m.a]||['UGV-1']; r.asset=pool[R(pool.length)]; ...}` — 랜덤 선택 — [M/console.html#L629](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L629), [#L660-L668](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L660-L668)
- 콘솔 JS는 `/api/assets`, `/api/asset/{id}`, `/command`, `/control`, `/estop`, `/return`만 호출하고 `/api/mission`·`/api/missions`·`/ws`는 호출하지 않음(코드 전체 검색 결과 `new WebSocket` 없음) — [M/console.html](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html)
- 콘솔의 `aiLog()`는 `"AI · HAIKU · 자동배정"` 라벨로 로그를 쓰려 하지만 대상 요소 `#vlog`가 HTML에 없어 즉시 return(사실상 무동작) — [M/console.html#L635-L638](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L635-L638)
- 백엔드 배정에 도달하는 실제 경로는 JARVIS 음성: `음성 "3번 지역 정찰"  → Haiku → [ACTION:MISSION:recon|37.482|127.036] → C2 자동배분` — [M/jarvis_ext/INTEGRATE.md#L33-L39](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/jarvis_ext/INTEGRATE.md#L33-L39)
- 쇼케이스 주장: `"Mission Queue의 AI 자동처리가 요청이 밀리면 자산을 자동 배정합니다. 도메인(지상/항공/해상)과 자산 타입별로 역할을 매칭하고, 다중 요청을 동시에 처리합니다."` — [D4D showcase API](https://d4d.tech/api/showcase)

### Inferences
- 우리 팀 차별점 후보: **전역 최적화(헝가리안/CBBA/VRP) + 동적 재배정 + 배정 근거(비용 분해) 표시**. SUPPORTY는 1건씩 탐욕 배정, 우선순위 미반영, 재계획 없음, 배정 이유 미표시.
- "AI 자동처리"라는 표현과 실제 랜덤 배정 사이의 간극은 심사위원이 질문하면 약점이 될 수 있었다(추정).

### Gaps
- 시연 당일 콘솔이 다른 버전(백엔드 연동 버전)이었는지는 확인 불가.

## A4. "인지부하"는 어떻게 계산되나 (4건 이상 경고 주장)

### Takeaway
인지부하는 **"신규요청+확인중 상태의 요청 수 `pend >= 4`"라는 단일 임계값**이며, 수동 모드에서는 요청이 아예 진행되지 않도록(`maxSt = 0`) 만들어져 있어 랜덤 요청이 4건 쌓이면 **반드시** 경고가 뜨는 스크립트다. 경고는 세션당 1회(`promptShown`)이고, 운용자 상태(반응시간, 작업 전환, 주의 분산 등)는 측정하지 않는다.

### Cited Findings
- 핵심 코드: `const maxSt = aiMode ? 3 : 0;        // 수동: 신규요청에서 대기(쌓임) · AI: 완료까지 자동처리` … `const pend=reqs.filter(r=>r.st<2).length` … `if(!aiMode && !promptShown && pend>=4) showAiPrompt();` — [M/console.html#L660-L675](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L660-L675)
- 경고 동작: `sayTTS('요청이 '+n+'건 밀렸습니다. AI 자동 처리로 전환할까요?');` + 버튼 `"예, 전환"` 클릭 시 `aiMode=true` — [M/console.html#L684-L691](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L684-L691)
- 큐 최대 5건 유지: `while(reqs.length>5){const o=reqs.pop(); ...}` — [M/console.html#L657](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L657)
- 쇼케이스 주장: `"백로그를 신규·진행·완료로 카운트하며, 요청이 4건 이상 쌓이면 인지부하로 감지해 JARVIS가 음성으로 알립니다. P1~P4 우선순위를 색상으로 구분하고, P1은 적색 점멸로 긴급 알림합니다."` — [D4D showcase API](https://d4d.tech/api/showcase)
- P1 강조: `r.el.classList.toggle('urgent', r.m.p==='p1' && r.st<3);` — [M/console.html#L646-L647](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L646-L647)

### Inferences
- 우리 팀이 "인지부하"로 차별화하려면: 큐 길이 외에 **가중 작업부하 지표**(우선순위 가중 대기 수 × 대기시간, 동시 수동조종 자산 수, 미확인 경보 수, 운용자 응답 지연)를 실시간 계산·시각화하고, 임계 초과 시 **자율 수준(LOA)을 자산별로 단계 조정**하는 것이 설득력 있다(추정·설계 제안).
- SUPPORTY의 HITL은 "전환할까요?" 1회 질의 후 전부 AI 모드로 넘어가는 이분법 → 우리는 **자산/임무별 부분 위임 + 승인 대기 큐**로 차별화 가능(추정).

### Gaps
- SUPPORTY가 인지부하 개선을 정량 측정(예: NASA-TLX, 과업 완료시간)했다는 증거는 저장소·쇼케이스 어디에도 없음.

## A5. JARVIS 음성 AI 구현

### Takeaway
JARVIS는 **저장소 밖의 별도 웹앱**(EC2 `:8340`, iframe 임베드)이다. 저장소에는 연동 모듈만 있다: LLM(문서상 Claude **Haiku**)이 시스템 프롬프트에 따라 `[ACTION:TYPE:payload]` 태그를 출력하면 `asset_control.py`가 이를 C2 REST 호출로 변환한다. TTS는 JARVIS `/api/say`(ElevenLabs 키 언급) 실패 시 브라우저 `speechSynthesis`로 폴백.

### Cited Findings
- 콘솔 임베드: `<iframe id="jframe" src="https://54-180-123-161.sslip.io:8340/" allow="microphone; autoplay; clipboard-write" ...>` — [M/console.html#L386](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L386)
- 연동 방식: `"JARVIS 태그 문법: [ACTION:TYPE:payload] / [QUERY:TYPE:payload], TYPE=대문자, 이미 검증됨"`, server.py 3군데 수정(import, `run_tag()` 디스패치, `system_prompt()`에 스니펫 추가) — [M/jarvis_ext/INTEGRATE.md#L1-L26](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/jarvis_ext/INTEGRATE.md#L1-L26)
- 시스템 프롬프트 스니펫(원문 일부): `"[ACTION:CONTROL:ugv-1|전진]     자산 직접 제어 ..."`, `"[ACTION:MISSION:recon|37.4820|127.0360]   임무 의도 하달(type|위도|경도) → 시스템이 자산 자동배분"`, `"안전: 운용자가 "정지/멈춰/스톱"이라 하면 즉시 [ACTION:CONTROL:<asset>|정지] 를 실행하세요."`, `"음성 응답은 짧게(집사 톤)."` — [M/jarvis_ext/asset_control.py#L107-L125](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/jarvis_ext/asset_control.py#L107-L125)
- 한국어→명령 사전: `_ALIASES = {"전진": "forward", "앞으로": "forward", ... "이륙": "takeoff", "착륙": "land", ...}` — [M/jarvis_ext/asset_control.py#L18-L35](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/jarvis_ext/asset_control.py#L18-L35)
  - 단, 백엔드 `DRONE_CMAP`에는 `takeoff`/`land` 키가 없어 이 명령은 400 오류가 됨(`"unknown command '{cmd}' for {aid}"`) — [M/c2/assets.py#L75-L86](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/assets.py#L75-L86), [M/c2/control_service.py#L184-L190](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/control_service.py#L184-L190)
- 환경변수: `ANTHROPIC_API_KEY` / `ELEVENLABS_API_KEY` `| JARVIS LLM/TTS (JARVIS 저장소)` — [M/README.md#L40-L46](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/README.md#L40-L46)
- TTS 폴백: `fetch('https://54-180-123-161.sslip.io:8340/api/say', ...)` 실패 시 `new SpeechSynthesisUtterance(t);u.lang='ko-KR'` — [M/console.html#L677-L681](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L677-L681)

### Inferences
- 음성 경로는 클라우드 LLM·클라우드 TTS·EC2 의존 → 인터넷 없는 현장에서는 작동 불가. 우리 팀 정책(오프라인 시연)과 대비되는 차별점.
- 음성이 "전진/정지" 같은 **스틱 수준 명령**까지 다루므로 "임무 단위 추상화" 주장과 부분적으로 상충.

### Gaps
- JARVIS 본체 코드(STT 엔진, 프롬프트 전체, 확인 절차)는 비공개라 확인 불가.

## A6. 통신 전환(4G/5G ↔ Starlink) — 실제인가?

### Takeaway
**코드상 Starlink 전환 구현은 전혀 없다.** "Starlink"라는 단어는 README와 시나리오 문서에만 등장하고, 콘솔 상단의 `LINK 4G · 92%` 칩은 하드코딩된 정적 HTML이다. 실제로 구현된 것은 LTE 모듈의 RSRP/SINR/RSRQ/RTT 값을 push받아 HUD에 "약함/보통/양호"로 표시하는 진단 기능뿐이다.

### Cited Findings
- 저장소 전체에서 `starlink` 검색 결과: `README.md` 1건, `scenarios/SKYFLEET_missions.md` 1건, 코드 0건 — [커밋 cad1fca](https://github.com/jang961111-hash/SKYFLEET-C2/commit/cad1fca6799deb5ef24c84721d889f2aec164816)
- 정적 칩: `<span class="chip" id="linkchip">...LINK <b>4G · 92%</b></span>`, 같은 줄 근처 `GPS <b>14 SAT</b>`, `MISSION <span>T+</span>00:41:12` 모두 하드코딩 — [M/console.html#L321-L325](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L321-L325)
- 신호 진단 API: `class SignalBody(BaseModel): net, rssi, rsrp, sinr, rsrq, rtt_ms`, `"모듈이 4G 신호품질을 push (AT+QCSQ → RSRP/SINR/RSRQ). 원격 진단용."` — [M/c2/control_service.py#L57-L63](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/control_service.py#L57-L63), [#L242-L248](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/control_service.py#L242-L248)
- 시나리오 문서: `"**공통 기술 축**: 4G/5G 셀룰러 ↔ Starlink 자동 전환 통신 모듈 — 장비·거리 무관 제어권 유지"` — [M/scenarios/SKYFLEET_missions.md#L4](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/scenarios/SKYFLEET_missions.md#L4)

### Inferences
- 통신 전환은 팀의 하드웨어 사업 비전(별도 모듈)일 수 있으나 해커톤 산출물로는 증명되지 않음. 우리 팀은 **링크 품질 모델(거리·지형 음영 기반 시뮬) + 링크 상실 시 자산별 자율 행동(lost-link 규칙) 시각화**를 실제로 돌리면 이 지점을 정면으로 넘을 수 있음(추정).

### Gaps
- 시연 현장에서 실제 Starlink 단말을 보여줬는지는 확인 불가.

## A7. 표시 지표와 UI 화면

### Takeaway
UI는 단일 HTML(695줄)의 다크 테마 대시보드: 좌측 레일, 상단 바(정적 칩), FPV 영상 2개(UGV·AIR)+HUD, 우측 Mission Queue + JARVIS iframe, 하단 Leaflet 전술지도 + Asset Roster. **지도에는 선택된 자산 1대만 마커로 표시**되고, 지도 타일은 온라인(OSM/Esri/CARTO)이다. "인력 절감률·임무 성공률" 지표는 구현되지 않았고, AI 모드 라벨의 `완료 N` 카운터와 `x/N LIVE`만 있다.

### Cited Findings
- README 구성 설명: `"FPV 영상 + HUD(속도·나침반·GPS·좌표·복귀상태)"`, `"택티컬 지도(위성/2D/다크), 실 GPS 경로"`, `"Mission Queue(우선순위 요청 → 백로그 시 AI 자동처리 전환)"`, `"Asset Roster, JARVIS 음성 패널"`, `"조작: 방향키 + G29(휠/패들기어/페달), 계기(DRIVE/GEAR/STOP/RTB)"` — [M/README.md#L9-L14](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/README.md#L9-L14)
- 온라인 타일: `street: 'https://{s}.tile.openstreetmap.org/...'`, `sat: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/...'`, `dark: 'https://{s}.basemaps.cartocdn.com/dark_all/...'`; Leaflet도 unpkg CDN — [M/console.html#L573-L577](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L573-L577), [#L2-L3](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L2-L3)
- 지도 마커는 1개(`vMk=L.circleMarker(...)`)이며 `updateMap(a)`는 `poll()`에서 선택 자산(`SEL`)에 대해서만 호출 — [M/console.html#L548](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L548), [#L578-L581](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L578-L581), [#L605](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L605)
- 지표 표시: `lb.innerHTML=...(aiMode?('AI 자동 · 진행 '+ac+' · 완료 '+doneCount):('대기 '+pend+'건'))`; Roster 헤더 `A.length+' · '+liveN+' LIVE'`; `.stats .sval` 갱신 코드는 있으나 해당 요소가 HTML에 없음 — [M/console.html#L671-L673](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L671-L673), [#L560-L562](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L560-L562)
- 쇼케이스 주장: `"5. 인력 절감률·임무 성공률 측정 프레임워크 — 1인 다중통제로 한 명이 다수 자산을 운용해 인력 절감을 정량화하며, Mission Queue의 완료 카운터와 성공/진행 통계를 실시간으로 집계합니다."` — [D4D showcase API](https://d4d.tech/api/showcase)
- 백엔드에는 `/ws`(0.25초 주기 assets+missions 푸시)가 있지만 콘솔은 0.7초/3초 HTTP 폴링 사용 — [M/c2/control_service.py#L305-L317](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/control_service.py#L305-L317), [M/console.html#L567](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/console.html#L567)

### Inferences
- "다중 자산 공통상황도(COP)"라는 T1 핵심 그림이 지도에 없다(한 번에 1대만). 우리 팀은 **전 자산·전 임무·경로·배정선을 한 지도에 동시 표시**하는 것만으로도 시각적 차별화가 크다.
- 정량 지표(운용자 1인당 자산 수, 개입 횟수, 임무 완료시간, 배정 최적성 gap)를 실제 계산해 보여주면 SUPPORTY의 미구현 주장 영역을 실증으로 채울 수 있다(추정).

### Gaps
- 시연 당일 화면 녹화가 없어 UI 사용 흐름 확인 불가.

## A8. 심사위원 관점 강·약점 + 우리 팀 한 문장 차별화

### Takeaway
SUPPORTY의 수상 동력은 **실물 하드웨어(UGV+VTOL 실제 구동, 조종석 리그), 강한 스토리(우크라이나 부상병 인터뷰), 음성 코파일럿 연출**로 보인다. 소프트웨어적으로는 임무 할당·인지부하·통신 전환·성과지표가 **스크립트/정적 연출 또는 미구현**이다. 우리 팀은 "실제로 계산되는 자율 배정·재계획 + 측정되는 인지부하 + 오프라인 COP"로 정면 차별화할 수 있다.

### Cited Findings
- 강점 근거: 실물 2대 게이트웨이 제어·영상 스트림 — [M/c2/assets.py#L97-L104](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/assets.py#L97-L104); GPS-denied 명령로그 역재생 복귀 — [M/c2/missions_nav.py#L106-L155](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/missions_nav.py#L106-L155); ESC 보호용 방향전환 중립삽입(`DIR_NEUTRAL_MS = 250`) — [M/c2/control_service.py#L69-L91](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/control_service.py#L69-L91); 인터뷰 기반 문제 정의와 P1~P4 우선순위 기준 `"생명 직결도 > 시간 민감도 > 회복 불가능성 > 임무 파급효과"` — [M/scenarios/SKYFLEET_missions.md#L6](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/scenarios/SKYFLEET_missions.md#L6), [D4D showcase API](https://d4d.tech/api/showcase)
- 약점 근거: 랜덤 Mission Queue·랜덤 배정(A3), 고정 임계 `pend>=4`(A4), Starlink 코드 0건·정적 LINK 칩(A6), 지도 단일 마커·온라인 타일(A7), 테스트 0개·단일 커밋(A1), MAVLink 등 표준 인터페이스 미사용(RC PWM 직접) — 위 각 절의 URL
- 수상 분류는 T1 본상 아닌 `"award": "OREGON"`(오리건 연계 특별상) — [D4D showcase API](https://d4d.tech/api/showcase)

### Inferences
- 한 문장 차별화 후보(추정·제안):
  1. "SUPPORTY가 음성으로 자산 1대씩을 조종하는 콘솔이었다면, 우리는 운용자 1명이 **임무만 던지면 이기종 자산 3+대에 최적 배정·자동 재계획하고, 운용자 부하를 실시간 측정해 자율 수준을 조절하는** 오프라인 C2다."
  2. (짧은 버전) "스크립트된 큐가 아니라 **실제로 계산되는 배정·재계획과 측정되는 인지부하**."
- 심사위원(군 출신) 질문 예상: "배정 알고리즘이 뭔가? 통신 끊기면? 표준(MAVLink/STANAG 4586/CoT) 호환되나?" → B4·B5의 도구로 답을 준비하면 SUPPORTY 대비 우위.
- 하드웨어가 없는 우리 팀은 SITL(B1)로 "실제 오토파일럿 펌웨어가 도는 기체"를 보여주는 것이 SUPPORTY의 실물 임팩트에 대한 대응 카드가 될 수 있음(추정).

### Gaps
- 심사 기준표·점수, SUPPORTY가 T1 본상을 받지 못한 이유는 공개 자료 없음.

## B1. PX4 / ArduPilot SITL 다중 기체 + MAVSDK / pymavlink (노트북 24시간 적합성)

### Takeaway
**ArduPilot SITL이 24시간 데모에 가장 현실적**: Copter·Rover·**motorboat(USV)** 프레임을 모두 내장 물리모델로 지원하고(Gazebo 불필요), `-I` 인스턴스 번호로 포트가 10씩 자동 오프셋되며, **x86_64 Linux용 사전 빌드 SITL 바이너리**가 공식 서버에 있다. PX4는 Gazebo 다중 기체가 Linux 전용이고 공식 문서상 보트 모델이 없으며, 헤드리스 SIH에는 Rover는 있으나 보트 없음. MAVSDK-Python은 **2026-09~10 패키지 이름 변경**(gRPC판 → `mavsdk-grpc`, `mavsdk` 4.x = API가 다른 네이티브 바인딩)이 있어 주의.

### Cited Findings
- ArduPilot 다중 기체: `"SITL has support for launching multiple vehicles from a single command."`, `"each one will need a unique SysId parameter"`, `"The easiest method to avoid SysId conflicts is with the --auto-sysid option."`, `--auto-offset-line 90,10`, `--mcast`, `Tools/autotest/swarminit.txt` — [ArduPilot SITL docs](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html)
- `sim_vehicle.py` 옵션 원문: `"-I", "--instance" ... help="instance of simulator"`, `"-n", "--count" ... help="vehicle count; if this is specified, -I is used as a base-value"`, `"--no-mavproxy" ... help="Don't launch MAVProxy"`, `"--auto-sysid" ... help="Set MAV_SYSID based upon instance number"`, `"-S", "--speedup"` — [sim_vehicle.py (master)](https://github.com/ArduPilot/ardupilot/blob/master/Tools/autotest/sim_vehicle.py)
- 포트 규칙(소스): `"tcp:127.0.0.1:" + str(5760 + 10 * i)`, `ports = [14550 + 10 * i]`, `"--sitl", "127.0.0.1:" + str(5501 + 10 * i)` — [sim_vehicle.py (master)](https://github.com/ArduPilot/ardupilot/blob/master/Tools/autotest/sim_vehicle.py)
- `--no-mavproxy` 시 `"SITL will be listening for any GGS station to connect via TCP port 5760"`, 기본 GCS UDP 14550 — [ArduPilot SITL docs](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html)
- USV: SITL 내장 `{ "motorboat", MotorBoat::create }`, `"a MotorBoat simulator. We re-use SailBoat but force motor_connected and sail_area to 0"`, 자동시험 `model = "motorboat-skid"`; Rover 프레임 목록에 `rover-skid, sailboat, sailboat-motor, balancebot` — [SITL_cmdline.cpp](https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_HAL_SITL/SITL_cmdline.cpp), [SIM_MotorBoat.h](https://github.com/ArduPilot/ardupilot/blob/master/libraries/SITL/SIM_MotorBoat.h), [ArduPilot SITL docs](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html)
- 사전 빌드 바이너리: `https://firmware.ardupilot.org/Copter/stable/SITL_x86_64_linux_gnu`, `.../Rover/stable/SITL_x86_64_linux_gnu` 존재, `ardurover` 바이너리 HTTP 200, Last-Modified 2026-09-03 — [firmware.ardupilot.org Rover/stable SITL](https://firmware.ardupilot.org/Rover/stable/SITL_x86_64_linux_gnu/)
- ArduPilot 저장소 활발(pushed 2026-10-08, GPL-3.0), MAVProxy(2026-10-08), pymavlink(2026-10-06, PyPI 2.4.50 2026-09-24) — [ArduPilot/ardupilot](https://github.com/ArduPilot/ardupilot), [ArduPilot/MAVProxy](https://github.com/ArduPilot/MAVProxy), [ArduPilot/pymavlink](https://github.com/ArduPilot/pymavlink), [PyPI pymavlink](https://pypi.org/project/pymavlink/)
- PX4 Gazebo 다중 기체: 형식 `ARGS ./build/px4_sitl_default/bin/px4 [-i <instance>]`, 예 `PX4_GZ_STANDALONE=1 PX4_SYS_AUTOSTART=4001 PX4_GZ_MODEL_POSE="0,1" PX4_SIM_MODEL=gz_x500 ./build/px4_sitl_default/bin/px4 -i 2`, `"Multi-Vehicle Simulation with Gazebo is only supported on Linux."`, ROS 2 연동 `MicroXRCEAgent udp4 -p 8888` — [PX4 Multi-Vehicle Sim (Gazebo)](https://docs.px4.io/main/en/sim_gazebo_gz/multi_vehicle_simulation)
- PX4 포트: `"PX4's remote UDP Port 14550 is used for communication with ground control stations."`, `"PX4's remote UDP Port 14540 is used for communication with offboard APIs."`; 다중 인스턴스는 14540~14549 순차 할당, 초과분은 14549 공유 — [PX4 Simulation](https://docs.px4.io/main/en/simulation/)
- PX4 시뮬레이터별 기체: Gazebo `"Quad, VTOL (Standard, Tailsitter, Tiltroter), Plane, Rovers"`, SIH(헤드리스 기본) Quad/Hex/Plane/Tailsitter/Standard VTOL/Rover, Gazebo Classic에 Submarine; 보트/USV 없음 — [PX4 Simulation](https://docs.px4.io/main/en/simulation/)
- PX4 활발(pushed 2026-10-07, BSD-3), jMAVSim 마지막 push 2026-01-29 — [PX4/PX4-Autopilot](https://github.com/PX4/PX4-Autopilot), [PX4/jMAVSim](https://github.com/PX4/jMAVSim)
- MAVSDK-Python 이름 변경 원문: `"This wrapper used to be published as mavsdk. That name on PyPI now refers to the native MAVSDK binding, which has a **different API** and no gRPC dependency"`, `"Install mavsdk-grpc and use import mavsdk_grpc as mavsdk"`, `"Or pin mavsdk<4"`; `System()` 인자 `mavsdk_server_address`, `port`(기본 50051); 예 `await drone.connect(system_address="udpin://0.0.0.0:14540")` — [MAVSDK-Python README](https://github.com/mavlink/MAVSDK-Python)
- PyPI: `mavsdk` 4.0.0(2026-09-22)~4.0.5(2026-10-07), 마지막 3.x는 3.17.4(2026-09-17); `mavsdk-grpc` 4.0.5 — [PyPI mavsdk](https://pypi.org/project/mavsdk/), [PyPI mavsdk-grpc](https://pypi.org/project/mavsdk-grpc/)
- MAVSDK-Python 예제 목록에 다중 기체 전용 예제 없음(goto, mission, offboard_* 등) — [MAVSDK-Python examples](https://github.com/mavlink/MAVSDK-Python/tree/main/examples)
- DroneKit-Python 마지막 push 2024-05-30 → 사실상 유지보수 정체 — [dronekit/dronekit-python](https://github.com/dronekit/dronekit-python)

### Inferences
- 권장 구성(추정): ArduPilot SITL 사전빌드 바이너리 3~5개(`arducopter` ×1~2, `ardurover` rover ×1, `ardurover` `--model motorboat` ×1)를 `-I 0..4`로 띄우고, 백엔드는 **pymavlink**로 각 `tcp:127.0.0.1:5760+10*i`에 직접 연결(GUIDED 모드 `SET_POSITION_TARGET_GLOBAL_INT`/`MISSION_ITEM_INT`). MAVProxy/QGC 없이도 가능. 서울 좌표는 `--home lat,lon,alt,heading`(또는 `-L` 위치)로 지정.
- 2026-10 시점 MAVSDK는 API 전환기 → 24시간 해커톤에서는 문서·예제가 오래 축적된 **pymavlink** 쪽이 리스크가 낮다(추정). MAVSDK를 쓰려면 `mavsdk<4` 고정 또는 `mavsdk-grpc` 사용, 기체마다 `System(port=50051+i)`로 서버 포트를 분리(README의 `port` 인자 설명에서 추론).
- 노트북 자원(추정, 출처 없음): ArduPilot SITL 내장 물리모델 인스턴스는 프로세스당 CPU 수%·수십 MB 수준이라 5대도 무난, PX4+Gazebo(gz)는 GPU 렌더링 포함 시 무겁고 Linux 전용 → WSL2/윈도 노트북에서는 ArduPilot 쪽이 안전.
- 셋업 시간(추정): ArduPilot 사전빌드 바이너리+pymavlink는 1~2시간 내, 소스 빌드(waf)는 환경 설치 포함 반나절 위험, PX4+Gazebo는 반나절~하루 위험.
- 리스크 헤지: 데모 경로는 팀 자체 **순수 Python 운동학 시뮬**(B3)로 돌리고, SITL은 "실 오토파일럿 연동 가능" 증명용 옵션 어댑터로 두는 이중화가 안전(추정).

### Gaps
- 노트북 기준 SITL 인스턴스당 CPU/RAM 공식 수치는 찾지 못함.
- ArduPilot 공식 문서에서 서로 다른 기체 종류(Copter+Rover+boat) 혼합 실행 예시는 찾지 못함 — `-I`로 개별 실행하면 된다는 것은 옵션 설명에 근거한 추론.
- 사전빌드 SITL 바이너리를 `sim_vehicle.py` 없이 직접 실행할 때의 정확한 인자(`--model`, `--defaults`, `-I`)는 이번에 검증하지 못함(바이너리 `--help` 확인 필요).

## B2. AFRL OpenUxAS + OpenAMASE (LMCP) — 2026년 실용성

### Takeaway
OpenUxAS는 **아직 유지보수 중**(develop 브랜치 2026-08-07 커밋)이고 다중 UxV 작업 할당 파이프라인(약 30개 서비스, ZeroMQ+LMCP)을 갖춘 "정답지" 같은 레퍼런스지만, **Ubuntu 20.04/22.04 + 자체 `anod` 빌드 + Java 11(OpenAMASE)** 의존이 무겁고 라이선스에 **사용 등록 이메일 조건**이 있다. 24시간 데모의 핵심 경로로는 비추천, 개념·메시지 설계 참고용으로 적합.

### Cited Findings
- README 원문: `"UxAS is a collection of modular services that interact via a common message-passing architecture. Similar in design to Robot Operating System (ROS)..."`, `"UxAS uses the open-source library ZeroMQ to connect all services to each other."`, `"The content of each message conforms to the Light-weight Message Control Protocol (LMCP) format."`, `"In all, UxAS has approximately 30 services."`, `"A core functionality provided by UxAS is the mechanism to calculate near-optimal task allocation across teams of unmanned vehicles."` — [afrl-rq/OpenUxAS README](https://github.com/afrl-rq/OpenUxAS)
- 빌드 요건: `"1. Ubuntu 22.04 or 20.04"`, `OpenUxAS$ ./anod build uxas`, `./anod build amase`, `./run-example 02_Example_WaterwaySearch` — [afrl-rq/OpenUxAS README](https://github.com/afrl-rq/OpenUxAS)
- 라이선스: `"publicly released under the Air Force Open Source Agreement Version 1.0"`, `"**NOTE the terms of the license include registering use of the software by emailing afrl.rq.opensource@us.af.mil**"` — [afrl-rq/OpenUxAS README](https://github.com/afrl-rq/OpenUxAS)
- 유지보수: OpenUxAS 기본 브랜치 `develop` 최근 커밋 2026-08-07(`Updated session files associated with atbb.`), 2026-04 VisibilityGraph 수정들; 별 68개 — [OpenUxAS commits](https://github.com/afrl-rq/OpenUxAS/commits/develop)
- OpenAMASE: 기본 브랜치 `master` 최근 커밋 2024-07-11(`Updated readme to reflect requirment of Java JDK 11.`), 최신 릴리스 v1.3.2(2024-01-23); 설명 `"Project for simulating multi-UAV missions"` — [afrl-rq/OpenAMASE](https://github.com/afrl-rq/OpenAMASE), [OpenAMASE commits](https://github.com/afrl-rq/OpenAMASE/commits/master)
- LmcpGen 최근 push 2024-11-13, OpenUxAS-bootstrap은 archived(2021) — [afrl-rq/LmcpGen](https://github.com/afrl-rq/LmcpGen), [afrl-rq/OpenUxAS-bootstrap](https://github.com/afrl-rq/OpenUxAS-bootstrap)

### Inferences
- 심사위원 어필용으로 "AFRL OpenUxAS의 Task/Assignment 개념(LMCP `Task`, `AutomationRequest`, `AssignmentCostMatrix` 구조)을 참고해 경량 Python으로 재구현"이라고 설명하는 정도가 비용 대비 효과적(추정). 메시지 이름은 OpenUxAS 문서로 재확인 필요.
- OpenAMASE는 Java GUI 시뮬레이터라 우리 MapLibre COP와 중복 → 채택 실익 낮음(추정).

### Gaps
- 최신 OpenUxAS가 WSL2·Ubuntu 24.04에서 빌드되는지, 빌드 소요시간은 확인 못함.
- LMCP 메시지 세부(필드명)는 이번에 원문 확인하지 않음.

## B3. 경량 대안 (순수 Python 운동학 시뮬, Mesa 등)

### Takeaway
24시간·Python 3.11 스택에서는 **자체 운동학 시뮬(점질량 + 도메인별 속도/선회율/체공·배터리 + 링크 모델)**이 가장 안전하다. Mesa는 최신판이 Python 3.12 이상을 요구하므로 3.11이면 `mesa<3.4`(3.3.1) 고정이 필요하고, 실시간 WebSocket 스트리밍 구조와는 궁합이 애매하다. SUPPORTY의 시뮬도 사실상 70줄짜리 등속 직선 모델이었다(A2).

### Cited Findings
- Mesa 설명 `"Mesa is an open-source Python library for agent-based modeling..."`, Apache-2.0, 활발(pushed 2026-10-06) — [mesa/mesa](https://github.com/projectmesa/mesa)
- Mesa 버전별 `requires_python`: 3.3.1(>=3.11, 2025-11-07)까지 3.11 지원, 3.4.0(2025-12-24)부터 `>=3.12`, 최신 3.5.1(2026-03-15) `>=3.12` — [PyPI mesa](https://pypi.org/project/mesa/)
- SUPPORTY 비교 기준: `SPEED = {"air": 18.0, "ground": 4.0, "sea": 6.0}` 등속 이동 — [M/c2/sim.py#L34-L60](https://github.com/jang961111-hash/SKYFLEET-C2/blob/cad1fca6799deb5ef24c84721d889f2aec164816/c2/sim.py#L34-L60)
- PX4 SIH는 `"Headless by default for fastest iteration"`(외부 시뮬레이터 없이 PX4 내부 물리) — [PX4 Simulation](https://docs.px4.io/main/en/simulation/)
- MAVLink 호환 경량 시뮬로는 ArduPilot SITL 내장 물리모델(Gazebo 불필요, 사전빌드 바이너리) — [ArduPilot SITL docs](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html), [firmware.ardupilot.org](https://firmware.ardupilot.org/Rover/stable/SITL_x86_64_linux_gnu/)

### Inferences
- 권장(추정): `modules/sim`에 도메인별 파라미터(공중: 순항 15–20 m/s, 지상: 3–5 m/s 도로/험지 계수, 해상: 5–8 m/s 수역 마스크)와 **링크 품질(거리·음영 폴리곤)**, 배터리/체공시간 소모, 고장/링크상실 이벤트 주입을 넣으면 SUPPORTY 대비 "현실감 + 재계획 트리거"를 확보. 수치는 가상값으로 명시.
- 해상 자산은 육지 진입을 막는 수역 마스크(한강 폴리곤 등, 로컬 GeoJSON)가 있어야 지도상 어색함이 없음(추정).

### Gaps
- 공중/지상/해상 UxV의 공개 대표 성능값(속도·체공) 출처는 이번에 조사하지 않음 → 가상값으로 표기 필요.

## B4. 이기종 팀 작업 할당·실시간 재계획 알고리즘

### Takeaway
24시간 데모에는 **(1) 기본: 비용행렬 + `scipy.optimize.linear_sum_assignment`(직사각 행렬·불가능 쌍 큰 비용) 로 즉시 최적 1:1 배정, (2) 이벤트 시(신규 임무·자산 상실) 재실행 = 재계획, (3) 고급 옵션: OR-Tools 라우팅(자산별 시작점·다중 임무 순서·시간창) 또는 CBBA(분산·통신 단절 강인성 스토리)** 가 적합. 단, 최신 scipy 1.18은 Python 3.12 이상이므로 3.11 스택에선 scipy 1.17.x가 설치된다.

### Cited Findings
- scipy: 시그니처 `scipy.optimize.linear_sum_assignment(cost_matrix, maximize=False)`, `"This function can also solve a generalization of the classic assignment problem where the cost matrix is rectangular."`, `"This implementation is a modified Jonker-Volgenant algorithm with no initialization."`(Crouse 2016) — [scipy docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html)
- scipy 버전: 1.17.1(>=3.11, 2026-02-23)이 3.11 지원 마지막, 1.18.0(2026-06-19)부터 `>=3.12` — [PyPI scipy](https://pypi.org/project/scipy/)
- OR-Tools VRP: `"the goal is to find optimal routes for multiple vehicles visiting a set of locations"`; API `pywrapcp.RoutingIndexManager(...)`, `pywrapcp.RoutingModel(manager)`, `routing.SolveWithParameters(search_parameters)`, `FirstSolutionStrategy.PATH_CHEAPEST_ARC` — [OR-Tools VRP](https://developers.google.com/optimization/routing/vrp)
- OR-Tools 자산별 시작/종료: `"You can also set possibly different start and end locations for each vehicle in the problem."`, `"vehicles are allowed to start and end at arbitrary locations."`, 시간 제한 `search_parameters.time_limit.seconds = 30` — [OR-Tools routing tasks](https://developers.google.com/optimization/routing/routing_tasks)
- OR-Tools 버전 9.15.6755(2026-01-14, `>=3.9`), Apache-2.0, 활발 — [PyPI ortools](https://pypi.org/project/ortools/), [google/or-tools](https://github.com/google/or-tools)
- CBBA 원 논문: `Choi, H.-L., Brunet, L., and How, J. P., "Consensus-Based Decentralized Auctions for Robust Task Allocation," IEEE Transactions on Robotics, vol. 25, Aug. 2009, pp. 912–926.` — [IEEE Xplore 5072249](https://ieeexplore.ieee.org/abstract/document/5072249), 인용 출처 [CBBA-Python README](https://github.com/zehuilu/CBBA-Python)
- CBBA 구현: `zehuilu/CBBA-Python`(MIT, 별 131, 마지막 push 2021-04-22, 의존성 numpy+matplotlib, 설정 `AGENT_TYPES: ["quad", "car"]`, `TASK_TYPES: ["track", "rescue"]`, `"The i-th task type is associated with the i-th agent type."`, 과업 `TASK_VALUE`, `START_TIME`, `END_TIME`, `DURATION` 시간창) — [zehuilu/CBBA-Python](https://github.com/zehuilu/CBBA-Python)
- 기타 CBBA 구현: `keep9oing/consensus-based-bundle-algorithm`(Python, 2022-11), `filloax/tesi-task-auction`(CBAA·CBBA, Python, 2021-09), `jfangwpi/cbba_sim`(C++ 하드웨어 데모, 2019) — [GitHub search: cbba](https://github.com/search?q=cbba&type=repositories)
- 참고 구현 사례: OpenUxAS도 `"near-optimal task allocation across teams of unmanned vehicles"`를 핵심 기능으로 둠 — [afrl-rq/OpenUxAS](https://github.com/afrl-rq/OpenUxAS)

### Inferences
- 설계 제안(추정): 비용 = `ETA(거리/도메인속도, 도메인 불가능=∞) × 우선순위 가중 + 배터리 위험 + 링크 위험`. 능력 불일치·도메인 불가(예: USV→내륙)는 큰 상수로 막음. 화면에 **"왜 이 자산인가" 비용 분해 툴팁**을 띄우면 SUPPORTY의 블랙박스/랜덤 배정과 확실히 대비.
- 재계획 트리거: 신규 P1 임무, 자산 링크 상실/배터리 임계, 운용자 거부 — 트리거마다 헝가리안 재실행(수십×수십 행렬은 ms 단위, 추정). 변경분만 "승인 대기"로 운용자에게 제시 → 인지부하 지표와 연결.
- CBBA는 코드가 오래됐지만 numpy만 필요해 이식 쉬움. "통신 단절 시 자산 간 합의로 배정 유지" 스토리는 군 심사위원에게 어필되나 24시간 내 디버깅 리스크 있음 → 2순위.
- OR-Tools는 다중 임무 순서(한 자산이 여러 정찰점 순회)에 필요할 때만. 시간 제한을 1–2초로 걸어 UI 응답성 유지(추정).

### Gaps
- 헝가리안 vs CBBA vs VRP의 소규모(3–10 자산) 실시간 성능 비교 공개 벤치마크는 찾지 못함.

## B5. 상호운용 표준 (MAVLink, STANAG 4586, JAUS, MOSA/UCI, ROS 2) + CoT/TAK 연동

### Takeaway
24시간 안에 **실제로 보여줄 수 있는 표준은 MAVLink(SITL 연동)와 CoT(Cursor-on-Target)**다. `pytak`으로 자산 위치를 CoT XML로 만들어 **UDP 멀티캐스트 `239.2.3.1:6969`(Mesh SA)**에 쏘면 같은 LAN의 ATAK/WinTAK에 TAK 서버 없이 마커가 뜬다(벤더 자료로 확인, 우리 환경 미검증). STANAG 4586(LOI 1–5)·JAUS(AS5669)·OMS/UCI는 구현보다는 **"어댑터 계층(VSM) 구조로 설계했다"는 설명용**이 현실적이다.

### Cited Findings
- pytak: `"PyTAK is a Python library and command-line TAK client for building small, usable TAK clients, servers, and gateways."`, 전송 `"TCP, TLS, UDP unicast, UDP multicast (Mesh SA), UDP broadcast, file, stdout, WebSockets"`, `"No required external deps: pure-Python asyncio core"`; 예제 CoT 이벤트 `ET.Element("event", version="2.0", type="t-x-d-d", uid="myMarker", how="m-g", time=pytak.cot_time(), start=pytak.cot_time(), stale=pytak.cot_time(3600))` — [snstac/pytak README](https://github.com/snstac/pytak)
- pytak 기본 COT_URL: `"udp+wo://239.2.3.1:6969 (ATAK Mesh SA multicast, write-only)"`; `"Add the +wo modifier (udp+wo://) to run write-only without binding the port."`; `PYTAK_MULTICAST_LOCAL_ADDR` = `"Set this to the IP of the interface connected to your TAK network."` — [pytak configuration](https://pytak.readthedocs.io/en/latest/configuration/)
- pytak 7.6.1(2026-08-23, `>=3.6,<4`), 활발(pushed 2026-10-01), Apache-2.0 — [PyPI pytak](https://pypi.org/project/pytak/), [snstac/pytak](https://github.com/snstac/pytak)
- 같은 저자의 게이트웨이 패턴: `adsbcot` "Display Aircraft in TAK - ADS-B to TAK Gateway", `aiscot` "Display Ships in TAK - AIS to TAK Gateway" — [snstac/adsbcot](https://github.com/snstac/adsbcot), [snstac/aiscot](https://github.com/snstac/aiscot)
- 239.2.3.1:6969 = Mesh SA: `"Out-of-the-box, the device will transmit Cursor on Target CoT to the multicast Mesh SA group of 239.2.3.1:6969"`, `"tested with all TAK Products, including iTAK, WinTAK & ATAK"`(벤더 문서) — [AryaOS AirTAK C-UAS Getting Started](https://aryaos.readthedocs.io/en/latest/airtak_cuas_getting_started/); HyteraTAK도 이를 `"default WinTAK multicast address 239.2.3.1 and port 6969"`로 기술 — [PyPI hyteratak](https://pypi.org/project/hyteratak/)
- TAK 서버(필요 시): FreeTAKServer 마지막 push 2024-10-29(EPL-2.0, 유지보수 정체 의심), OpenTAKServer 활발(2026-10-07, GPL-3.0, `"Yet another open source TAK Server for ATAK, iTAK, and WinTAK"`) — [FreeTAKTeam/FreeTakServer](https://github.com/FreeTAKTeam/FreeTakServer), [brian7704/OpenTAKServer](https://github.com/brian7704/OpenTAKServer)
- 클라이언트 입수: ATAK-CIV는 Google Play 공개 배포(2020 승인), WinTAK-CIV는 tak.gov 제품 페이지에서 제공(계정 필요 추정); 위키백과는 배포 채널을 더 좁게 기술 → 상충 — [tak.gov products](https://tak.gov/products), [Wikipedia ATAK](https://en.wikipedia.org/wiki/Android_Team_Awareness_Kit)
- STANAG 4586 LOI: `"Level 1: Indirect receipt/transmission of UAV related data and metadata."` … `"Level 4: Control and monitoring of the UAV without launch and recovery."`, `"Level 5: Control and monitoring of the UAV including launch and recovery."`; 구성요소 VSM(Vehicle Specific Module), CUCS(Core UCS), CCI 등 — [Kutta: STANAG 4586 Interoperability](https://kuttatech.com/stanag-4586-interoperability/), [US10384779B2 patent](https://patents.google.com/patent/US10384779), [NATO STO EN-SCI-271-03](https://www.sto.nato.int/publications/STO%20Educational%20Notes/STO-EN-SCI-271/EN-SCI-271-03.pdf); Edition 3 초안 문서 — [archives.defense.gouv.fr 4586 draft](https://archives.defense.gouv.fr/content/download/552732/9407966/file/4586eed3draft.pdf)
- JAUS: OpenJAUS(C++ SDK, AS5669A 전송 구현, 일부 패키지는 표준 문서 배포권 때문에 제한), JAUS++(BSD, AS5669/AS5710/AS6009, 2011–2013 활동), JTS(JSIDL/AS5684A 설계 도구) — [docs.openjaus.com](https://docs.openjaus.com/2024.0/home/), [openjaus.com/compare](https://openjaus.com/compare), [ACTIVE-IST JAUS++](https://active-ist.sourceforge.net/jaus++.php?menu=jaus), [Wikipedia JAUS Tool Set](https://en.wikipedia.org/wiki/JAUS_Tool_Set)
- MOSA/OMS/UCI: 2019년 미 육·해·공군 장관 메모가 MOSA 하위 표준으로 `SOSA, FACE, VICTORY, and OMS/UCI`를 명시; UCI는 공중 플랫폼 임무 수준 통제를 위한 공통 메시지 어휘 — [Military Aerospace (2019)](https://www.militaryaerospace.com/home/article/16709609/pentagon-reinforces-mandate-for-open-systems-standards-like-sosa-face-and-victory), [DSIAC](https://dsiac.dtic.mil/articles/pentagon-reinforces-mandate-for-electronics-design-open-systems-standards-like-sosa-face-and-victory), [AFRL OAM brochure](https://www.vdl.afrl.af.mil/programs/oam/brochure.php), [Tokar HILT 2016](https://sigada.hosting.acm.org/conf/hilt2016/paper-Tokar.pdf)
- ROS 2 생태계: PX4 ↔ ROS 2는 uXRCE-DDS(`MicroXRCEAgent udp4 -p 8888`); 다중 공중로봇 ROS 2 프레임워크 Aerostack2(활발, 2026-09), 이기종 로봇 플릿 관리 Open-RMF(활발, 2026-08) — [PX4 Multi-Vehicle Sim](https://docs.px4.io/main/en/sim_gazebo_gz/multi_vehicle_simulation), [aerostack2/aerostack2](https://github.com/aerostack2/aerostack2), [open-rmf/rmf](https://github.com/open-rmf/rmf)
- MAVLink 본체 활발(2026-10-07), QGroundControl 활발(2026-10-07) — [mavlink/mavlink](https://github.com/mavlink/mavlink), [mavlink/qgroundcontrol](https://github.com/mavlink/qgroundcontrol)

### Inferences
- CoT 연동은 gateway 모듈에 "CoT 출력 어댑터" 1개 파일로 붙일 수 있는 크기(pytak 의존 없이도 CoT XML 문자열 + `socket` UDP 멀티캐스트로 수십 줄, 추정). 시연: 노트북 COP와 **팀원 안드로이드 폰의 ATAK-CIV**에 같은 자산이 동시에 뜨는 장면 → "기존 군 전술망(TAK)에 바로 꽂힌다"는 메시지. 인터넷 불필요(같은 Wi-Fi/핫스팟)라 오프라인 정책과도 맞음. 단 Wi-Fi AP의 멀티캐스트 차단·클라이언트 격리 가능성은 사전 리허설 필요(추정).
- CoT type 코드(예: 우군 공중 `a-f-A`, 우군 지상 `a-f-G`, 우군 해상 `a-f-S`)는 MIL-STD-2525 기반 관례 — 이번 조사에서 1차 출처 미확인(추정, 확인 필요).
- STANAG 4586은 "도메인별 Vehicle Specific Module(VSM) 어댑터 + 공통 코어" 구조로 우리 아키텍처(sim/SITL/실기체 어댑터 → 공통 contracts)를 설명하는 데 쓰면 좋음. 실제 메시지 구현은 문서 비공개·분량상 비현실적.
- SUPPORTY는 표준 인터페이스가 전무(RC PWM 직접 HTTP) → **"MAVLink + CoT + STANAG 4586식 VSM 계층"** 은 명확한 차별점.

### Gaps
- ATAK/WinTAK이 기본 설정에서 239.2.3.1:6969 입력을 자동 수신하는지에 대한 TAK 공식 문서는 찾지 못함(벤더/서드파티 자료 기반).
- WinTAK-CIV 다운로드 조건(계정·승인)과 최신 버전은 tak.gov에서 직접 확인 필요.
- STANAG 4586 Ed.4 등 최신판 내용은 비공개라 확인 불가.

## B6. 다중 도메인 무인 작전용 공개 데이터셋·시나리오 생성기

### Takeaway
"이기종 다중 UxV 임무" 전용으로 바로 쓸 공개 데이터셋/시나리오 생성기는 **사실상 없다**. 2026년 연구 프레임워크(MultiUAV-Plat 벤치마크, AUSPEX, HERCULES)와 OpenUxAS 예제 시나리오가 참고 가능한 수준이며, 해커톤에서는 **시드 고정 합성 시나리오 생성기**를 직접 만드는 것이 정책(공개·가상 데이터)에도 맞다.

### Cited Findings
- MultiUAV-Plat(arXiv 2606.31073): LLM 지향 다중 UAV 협업 과업계획 플랫폼·벤치마크, 3개 시나리오 계열(area search, area assignment with patrol, target assignment) × 5개 난이도 × 난이도별 5개 시드 — [arXiv 2606.31073](https://arxiv.org/pdf/2606.31073)
- AUSPEX: `"an open-source framework for automated planning and execution in multi-UAV systems"`, 이기종 UAV·여러 AI 플래너 통합, SAR 시나리오 HIL 검증 — [ICAPS 2026 demos](https://icaps26.icaps-conference.org/program/demos), [AAMAS 2026 paper](https://ifaamas.org/Proceedings/aamas2026/pdfs/QTXJ5819.pdf)
- HERCULES(arXiv 2606.22756): 이기종 UAV–UGV SLAM·협업 인지·탐사용 오픈소스 시뮬 + 데이터 수집 도구 — [arXiv 2606.22756](https://arxiv.org/pdf/2606.22756)
- QGroundControl 확장(자동 계획·재계획 인터페이스) — [arXiv 2402.18754](https://arxiv.org/html/2402.18754v1)
- OpenUxAS 내장 예제 시나리오: `01_HelloWorld`, `02_Example_WaterwaySearch`, `./run-example --list` — [afrl-rq/OpenUxAS](https://github.com/afrl-rq/OpenUxAS)
- ArduPilot 군집 배치 파일 `Tools/autotest/swarminit.txt` — [ArduPilot SITL docs](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html)
- (배경 교통 레이어 아이디어) AIS·ADS-B를 TAK로 보내는 공개 게이트웨이 존재 — [snstac/aiscot](https://github.com/snstac/aiscot), [snstac/adsbcot](https://github.com/snstac/adsbcot)

### Inferences
- 권장(추정): `demo/scenarios/*.json`에 시드 고정 시나리오(서울 한강·산지·도심 혼재, 가상 요청 타임라인, 링크 음영 폴리곤, 자산 고장 이벤트)를 정의하고, 같은 시나리오를 "수동 운용" vs "우리 시스템"으로 재생해 **완료시간·개입 횟수·부하 지표를 A/B 비교**하면 SUPPORTY가 주장만 한 "인력 절감·성공률 측정"을 실제 숫자로 보여줄 수 있음.
- 실제 AIS/ADS-B 실시간 데이터는 인터넷·개인정보(선박·항공기 식별) 이슈 → 정책상 데모 경로에서는 배제하고 가상 배경 트래픽만 사용(추정).

### Gaps
- MultiUAV-Plat·AUSPEX의 저장소 URL·라이선스는 이번에 확인하지 못함.
- 공개된 "다중 도메인(공·지·해) 무인 임무 요청 로그" 데이터셋은 찾지 못함.
