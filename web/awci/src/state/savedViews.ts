/** Named views (the URL state) kept in this browser only; every storage access may fail (private mode, quota). */
export interface SavedView { name: string; search: string }
const KEY = "awci.savedViews";

export function loadViews(): SavedView[] {
  try {
    const raw = window.localStorage.getItem(KEY);
    const parsed: unknown = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed)
      ? parsed.filter((v): v is SavedView => typeof v?.name === "string" && typeof v?.search === "string") : [];
  } catch {
    return [];
  }
}

function store(views: SavedView[]): void {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(views));
  } catch {
    /* storage unavailable: the view stays shareable through its URL */
  }
}

export function saveView(name: string, search: string): void {
  store([...loadViews().filter((v) => v.name !== name), { name, search }]);
}

export function deleteView(name: string): void {
  store(loadViews().filter((v) => v.name !== name));
}
