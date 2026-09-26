import { render, screen } from "@testing-library/react";
import { layerDef } from "./layers";
import { Legend } from "./Legend";

const BOUNDS = [20, 35, 50, 65, 85];
const LABELS = ["Very Low", "Low", "Moderate", "High", "Very High", "Extreme"];

describe("Legend with the ONM vigilance colours", () => {
  it("gives each AWCI class its vigilance level and says the colours are not an official vigilance", () => {
    render(<Legend def={layerDef("awci")} classLabels={LABELS} awciBounds={BOUNDS} />);
    expect(screen.getByText("Moderate").closest("li")).toHaveTextContent("jaune");
    expect(screen.getByText("High").closest("li")).toHaveTextContent("orange");
    expect(screen.getByText("Extreme").closest("li")).toHaveTextContent("rouge (au-delà)");
    expect(screen.getByText("Teintes vigilance ONM, non officielles")).toHaveAttribute("title", expect.stringMatching(/sans valeur de vigilance officielle/));
  });

  it("keeps a continuous quantity (wind) out of the vigilance convention", () => {
    render(<Legend def={layerDef("wind_speed")} classLabels={LABELS} awciBounds={BOUNDS} />);
    expect(screen.queryByText(/vigilance ONM/)).not.toBeInTheDocument();
  });
});

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
