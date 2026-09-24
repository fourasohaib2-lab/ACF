/**
 * Minimal ambient types for the `georaster`/`georaster-layer-for-leaflet`
 * packages (no official @types package exists on npm as of this
 * writing) - only the real shapes this codebase actually uses.
 */

declare module "georaster" {
  export interface GeoRasterMetadata {
    noDataValue: number
    projection: number
    xmin: number
    ymax: number
    pixelWidth: number
    pixelHeight: number
  }

  export interface GeoRaster {
    values: number[][][]
    width: number
    height: number
    xmin: number
    xmax: number
    ymin: number
    ymax: number
    pixelWidth: number
    pixelHeight: number
    projection: number
    noDataValue: number
    numberOfRasters: number
  }

  export default function parseGeoraster(
    values: number[][][],
    metadata: GeoRasterMetadata,
  ): Promise<GeoRaster>
}

declare module "georaster-layer-for-leaflet" {
  import type { GridLayer, GridLayerOptions, LatLngBounds } from "leaflet"
  import type { GeoRaster } from "georaster"

  export interface GeoRasterLayerOptions extends GridLayerOptions {
    georaster: GeoRaster
    opacity?: number
    resolution?: number
    pixelValuesToColorFn?: (values: number[]) => string | null
    resampleMethod?: "nearest" | "bilinear"
  }

  export default class GeoRasterLayer extends GridLayer {
    constructor(options: GeoRasterLayerOptions)
    getBounds(): LatLngBounds
  }
}
