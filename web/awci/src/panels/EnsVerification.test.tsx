import { render, screen, within } from "@testing-library/react";
import type { EnsVerification as Report } from "../api/types";
import real from "../test-data/ens_verification_north_africa_2026092600.json";
import { EnsVerification, reading } from "./EnsVerification";

const report = real as unknown as Report;

describe("EnsVerification (real /ens/verification, IFS ENS 2026-09-26 00Z, North Africa)", () => {
  it("gives the Brier scores per step and in total, next to the deterministic run", () => {
    render(<EnsVerification report={report} isLoading={false} error={null} available />);
    const table = screen.getByRole("table", { name: "P(TCU/Cb réalisé)" });
    const total = within(table).getByRole("row", { name: /^Total/ });
    const conv = report.events.convective!.total;
    expect(within(total).getAllByRole("cell")[0]).toHaveTextContent(String(conv.n));
    expect(total).toHaveTextContent(conv.brier!.toFixed(3).replace(".", ","));  // French decimal comma
    expect(total).toHaveTextContent(conv.brier_deterministic!.toFixed(3).replace(".", ","));
    const steps = report.events.convective!.by_step.map((s) => `+${s.step} h`);
    for (const s of steps) expect(within(table).getByRole("row", { name: new RegExp(`^\\${s}`) })).toBeInTheDocument();
  });

  it("draws one reliability diagram per event with its data table", () => {
    render(<EnsVerification report={report} isLoading={false} error={null} available />);
    expect(screen.getAllByRole("img", { name: /^Diagramme de fiabilité/ })).toHaveLength(2);
    const bins = report.events.convective!.total.diagram.filter((b) => b.n > 0);
    expect(screen.getByRole("img", { name: /TCU\/Cb/ })).toHaveAccessibleName(new RegExp(`${bins.length} classes`));
  });

  it("warns that the deterministic reference used another cloud profile", () => {
    render(<EnsVerification report={report} isLoading={false} error={null} available />);
    expect(screen.getByRole("note")).toHaveTextContent("Profil nuageux 1.2.0 pour l'ensemble, 1.1.0 pour le déterministe");
  });

  it("reads the total scores in plain words, and says nothing definite about an insufficient sample", () => {
    const conv = report.events.convective!.total;  // 17 observed events: sufficient
    const lines = reading(conv);
    expect(lines[0]).toMatch(/^Erreur de Brier réduite de \d+ % par rapport au déterministe/);
    expect(lines.join(" ")).toContain("Meilleur que la fréquence observée");
    expect(reading(conv, false)[0]).toContain("mêle l'apport de l'ensemble et le changement de règles");
    expect(reading({ ...conv, observed_events: 3, sufficient: false })).toEqual([
      "Moins d'événements observés que le minimum requis (3) : scores indicatifs seulement."]);
  });

  it("says when the run has no ensemble, and shows loading and error states", () => {
    const { rerender } = render(<EnsVerification report={undefined} isLoading={false} error={null} available={false} />);
    expect(screen.getByText(/Pas d'ensemble calculé pour ce run/)).toBeInTheDocument();
    rerender(<EnsVerification report={undefined} isLoading error={null} available />);
    expect(screen.queryByText(/Pas d'ensemble/)).not.toBeInTheDocument();
    rerender(<EnsVerification report={undefined} isLoading={false} error={new Error("HTTP 500")} available />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});
