<!-- prefix: ONT -->
# ontology SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| ONT-01 | kind_chain | kind, Ontology | list[VehicleKind] | recon_drone → air_vehicle → vehicle, 맨 위는 자기 하나 | kth9245 | 완료 |
| ONT-02 | explain_capability | kind, ActionKind, Ontology | CapabilityReason | 정찰 드론 watch_target 허용 경로·via, strike_target 불가 경로 전체, 지상 로봇 watch_point 허용(행동 하나 provides) | kth9245 | 완료 |
| ONT-03 | infer_capabilities | kind, Ontology | list[ActionKind] | 정찰 드론 9개(타격 없음), 무장 수상정은 타격 있고 통신 중계 없음, 지상 로봇 5개 | kth9245 | 완료 |
| ONT-04 | fill_vehicle_kinds | Scenario | Scenario | d1 타격 없음·kind_path 정찰 드론→공중 기체→기체, 옛 capabilities를 덮어씀, ontology 없거나 kind 없으면 그대로 | kth9245 | 완료 |
| ONT-05 | ontology_view | Scenario(ontology 있음) | OntologyView | 기체 5대 × 행동 10개, d1 strike_target 불가 경로 | kth9245 | 완료 |
