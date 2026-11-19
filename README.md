# Accès au médecin généraliste et précarité dans le Val-d'Oise

Étude à la maille communale : où l'accessibilité au médecin généraliste est-elle
la plus fragile dans le Val-d'Oise, et quelles communes cumulent faible
accessibilité et faible niveau de vie ?

> Résultat principal : [à compléter — une phrase chiffrée].

## Données

| Source | Fichier attendu dans `data/raw/` | Contenu |
| --- | --- | --- |
| DREES — Indicateur d'APL aux médecins généralistes | `apl_medecins_generalistes.xlsx` | APL par commune 2022 à 2024, tous âges et médecins de 65 ans ou moins, populations standardisée et totale |
| INSEE — Filosofi 2023, niveau communal | `filosofi_communes.csv` | Niveau de vie médian, taux de pauvreté |
| Contours communaux (IGN Admin Express ou équivalent) | utilisé dans QGIS uniquement | Fonds de carte |

Les fichiers bruts ne sont pas versionnés. Millésimes utilisés : [à compléter].

## Reproduire

```bash
pip install -r requirements.txt
python src/load.py      # charge data/raw/ dans data/etude.duckdb
python src/run.py       # exécute sql/*.sql et écrit output/*.csv
```

Avant le premier chargement, ajuster le bloc CONFIGURATION en tête de
`src/load.py` (noms d'onglets, ligne d'en-tête, noms de colonnes) d'après les
fichiers réellement téléchargés.

## Requêtes

| Fichier | Question |
| --- | --- |
| `sql/01_rang_departement.sql` | Où se situe le Val-d'Oise parmi les départements ? |
| `sql/02_classement_communes.sql` | Quelles communes du 95 sont les moins bien dotées ? |
| `sql/03_evolution.sql` | Où l'accessibilité a-t-elle le plus reculé ? |
| `sql/04_fragilite_prospective.sql` | Quelles communes dépendent le plus de médecins proches de la retraite ? |
| `sql/05_typologie.sql` | Quelles communes cumulent faible accessibilité et faible niveau de vie ? |
| `sql/06_population_par_classe.sql` | Combien d'habitants dans chaque classe ? |

## Livrables

- `note/` : note de synthèse de deux pages.
- `carte/` : carte QGIS de la typologie (jointure de `output/05_typologie.csv`
  sur les contours communaux, clé `code_commune`).

## Limites

- L'APL est un indicateur d'offre potentielle, pas de recours effectif.
- Le niveau de vie médian est soumis au secret statistique dans les très
  petites communes : elles sont « non classées » dans la typologie.
- La typologie est relative au département (seuils = médianes du Val-d'Oise).
- Moyennes d'APL pondérées par la population standardisée, comptes d'habitants
  sur la population totale, conformément à la note DREES.
