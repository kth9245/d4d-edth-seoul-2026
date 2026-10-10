import type { Frame, Target } from "../../contracts.gen";
import { kstTime } from "../cards/kstTime";
import { mmss } from "../run/mmss";
import type { Track } from "./trackState";
import { clueTags } from "./clueTags";

export type StageKey = "gone" | "strike" | "ask" | "lost" | "rf" | "never" | "track" | "found";
export interface Stage { key: StageKey; label: string; detail: string; away: boolean }

const DIR_KO = { still: "정지", approach: "접근 추정", away: "이탈(도주) 추정" } as const;

// One target's stage (Part1-32). Targets move through these on their own (one can wait for strike approval while
// another is just found), so the screen counts them and never shows one order for the whole operation.
export function targetStage(f: Frame, t: Target, track: Track): Stage {
  const st = (key: StageKey, label: string, detail: string, away = false): Stage => ({ key, label, detail, away });
  if (track.k === "gone") return st("gone", "무력화", kstTime(t.neutralized_ms ?? f.t_ms));
  const on = f.vehicles.filter((v) => v.status === "active" && v.target_id === t.id);
  const strikers = on.filter((v) => v.active?.command.kind === "strike");
  if (strikers.length) return st("strike", "타격 중", strikers.map((v) => v.id).join("·"));
  const ask = f.reports.find((r) => r.target_id === t.id && !r.resolved_ms && (r.choices ?? []).length > 0
    && r.text.startsWith("타격 승인 요청"));
  if (ask) return st("ask", "허락 대기", `${ask.vehicle_id} 요청`);
  if (track.k === "lost") {
    const speed = (track.speed ?? 0) >= 0.3 ? ` ${(track.speed ?? 0).toFixed(1)} m/s` : "";
    return st("lost", "놓침", `${mmss(track.agoMs ?? 0)} 전 · ${DIR_KO[track.dir ?? "still"]}${speed}`, track.dir === "away");
  }
  if (track.k === "rf") {  // radio, heat or sound only (decision 0069): say what was really picked up
    const tags = clueTags(t).join("·");
    return tags === "RF" ? st("rf", "RF 탐지", "무선만 잡힘") : st("rf", `${tags} 탐지`, `${tags}만 잡힘`);
  }
  if (track.k === "never") return st("never", "미탐", "센서에 안 잡힘");
  if (on.length) return st("track", "추적", on.map((v) => v.id).join("·"));
  return st("found", "발견", `${(t.seen_by ?? []).join("·")} 관측`);
}
