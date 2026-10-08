<!-- prefix: ASM -->
# assess SPEC

T1-3용, 휴면(결정 0007·docs/research/09 3.9). 파이프라인에서만 뺀다.

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| ASM-01 | classify_track | Track | ObjectClass | 속도·고도 규칙으로 drone/balloon/bird/unknown | 리드 | 완료 |
| ASM-02 | score_threat | Track, ObjectClass, 보호 지점 | (float, str) | 거리·접근 여부·분류로 0~1 점수와 근거 | 리드 | 완료 |
