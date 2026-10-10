// 자동 생성 파일 (scripts/gen_contracts.py). 직접 수정하지 마세요.
export interface GeoPoint {
  lat: number;
  lon: number;
  alt_m?: number;
}

export interface Polygon {
  points: GeoPoint[];
}

export type ActionKind = "move_to" | "patrol_route" | "search_area" | "return_home" | "watch_target" | "watch_point" | "approach_target" | "relay_comms" | "hold" | "strike_target";

export type Domain = "air" | "sea" | "ground";

export interface VehicleSpec {
  id: string;
  name: string;
  domain: Domain;
  speed_mps: number;
  endurance_min: number;
  sensor_range_m: number;
  capabilities?: ActionKind[];
  home: GeoPoint;
  recharge_min?: number;
  kind?: string | null;
  kind_path?: string[];
  rf_range_m?: number;
}

export interface Command {
  id: string;
  vehicle_id: string;
  kind: CommandKind;
  params?: Record<string, unknown>;
  provenance?: Provenance | null;
}

export type CommandKind = "move" | "orbit" | "keep_distance" | "hold" | "follow_route" | "zigzag" | "return_home" | "relay" | "strike";

export type CommandSource = "play_step" | "operator_decision" | "operator_direct" | "injected_plan" | "emergency";

export type EmergencyKind = "link_lost" | "battery_low" | "operator_call";

export interface PassedCommand {
  command: Command;
  checks: string[];
  passed_ms: number;
}

export interface Provenance {
  source: CommandSource;
  play_id?: string | null;
  step_id?: string | null;
  decision_id?: string | null;
  injection_id?: string | null;
  operator_id?: string | null;
  issued_ms: number;
}

export type VehicleStatus = "ready" | "active" | "returning" | "maintenance" | "lost";

export interface VehicleState {
  id: string;
  t_ms: number;
  pos: GeoPoint;
  heading_deg: number;
  battery_pct: number;
  status: VehicleStatus;
  play_id?: string | null;
  step_id?: string | null;
  entered_step?: boolean;
  waypoint_idx?: number;
  active?: PassedCommand | null;
  pending_report_id?: string | null;
  target_id?: string | null;
  decision_id?: string | null;
  emergency?: EmergencyKind | null;
  resume_play_id?: string | null;
  resume_step_id?: string | null;
}

export interface Switch {
  id: string;
  label: string;
  play_by_vehicle: Record<string, string>;
}

export interface Operation {
  id: string;
  name: string;
  purpose?: string;
  area: Polygon;
  zone: Polygon;
  vehicle_ids: string[];
  started_ms?: number | null;
  assign?: Record<string, string>;
  reserve?: Record<string, string[]>;
  switches?: Switch[];
  rotation?: string[];
  rotation_plays?: string[];
  rotation_pools?: Record<string, string[]>;
}

export type TargetKind = "boat" | "fast_boat" | "person" | "unknown";

export interface EnemySpec {
  id: string;
  kind: TargetKind;
  speed_mps: number;
  appear_offset_ms: number;
  pos?: GeoPoint | null;
  from_enemy?: string | null;
  play_id: string;
  emit_start_offset_ms?: number | null;
}

export interface WatchPoint {
  id: string;
  name: string;
  pos: GeoPoint;
  radius_m: number;
}

export interface RouteOffset {
  north_m: number;
  east_m: number;
}

export interface RouteDef {
  id: string;
  name: string;
  points?: GeoPoint[];
  offsets?: RouteOffset[];
}

export type ConditionKind = "target_found" | "arrived" | "time_elapsed" | "battery_below" | "operator_choice" | "signal_received" | "at_time";

export interface Condition {
  kind: ConditionKind;
  params?: Record<string, number | string>;
}

export interface Action {
  kind: ActionKind;
  params?: Record<string, unknown>;
}

export interface Exit {
  cond: Condition;
  go_step: string;
}

export interface Choice {
  id: string;
  label: string;
  play_by_vehicle?: Record<string, string>;
  target_by_vehicle?: Record<string, string>;
}

export interface ReportSpec {
  text: string;
  choices?: Choice[];
  auto_choices?: boolean;
}

export interface Step {
  id: string;
  name: string;
  do: Action;
  on?: Exit[];
  report?: ReportSpec | null;
  ui?: Record<string, unknown>;
}

export interface EmergencyRules {
  battery_low_pct?: number;
  link_lost_step?: string | null;
  battery_low_step?: string | null;
  operator_call_step?: string | null;
}

export interface Play {
  id: string;
  name: string;
  domains: Domain[];
  steps: Step[];
  entry: string;
  emergency?: EmergencyRules;
  origin?: "human" | "ai_draft";
  approved?: boolean;
  template?: boolean;
}

export interface ValidationIssue {
  code: string;
  step_id?: string | null;
  message: string;
}

export interface PlayCheck {
  ok: boolean;
  issues: ValidationIssue[];
  est_return_battery?: Record<string, number>;
}

export type BlockReason = "no_provenance" | "outside_zone" | "battery_insufficient";

export interface Block {
  command_id: string;
  vehicle_id: string;
  reason: BlockReason;
  detail: string;
  alternative?: Command | null;
  t_ms: number;
}

