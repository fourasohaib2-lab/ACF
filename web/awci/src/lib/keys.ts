/**
 * True when the focused element needs the arrow keys and Space itself: form controls (a radio group is
 * only operable with the arrows, WCAG 2.1.1) and the map (arrows pan it). Global shortcuts yield to them.
 */
export function ownsKeys(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  return ["INPUT", "SELECT", "TEXTAREA"].includes(target.tagName) || target.isContentEditable
    || target.closest('[role="application"]') !== null;
}
