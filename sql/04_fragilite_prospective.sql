-- Quelles communes dépendent le plus de médecins proches de la retraite ?
-- Écart entre l'APL tous âges et l'APL limitée aux médecins de 65 ans et moins.
SELECT
    code_commune,
    commune,
    population,
    round(apl_mg, 2)                                         AS apl_mg,
    round(apl_mg_moins65, 2)                                 AS apl_mg_moins65,
    round(apl_mg - apl_mg_moins65, 2)                        AS perte_potentielle,
    round(100 * (apl_mg - apl_mg_moins65) / nullif(apl_mg, 0), 1) AS part_seniors_pct,
    apl_mg >= 2.5 AND apl_mg_moins65 < 2.5                   AS bascule_sous_le_seuil
FROM apl
WHERE annee = (SELECT max(annee) FROM apl)
  AND code_commune LIKE '95%'
  AND apl_mg IS NOT NULL
  AND apl_mg_moins65 IS NOT NULL
ORDER BY part_seniors_pct DESC
