import { render, screen } from "@testing-library/react";
import { LineChart } from "./LineChart";

test("line chart exposes its data as a table", () => {
  render(<LineChart yLabel="AWCI" series={[{ id: "p", label: "Point", color: "#3987e5",
    points: [{ x: 0, y: 10 }, { x: 3600000, y: null }] }]} format={(v) => String(v)} />);
  expect(screen.getByRole("table")).toBeInTheDocument();
  expect(screen.getByText("—")).toBeInTheDocument(); // missing value stays visible as missing
});
