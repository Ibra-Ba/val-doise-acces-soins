"""Charge les fichiers bruts de data/raw/ dans data/etude.duckdb.

Tables créées (France entière, le filtre Val-d'Oise est fait en SQL) :
  apl(code_commune, commune, annee, apl_mg, apl_mg_moins65, pop_standardisee, population)
  revenu(code_commune, revenu_median, taux_pauvrete)
  revenu_dep(departement, revenu_median, taux_pauvrete)
"""
from pathlib import Path

import duckdb
import pandas as pd

# --- CONFIGURATION : à ajuster d'après les fichiers téléchargés -------------
RAW = Path("data/raw")
DB = Path("data/etude.duckdb")

# Fichier DREES « Indicateur d'APL aux médecins généralistes » (un onglet par millésime).
APL_FILE = RAW / "apl_medecins_generalistes.xlsx"
APL_SHEETS = {2022: "APL 2022", 2023: "APL 2023", 2024: "APL 2024"}
APL_HEADER_ROW = 8  # ligne d'en-tête (base 0) ; la ligne suivante contient les unités
# Les intitulés changent d'un onglet à l'autre (« et moins » / « ou moins »,
# année de population) : les colonnes sont donc lues par position.
APL_POSITIONS = {
    0: "code_commune",
    1: "commune",
    2: "apl_mg",
    3: "apl_mg_moins65",
    6: "pop_standardisee",  # pour les moyennes d'APL (consigne DREES)
    7: "population",        # pour compter des habitants et calculer des quantiles
}

# Fichier INSEE « Revenus et pauvreté des ménages en 2023 - Tous les niveaux
# géographiques » (FILOSOFI_CC_2023_FR.xlsx), onglet des communes.
FILO_FILE = RAW / "filosofi_2023.xlsx"
FILO_SHEET = "COM"
FILO_SKIPROWS = 5  # titre, lignes vides, intitulés, ligne « GEO / Géographie »
FILO_POSITIONS = {0: "code_commune", 2: "revenu_median", 3: "taux_pauvrete"}
FILO_SHEET_DEP = "DEP"  # valeurs départementales, servent de seuils à la typologie
# -----------------------------------------------------------------------------


def lire_apl() -> pd.DataFrame:
    tables = []
    for annee, onglet in APL_SHEETS.items():
        df = pd.read_excel(APL_FILE, sheet_name=onglet, header=APL_HEADER_ROW, dtype=str)
        entete = list(df.columns)
        df = df.iloc[:, list(APL_POSITIONS)]
        df.columns = list(APL_POSITIONS.values())
        print(f"{onglet}: " + " | ".join(f"{entete[i].strip()} -> {nom}" for i, nom in APL_POSITIONS.items()))
        df["annee"] = annee
        tables.append(df)
    apl = pd.concat(tables, ignore_index=True)
    # Écarte la ligne des unités et les lignes vides : un code commune fait 5 caractères.
    apl = apl[apl["code_commune"].str.strip().str.len() == 5].copy()
    apl["code_commune"] = apl["code_commune"].str.strip()
    for col in ("apl_mg", "apl_mg_moins65", "pop_standardisee", "population"):
        apl[col] = pd.to_numeric(apl[col], errors="coerce")
    apl["population"] = apl["population"].round()
    return apl[["code_commune", "commune", "annee", "apl_mg", "apl_mg_moins65",
                "pop_standardisee", "population"]]


def lire_revenu() -> pd.DataFrame:
    df = pd.read_excel(FILO_FILE, sheet_name=FILO_SHEET, header=None,
                       skiprows=FILO_SKIPROWS, dtype=str)
    rev = df.iloc[:, list(FILO_POSITIONS)]
    rev.columns = list(FILO_POSITIONS.values())
    rev = rev[rev["code_commune"].str.strip().str.len() == 5].copy()  # écarte la note de source
    rev["code_commune"] = rev["code_commune"].str.strip()
    # « s » = secret statistique -> NULL.
    for col in ("revenu_median", "taux_pauvrete"):
        rev[col] = pd.to_numeric(rev[col], errors="coerce")
    return rev


def lire_revenu_dep() -> pd.DataFrame:
    df = pd.read_excel(FILO_FILE, sheet_name=FILO_SHEET_DEP, header=None,
                       skiprows=FILO_SKIPROWS, dtype=str)
    dep = df.iloc[:, [0, 2, 3]]
    dep.columns = ["departement", "revenu_median", "taux_pauvrete"]
    dep = dep[dep["departement"].str.strip().str.len().between(2, 3)].copy()
    for col in ("revenu_median", "taux_pauvrete"):
        dep[col] = pd.to_numeric(dep[col], errors="coerce")
    return dep


def main() -> None:
    apl, revenu, revenu_dep = lire_apl(), lire_revenu(), lire_revenu_dep()
    con = duckdb.connect(str(DB))
    con.execute("CREATE OR REPLACE TABLE apl AS SELECT * FROM apl")
    con.execute("CREATE OR REPLACE TABLE revenu AS SELECT * FROM revenu")
    con.execute("CREATE OR REPLACE TABLE revenu_dep AS SELECT * FROM revenu_dep")
    for table in ("apl", "revenu"):
        total = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        vo = con.execute(
            f"SELECT count(DISTINCT code_commune) FROM {table} WHERE code_commune LIKE '95%'"
        ).fetchone()[0]
        print(f"{table:7s}: {total:6d} lignes, {vo} communes du Val-d'Oise")
    con.close()


if __name__ == "__main__":
    main()