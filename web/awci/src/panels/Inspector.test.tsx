import { render, screen } from "@testing-library/react";
import { Inspector } from "./Inspector";

test("inspector explains the composite and flags missing inputs", () => {
  render(<Inspector point={{ lat: 36.75, lon: 3, level_hpa: 300, flight_level: 301, awci: 42.1, awci_level: "Moderate",
    modules: { dynamic: 0.5, thermodynamic: 0.4, convective: null, microphysical: 0.1, topographic: 0.2 },
    missing_inputs: ["convective", "temporal", "confidence"], present_weight: 0.7,
    decomposition: { dynamic: 12.5, thermodynamic: 14.3, microphysical: 2.1, topographic: 2.9 },
    level_layers: { t: 230.1, gh: 9400 }, surface_layers: { mucape: 0 }, scientific_status: { awci: "HYPOTHESIS" },
    provenance: { run: "2026092512", step: 24, valid_time: "2026-09-26T12:00:00+00:00", attribution: "© ECMWF, CC-BY-4.0" } } as never}
    registry={undefined} />);
  expect(screen.getByText(/calculé sur 70 % des poids/i)).toBeInTheDocument();
  expect(screen.getByText(/convective/i)).toBeInTheDocument();
  expect(screen.getByText(/HYPOTHESIS/)).toBeInTheDocument();
  expect(screen.getByText(/© ECMWF/)).toBeInTheDocument();
});

test("a null ceiling reads 'no ceiling', not a missing value", () => {
  render(<Inspector point={{ lat: 36.75, lon: 3, level_hpa: 300, flight_level: 301, awci: 10, awci_level: "Low",
    modules: {}, missing_inputs: [], present_weight: 1, decomposition: {}, level_layers: { gh: 9400 },
    surface_layers: { ceiling_m: null }, scientific_status: {},
    provenance: { run: "2026092512", step: 24, valid_time: null, attribution: "© ECMWF" } } as never} registry={undefined} />);
  expect(screen.getByRole("row", { name: /Plafond/ })).toHaveTextContent(/pas de plafond/i);
});
