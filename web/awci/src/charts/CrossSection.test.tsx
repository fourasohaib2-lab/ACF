import { render, screen, within } from "@testing-library/react";
import type { RouteSection } from "../api/types";
import { layerDef } from "../map/layers";
import real from "../test-data/route_section_gmmn_heca.json";
import { CrossSection, pressureBands, valueText } from "./CrossSection";

const section = real as unknown as RouteSection;
const BOUNDS = [20, 35, 50, 65, 85];
const LABELS = ["Very Low", "Low", "Moderate", "High", "Very High", "Extreme"];

describe("CrossSection (real /route/section, GMMN → DAAG → DTTA → HECA, IFS 2026-09-25 12Z +12 h)", () => {
  it("bands levels between the geometric means of their neighbours", () => {
    const b = pressureBands([1000, 850, 700]);
    expect(b[1]!.top).toBeCloseTo(Math.sqrt(850 * 700), 9);
    expect(b[1]!.bottom).toBeCloseTo(Math.sqrt(1000 * 850), 9);
    expect(b[0]!.bottom / 1000).toBeCloseTo(1000 / b[0]!.top, 9); // mirrored in log p at the ends
  });

  it("formats values in the layer's own terms", () => {
    expect(valueText(layerDef("awci"), 52.4, LABELS, BOUNDS)).toBe("52 (High)");
    expect(valueText(layerDef("icing_potential"), 1, LABELS, BOUNDS)).toBe("Oui");
    expect(valueText(layerDef("wind_speed"), null, LABELS, BOUNDS)).toBe("sans donnée");
  });

  it("draws the section with the relief, the waypoints and an accessible summary per level", () => {
    const { container } = render(<CrossSection section={section} def={layerDef("awci")} awciBounds={BOUNDS} classLabels={LABELS}
                                               currentLevel={700} waypointLabels={["GMMN", "DAAG", "DTTA", "HECA"]} />);
    const img = screen.getByRole("img", { name: /^Coupe verticale de AWCI le long de la route, 3\s770 km/ });
    expect(img).toBeInTheDocument();
    expect(container.querySelector(".xs-terrain")).not.toBeNull(); // the Atlas and the Tell rise above 1000 hPa
    for (const icao of ["GMMN", "DAAG", "DTTA", "HECA"]) expect(within(img).getByText(icao)).toBeInTheDocument();
    const table = screen.getByRole("table", { name: /maximum par niveau le long de la route/ });
    expect(within(table).getAllByRole("row")).toHaveLength(section.levels_hpa.length + 1);
    const i700 = section.levels_hpa.indexOf(700);
    const max = Math.max(...section.values[i700]!.filter((v): v is number => v !== null));
    expect(within(table).getByRole("row", { name: /FL099 \(700 hPa\)/ })).toHaveTextContent(String(Math.round(max)));
  });
});
