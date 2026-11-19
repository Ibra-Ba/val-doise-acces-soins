-- Où l'accessibilité a-t-elle le plus reculé entre l'avant-dernier et le dernier millésime ?
-- (2023 -> 2024 avec le fichier DREES actuel)
WITH suivi AS (
    SELECT
        code_commune,
        commune,
        annee,
        population,
        apl_mg,
        lag(apl_mg) OVER (PARTITION BY code_commune ORDER BY annee) AS apl_precedente,
        lag(annee)  OVER (PARTITION BY code_commune ORDER BY annee) AS annee_precedente
    FROM apl
    WHERE code_commune LIKE '95%'
)
SELECT
    code_commune,
    commune,
    population,
    annee_precedente,
    annee,
    round(apl_precedente, 2)                                 AS apl_avant,
    round(apl_mg, 2)                                         AS apl_apres,
    round(apl_mg - apl_precedente, 2)                        AS variation,
    round(100 * (apl_mg - apl_precedente) / nullif(apl_precedente, 0), 1) AS variation_pct
FROM suivi
WHERE annee = (SELECT max(annee) FROM apl)
  AND apl_precedente IS NOT NULL
ORDER BY variation
