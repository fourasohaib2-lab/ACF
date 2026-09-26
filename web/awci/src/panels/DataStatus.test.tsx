import { render, screen } from "@testing-library/react";
import { DataStatus } from "./DataStatus";

test("partial and stale runs are flagged with text, not colour only", () => {
  render(<DataStatus run={{ run: "2026092500", run_time: "2026-09-25T00:00:00+00:00", status: "partial",
    steps: [0, 3], missing_steps: [3], ingested_at: "2026-09-25T08:10:00+00:00" } as never}
    cloudStatus="degraded" now={new Date("2026-09-25T20:00:00Z")} />);
  expect(screen.getByText(/partiel/i)).toBeInTheDocument();
  expect(screen.getByText(/run ancien/i)).toBeInTheDocument();
  expect(screen.getByText(/nuages : cohérence dégradée/i)).toBeInTheDocument();
});
