import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TimeBar } from "./TimeBar";

const meta = { steps: [0, 3, 6], missing_steps: [3], valid_times: ["2026-09-25T12:00:00+00:00",
  "2026-09-25T15:00:00+00:00", "2026-09-25T18:00:00+00:00"] } as never;

test("missing steps are disabled and announced", async () => {
  const onStep = vi.fn();
  render(<TimeBar meta={meta} step={0} onStep={onStep} />);
  const missing = screen.getByRole("button", { name: /\+3 h.*manquante/i });
  expect(missing).toBeDisabled();
  await userEvent.click(screen.getByRole("button", { name: /\+6 h/ }));
  expect(onStep).toHaveBeenCalledWith(6);
});
