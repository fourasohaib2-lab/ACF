import { AlertOctagon, AlertTriangle, CheckCircle2, XOctagon } from "lucide-react";
import type { Badge as BadgeValue } from "../api/types";
import { fr } from "../i18n/fr";

const ICONS = { ok: CheckCircle2, attention: AlertTriangle, serious: AlertOctagon, critical: XOctagon } as const;

/** Status badge: icon + text, colour never carries the meaning alone. */
export function StatusBadge({ value }: { value: BadgeValue | undefined }) {
  if (!value) return null;
  const Icon = ICONS[value];
  return <span className={`status-badge status-${value}`}><Icon size={13} aria-hidden="true" />{fr.badge[value]}</span>;
}
