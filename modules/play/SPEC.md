<!-- prefix: PLY -->
# play SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| PLY-01 | load_play | path | Play | 템플릿 2개 로드, 잘못된 파일은 ValueError에 위치 | 황승주 | 예정 |
| PLY-02 | check_links | Play | list[ValidationIssue] | 없는 step을 가리키는 go_step·entry, entry에서 닿을 수 없는 step | 황승주 | 예정 |
| PLY-03 | check_report_points | Play | list[ValidationIssue] | target_found 탈출 뒤 choices 있는 report 없이 approach_target에 닿으면 오류 | 황승주 | 예정 |
| PLY-04 | check_return_battery | Play, specs | (list[ValidationIssue], est_return_battery) | 역할별 경로 길이로 추정, 30% 미만이면 오류. safety.return_feasible 재사용 가능 | 황승주 | 예정 |
| PLY-05 | check_zone | Play, Operation | list[ValidationIssue] | 경로점·목적지가 zone 밖이면 오류 (safety.point_in_polygon) | 황승주 | 예정 |
| PLY-06 | check_play | Play, Operation, specs | PlayCheck | 플레이 하나 검사: 3-2 + 그 플레이를 받는 기체의 영역·능력(domains, capabilities). 기체별 템플릿 통과 | 황승주 | 예정 |
| PLY-07 | expand_action | Action, Domain | CommandKind/None | expand_table.json 9×3 전부 테스트(표 초안은 09 6절), None이면 후보 제외 | 황승주 | 예정 |
| PLY-08 | list_templates | — | list[Play] | demo/plays/*.json 중 template=True | 황승주 | 예정 |
| PLY-09 | draft_play | 문장, Operation | Play(origin=ai_draft) | 캐시 hit면 호출 없음, miss면 1회 호출·스키마 밖이면 재요청 1회, 실패 시 템플릿 반환 | 황승주 | 예정 |
| PLY-11 | check_operation | Operation, plays, specs | PlayCheck | 예시 작전 통과, 보고 지점 뺀 작전 실패 | 황승주 | 예정 |
