# cop-ui — 지도 관제 화면 (React + MapLibre)

- 책임: gateway `/ws`의 Frame을 받아 지도에 표적·분류·위협도·대응 추천을 표시한다.
- 데이터 타입은 `src/contracts.gen.ts`(자동 생성)만 쓴다. 직접 수정 금지.
- 구조: `src/features/<기능>/` 아래 컴포넌트·hook 1개 = 파일 1개(줄 수 제한 없음, 결정 0023).
- 로직(데이터 변환, hook)은 vitest 테스트를 둔다. 화면 컴포넌트는 테스트 생략 가능.
- 로컬 타일 우선, 온라인 허용(결정 0001). 지도 배경은 `public/tiles/baengnyeong/{z}/{x}/{y}.jpg`(scripts/fetch_tiles_baengnyeong.sh, EOX Sentinel-2, 출처 표기). 옛 서울 벡터 타일(seoul.pmtiles)은 레거시.
- 실행: `npm run dev` (5173, /ws는 8000 proxy) / 테스트: `npm test`
- 담당: map·live·replay 리드 kth9245, editor·setup도 리드(결정 0009: React 경험자가 없어 읽기 전용 카드 + "보고 카드 끼워 넣기" 버튼으로 고정). 작업은 자기 worktree에서 main으로(결정 0010·0014).
