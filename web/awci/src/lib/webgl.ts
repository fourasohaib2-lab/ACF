/** WebGL2 is required by the 3-D view (deck.gl 9); without it the app stays in 2-D with an explicit message. */
export function hasWebGL2(): boolean {
  try {
    return !!document.createElement("canvas").getContext("webgl2");
  } catch {
    return false;
  }
}
