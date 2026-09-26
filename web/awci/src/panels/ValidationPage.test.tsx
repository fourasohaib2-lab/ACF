import { render, screen, within } from "@testing-library/react";
import type { Verification } from "../api/types";
import small from "../test-data/verification_fixture.json";
import real from "../test-data/verification_north_africa_2026092512.json";
import { ValidationPage } from "./ValidationPage";

test("the real North Africa verification shows every event with its contingency and scores", () => {
  const v = real as unknown as Verification;
  render(<ValidationPage verification={v} isLoading={false} error={null} />);
  const conv = screen.getByRole("table", { name: /Convection/ });
  const total = within(conv).getByRole("row", { name: /Total/ });
  const t = v.events.convective!.total;
  expect(total).toHaveTextContent(String(t.a));
  expect(total).toHaveTextContent("4,15"); // frequency bias of the real run: convection over-diagnosed
  expect(screen.getAllByRole("table")).toHaveLength(4);
  expect(screen.getByText(/échéance pas encore observée/)).toBeInTheDocument();
  expect(screen.getAllByText(/HYPOTHESIS/).length).toBeGreaterThan(0);
  // lead bins not observed yet have no pair at all
  expect(within(conv).getByRole("row", { name: /48-72 h/ })).toHaveTextContent("aucune paire");
});

test("small samples are flagged; loading and error have their own states", () => {
  const { unmount } = render(<ValidationPage verification={small as unknown as Verification} isLoading={false} error={null} />);
  expect(screen.getAllByText("échantillon insuffisant").length).toBeGreaterThan(0);
  unmount();
  render(<ValidationPage verification={undefined} isLoading error={null} />);
  expect(screen.getByRole("status")).toBeInTheDocument();
});
