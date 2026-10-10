const KST_OFFSET_MS = 9 * 3600 * 1000;

// Decision 0012: people see KST (+09:00) regardless of the machine time zone; contracts keep UTC t_ms.
export function kstTime(t_ms: number): string {
  return new Date(t_ms + KST_OFFSET_MS).toISOString().slice(11, 19);
}
