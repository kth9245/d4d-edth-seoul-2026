// 자동 생성 파일 (scripts/gen_contracts.py). 직접 수정하지 마세요.
export type SensorType = "rf" | "eoir" | "radar";

export interface Detection {
  id: string;
  sensor: SensorType;
  t_ms: number;
  lat: number;
  lon: number;
  alt_m: number;
  strength: number;
}

export interface Track {
  id: string;
  t_ms: number;
  lat: number;
  lon: number;
  alt_m: number;
  vel_east_mps?: number;
  vel_north_mps?: number;
  hits?: number;
  last_seen_ms: number;
}

export type ObjectClass = "drone" | "balloon" | "bird" | "unknown";

export interface Assessment {
  track_id: string;
  object_class: ObjectClass;
  threat: number;
  reason: string;
}

export type ResponseKind = "observe" | "soft_kill" | "hard_kill";

export interface Response {
  track_id: string;
  kind: ResponseKind;
  reason: string;
}

export interface Frame {
  t_ms: number;
  tracks: Track[];
  assessments: Assessment[];
  responses: Response[];
}
