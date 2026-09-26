import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { App } from "./App";

function routeFetch(routes: Record<string, unknown>) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const path = new URL(String(input), "http://x").pathname.replace("/api/v1/awci", "");
    if (!(path in routes)) return new Response(JSON.stringify({ detail: "not found" }), { status: 404 });
    return new Response(JSON.stringify(routes[path]), { status: 200, headers: { "Content-Type": "application/json" } });
  });
}

test("an empty domain shows the explicit no-run state with the ingestion command", async () => {
  vi.stubGlobal("fetch", routeFetch({
    "/domains": [{ name: "north_africa", label: "Afrique du Nord", south: 15, north: 45, west: -20, east: 40,
      default: true, resolution_deg: 0.25 }],
    "/runs": [], "/registry": { layers: {}, classes: [], profile: {}, cloud_profile: {}, codes: {}, summary_thresholds: {} },
  }));
  render(<QueryClientProvider client={new QueryClient()}><App /></QueryClientProvider>);
  expect(await screen.findByText(/aucun run ingéré/i)).toBeInTheDocument();
  expect(screen.getByText(/acf-awci-ingest --run latest --domain north_africa/)).toBeInTheDocument();
  vi.unstubAllGlobals();
});
