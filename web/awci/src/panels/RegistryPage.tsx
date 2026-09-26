import type { Registry } from "../api/types";

/** What every served quantity is: unit, equation, source and scientific status, from /registry. */
export function RegistryPage({ registry }: { registry: Registry | undefined }) {
  if (!registry) return null;
  const layers = Object.values(registry.layers).sort((a, b) => a.name.localeCompare(b.name));
  return (
    <section className="panel registry-page" aria-label="API et registre">
      <h2>API et registre scientifique</h2>
      <p className="panel-note">
        API en lecture seule sous <code>/api/v1/awci</code>. Documentation interactive : <a href="/docs">OpenAPI (Swagger)</a>.
        Données : {registry.attribution} ; observations © EUMETSAT.
      </p>
      <h3 className="subhead">Profil AWCI {registry.profile.name} {registry.profile.version}</h3>
      <p className="panel-note">
        Classes : {registry.classes.map((c) => `${c.label}${c.upper_bound === null ? "" : ` < ${c.upper_bound}`}`).join(" · ")} ·
        AWCI calculé seulement si les modules présents pèsent au moins {Math.round(registry.profile.min_present_weight * 100)} %.
      </p>
      <div className="table-scroll">
        <table className="data-table">
          <caption className="visually-hidden">Couches servies</caption>
          <thead><tr><th scope="col">Couche</th><th scope="col">Libellé</th><th scope="col">Unité</th><th scope="col">Équation</th>
            <th scope="col">Source</th><th scope="col">Statut</th></tr></thead>
          <tbody>
            {layers.map((l) => (
              <tr key={l.name}><td className="mono">{l.name}</td><td>{l.label}</td><td>{l.unit}</td><td>{l.equation}</td>
                <td>{l.source}</td><td className="status-cell">{l.status}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="panel-note">HYPOTHESIS : formule publiée ou choix ACF non encore validé contre des observations ; CONFIRMED : champ du modèle ou définition exacte.</p>
    </section>
  );
}
