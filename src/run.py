"""Exécute chaque fichier de sql/ dans l'ordre et écrit le résultat dans output/."""
from pathlib import Path

import duckdb

con = duckdb.connect("data/etude.duckdb")
Path("output").mkdir(exist_ok=True)

for fichier in sorted(Path("sql").glob("*.sql")):
    # Un fichier peut contenir plusieurs instructions ; la dernière est le SELECT exporté.
    instructions = [s.strip() for s in fichier.read_text(encoding="utf-8").split(";") if s.strip()]
    for instruction in instructions[:-1]:
        con.execute(instruction)
    resultat = con.execute(instructions[-1]).df()
    sortie = Path("output") / f"{fichier.stem}.csv"
    resultat.to_csv(sortie, index=False)
    print(f"{fichier.name}: {len(resultat)} lignes -> {sortie}")

con.close()
