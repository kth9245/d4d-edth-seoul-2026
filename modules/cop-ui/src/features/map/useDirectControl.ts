import { useEffect, useState } from "react";
import type { GeoPoint } from "../../contracts.gen";
import { postDirect } from "../cards/postDirect";
import type { Aim, DirectProps } from "./MapView";

const at = (p: GeoPoint) => `${p.lat.toFixed(4)}, ${p.lon.toFixed(4)}`;

// Direct control on the map (Part1-11): click a vehicle to select it, click the map to send it there
// (POST /direct), Esc or the same vehicle again cancels. Whether the order passes is the server's safety
// check; a refusal shows up as a block card.
export function useDirectControl(): DirectProps & { hint: string | null } {
  const [selected, setSelected] = useState<string | null>(null);
  const [aim, setAim] = useState<Aim | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!selected) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSelected(null);
    };
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  }, [selected]);

  const onVehicleClick = (id: string) => {
    setSelected((s) => (s === id ? null : id));
    setStatus(null);
  };
  const onMapClick = async (p: GeoPoint) => {
    if (!selected) return;
    const v = selected;
    setSelected(null);
    setAim({ ...p, label: v });
    setStatus(`${v} → ${at(p)} 보내는 중`);
    const r = await postDirect(v, p);
    setStatus(r.ok ? `보냄 ${r.id} · ${v} → ${at(p)}` : `보내기 실패: ${r.error}`);
  };

  const hint = selected ? `${selected} 선택 · 지도를 누르면 그 지점으로 이동 명령 · Esc 취소` : status;
  return { selected, aim, onVehicleClick, onMapClick, hint };
}
