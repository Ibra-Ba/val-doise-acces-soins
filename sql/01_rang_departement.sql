-- Où se situe le Val-d'Oise parmi les départements ?
-- APL moyenne pondérée par la population standardisée (consigne DREES),
-- dernier millésime, et rang national.
WITH par_departement AS (
    SELECT
        CASE WHEN code_commune LIKE '97%' THEN left(code_commune, 3)
             ELSE left(code_commune, 2) END                  AS departement,
        sum(apl_mg * pop_standardisee) / sum(pop_standardisee) AS apl_moyenne,
        sum(population)                                      AS population
    FROM apl
    WHERE annee = (SELECT max(annee) FROM apl)
      AND apl_mg IS NOT NULL
      AND population > 0
    GROUP BY 1
)
SELECT
    departement,
    round(apl_moyenne, 2)                                    AS apl_moyenne,
    population,
    rank() OVER (ORDER BY apl_moyenne DESC)                  AS rang,
    count(*) OVER ()                                         AS nb_departements
FROM par_departement
ORDER BY rang
