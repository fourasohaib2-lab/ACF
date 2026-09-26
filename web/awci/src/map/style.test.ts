import { graticule, wmsTileUrl } from "./style";

test("graticule every 5 degrees inside the bounds", () => {
  const lines = graticule({ west: -20, south: 15, east: 40, north: 45 }, 5).features;
  expect(lines.length).toBe(13 + 7);
});
test("WMS tile URL uses the relay, an explicit time and the MapLibre bbox token", () => {
  expect(wmsTileUrl("mtg_fd:ir105_hrfi", "2026-09-25T18:50:00Z")).toBe(
    "/api/v1/awci/wms?layer=mtg_fd%3Air105_hrfi&time=2026-09-25T18%3A50%3A00Z&width=256&height=256&bbox={bbox-epsg-3857}");
});
