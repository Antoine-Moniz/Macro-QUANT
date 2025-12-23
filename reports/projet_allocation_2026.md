# Projet d'allocation d'actifs – 2026

## Bloc 1 – Scénario économique (choix discrétionnaire)

**Narratif retenu : hard landing US début 2026**, récession technique sur trois trimestres, PIB réel 2026 autour de ‑2 % a/a. L’Europe suit avec retard (croissance proche de 0), mais sans crise financière.

- **Chocs appliqués (voir `notebooks/scenario_dashboard.ipynb`, overrides 2026)**  
  `us_gdp_qoq –10 % annualisé`, `ISM 34`, `Michigan 40`, `Initial claims +150 %`, `NFP –500 k`, `CPI MoM –0,4 %`. chocs uniquement sur les projections 2026, historique inchangé.
- **Consommateurs** : moral bas (Michigan 40) et marché du travail qui se retourne (claims >300k, NFP négatifs) → consommation recule dès T1 2026, désinflation rapide via baisse des salaires.
- **Entreprises** : ISM 34 → contraction profonde de la production et des commandes ; marges sous pression, gel du capex et de l’emploi.
- **Politiques monétaire et budgétaire** : Fed coupe vers 2,50 % fin 2026 ; reprise du QE en cas de stress de liquidité. Budgets US/UE laissent jouer les stabilisateurs automatiques, avec soutien ciblé à l’industrie/emploi.
- **Commerce international** : demande mondiale molle, dollar plus fort → export US pénalisées ; zone euro affectée via chaînes industrielles mais bénéficie d’énergie moins chère.

## Bloc 2 – Scénario financier et outil quantitatif

### Outil quanti 
- Modèle **Markov 4 régimes** sur `us_gdp_qoq` + **Kalman** sur indicateurs avancés (ISM, Michigan, claims, NFP) → probabilité de récession.
- Baseline (nov. 2025) : blend ≈ **11 %** (phase « reprise »).  
  Scénario chocs 2026 : Markov = **1**, Kalman ≈ **0,964**, **blend ≈ 1** → régime « récession » quasi certain pendant le choc.

### Traduction financière du scénario

**Lien direct macro → prix/taux (ce qui sera évalué)**  
- Chute PIB/ISM → baisse BPA et compression modérée des multiples actions (US/EU).  
- Claims + NFP négatifs → détente forte des Fed Funds, rally sur la duration US.  
- Désinflation rapide (CPI -0,4 % MoM) → BCE suit avec retard, soutien aux Bund/OAT.  
- Dollar plus fort en récession US + demande mondiale faible → actions EU pénalisées mais moins que US si EUR faible.  
- Liquidité/prudence → poids du cash pour rebalancer si spreads/actions se disloquent.

| Classe d’actifs (5) | Hypothèse 2026 | Lien direct avec bloc 1 + probas |
| --- | --- | --- |
| Actions US (SPX) | -15 % prix, BPA -10 %, PER en baisse modérée (peur récession) | Récession US confirmée par blend 1 → baisse bénéfices et compression légère des multiples. |
| Actions Europe (SX5E) | -12 % prix, surperformance vs US si EUR <1,05 | Recul export et capex mais soutien budgétaire UE ; dépendance moindre à tech US. |
| Taux US 10 ans | Rally vers **3,0 %** fin 2026, pente 2s10s se repentit légèrement | Fed coupe agressivement en récession ; achats duration recherchés. |
| Taux EUR core (Bund/OAT 10 ans) | Bund vers **1,8 %**, OAT vers **2,4 %** | BCE suit Fed avec retard, désinflation rapide ; spread OAT stable avec soutien budgétaire. |
| Cash EUR (ESTRON) | Rendement glisse de 2 % à 1,2 % | Détente monétaire progressive ; garder du dry powder pendant la récession. |

## Bloc 3 – Allocation stratégique 2026 (8 lignes, ref 12,5 % chacune)

Référence : benchmark égal-pondéré 8 lignes × 12,5 %. Si l’on anticipe une baisse marquée des actions en hard landing 2026, on réduit fortement l’exposition actions et on concentre la performance attendue sur la duration longue. Le cash reste présent pour rebalancer en cours d’année si les points d’entrée s’améliorent.

**Achats / ventes vs benchmark (Δ en points de %)**
- Actions coupées nettement : SPX -9,0 ; SX5E -7,0.  
- Duration longue achetée : US10 +19,5 ; Bund10 +12,5 ; OAT10 +5,5.  
- Courts réduits : US2 -7,5 ; Bund2 -9,0.  
- Cash ESTRON -5,0 (léger maintien) pour garder de la flexibilité.

| Ligne (indice) | Poids final | Δ vs 12,5 % | Rationale (hard landing 2026, baisse actions) |
| --- | --- | --- | --- |
| Actions US (SPX) | **3,5 %** | -9,0 | Forte sous-pondération : BPA en baisse, compression des multiples ; on garde un minimum pour la convexité de rebond ultérieur. |
| Actions Europe (SX5E) | **5,5 %** | -7,0 | Sous-pondération mais un léger maintien pour valorisations plus basses et soutien budgétaire UE. |
| US Treasuries 10Y (USGG10) | **32 %** | +19,5 | Pilier principal : capter la détente Fed en récession, couverture actions. |
| US Treasuries 2Y (USGG2) | **5 %** | -7,5 | Front-end moins protecteur ; on privilégie la convexité du 10Y. |
| Bund 10Y (GDBR10) | **25 %** | +12,5 | Duration core EUR pour amortir la récession ; BCE suit avec retard. |
| Bund 2Y (GDBR2) | **3,5 %** | -9,0 | Réduction du court EUR ; portage moins utile si la BCE coupe. |
| OAT 10Y (GFRN10) | **18 %** | +5,5 | Carry vs Bund, bénéfice de la détente monétaire en zone euro. |
| Marché monétaire EUR (ESTRON) | **7,5 %** | -5,0 | Cash maintenu pour rebalancer si les spreads/actions deviennent attractifs. |

Total = 100 %. Lecture : portefeuille très défensif, performance attendue surtout de la duration longue (US/EUR). Actions très réduites pour protéger contre la baisse anticipée, cash pour l’option de renforcement futur. Courts (US2, Bund2) coupés car peu convexes en hard landing.

**Pourquoi cette exposition globale ?**  
Nous assumons un hard landing avec baisse actions : la source principale de performance devient la duration longue (Fed et BCE qui coupent), les actions sont fortement sous-pondérées pour limiter la baisse, et le cash offre une option d’achat si les valorisations deviennent nettement plus attractives. Les maturités courtes sont réduites car elles apportent moins de protection et de convexité que la longue en récession.

**Cadre temporel**  
Allocation décidée **début 2026** en vue de la trajectoire projetée **fin 2026** : on se positionne tôt sur la duration, on reste prudent sur les actions tant que le blend reste en régime « récession », et on conserve du cash pour ajuster si le cycle se retourne plus vite que prévu.

### Risques clés
1. **Rebond plus rapide que prévu** (données US se retournent fin 2025) → sous-pondération actions coûteuse, pente US se pentifie brutalement.
2. **Inflation ré-accélère** (chocs énergie/géopolitique) → baisses de taux limitées, duration pénalisée.
3. **Stress de liquidité/crédit** non capté par nos indicateurs de flux réels → spreads crédit et actions chutent plus que prévu, nécessité d’augmenter le cash.
