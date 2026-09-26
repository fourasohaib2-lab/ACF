import { AlertOctagon, Inbox } from "lucide-react";
import type { ReactNode } from "react";
import { ApiError } from "../api/client";
import { fr } from "../i18n/fr";

export const Skeleton = ({ height = 120, label = fr.loading }: { height?: number; label?: string }) => (
  <div className="skeleton" style={{ minHeight: height }} role="status" aria-live="polite"><span className="visually-hidden">{label}</span></div>
);

export function ErrorBox({ error, what }: { error: unknown; what: string }) {
  const status = error instanceof ApiError ? error.status : undefined;
  const detail = error instanceof Error ? error.message : String(error);
  return (
    <div className="error-box" role="alert">
      <AlertOctagon size={16} aria-hidden="true" />
      <div><strong>{what} : erreur{status ? ` ${status}` : ""}.</strong> <span>{detail}</span></div>
    </div>
  );
}

export const EmptyRuns = ({ domain }: { domain: string }) => (
  <div className="empty-state" role="status">
    <Inbox size={28} aria-hidden="true" />
    <p><strong>{fr.noRun}</strong></p>
    <p>{fr.noRunHint.split("--domain")[0]}</p>
    <code className="mono">acf-awci-ingest --run latest --domain {domain}</code>
  </div>
);

export const Banner = ({ children }: { children: ReactNode }) => <div className="banner" role="status">{children}</div>;
