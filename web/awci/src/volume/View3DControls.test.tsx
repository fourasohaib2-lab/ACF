import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { View3DControls } from "./View3DControls";

const base = { vol: ["clouds"] as ("clouds" | "icing" | "cat" | "awci")[], exag: 40, cth: 0.625, loading: false,
  onChange: vi.fn(), onCamera: vi.fn(), onExit: vi.fn() };

test("the exaggeration is always stated, layers respect the pairing rules, the threshold reads in oktas", async () => {
  const onChange = vi.fn();
  render(<View3DControls {...base} vol={["clouds", "icing"]} onChange={onChange} />);
  expect(screen.getByText(/Relief et altitudes exagérés ×40/)).toBeInTheDocument();
  expect(screen.getByRole("checkbox", { name: /Turbulence/ })).toBeDisabled(); // already two layers
  await userEvent.click(screen.getByRole("checkbox", { name: /Givrage/ }));
  expect(onChange).toHaveBeenCalledWith({ vol: ["clouds"] });
  expect(screen.getByRole("slider", { name: /Seuil de fraction nuageuse/ })).toHaveAttribute("aria-valuetext", "5/8 (BKN)");
  expect(screen.getByText("Cumulonimbus")).toBeInTheDocument(); // legend of the active layers
});

test("AWCI cannot be combined with CAT; camera presets and the way back to 2-D exist", async () => {
  const onCamera = vi.fn();
  const onExit = vi.fn();
  render(<View3DControls {...base} vol={["cat"]} onCamera={onCamera} onExit={onExit} />);
  expect(screen.getByRole("checkbox", { name: /AWCI/ })).toBeDisabled();
  await userEvent.click(screen.getByRole("button", { name: /Oblique sud/ }));
  expect(onCamera).toHaveBeenCalledWith("south");
  await userEvent.click(screen.getByRole("button", { name: /Revenir en 2D/ }));
  expect(onExit).toHaveBeenCalled();
});
