import { Bookmark, Trash2 } from "lucide-react";
import { useState } from "react";
import { deleteView, loadViews, saveView, type SavedView } from "../state/savedViews";

/** "Save scenario" of the mockup: named views (URL state) stored in this browser only. */
export function SavedViews({ onApply }: { onApply: (search: string) => void }) {
  const [views, setViews] = useState<SavedView[]>(() => loadViews());
  const [name, setName] = useState("");
  const save = () => {
    const n = name.trim();
    if (!n) return;
    saveView(n, window.location.search);
    setViews(loadViews());
    setName("");
  };
  return (
    <section className="saved-views" aria-label="Vues enregistrées">
      <p className="layer-group-title"><Bookmark size={12} aria-hidden="true" /> Vues enregistrées (ce navigateur)</p>
      <div className="saved-form">
        <input aria-label="Nom de la vue" value={name} onChange={(e) => setName(e.target.value)} placeholder="Nom de la vue"
               onKeyDown={(e) => { if (e.key === "Enter") save(); }} />
        <button type="button" className="text-button" onClick={save}>Enregistrer</button>
      </div>
      <ul>
        {views.map((v) => (
          <li key={v.name}>
            <button type="button" className="link-button" onClick={() => onApply(v.search)}>{v.name}</button>
            <button type="button" className="icon-button" aria-label={`Supprimer la vue ${v.name}`}
                    onClick={() => { deleteView(v.name); setViews(loadViews()); }}><Trash2 size={12} aria-hidden="true" /></button>
          </li>
        ))}
      </ul>
    </section>
  );
}
