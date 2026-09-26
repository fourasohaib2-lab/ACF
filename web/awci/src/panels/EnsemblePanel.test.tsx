import { render, screen, within } from "@testing-library/react";
import type { EnsPoint } from "../api/types";
import point from "../test-data/ens_point_fixture.json";
import { EnsemblePanel } from "./EnsemblePanel";

const p = point as unknown as EnsPoint;

test("the ensemble panel shows real probabilities at the point, the member count and the AWCI spread", () => {
  render(<EnsemblePanel point={p} step={6} deterministicAwci={42} />);
  const panel = screen.getByRole("region", { name: "Ensemble ECMWF" });
  const at6 = p.points.find((x) => x.step === 6)!;
  expect(panel).toHaveTextContent(`${at6.members} membres`);
  const row = within(panel).getByRole("row", { name: /Convection/ });
  const expected = at6.probabilities!.p_convection;
  expect(row).toHaveTextContent(expected === null ? "—" : `${Math.round(expected * 100)} %`);
  expect(panel).toHaveTextContent(/Déterministe 42/);
});

test("a step without ENS says why instead of borrowing the neighbour", () => {
  render(<EnsemblePanel point={p} step={3} deterministicAwci={null} />);
  expect(screen.getByText(/pas calculée par l'ensemble/)).toBeInTheDocument();
});

test("without ENS for the run the panel says so plainly", () => {
  render(<EnsemblePanel point={undefined} step={3} deterministicAwci={null} unavailable />);
  expect(screen.getByText(/acf-awci-ens/)).toBeInTheDocument();
});
