# Projet d'allocation d'actifs – 2026

## Bloc 1 – Scénario économique

### Outil quantitatif : cycle Markov (4 régimes) + filtre de Kalman
- Le modèle de Markov à **4 régimes** (Récession, Reprise, Boom, Ralentissement) appliqué au PIB US (`us_gdp_qoq`) fournit les probabilités de chaque phase ; le filtre de Kalman agrège les indicateurs avancés (ISM, Michigan, NFP, Initial Claims) pour capturer le momentum.
- Dernière observation (nov. 2025) : `reprise` domine à **93,9 %** (récession 4,7 %, ralentissement 1,1 %, boom 0,3 %).  
  Probabilités synthétiques arrondies : Markov **5,2 %**, Kalman **16,9 %**, **blend 10,8 %** (formule \(0{,}6\,p_M + 0{,}4\,p_K + p_M p_K\) plafonnée à 1).  
  → La probabilité reste basse en régime normal mais grimpe fortement dès que les deux signaux se tendent (pics ≈1 en 1973, 2008, 2020).
- Les **quatre indicateurs avancés** retenus couvrent les principaux piliers, avec un minimum d’informations “métier” :
  1. ISM Manufacturing PMI – enquête mensuelle de l’Institute for Supply Management (~300 directeurs achats). Diffusion base 50 : >50 = expansion industrielle (soutient la croissance, justifie une politique monétaire plus restrictive), <50 = contraction (pression sur les marges, plaide pour un assouplissement).
  
  Cet indicateur capte directement le momentum de l’activité manufacturière, via les commandes, la production et l’emploi. Comme l’industrie est cyclique et réagit en amont aux variations de la demande, le PMI est un signal avancé du cycle économique : un repli durable sous 50 anticipe généralement un ralentissement du PIB. Il influence les anticipations de la Fed car une activité industrielle forte se traduit souvent par tensions sur l’offre et sur les prix, donc un risque inflationniste, alors qu’un repli reflète une désinflation future.
  
  2. Sentiment des ménages U. Michigan – enquête téléphonique (~500 foyers, indice base 1966=100). Niveau <60 = prudence des ménages ⇒ consommation fragilisée et argument pour une Fed accommodante ; >80 = confiance élevée, risque de surchauffe.
  
  Cet indicateur reflète la perception des ménages sur leur situation financière et sur l’économie à venir. Il est essentiel car la consommation représente environ 70 % du PIB américain. Un moral élevé favorise la dépense, la croissance et potentiellement l’inflation, tandis qu’un moral en berne signale une contraction de la demande et un risque de ralentissement. C’est donc un baromètre avancé du cycle domestique, très suivi par la Fed pour ajuster son ton monétaire.

  3. Initial Jobless Claims – statistique hebdomadaire exhaustive du Département du Travail (toutes les demandes d’allocations). Une valeur durablement >300k signale un retournement du marché du travail (frein à la croissance, baisse de l’inflation salariale).  

  Ces chiffres sont un indicateur à haute fréquence de la santé du marché de l’emploi. Une hausse des inscriptions au chômage traduit une baisse de la demande de travail, qui précède souvent une montée du chômage et un ralentissement économique. À l’inverse, des niveaux bas (<250k) reflètent un marché du travail tendu, avec pressions salariales susceptibles d’alimenter l’inflation. L’emploi étant un pilier de la mission de la Fed, ces données influencent directement ses arbitrages entre soutien à la croissance et lutte contre l’inflation.

  4. Variation mensuelle des Nonfarm Payrolls (NFP) – enquête BLS auprès d’environ 130 000 entreprises et 60 000 ménages. Seuil d’équilibre ≈100 000 emplois : en dessous, chômage en hausse ; au-dessus, vigilance sur l’inflation salariale.
  
  Les NFP mesurent la création nette d’emplois hors secteur agricole et constituent un indicateur central du cycle du travail. Un rythme de créations supérieur à 100 000 reflète une économie en expansion, susceptible de renforcer la consommation et l’inflation, tandis qu’un rythme inférieur traduit une perte de vitesse du cycle et un probable assouplissement monétaire. Les marchés réagissent fortement à ce chiffre, car il concentre les signaux de croissance, d’emploi et d’inflation.

Chaque série est standardisée (z-score) : signe du z-score = contribution (+ = favorable, – = risque). Le panier alimente le filtre de Kalman pour un signal “temps réel” cohérent avec les conséquences macro (croissance, inflation, politique monétaire).

La standardisation en z-score permet de comparer des indicateurs hétérogènes sur une même échelle, en mesurant leur écart à la moyenne historique. Le filtre de Kalman agrège ces signaux pour extraire une probabilité de phase du cycle (expansion vs ralentissement), traduisant la synthèse entre production, emploi, consommation et confiance. Ce mécanisme fournit une lecture dynamique du cycle économique utile pour anticiper les inflexions de politique monétaire.

### Consommateurs
- **Sentiment** (U. Michigan) stabilisé à 53,6 (moyenne longue 86) : ménages encore prudents mais en amélioration par rapport au point bas 2022.
- **Marché du travail US** : Initial claims à 219 k et créations d’emplois encore positives (+22 k NFP) → désinflation sans choc social.
- **Inflation au détail** : CPI US MoM à 0,3 % et HICP zone euro 2,1 % YoY. Le pouvoir d’achat cesse d’être érodé, ce qui soutient la consommation 2024‑2025.

