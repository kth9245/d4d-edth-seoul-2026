import { useEffect, useState } from "react";
import type { GeoPoint } from "../../contracts.gen";
import { postPoint } from "../board/postPoint";
import { postDirect } from "../cards/postDirect";
import type { PendingAim } from "./directAims";
import type { DirectProps, Pick } from "./MapView";

const at = (p: GeoPoint) => `${p.lat.toFixed(4)}, ${p.lon.toFixed(4)}`;

// Direct control on the map (Part1-11): click a vehicle to select it, click the map to send it there
// (POST /direct), Esc or the same vehicle again cancels. Whether the order passes is the server's safety
// check; a refusal shows up as a block card. frameT is the current frame time: the sent order (cross and
// "보냄" line) shows until a newer frame arrives, then the frame says where vehicles are really heading.
// Pointing (Part1-32, decisions 0048, 0049): with a vehicle selected, a target click opens a role menu (pick);
// pressing a role sends it approved at once; a map click while the menu is open only closes the menu.
export function useDirectControl(frameT: number): DirectProps & { hint: string | null } {
  const [selected, setSelected] = useState<string | null>(null);
  const [pending, setPending] = useState<PendingAim | null>(null);
  const [pick, setPick] = useState<Pick | null>(null);
  const [status, setStatus] = useState<{ text: string; sentAt: number | null } | null>(null);

  useEffect(() => {
    if (!selected) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      setSelected(null);
      setPick(null);
    };
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  }, [selected]);

  const onVehicleClick = (id: string) => {
    setSelected((s) => (s === id ? null : id));
    setPick(null);
    setStatus(null);
  };
  const onMapClick = async (p: GeoPoint) => {
    if (pick) return setPick(null);
    if (!selected) return;
    const v = selected;
    const sentAt = frameT;
    setSelected(null);
    setPending({ ...p, label: v, sentAt });
    setStatus({ text: `${v} → ${at(p)} 보내는 중`, sentAt });
    const r = await postDirect(v, p);
    if (!r.ok) setPending(null);
    // A failed send stays on screen (sentAt null); a sent one goes once the next frame shows the result.
    setStatus(r.ok ? { text: `보냄 ${r.id} · ${v} → ${at(p)}`, sentAt } : { text: `보내기 실패: ${r.error}`, sentAt: null });
  };
  const onTargetClick = (id: string, x: number, y: number) => {
    if (selected) setPick({ target: id, x, y });
  };
  const cancelPick = () => setPick(null);
  const onPoint = async (role: string) => {
    if (!selected || !pick) return;
    const v = selected;
    const t = pick.target;
    const sentAt = frameT;
    setSelected(null);
    setPick(null);
    setStatus({ text: `${v} → ${t} 지목 보내는 중`, sentAt });
    const r = await postPoint(v, role, t);
    setStatus(r.ok ? { text: `지목 ${r.id} · ${v} → ${t}`, sentAt } : { text: `보내기 실패: ${r.error}`, sentAt: null });
  };

  const shown = status && (status.sentAt === null || frameT <= status.sentAt) ? status.text : null;
  const hint = !selected ? shown
    : pick ? `${selected} → ${pick.target} · 붙일 Role을 고르세요 · Esc 취소`
    : `${selected} 선택 · 표적을 누르면 붙일 Role · 지도를 누르면 그 지점으로 이동 명령 · Esc 취소`;
  return { selected, pending, pick, onVehicleClick, onMapClick, onTargetClick, onPoint, cancelPick, hint };
}
