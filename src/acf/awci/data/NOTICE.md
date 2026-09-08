# Real terrain elevation data — provenance and license

**File**: `earth_relief_01d.nc` (113,646 bytes)

**What it is**: a real, global land+ocean elevation/bathymetry grid at
1 arc-degree resolution (180 x 360 points, `z` in metres, -7057 to
5326.5 m in this exact file). This is the coarsest resolution of the
"IGPP Earth Relief" dataset served by the Generic Mapping Tools (GMT)
project's official remote-data server, itself a reduction (Gaussian
Cartesian filtering, ~315 km full width) of **SRTM15+ V2.7**.

**Source URL** (fetched 2026-09-04):
`https://oceania.generic-mapping-tools.org/server/earth/earth_relief/earth_relief_01d_p.grd`

**Reference documentation**:
`https://www.generic-mapping-tools.org/remote-datasets/earth-relief.html`

**Citation** (SRTM15+ V2.7):
Tozer, B., Sandwell, D. T., Smith, W. H. F., Olson, C., Beale, J. R.,
& Wessel, P. (2019). "Global Bathymetry and Topography at 15 Arc Sec:
SRTM15+". *Earth and Space Science*, 6, 1847-1864.
https://doi.org/10.1029/2019EA000658

**License/terms**: distributed by GMT (a free, open-source project,
LGPL-licensed) as a public, unauthenticated download specifically for
scientific/research use; the underlying SRTM elevation data (NASA) is
US-government public domain. Kept here as the exact, unmodified file
served by GMT — no values are re-derived or altered.

**Why this file, this resolution**: this is the *coarsest* resolution
GMT offers (`01d`) — 1 arc-degree is already finer than every real
solver grid this Workstation runs (`CoupledEarthSolver`'s own native
grids), so no scientific accuracy is lost by not fetching a larger,
higher-resolution file; the ~111 KB size was chosen deliberately to
keep this a small, versionable, offline-usable data asset (no runtime
network dependency).

**Placement**: kept inside the `acf.awci` package tree (not `/data/`,
which this repo reserves for runtime-generated state — SQLite stores,
saved case studies — via `.gitignore`) since this is a real, static,
versioned source asset that ships with the package.

**Used by**: `acf.awci.terrain_elevation.load_real_terrain_elevation()`
— see that module's own docstring for how this file is read and
interpolated onto a real solver grid.
