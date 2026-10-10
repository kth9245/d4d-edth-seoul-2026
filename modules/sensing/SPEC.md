<!-- prefix: SNS -->
# sensing SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| SNS-01 | drop_invalid_detections | list[Detection] | list[Detection] | 위경도 범위 밖·음수 고도 제거 | 리드 | 완료 |
| SNS-02 | observe_targets | states, specs, targets, t_ms | targets | 범위 안이면 seen_by 추가·last_seen 갱신(그때 위치·속도 last_seen_pos·last_seen_vel_*, 결정 0047), 밖이면 제거. 잡음 없음 | 최동호 | 완료 |
| SNS-03 | score_target | 종류·위치·속력·관찰 여부·방출 여부·수신 기체(위치, rf_range_m)·기준점·누적값·tick_ms | ThreatScore(score 0~100, reasons, rf_detected, accum) | 종류+반경 안+RF+속도(결정 0039, 정수 0.01 단위, 상한 100). 점수 40 이상이고 관찰 중이면 accum += 점수×tick_ms, 아니면 0 | 최동호 | 완료 |
