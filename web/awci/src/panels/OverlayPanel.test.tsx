import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ObservedBadges } from "./ObservedBadge";
import { OverlayPanel } from "./OverlayPanel";

const layers = [
  { layer: "mtg_fd:ir105_hrfi", label: "MTG FCI IR 10,5 µm", group: "satellite", attribution: "© EUMETSAT" },
  { layer: "msg_fes:rgb_ash", label: "MSG Ash RGB (cendres)", group: "ash", attribution: "© EUMETSAT" },
];

test("a failing overlay is shown unavailable, unchecked, with a retry", async () => {
  const onRetry = vi.fn();
  render(<OverlayPanel layers={layers} active={["msg_fes:rgb_ash"]} states={{ "msg_fes:rgb_ash": { error: true } }}
                       onToggle={vi.fn()} onRetry={onRetry} />);
  expect(screen.getByText(/EUMETView indisponible/)).toBeInTheDocument();
  expect(screen.getByRole("checkbox", { name: /cendres/i })).not.toBeChecked();
  await userEvent.click(screen.getByRole("button", { name: /réessayer/i }));
  expect(onRetry).toHaveBeenCalledWith("msg_fes:rgb_ash");
});

test("observed badge states the observation time, age and attribution", () => {
  render(<ObservedBadges items={[{ label: "MTG FCI IR 10,5 µm", time: "2026-09-25T21:00:00Z" }]} now={new Date("2026-09-25T21:12:00Z")} />);
  expect(screen.getByText(/Observé 25\/09 21:00 UTC · il y a 12 min · © EUMETSAT/)).toBeInTheDocument();
});

test("re-checking a failed overlay retries it in one click instead of removing it", async () => {
  const onRetry = vi.fn();
  const onToggle = vi.fn();
  render(<OverlayPanel layers={layers} active={["msg_fes:rgb_ash"]} states={{ "msg_fes:rgb_ash": { error: true } }}
                       onToggle={onToggle} onRetry={onRetry} />);
  await userEvent.click(screen.getByRole("checkbox", { name: /cendres/i }));
  expect(onRetry).toHaveBeenCalledWith("msg_fes:rgb_ash");
  expect(onToggle).not.toHaveBeenCalled();
});
