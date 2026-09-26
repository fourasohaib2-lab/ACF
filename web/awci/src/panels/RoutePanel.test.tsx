import { fireEvent, render, screen } from "@testing-library/react";
import { layerDef } from "../map/layers";
import { RoutePanel, waypointLabels } from "./RoutePanel";

const AIRPORTS = [{ icao: "DAAG", lat: 36.691, lon: 3.215 }, { icao: "DTTA", lat: 36.851, lon: 10.227 }];
const idle = { data: undefined, isLoading: false, error: null };

describe("RoutePanel", () => {
  it("names waypoints after the aerodrome at their position", () => {
    expect(waypointLabels([[36.691, 3.215], [35, 5], [36.851, 10.227]], AIRPORTS)).toEqual(["DAAG", "P2", "DTTA"]);
  });

  it("builds a route from ICAO codes and refuses unknown ones", () => {
    const onRoute = vi.fn();
    render(<RoutePanel route={undefined} editing={false} onEditing={() => undefined} onRoute={onRoute} airports={AIRPORTS}
                       section={idle} meteogram={idle} def={layerDef("awci")} awciBounds={[]} classLabels={[]} step={0} level={700}
                       onSelect={() => undefined} />);
    fireEvent.change(screen.getByLabelText("Aérodromes OACI"), { target: { value: "DAAG ZZZZ" } });
    fireEvent.click(screen.getByRole("button", { name: "Tracer" }));
    expect(screen.getByRole("alert")).toHaveTextContent("Aérodrome inconnu dans ce domaine : ZZZZ.");
    fireEvent.change(screen.getByLabelText("Aérodromes OACI"), { target: { value: "daag dtta" } });
    fireEvent.click(screen.getByRole("button", { name: "Tracer" }));
    expect(onRoute).toHaveBeenCalledWith([[36.691, 3.215], [36.851, 10.227]]);
  });
});
