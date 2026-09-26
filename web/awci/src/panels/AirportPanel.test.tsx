import { render, screen, within } from "@testing-library/react";
import type { AirportDetail } from "../api/types";
import detail from "../test-data/airport_daag.json";
import { AirportPanel } from "./AirportPanel";

const d = detail as unknown as AirportDetail;

test("the aerodrome panel shows the real METAR at the valid time next to the model, and the TAF", () => {
  render(<AirportPanel detail={d} currentStep={3} now={new Date("2026-09-26T09:00:00Z")} loading={false} />);
  const panel = screen.getByRole("region", { name: "Aérodrome" });
  expect(within(panel).getByRole("heading", { name: /DAAG — Algiers Intl/ })).toBeInTheDocument();
  const pair = d.pairs.find((p) => p.step === 3)!;
  expect(within(panel).getByText(pair.observation!.raw)).toBeInTheDocument();
  expect(within(panel).getByText(d.taf!.raw)).toBeInTheDocument();
  const rows = within(panel).getAllByRole("row");
  expect(rows.some((r) => r.getAttribute("aria-current") === "true" && /\+3 h/.test(r.textContent ?? ""))).toBe(true);
  expect(within(panel).getByText(/Aviation Weather Center/)).toBeInTheDocument();
});

test("a valid time in the future says it is not observed yet, never 'no report'", () => {
  const future = { ...d, pairs: [], model: d.model.map((m) => ({ ...m, valid_time: "2030-01-01T00:00:00Z" })) };
  render(<AirportPanel detail={future} currentStep={3} now={new Date("2026-09-26T09:00:00Z")} loading={false} />);
  expect(screen.getByText(/pas encore observée/)).toBeInTheDocument();
});

test("a large station/model elevation gap is flagged", () => {
  render(<AirportPanel detail={{ ...d, dz_m: 850 }} currentStep={0} now={new Date("2026-09-26T09:00:00Z")} loading={false} />);
  expect(screen.getByText(/n'est pas comparable/)).toBeInTheDocument();
});

test("a TAF that does not cover the valid time on screen is said so; genus names are in French", () => {
  render(<AirportPanel detail={d} currentStep={3} now={new Date("2026-09-26T09:00:00Z")} loading={false} />);
  expect(screen.getByText(/ne couvre pas la validité affichée/)).toBeInTheDocument();
  expect(screen.queryByText("clear")).not.toBeInTheDocument();
});
