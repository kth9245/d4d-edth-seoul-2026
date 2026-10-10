<!-- prefix: SNS -->
# sensing SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| SNS-01 | drop_invalid_detections | list[Detection] | list[Detection] | 위경도 범위 밖·음수 고도 제거 | 리드 | 완료 |
| SNS-02 | observe_targets | states, specs, targets, t_ms | targets | 범위 안이면 seen_by 추가·last_seen 갱신, 밖이면 제거. 잡음 없음 | 최동호 | 완료 |
