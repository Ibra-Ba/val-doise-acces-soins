"""Lien entre accessibilité au médecin généraliste et niveau de vie, communes du Val-d'Oise.

Prérequis : python src/load.py puis python src/run.py (crée la vue typologie_95).
Sorties : statistiques dans le terminal, graphique output/correlation.png.
"""
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from scipy.stats import spearmanr

DB = "data/etude.duckdb"
SORTIE = Path("output/correlation.png")

# Mêmes classes que la carte. Le bleu est plus soutenu que sur la carte :
# un point est bien plus petit qu'une surface de commune.
COULEURS = {
    "1. Double fragilité": "#b2182b",
    "2. Faible accessibilité seule": "#ef8a62",
    "3. Faible niveau de vie seul": "#2166ac",
    "4. Ni l'un ni l'autre": "#9e9e9e",
}
A_NOMMER = 7  # communes en double fragilité les plus peuplées, nommées sur le graphique
# Décalages manuels (en points) pour les étiquettes qui se chevauchent.
DECALAGES = {"Villiers-le-Bel": (-8, 4, "right"), "Garges-lès-Gonesse": (8, -8, "left"),
             "Sarcelles": (8, 2, "left")}


def fr(x: float, dec: int = 2) -> str:
    """Nombre au format français : virgule décimale, signe moins typographique."""
    return f"{x:.{dec}f}".replace(".", ",").replace("-", "\u2212")

con = duckdb.connect(DB, read_only=True)
df = con.execute("""
    SELECT commune, population, apl_mg, revenu_median, classe
    FROM typologie_95
    WHERE revenu_median IS NOT NULL
""").df()
seuil_apl, seuil_revenu = con.execute("""
    SELECT
        (SELECT sum(apl_mg * pop_standardisee) / sum(pop_standardisee) FROM typologie_95),
        (SELECT revenu_median FROM revenu_dep WHERE departement = '95')
""").fetchone()
con.close()

# --- Statistiques ------------------------------------------------------------
rho, p = spearmanr(df["apl_mg"], df["revenu_median"])
n = len(df)
# Intervalle de confiance à 95 % par transformation de Fisher (approximation usuelle).
z, se = np.arctanh(rho), 1.06 / np.sqrt(n - 3)
ic_bas, ic_haut = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)

print(f"Communes classées : {n}")
print(f"Corrélation de Spearman (APL, niveau de vie médian) : rho = {rho:.3f}")
print(f"IC à 95 % : [{ic_bas:.3f} ; {ic_haut:.3f}]   p = {p:.3f}")

# --- Graphique ----------------------------------------------------------------
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(9, 6))

# Les communes les plus peuplées sont dessinées en premier pour ne pas masquer les petites.
for classe, couleur in COULEURS.items():
    d = df[df["classe"] == classe].sort_values("population", ascending=False)
    ax.scatter(d["apl_mg"], d["revenu_median"] / 1000,
               s=np.sqrt(d["population"]) * 0.9, c=couleur, alpha=0.85,
               edgecolors="white", linewidths=0.8, label=classe, zorder=3)

ax.axvline(seuil_apl, color="#555555", lw=0.8, ls="--", zorder=1)
ax.axhline(seuil_revenu / 1000, color="#555555", lw=0.8, ls="--", zorder=1)
ax.annotate(f"APL moyenne du département : {fr(seuil_apl)}",
            (seuil_apl, ax.get_ylim()[1]), xytext=(4, -12), textcoords="offset points",
            fontsize=8, color="#555555")
ax.annotate(f"Niveau de vie médian du département : {seuil_revenu:,.0f} €".replace(",", "\u202f"),
            (ax.get_xlim()[1], seuil_revenu / 1000), xytext=(-4, -11), textcoords="offset points",
            fontsize=8, color="#555555", ha="right")

rouges = df[df["classe"] == "1. Double fragilité"].nlargest(A_NOMMER, "population")
for _, r in rouges.iterrows():
    dx, dy, ha = DECALAGES.get(r["commune"], (6, -3, "left"))
    ax.annotate(r["commune"], (r["apl_mg"], r["revenu_median"] / 1000), xytext=(dx, dy),
                textcoords="offset points", fontsize=8, color="#222222", ha=ha)

ax.set_xlabel("Accessibilité au médecin généraliste, 2024 (consultations par an et par habitant)")
ax.set_ylabel("Niveau de vie médian, 2023 (milliers d'euros)")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fr(v, 1)))
ax.grid(color="#e6e6e6", lw=0.6, zorder=0)
ax.set_axisbelow(True)

ax.set_title("Accessibilité et niveau de vie varient presque indépendamment d'une commune à l'autre",
             loc="left", fontsize=12, fontweight="bold", pad=24)
ax.text(0, 1.02,
        f"Communes du Val-d'Oise (n = {n}). Corrélation de Spearman : {fr(rho, 3)} "
        f"[IC 95 % : {fr(ic_bas, 3)} ; {fr(ic_haut, 3)}], p = {fr(p, 3)}. Taille des points : population.",
        transform=ax.transAxes, fontsize=9, color="#555555")

poignees = [Line2D([], [], marker="o", ls="", markersize=7, markerfacecolor=c,
                  markeredgecolor="white", label=k) for k, c in COULEURS.items()]
leg = ax.legend(handles=poignees, loc="upper right", fontsize=8, frameon=False,
                title="Classe de la commune", title_fontsize=8)
leg._legend_box.align = "left"

fig.text(0.01, 0.01,
         "Sources : DREES, APL 2024 ; Insee, Filosofi 2023. Six communes sans niveau de vie publié "
         "(secret statistique) sont exclues.", fontsize=7, color="#777777")
fig.tight_layout(rect=(0, 0.03, 1, 1))
SORTIE.parent.mkdir(exist_ok=True)
fig.savefig(SORTIE, dpi=200)
print(f"Graphique : {SORTIE}")