### Entreprises
- Les PMI manufacturiers restent sous 50 (US ISM 48,7, France 44,9 env.) mais la dynamique s’améliore (IFO Allemagne 88,4, Sentiment économique zone euro 96,8).
- Les enquêtes ZEW/IFO indiquent un redressement des commandes export en 2025, même si la production japonaise reste erratique (volatilité MoM).
- Conclusion : 2024 reste une année de normalisation industrielle, mais la marge bénéficiaire se maintient grâce au ralentissement des coûts salariaux et de l’énergie.

### Politiques monétaire et budgétaire
- **FED** : fourchette haute Fed Funds à 4,00 % (contre 5,5 % à mi‑2023) > trajectoire déjà accommodante. Deux baisses supplémentaires sont anticipées sur S2 2025 puis stabilité en 2026 tant que l’inflation cœur reste >2 %.
- **BCE** : taux refi 2,15 % (après pic 4,5 %). La politique reste restrictive mais la désinflation française (0,9 % YoY) autorise des ajustements graduels.
- Budgets US/UE : soutien ciblé sur industrie (IRA, Net-Zero Industry Act) sans relancer la demande globale ⇒ biais désinflationniste.

### Commerce international / cycle global
- Probabilité réduite de choc externe : croissance japonaise (PIB SA QoQ) reste volatile mais positive, et la réouverture asiatique soutient les exportateurs européens.
- Les indicateurs italiens et allemands suggèrent un rebond du commerce intra‑UE à partir de 2025, aligné avec la détente logistique.

## Bloc 2 – Scénario financier

| Classe d’actifs | Hypothèses 2024‑2026 | Lien macro |
| --- | --- | --- |
| Actions US (SPX) | Croissance des BPA +5 %/an grâce à la résilience conso, multiples stables (PER 19x). | Prob. récession faible et inflation maîtrisée ⇒ prime de risque stable. |
| Actions EURO (SX5E) | Surperformance relative vs US si euro reste <1,10 ; gains attendus +6 %/an via reprise industrielle. | PMI/IFO repartent, BCE plus accommodante → re-rating cyclique. |
| US Treasuries 10Y (USGG10) | Taux terminal 3,75 % fin 2026 (contre 4,4 % actuels). Portage + convexité positive. | Fed en easing graduel car inflation core converge vers 2,3 %. |
| US Treasuries 2Y (USGG2) | Forte sensibilité à timing des baisses (range 4,0‑4,5 %). Rendement réel encore attractif pour parking. | Politique monétaire encore restrictive → portage élevé mais volatil. |
| Bund 10Y (GDBR10) | Rendement 2,0 % fin 2026, prime de terme basse. | BCE finira ses coupes avant Fed, inflation cœur <2 %. |
| Bund 2Y (GDBR2) | Rendement 2,1‑2,3 % (flat). Utilisé pour protéger contre un scénario hawkish BCE. | Data dépendante BCE ; Foothold sur cash en EUR. |
| OAT 10Y (GFRN10) | Spread vs Bund ≈65 pb, bénéfice du carry vs Bund. | France CPI 0,9 % YoY => premium limité, risque budgétaire modéré. |
| Marché monétaire EUR (ESTRON) | Rendement >2 % jusqu’à début 2026 puis glissement sous 1,75 %. | BCE détend lentement, laisse du rendement de transition. |

**Synthèse** : environnement « soft landing » → biais neutre/légèrement pro-risque, mais allocation garde des coussins en monétaire et taux longs EUR pour absorber une erreur de diagnostic.

## Bloc 3 – Allocation stratégique 2026

| Ligne | Pondération | Rationale |
| --- | --- | --- |
| Actions US (SPX) | **14 %** | Probabilité de récession faible (9 %), bénéfices soutenus par consommation : légère surpondération. |
| Actions EURO (SX5E) | **13 %** | Repricing cyclique positif (IFO, ZEW), euro encore compétitif → alpha vs US. |
| US Treasuries 10Y | **11 %** | Duration utile si la Fed relâche plus vite ; maintien pour convexité. |
| US Treasuries 2Y | **10 %** | Sous-pondération : risque de re-steepening si Fed coupe ; réduire la sensibilité au front-end. |
| Bund 10Y | **13 %** | Couverture euro + carry « core », profite de la désinflation rapide. |
| Bund 2Y | **12 %** | Position neutre pour gérer les réinvestissements EUR à court terme. |
| OAT 10Y | **12 %** | Spread > Bund pour booster le rendement sans changer de devise. |
| Marché monétaire EUR (ESTRON) | **15 %** | Surpondération cash pour saisir opportunités et amortir choc inflation surprise. |

Total = 100 %. Les pondérations s’écartent modérément du benchmark égal (12,5 %) afin de refléter :
1. **Biais pro-actions** tant que notre outil probabiliste reste <20 %.
2. **Préférence pour duration long-only en zone euro** (désinflation plus rapide qu’aux US).
3. **Coussin cash** pour gérer les incertitudes budgétaires/électorales 2026.

### Risques clés
1. **Inflation cœur US repart** (hausse salaires) → Fed plus restrictive, perte sur actions US et steepening brutal.
2. **Choc géopolitique Europe** (énergie) → break-even inflation remonte, Bunds moins protecteurs.
3. **Erreur de régime du modèle** : si les indicateurs de confiance se dégradent simultanément (ISM <45 + Sentiment <50), notre probabilité de récession passerait >30 %, nécessitant une réduction forte des actions.*** End Patch



