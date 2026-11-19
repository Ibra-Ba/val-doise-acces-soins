-- Combien d'habitants dans chaque classe de la typologie ?
-- Dépend de la vue typologie_95 créée par 05_typologie.sql.
-- Habitants : population totale. APL moyenne : pondérée par la population standardisée.
SELECT
    classe,
    count(*)                                                 AS nb_communes,
    sum(population)                                          AS population,
    round(100 * sum(population) / sum(sum(population)) OVER (), 1) AS part_population_pct,
    round(sum(apl_mg * pop_standardisee) / sum(pop_standardisee), 2) AS apl_moyenne
FROM typologie_95
GROUP BY classe
ORDER BY classe
