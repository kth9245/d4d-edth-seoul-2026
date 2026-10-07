<!-- prefix: TRK -->
# tracking SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| TRK-01 | predict_tracks | list[Track], t_ms | list[Track] | 등속 모델로 t_ms 위치 예측 | 리드 | 완료 |
| TRK-02 | associate_detections | list[Track], list[Detection], gate_m | dict[id, Detection], list[Detection] | 최근접(gate 이내) 1:1 짝짓기 | 리드 | 완료 |
| TRK-03 | update_tracks | list[Track], dict, t_ms | list[Track] | 위치=탐지, hits+1, 속도=예측오차 β(0.3) 보정 (첫 갱신은 변위/시간) | 리드 | 완료 |
| TRK-04 | initiate_tracks | list[Detection], t_ms, existing_ids | list[Track] | 짝 없는 탐지마다 새 표적, 기존·동시 생성 id와 겹치면 -2,-3 접미사 | 리드 | 완료 |
| TRK-05 | delete_stale_tracks | list[Track], t_ms, max_age_ms | list[Track] | 마지막 탐지 후 3초 지난 표적 삭제 | 리드 | 완료 |
