# Projet Allocation d’Actifs – 2026

Ce dépôt contient tous les éléments utilisés pour élaborer le scénario macro-financier et l’allocation stratégique 2026 d’une société de gestion.  
Les données proviennent d’un export Bloomberg (Excel), sont consolidées avec `pandas`, puis exploitées dans des notebooks et un rapport Markdown.

## Structure

```
├── data/
│   ├── processed/
│   │   ├── macro_panel.parquet  # Panel consolidé
│   │   ├── recession_prob.csv   # Probabilités historiques baseline
│   │   └── scenarios/           # CSV générés pour chaque scénario
├── notebooks/
│   ├── macro_dashboard.ipynb        # Contrôle des séries importées
│   ├── recession_indicator.ipynb    # Visualisation des probabilités Markov/Kalman
│   └── scenario_dashboard.ipynb     # Dashboard interactif pour tester des chocs
├── reports/
│   └── projet_allocation_2026.md    # Rapport complet blocs 1‑2‑3
├── scenarios/
│   └── us_hard_landing.yaml         # Exemple YAML décrivant un choc prospectif
├── src/
│   ├── ingest_bloomberg.py          # Lit l’Excel indicateurs -> macro_panel.parquet
│   ├── recession_indicator.py       # Modèle Markov (4 régimes) + Kalman
│   └── run_scenario.py              # Application des overrides + recalcul des probabilités
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

4. **Projeter des scénarios futurs**
   - Décrire vos chocs dans un fichier YAML (ex. `scenarios/us_hard_landing.yaml`). Chaque bloc précise la colonne, la période future concernée et soit une valeur absolue (`value`), soit un delta relatif (`delta_pct`). Aucune modification n’est appliquée sur l’historique : seuls les points > cutoff (fin 2025) sont écrasés.
   ```bash
   python src/run_scenario.py --config scenarios/us_hard_landing.yaml
   ```
   - Le script charge le panel de base, étend l’horizon jusqu’à la fin du scénario, applique les overrides, recalcule les probabilités et sauvegarde `data/processed/scenarios/scenario_<nom>.csv`.
   - Pour itérer sans YAML, utilisez `notebooks/scenario_dashboard.ipynb` : activez `USE_CUSTOM_OVERRIDES = True`, éditez la liste `USER_OVERRIDES`, puis exécutez. Le notebook rattache automatiquement la partie historique baseline, applique les chocs uniquement sur 2026+ et trace des graphes Markov/Kalman/blend cohérents avec `recession_indicator.ipynb`. Le dossier `notebooks/data` n’est plus utilisé : toutes les sorties sont dans `data/processed/scenarios/`.

## Scénario courant (exemple hard landing 2026)
- Chocs prospectifs (2026) : `us_gdp_qoq –10 % annualisé`, `ISM 34`, `Michigan 40`, `Initial claims +150 %`, `NFP –500 k`, `CPI MoM –0,4 %`. L’historique reste inchangé.
- Probabilités obtenues : Markov = 1, Kalman ≈ 0,96, blend ≈ 1 → régime « récession » certain pendant le choc.
- Rapport synthétique : voir `reports/projet_allocation_2026.md` (bloc 1 macro, bloc 2 lien macro→finance, bloc 3 allocation).

## Allocation 2026 (début 2026, vue fin 2026)
- Positionnement défensif pour hard landing : actions fortement réduites, duration longue surpondérée (US 10Y, Bund/OAT 10Y), courts réduits, cash conservé pour rebalancer.
- Détail ligne par ligne dans `reports/projet_allocation_2026.md` (8 lignes vs benchmark 12,5 % chacune).

## Notes

- Le fichier Excel doit contenir une feuille par indicateur, dates en colonne A et valeurs en B.
- Le script Markov/Kalman ajoute automatiquement les probabilités de chaque régime, la probabilité mixte (`blended_prob`) ainsi que le régime dominant.
- Les indicateurs avancés sont normalisés (z-score) pour pouvoir être combinés dans le filtre de Kalman.
- Le workflow de scénarisation évite toute dépendance à un Excel intermédiaire : les overrides sont saisis dans le YAML ou directement dans le notebook, et les sorties sont stockées uniquement dans `data/processed/scenarios/`.

N’hésitez pas à consulter le rapport (`reports/projet_allocation_2026.md`) pour un exposé détaillé du scénario macro, du lien avec les classes d’actifs et de l’allocation 2026.***

