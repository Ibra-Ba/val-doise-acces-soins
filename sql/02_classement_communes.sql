-- Quelles communes du Val-d'Oise sont les moins bien dotées ?
-- Classement par APL, quartile départemental et repère de sous-densité.
-- Seuil de 2,5 consultations par an et par habitant : repère usuel de
-- sous-densité, à confirmer dans la documentation DREES du millésime utilisé.
SELECT
    code_commune,
    commune,
    population,
    round(apl_mg, 2)                                         AS apl_mg,
    rank()  OVER (ORDER BY apl_mg)                           AS rang_du_moins_dote,
    ntile(4) OVER (ORDER BY apl_mg)                          AS quartile,
    apl_mg < 2.5                                             AS sous_dense
FROM apl
WHERE annee = (SELECT max(annee) FROM apl)
  AND code_commune LIKE '95%'
  AND apl_mg IS NOT NULL
ORDER BY apl_mg
