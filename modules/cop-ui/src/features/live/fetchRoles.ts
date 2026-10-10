import type { Role } from "../../contracts.gen";

// GET /roles for the switch panel. Any failure is an empty list, never a broken screen.
export async function fetchRoles(): Promise<Role[]> {
  try {
    const r = await fetch("/roles");
    if (!r.ok) return [];
    const data = await r.json();
    return Array.isArray(data) ? (data as Role[]) : [];
  } catch {
    return [];
  }
}
