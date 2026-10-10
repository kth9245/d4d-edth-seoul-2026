<!-- prefix: PLY -->
# role SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| PLY-01 | load_role | path | Role | 템플릿 2개 로드, 잘못된 파일은 ValueError에 위치 | 황승주 | 완료 |
| PLY-02 | check_links | Role | list[ValidationIssue] | 없는 step을 가리키는 go_step·entry, entry에서 닿을 수 없는 step | 황승주 | 완료 |
| PLY-03 | check_report_points | Role | list[ValidationIssue] | target_found 탈출 뒤 choices 있는 report 없이 approach_target에 닿으면 오류 | 황승주 | 완료 |
| PLY-04 | check_return_battery | Role, specs | (list[ValidationIssue], est_return_battery) | 역할별 경로 길이로 추정, 30% 미만이면 오류. safety.return_feasible 재사용 가능 | 황승주 | 완료 |
| PLY-05 | check_zone | Role, Operation | list[ValidationIssue] | 경로점·목적지가 zone 밖이면 오류 (safety.point_in_polygon) | 황승주 | 완료 |
| PLY-06 | check_role | Role, Operation, specs | RoleCheck | Role 하나 검사: 3-2 + 그 Role을 받는 기체의 영역·능력(domains, capabilities). 기체별 템플릿 통과 · 능력 부족 메시지에 kind_path 경로(결정 0038) | 황승주 | 완료 |
| PLY-07 | expand_action | Action, Domain | CommandKind/None | expand_table.json 9×3 전부 테스트(표 초안은 09 6절), None이면 후보 제외 | 황승주 | 완료 |
| PLY-08 | list_templates | — | list[Role] | demo/roles/*.json 중 template=True | 황승주 | 완료 |
| PLY-09 | draft_role | 문장, Operation | Role(origin=ai_draft) | 캐시 hit면 호출 없음, miss면 1회 호출·스키마 밖이면 재요청 1회, 실패 시 템플릿 반환 | 황승주 | 완료 |
| PLY-11 | check_operation | Operation, roles, specs | RoleCheck | 예시 작전 통과, 보고 지점 뺀 작전 실패 | 황승주 | 완료 |
| PLY-12 | build_draft_prompt | 문장, Operation | str | 같은 입력이면 같은 문자열, 문장·ActionKind 9·ConditionKind 6·zone 좌표 포함, started_ms·assign 등을 바꿔도 같음, 남은 자리표시 없음 | kth9245 | 완료 |
| PLY-13 | draft_cache_key | 문장, Operation | str(sha256 hex) | AI 초안 캐시 키 = 문장(앞뒤 공백 제외)·작전 지역·작전 구역. 작전 이름·목적·배정·시각은 안 넣음, 같은 구역의 새 작전·24시간 작전도 시연 캐시를 씀(결정 0062) | kth9245 | 완료 |
