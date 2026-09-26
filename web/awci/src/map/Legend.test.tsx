import { render, screen } from "@testing-library/react";
import { Legend } from "./Legend";
import { layerDef } from "./layers";

test("ceiling legend says 'no ceiling' for empty cells, not 'no data', and the ramp end is open", () => {
  render(<Legend def={layerDef("ceiling_m")} classLabels={[]} awciBounds={[]} />);
  expect(screen.getByText(/Pas de plafond/)).toBeInTheDocument();
  expect(screen.queryByText(/Sans donnée/)).not.toBeInTheDocument();
  expect(screen.getByText(/≥ 10.000/)).toBeInTheDocument();
});

test("other layers keep the no-data hatch", () => {
  render(<Legend def={layerDef("awci")} classLabels={[]} awciBounds={[20, 40]} />);
  expect(screen.getByText(/Sans donnée/)).toBeInTheDocument();
});
