import type { Operation } from "../../contracts.gen";

// One vehicle's start role in the operation (decision 0053); null = no start role (it waits at home).
export function setStartRole(op: Operation, vehicleId: string, roleId: string | null): Operation {
  const assign = Object.fromEntries(Object.entries(op.assign ?? {}).filter(([v]) => v !== vehicleId));
  return { ...op, assign: roleId ? { ...assign, [vehicleId]: roleId } : assign };
}
