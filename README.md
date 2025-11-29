# Projet Allocation d’Actifs – 2026

Ce dépôt contient tous les éléments utilisés pour élaborer le scénario macro-financier et l’allocation stratégique 2026 d’une société de gestion.  
Les données proviennent d’un export Bloomberg (Excel), sont consolidées avec `pandas`, puis exploitées dans des notebooks et un rapport Markdown.

## Structure

```
├── data/
│   ├── processed/               # Séries consolidées (parquet, csv)
├── notebooks/
│   ├── macro_dashboard.ipynb    # Contrôle des séries importées
│   └── recession_indicator.ipynb# Visualisation des probabilités Markov/Kalman
├── reports/
│   └── projet_allocation_2026.md# Rapport complet blocs 1‑2‑3
├── src/
│   ├── ingest_bloomberg.py      # Lit l’Excel indicateurs -> macro_panel.parquet
│   └── recession_indicator.py   # Modèle Markov (4 régimes) + Kalman
└── README.md
```

## Installation

1. Créer un environnement Python (>=3.10).
2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Workflow

1. **Importer les séries Excel**
   ```bash
   python src/ingest_bloomberg.py
   ```
   - lit le fichier `Indices_Bloomberg_Macro données.xlsx`
   - produit `data/processed/macro_panel.parquet` et `macro_metadata.csv`

2. **Calculer l’outil probabiliste**
   ```bash
   python src/recession_indicator.py
   ```
   - modèle de Markov à quatre régimes sur la croissance du PIB
   - filtre de Kalman sur ISM, Michigan, NFP, Initial Claims
   - exporte `data/processed/recession_prob.csv`

3. **Explorer / rédiger**
   - Notebooks (`notebooks/*.ipynb`) pour visualiser séries et probabilités.
   - Rapport final dans `reports/projet_allocation_2026.md`.

## Notes

- Le fichier Excel doit contenir une feuille par indicateur, dates en colonne A et valeurs en B.
- Le script Markov/Kalman ajoute automatiquement les probabilités de chaque régime, la probabilité mixte (`blended_prob`) ainsi que le régime dominant.
- Les indicateurs avancés sont normalisés (z-score) pour pouvoir être combinés dans le filtre de Kalman.

N’hésitez pas à consulter le rapport (`reports/projet_allocation_2026.md`) pour un exposé détaillé du scénario macro, du lien avec les classes d’actifs et de l’allocation 2026.***

