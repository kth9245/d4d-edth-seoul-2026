# 해커톤 문제 (T1 중심)

출처: 참가자 안내 시트 https://docs.google.com/spreadsheets/d/1z-knlD7tXlieexed2eHruSseUu6dBYt3K-mT5NAbXHg (B-1, B-2 탭)

## 공통 규칙
- 일정: 10/10(토) 10:00 개발 시작 → 10/11(일) 10:00 제출(d4d.tech) → 10:30 1차 현장 심사(팀당 5분) → 14:30 2차 메인 스테이지 피칭.
- 팀당 최대 4명, 트랙 하나의 문제 하나. 트랙 피켓(T1 카키)을 테이블에 비치.
- NO SLIDES: 작동하는 결과물로 증명. 기존 기술을 써도 되지만 해커톤에서 새로 만든 부분을 구분해 발표.
- 공개·가상 데이터만. 비밀·수출통제 정보, 특정 개인 식별·표적화 금지.
- 스페셜 챌린지: SC1 CLIKA BYOD On-device AI(같은 앱을 2종 이상 기기에서 구동 시 우대), SC2 NUCODE Board, SC3 WAY to OREGON(T1 결과물 중심, 미국 Oregon UAS Accelerator 연결).

## T1 Autonomy, Unmanned Systems & Counter-UAS (자율·무인 시스템 및 대드론)
| No. | 유형 | 문제 | SC |
|---|---|---|---|
| T1-1 | 범용 | 1인 다중 무인기 동시 통제 (Multi-UxV Control): 단일 운용자가 공중·지상·해상 이종 무인체계 3대 이상을 동시에 임무 부여·감시·통제. 인지부하 최소화. | — |
| T1-2 | 특수상황 | 산악·도심 혼재 지형 자율 드론 운용 (Terrain-Aware Autonomy): GPS 음영·통신 단절·전자전 속 지형 활용 이동·통신 유지·임무 지속. | SC1 |
| T1-3 | 특수상황 | 수도권 영공 소형드론·풍선 침투 대응 (Gray-zone C-UAS): RF·EO/IR·레이더 융합 저신호 탐지, 도심 오탐 저감, 드론/풍선/조류 분류·위협도, 부수피해 고려 대응(소프트킬/하드킬) 추천, 다중 표적 추적·경보 시각화. | SC1+SC2 |
| T1-4 | 범용 | 무선침묵 환경 피아식별 (Radio-silent IFF): 저방출 피아식별 프로토콜, 2-컴포넌트 challenge-response, MITM·replay 방어, 식별 실패 시 fail-safe 교전규칙 연동. | SC2 |

## 이 저장소의 기본 가정
T1-3을 기준으로 골격을 만들었다. 다른 T1 문제로 바꿀 때 교체할 모듈은 설계 문서 3.1절 참고.
