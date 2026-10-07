# cop-ui — 지도 관제 화면 (React + MapLibre)

- 책임: gateway `/ws`의 Frame을 받아 지도에 표적·분류·위협도·대응 추천을 표시한다.
- 데이터 타입은 `src/contracts.gen.ts`(자동 생성)만 쓴다. 직접 수정 금지.
- 구조: `src/features/<기능>/` 아래 컴포넌트·hook 1개 = 파일 1개, 200줄 이하.
- 로직(데이터 변환, hook)은 vitest 테스트를 둔다. 화면 컴포넌트는 테스트 생략 가능.
- 외부 네트워크 금지: 지도 배경은 `public/tiles/seoul.pmtiles`(scripts/fetch_tiles.sh). 글꼴·라벨 없이 그린다.
- 실행: `npm run dev` (5173, /ws는 8000 proxy) / 테스트: `npm test`
- 담당: 팀원 4. 브랜치 `cop-ui/<주제>`.