export interface Target {
  id: string;
  kind: TargetKind;
  pos: GeoPoint;
  vel_east_mps: number;
  vel_north_mps: number;
  first_seen_ms: number;
  last_seen_ms: number;
  seen_by?: string[];
  neutralized_ms?: number | null;
  reported_by?: string | null;
  play_id?: string | null;
  step_id?: string | null;
  waypoint_idx?: number;
  step_since_ms?: number | null;
  emitting?: boolean;
  rf_detected?: boolean;
  threat?: number;
  threat_reasons?: string[];
  threat_accum?: number;
}

export type ReportKind = "target_detected" | "target_select" | "vehicle_gap" | "vehicle_lost" | "battery_low" | "injection_pending" | "command_blocked" | "target_neutralized";

export interface Report {
  id: string;
  t_ms: number;
  kind: ReportKind;
  vehicle_id?: string | null;
  target_id?: string | null;
  text: string;
  choices?: Choice[];
  resolved_ms?: number | null;
  decision_id?: string | null;
}

export interface Decision {
  id: string;
  t_ms: number;
  report_id: string;
  choice_id: string;
  operator_id?: string;
}

export interface Assignment {
  vehicle_id: string;
  play_id: string;
  since_ms: number;
  reason: string;
}

export interface Injection {
  id: string;
  t_ms: number;
  label: string;
  play_by_vehicle: Record<string, string>;
  switch_id?: string | null;
  status?: "pending" | "approved" | "rejected";
}

export interface DirectControl {
  id: string;
  vehicle_id: string;
  target: GeoPoint;
  t_ms: number;
}

export interface Metrics {
  operator_actions?: number;
  manual_baseline_actions?: number;
  open_reports_max?: number;
  vehicle_gap_ms?: number;
  blocked_commands?: number;
  decisions?: number;
  commands_sent?: number;
  mission_success?: boolean | null;
}

export type RunStatus = "running" | "paused" | "ended";

export interface RunState {
  status?: RunStatus;
  speed?: number;
}

export interface Frame {
  t_ms: number;
  run: RunState;
  vehicles: VehicleState[];
  targets: Target[];
  reports: Report[];
  assignments: Assignment[];
  blocks: Block[];
  injections: Injection[];
  metrics: Metrics;
  log?: string[];
}

export interface ScenarioEvent {
  offset_ms: number;
  kind: "spawn_target" | "target_move" | "vehicle_link_lost" | "vehicle_battery_set" | "split_target";
  params: Record<string, unknown>;
}

export interface ActionGroup {
  id: string;
  label: string;
  actions: ActionKind[];
}

export interface Ontology {
  groups: ActionGroup[];
  kinds: VehicleKind[];
}

export interface VehicleKind {
  id: string;
  label: string;
  is_a?: string | null;
  provides?: string[];
}

export interface Scenario {
  id: string;
  operation: Operation;
  vehicles: VehicleSpec[];
  plays: Play[];
  events?: ScenarioEvent[];
  enemies?: EnemySpec[];
  watch_points?: WatchPoint[];
  routes?: RouteDef[];
  land?: Polygon[];
  ontology?: Ontology | null;
  seed?: number;
  tick_ms?: number;
  speed?: number;
}

export interface TickInputs {
  decisions?: Decision[];
  direct?: DirectControl[];
  injections?: Injection[];
}

export interface TickOutcome {
  inputs?: TickInputs;
  commands?: Command[];
  passed?: PassedCommand[];
  blocks?: Block[];
  new_reports?: Report[];
  reports?: Report[];
  assignments?: Assignment[];
  states?: VehicleState[];
  targets?: Target[];
  plays?: Record<string, Play>;
}

export interface CapabilityReason {
  action: ActionKind;
  allowed: boolean;
  path: string[];
  via?: string | null;
}

export interface VehicleCapabilities {
  vehicle_id: string;
  kind: string;
  reasons: CapabilityReason[];
}

export interface OntologyView {
  ontology: Ontology;
  vehicles: VehicleCapabilities[];
}

export interface ObjectNode {
  id: string;
  type: "vehicle" | "target" | "report" | "decision" | "command" | "block";
  label: string;
  t_ms?: number | null;
}

export interface ObjectLink {
  src: string;
  dst: string;
  rel: "reported" | "about" | "answers" | "from_decision" | "sent_to" | "aims_at" | "blocked";
}

export interface ObjectGraph {
  focus: string;
  nodes: ObjectNode[];
  links: ObjectLink[];
}

export interface DecisionIn {
  report_id: string;
  choice_id: string;
}

export interface DirectIn {
  vehicle_id: string;
  target: GeoPoint;
}

export interface SwitchIn {
  switch_id?: string | null;
  play_by_vehicle?: Record<string, string>;
}

export interface DraftIn {
  text: string;
}

export interface Accepted {
  id: string;
  t_ms: number;
}

export interface ScenarioInfo {
  id: string;
  name: string;
  purpose?: string;
  active?: boolean;
}

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

export interface LegacyFrame {
  t_ms: number;
  tracks: Track[];
  assessments: Assessment[];
  responses: Response[];
}
