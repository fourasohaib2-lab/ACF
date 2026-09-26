import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

type Theme = "dark" | "light";
const KEY = "awci.theme";
const read = (): Theme => { try { return window.localStorage.getItem(KEY) === "light" ? "light" : "dark"; } catch { return "dark"; } };

/** Dark by default (forecast rooms); light for bright offices. The map keeps its dark validated surface. */
export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(read);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { window.localStorage.setItem(KEY, theme); } catch { /* per-browser preference only */ }
  }, [theme]);
  const next = theme === "dark" ? "light" : "dark";
  return (
    <button type="button" className="icon-button" onClick={() => setTheme(next)}
            aria-label={next === "light" ? "Passer au thème clair" : "Passer au thème sombre"}>
      {next === "light" ? <Sun size={16} aria-hidden="true" /> : <Moon size={16} aria-hidden="true" />}
    </button>
  );
}
