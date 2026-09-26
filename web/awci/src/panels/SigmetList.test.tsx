import { render, screen } from "@testing-library/react";
import type { SigmetCollection } from "../api/types";
import sigmets from "../test-data/sigmets_real.json";
import { SigmetList } from "./SigmetList";

test("real SIGMETs are listed with hazard text, flight levels, validity and raw text; ash is marked", () => {
  const c = sigmets as unknown as SigmetCollection;
  const { container } = render(<SigmetList sigmets={c} isError={false} />);
  expect(screen.getAllByText("Cendres volcaniques (VA)")).toHaveLength(2);
  expect(screen.getByText("Orages (TS)")).toBeInTheDocument();
  expect(container.querySelectorAll(".sigmet-item.is-ash")).toHaveLength(2);
  expect(screen.getAllByText("Texte du SIGMET")).toHaveLength(3);
  expect(screen.getAllByText(/FL\d{3}|SFC/).length).toBeGreaterThan(0);
});

test("no SIGMET at this time is said so", () => {
  render(<SigmetList sigmets={{ type: "FeatureCollection", features: [], time: "2026-09-25T03:00:00Z", ingested_at: null, attribution: "AWC" }} isError={false} />);
  expect(screen.getByText(/Aucun SIGMET valide/)).toBeInTheDocument();
});
