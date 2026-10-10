import type { Operation } from "../../contracts.gen";

// GET /operation as sent; callers check the fields they need (zone, started_ms).
// Any failure (old gateway, network, non-JSON) is null, never a broken screen.
export async function fetchOperation(): Promise<Partial<Operation> | null> {
  try {
    const r = await fetch("/operation");
    if (!r.ok) return null;
    return (await r.json()) as Partial<Operation>;
  } catch {
    return null;
  }
}
