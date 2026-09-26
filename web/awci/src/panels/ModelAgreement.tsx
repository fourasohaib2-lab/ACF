import { fr } from "../i18n/fr";

/** Model agreement needs several models or an ensemble: stated plainly instead of a fake score. */
export const ModelAgreement = () => (
  <section className="panel" aria-label="Accord des modèles">
    <h2>Accord des modèles</h2>
    <p className="panel-note">{fr.singleModel}</p>
  </section>
);
