import { fireEvent, render, screen } from "@testing-library/react";
import type { RouteMeteogram as Payload } from "../api/types";
import real from "../test-data/route_meteogram_gmmn_heca.json";
import { RouteMeteogram } from "./RouteMeteogram";

const m = real as unknown as Payload;
const BOUNDS = [20, 35, 50, 65, 85];
const LABELS = ["Very Low", "Low", "Moderate", "High", "Very High", "Extreme"];

describe("RouteMeteogram (real /route/meteogram, GMMN → HECA, IFS 2026-09-25 12Z)", () => {
  it("has one button per step and level, labelled with the route statistics, and selects both", () => {
    const onSelect = vi.fn();
    render(<RouteMeteogram meteogram={m} awciBounds={BOUNDS} classLabels={LABELS} currentStep={12} currentLevel={700} onSelect={onSelect} />);
    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(m.steps.length * m.levels_hpa.length);
    const li = m.levels_hpa.indexOf(700);
    const s12 = m.steps.find((s) => s.step === 12)!;
    const cell = screen.getByRole("button", { name: /^\+12 h, FL99 : AWCI max/ });
    expect(cell).toHaveAttribute("aria-pressed", "true");
    expect(cell).toHaveTextContent(String(Math.round(s12.awci_max![li]!)));
    fireEvent.click(screen.getByRole("button", { name: /^\+24 h, FL301 : AWCI max/ }));
    expect(onSelect).toHaveBeenCalledWith(24, 300);
  });
});
