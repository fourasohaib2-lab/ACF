import { Eye } from "lucide-react";
import { fr } from "../i18n/fr";
import { ageLabel, utcLabel } from "../lib/format";

/** Every observation overlay states its own time: it is never presented as synchronous with the forecast step. */
export function ObservedBadges({ items, now }: { items: { label: string; time: string }[]; now: Date }) {
  if (!items.length) return null;
  return (
    <div className="observed-badges" aria-live="polite">
      {items.map((i) => (
        <span key={i.label} className="observed-badge">
          <Eye size={12} aria-hidden="true" /> {i.label} — {`Observé ${utcLabel(i.time)} · ${ageLabel(i.time, now)} · ${fr.observationAttribution}`}
        </span>
      ))}
    </div>
  );
}
