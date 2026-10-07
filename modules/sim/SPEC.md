<!-- prefix: SIM -->
# sim SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| SIM-01 | load_scenario | path | Scenario | 잘못된 값은 로딩 시 ValueError로 위치와 이유 표시 | 리드 | 완료 |
| SIM-02 | object_positions | Scenario, t_ms | list[TruthPoint] | 등속 이동, appear_s 이전 객체 제외 | 리드 | 완료 |
| SIM-03 | emit_detections | list[TruthPoint], t_ms, seed | list[Detection] | 레이더 탐지 1개/객체, 위치 잡음 σ≈3m, 재현 가능 | 리드 | 완료 |
