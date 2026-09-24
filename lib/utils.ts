import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Turbo-like colormap (blue -> cyan -> green -> yellow -> red) for a
 * normalized value t in [0, 1]. Returns an "r,g,b" string.
 */
export function turbo(t: number): [number, number, number] {
  const x = Math.max(0, Math.min(1, t))
  const r =
    34.61 +
    x * (1172.33 + x * (-10793.56 + x * (33300.12 + x * (-38394.49 + x * 14825.05))))
  const g =
    23.31 +
    x * (557.33 + x * (1225.33 + x * (-3574.96 + x * (3480.68 + x * -1102.5))))
  const b =
    27.2 +
    x * (3211.1 + x * (-15327.97 + x * (27814 + x * (-22569.18 + x * 6838.66))))
  return [
    Math.max(0, Math.min(255, Math.round(r))),
    Math.max(0, Math.min(255, Math.round(g))),
    Math.max(0, Math.min(255, Math.round(b))),
  ]
}

export function turboCss(t: number, alpha = 1) {
  const [r, g, b] = turbo(t)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}
