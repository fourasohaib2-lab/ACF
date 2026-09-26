import { greatCircleLine, parseRoute, routeFromIcao, serializeRoute } from "./route";

describe("route", () => {
  it("parses and serialises the URL form, refusing anything malformed", () => {
    expect(parseRoute("36.691,3.215;36.851,10.227")).toEqual([[36.691, 3.215], [36.851, 10.227]]);
    expect(serializeRoute([[36.6914, 3.2154], [36.85, 10.2]])).toBe("36.691,3.215;36.85,10.2");
    for (const bad of ["36,3;x,4", "36,3;95,4", "36;3", "36,3,1", ",3", Array(21).fill("36,3").join(";")]) {
      expect(parseRoute(bad)).toBeUndefined();
    }
  });

  it("draws the great circle, not the Mercator straight line", () => {
    const line = greatCircleLine([[40, -70], [50, 0]], 10); // New York area → Europe: the great circle bulges north
    expect(line).toHaveLength(11);
    expect(line[0]![1]).toBeCloseTo(40, 9);
    expect(line[10]![0]).toBeCloseTo(0, 9);
    const mid = line[5]!;
    expect(mid[1]).toBeGreaterThan(45 + 3); // north of the rhumb/straight midpoint
  });

  it("resolves ICAO codes and reports the unknown ones", () => {
    const airports = [{ icao: "DAAG", lat: 36.691, lon: 3.215 }, { icao: "DTTA", lat: 36.851, lon: 10.227 }];
    expect(routeFromIcao("daag dtta xxxx", airports)).toEqual({ points: [[36.691, 3.215], [36.851, 10.227]], unknown: ["XXXX"] });
  });
});
