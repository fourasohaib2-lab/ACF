# AWCI Web — couleurs des échelles (convention de vigilance ONM)

Choix de l'utilisateur (2026-09-26) : appliquer la **convention de vigilance de l'ONM** aux classes AWCI et aux
catégories de danger. La convention est vert, puis jaune (niveau I), orange (niveau II) et rouge (niveau III),
comme dans les bulletins météorologiques spéciaux (BMS).

- **Pas de valeur officielle** : AWCI n'est pas un produit de vigilance de l'ONM. Les couleurs en reprennent la
  convention mais n'annoncent aucune vigilance officielle, et la légende de la carte le dit.
- **Pas de codes publiés** : aucun code couleur officiel n'est publié par l'ONM (site meteo.dz rendu
  dynamiquement ; document « Vigilance et Alerte Météorologique » du ministère de l'Intérieur inaccessible le
  2026-09-26). Les teintes ont donc été choisies **par mesure**, et une charte ONM fournie les remplacera.

## Palette AWCI (`web/awci/src/theme/palette.ts`)

| Classe | Couleur | Vigilance | Contraste sur la carte (#0b1220) | Texte posé dessus |
|---|---|---|---|---|
| Very Low | `#2e7d32` | vert | 3,65:1 | blanc 5,13:1 |
| Low | `#66bb6a` | vert | 7,92:1 | sombre 7,92:1 |
| Moderate | `#ffeb3b` | jaune (I) | 15,3:1 | sombre 15,3:1 |
| High | `#ff9100` | orange (II) | 8,29:1 | sombre 8,29:1 |
| Very High | `#e8413c` | rouge (III) | 4,68:1 | sombre 4,68:1 |
| Extreme | `#a52cba` | au-delà du rouge (pourpre) | 3,27:1 | blanc 5,72:1 |

- **Extreme en pourpre** : un rouge plus sombre tombait sous 3:1 sur la carte et se confondait avec le vert foncé
  pour les daltoniens. Le pourpre au-delà du rouge est une convention courante pour l'extrême.
- **À changer si besoin** : si l'ONM impose 4 couleurs strictes, Extreme reprend le rouge, et la classe ne se
  distingue plus que dans la légende et l'inspecteur.

## Dangers

| Couche | Couleurs |
|---|---|
| Turbulence CAT (Ellrod TI2) | nulle transparente, légère jaune, modérée orange, modérée à sévère rouge |
| Givrage potentiel | oui jaune |
| Convection | Cu vert, TCU orange, Cb (calvus, capillatus) rouge |
| Vue 3D | givrage jaune, CAT modérée orange et modérée à sévère rouge, AWCI ≥ High orange, rouge, pourpre |

**Hors de la convention**, et c'est voulu :
- les grandeurs continues (vent, cisaillement, couvertures, probabilités) gardent la rampe bleue séquentielle ;
- les genres nuageux gardent leurs couleurs catégorielles, car ce sont des types, pas des niveaux de danger ;
- les catégories FAA des aérodromes (VFR, MVFR, IFR, LIFR) suivent leur propre convention.

## Mesures (reproductibles)

```bash
.venv/bin/python tools/awci/check_palette.py "#2e7d32,#66bb6a,#ffeb3b,#ff9100,#e8413c,#a52cba" VL,L,M,H,VH,EX
```

Plus petit écart CIEDE2000 entre deux classes, en vision normale et en simulation de daltonisme (Machado et al.
2009, sévérité totale) :

| Vision | Ancienne palette | Nouvelle palette |
|---|---|---|
| normale | 12,8 | 20,7 |
| deutéranopie | 6,3 | 10,2 |
| protanopie | 7,2 | 6,3 (vert foncé / rouge, classes non adjacentes ; adjacentes ≥ 18,3) |
| tritanopie | 5,5 | 13,8 |

- **Limite** : la confusion rouge/vert est inhérente à une convention de vigilance. Pour les protanopes, seule la
  paire non adjacente Very Low / Very High reste proche. La légende nomme toujours la classe et son niveau.
- **Vérification de l'outil** : son implémentation de CIEDE2000 reproduit les paires de référence de Sharma, Wu &
  Dalal (2005) à 10⁻⁴ près (`tests/test_awci_tools_check_palette.py`).
- **Contrastes vérifiés par les tests du front** : `theme/palette.test.ts` impose au moins 3:1 sur la carte et
  4,5:1 pour le texte.
