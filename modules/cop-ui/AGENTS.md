# cop-ui — 지도 관제 화면 (React + MapLibre)

- 책임: gateway `/ws`의 Frame과 `GET /operation`의 구역(작전 생성 때 한 번 정함)을 받아 백령도 지도에 기체·표적·구역을 그린다. 카드 열은 Part1-10.
- 데이터 타입은 `src/contracts.gen.ts`(자동 생성)만 쓴다. 직접 수정 금지.
- 구조: `src/features/<기능>/` 아래 컴포넌트·hook 1개 = 파일 1개(줄 수 제한 없음, 결정 0023).
- 로직(데이터 변환, hook)은 vitest 테스트를 둔다. 화면 컴포넌트는 테스트 생략 가능.
- 로컬 타일 우선, 온라인 허용(결정 0001). 지도 배경은 `public/tiles/baengnyeong/{z}/{x}/{y}.jpg`(scripts/fetch_tiles_baengnyeong.sh, EOX Sentinel-2, 출처 표기). 옛 서울 벡터 타일(seoul.pmtiles)은 쓰지 않음.
- 지도에 글자 레이어(symbol) 금지: 오프라인이라 글꼴(glyphs)이 없다. 이름표는 HTML Marker(`features/map/markers.ts`).
- 게이트웨이 없이 화면 개발: `npm run dev` 뒤 `?scene=s1`~`s6`(contracts/examples/frames, 개발 서버 전용).
- 실행: `npm run dev` (5173, /ws는 8000 proxy) / 테스트: `npm test`
- 담당: map·live·replay 리드 kth9245, editor·setup도 리드(결정 0009: React 경험자가 없어 읽기 전용 카드 + "보고 카드 끼워 넣기" 버튼으로 고정). 작업은 자기 worktree에서 main으로(결정 0010·0014).
