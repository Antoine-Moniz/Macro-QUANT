# Plan d’exécution

## Étape 1 – Ingérer les indicateurs depuis Bloomberg
- **Extraction** : lire les feuilles du classeur [`Indices_Bloomberg_Macro données.xlsx`](Indices_Bloomberg_Macro données.xlsx) (dates en `A`, valeurs en `B`, données à partir de la ligne 3) et consolider les séries dans un dataframe unique (fichier cible `data/processed/macro_panel.parquet`).
- **Documentation** : créer un tableau de métadonnées (nom de la feuille, ticker, fréquence, pilier économique) dans `data/processed/macro_metadata.csv` pour justifier chaque indicateur du bloc 1.
- **Nettoyage** : harmoniser la fréquence (passage en mensuel via forward-fill), calculer YOY/MoM si nécessaire et produire un notebook exploratoire `notebooks/macro_dashboard.ipynb` avec graphiques rapides.

## Étape 2 – Construire l’outil probabiliste (Markov + Kalman)
- **Préparation** : dériver la croissance trimestrielle du PIB (approximation via séries disponibles) et sélectionner 3‑4 indicateurs avancés (ISM, NFP, Sentiment, Claims) depuis le panel traité.
- **Implémentation** : coder dans `src/recession_indicator.py` un modèle à deux régimes (Hamilton) sur la croissance + un filtre de Kalman qui agrège les indicateurs avancés ; sauvegarder la probabilité lissée dans `data/processed/recession_prob.csv`.
- **Analyse** : documenter dans `notebooks/recession_indicator.ipynb` les graphiques des probabilités et interpréter les régimes attendus fin 2024‑2026 pour alimenter le Bloc 1.

## Étape 3 – Scénario économique 2024 et projections 2025‑2026
- **Rédaction** : dans `reports/projet_allocation_2026.md`, décrire chaque pilier (Consommateurs, Entreprises, Politiques M/B, Commerce) en citant les indicateurs du bloc 1 et l’outil de probabilité.
- **Hypothèses** : expliciter les hypothèses d’inflation, croissance, politique monétaire/fiscale jusqu’à fin 2026 et relier les signaux de l’outil probabiliste.

## Étape 4 – Scénario financier
- **Traduction** : mapper le scénario macro sur les classes d’actifs demandées (Actions US/EU, taux US/EU, monétaire EUR) en chiffrant direction/tendance (par ex. target yield, range de performance) dans `reports/projet_allocation_2026.md`.
- **Lien** : pour chaque classe, expliciter le mécanisme reliant un indicateur ou la probabilité de récession au comportement financier (Bloc 1 → Bloc 2).

## Étape 5 – Allocation stratégique 2026
- **Tableau** : compléter dans le rapport la matrice 8 lignes × 12,5 % avec sur/sous-pondérations justifiées.
- **Justification & risques** : fournir 2‑3 phrases par ligne rappelant l’outil probabiliste et les hypothèses financières, puis conclure par les risques majeurs (inflation surprise, erreur de régime, choc géopolitique).



