import { render, screen, within } from "@testing-library/react";
import type { SoundingVerification as Report } from "../api/types";
import gfsReal from "../test-data/sounding_verification_fixture_gfs.json";
import ifsReal from "../test-data/sounding_verification_fixture_ifs.json";
import { SoundingVerification, type ModelReport } from "./SoundingVerification";

const ifs = ifsReal as unknown as Report;
const gfs = gfsReal as unknown as Report;
const both: ModelReport[] = [
  { label: "IFS", color: "var(--series-1)", report: ifs, isLoading: false, error: null },
  { label: "GFS", color: "var(--series-2)", report: gfs, isLoading: false, error: null },
];
const comma = (v: number, d: number) => v.toFixed(d).replace(".", ",");

describe("SoundingVerification (real /soundings/verification: IFS and GFS 2026-09-25 00Z against the Algiers sounding)", () => {
  it("draws the bias and RMSE profiles of both models against pressure", () => {
    render(<SoundingVerification models={both} />);
    const t = screen.getByRole("img", { name: /^Température \(K\) selon la pression/ });
    expect(t).toHaveAccessibleName(/IFS biais, 12 niveaux ; IFS RMSE, 12 niveaux ; GFS biais, 12 niveaux ; GFS RMSE, 12 niveaux/);
    expect(screen.getByRole("img", { name: /^Humidité relative \(eau\)/ })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /^Vent \(m\/s\).*RMSE vect\./ })).toBeInTheDocument();
    const data = screen.getAllByRole("table", { name: "Température (K)" })[0]!;
    const row500 = within(data).getAllByRole("row").find((r) => r.textContent?.startsWith("500"))!;
    const lv = ifs.levels.find((l) => l.level_hpa === 500)!;
    expect(row500).toHaveTextContent(comma(lv.t.bias!, 1));
  });

  it("gives the column totals per model, shear in 10⁻³ s⁻¹", () => {
    render(<SoundingVerification models={both} />);
    const table = screen.getByRole("table", { name: "Scores sur toute la colonne" });
    const ifsRow = within(table).getByRole("row", { name: /^IFS/ });
    expect(ifsRow).toHaveTextContent(comma(ifs.total.t.rmse!, 2));
    expect(ifsRow).toHaveTextContent(comma(ifs.total.wind_vector_rmse!, 1));
    expect(ifsRow).toHaveTextContent(comma(ifs.total.vws.rmse! * 1000, 2));
    expect(within(table).getByRole("row", { name: /^GFS/ })).toHaveTextContent(comma(gfs.total.t.rmse!, 2));
  });

  it("states that the icing reference is the diagnostic on the observed profile, not observed icing", () => {
    render(<SoundingVerification models={both} />);
    const icing = screen.getByRole("table", { name: /^Givrage potentiel/ });
    const row = within(icing).getByRole("row", { name: /^IFS/ });
    expect(row).toHaveTextContent(String(ifs.total.icing.d));
    expect(row).toHaveTextContent("échantillon insuffisant");  // no icing level in this sounding
    expect(screen.getByText(/ce tableau valide donc les entrées du diagnostic, pas le givrage réel/i)).toBeInTheDocument();
    expect(screen.getByText(/IFS : 1 sondage, 1 station · GFS : 1 sondage, 1 station sur 1 station connue/)).toBeInTheDocument();
  });

  it("says when no sounding matches the run, and shows loading and error states", () => {
    const none = { ...ifs, soundings: 0, stations: 0 };
    const { rerender } = render(<SoundingVerification models={[{ ...both[0]!, report: none }]} />);
    expect(screen.getByText(/Aucun radiosondage archivé aux heures de validité de ce run \(1 station connue/)).toBeInTheDocument();
    rerender(<SoundingVerification models={[{ ...both[0]!, report: undefined, isLoading: true }]} />);
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
    rerender(<SoundingVerification models={[{ ...both[0]!, report: undefined, error: new Error("HTTP 500") }]} />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});
