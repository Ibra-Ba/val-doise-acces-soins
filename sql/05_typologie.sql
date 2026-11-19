-- Quelles communes cumulent faible accessibilité et faible niveau de vie ?
-- Typologie relative au département : seuils = médianes des communes du 95.
-- Les communes sans revenu médian publié (secret statistique) sont non classées.
CREATE OR REPLACE VIEW typologie_95 AS
WITH base AS (
    SELECT
        a.code_commune,
        a.commune,
        a.population,
        a.pop_standardisee,
        a.apl_mg,
        r.revenu_median,
        r.taux_pauvrete
    FROM apl AS a
    LEFT JOIN revenu AS r USING (code_commune)
    WHERE a.annee = (SELECT max(annee) FROM apl)
      AND a.code_commune LIKE '95%'
      AND a.apl_mg IS NOT NULL
),
seuils AS (
    SELECT
        median(apl_mg)        AS seuil_apl,
        median(revenu_median) AS seuil_revenu
    FROM base
)
SELECT
    b.*,
    CASE
        WHEN b.revenu_median IS NULL THEN 'Non classée'
        WHEN b.apl_mg <  s.seuil_apl AND b.revenu_median <  s.seuil_revenu THEN '1. Double fragilité'
        WHEN b.apl_mg <  s.seuil_apl AND b.revenu_median >= s.seuil_revenu THEN '2. Faible accessibilité seule'
        WHEN b.apl_mg >= s.seuil_apl AND b.revenu_median <  s.seuil_revenu THEN '3. Faible niveau de vie seul'
        ELSE '4. Ni l''un ni l''autre'
    END AS classe
FROM base AS b
CROSS JOIN seuils AS s;

SELECT
    code_commune,
    commune,
    population,
    round(apl_mg, 2) AS apl_mg,
    revenu_median,
    taux_pauvrete,
    classe
FROM typologie_95
ORDER BY classe, apl_mg
