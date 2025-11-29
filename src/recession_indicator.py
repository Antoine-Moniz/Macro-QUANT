"""
==============================
Indicateur probabiliste de cycle
==============================

Ce module assemble deux approches classiques de détection de cycle :

1. **Markov 4 régimes** sur la croissance du PIB US (`us_gdp_qoq`).
   L’objectif est d’identifier l’état structurel de l’économie
   (Récession, Reprise, Boom, Ralentissement). On obtient des probabilités
   lissées par régime et le régime dominant.

2. **Filtre de Kalman** sur des indicateurs avancés (ISM, sentiment, emploi).
   Cela donne une mesure rapide du momentum macro.

La fusion des deux fournit trois probabilités :
    - `markov_prob` : stress structurel (récession + 0,5 ralentissement)
    - `kalman_prob` : signal avancé lissé
    - `blended_prob` : combinaison pondérée + interaction

Le pipeline principal écrit un CSV `data/processed/recession_prob.csv` contenant
ces colonnes ainsi que les probabilités de chaque régime.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "data" / "processed" / "macro_panel.parquet"
OUTPUT_PATH = ROOT / "data" / "processed" / "recession_prob.csv"

REGIME_LABELS = ["recession", "reprise", "boom", "ralentissement"]
# Nombre de régimes ; utilisé partout pour éviter les constantes magiques.
K_REGIMES = len(REGIME_LABELS)


def load_panel() -> pd.DataFrame:
    """
    Charge le fichier parquet `macro_panel.parquet` produit par
    `src/ingest_bloomberg.py`. On le trie par date pour éviter les
    surprises (certaines feuilles Excel sont dans le désordre).

    Returns
    -------
    pd.DataFrame
        Panel complet (index = datetime, colonnes = indicateurs).
    """
    panel = pd.read_parquet(PANEL_PATH)
    return panel.sort_index()


def normal_pdf(x: float, mu: float, sigma: float) -> float:
    """
    Densité d’une loi normale N(mu, sigma^2). Utilisée dans la partie Markov
    pour calculer les vraisemblances.

    On borne `sigma` pour éviter les divisions par zéro, ce qui pourrait
    arriver si la variance estimée d’un régime devient très faible.
    """
    sigma = max(sigma, 1e-6)
    coef = 1.0 / (math.sqrt(2 * math.pi) * sigma)
    return coef * math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def forward_backward(
    data: np.ndarray,
    mu: np.ndarray,
    sigma: np.ndarray,
    trans: np.ndarray,
    pi: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Algorithme forward-backward utilisé lors de l’étape E de l’EM.

    Parameters
    ----------
    data : np.ndarray
        Observations (croissance du PIB).
    mu, sigma : np.ndarray
        Paramètres moyens/variances de chaque régime.
    trans : np.ndarray
        Matrice de transition.
    pi : np.ndarray
        Distribution initiale.

    Returns
    -------
    gamma : np.ndarray (T, K)
        Probabilités lissées d’appartenance à chaque régime.
    xi : np.ndarray (T-1, K, K)
        Probabilités de transition utilisées pour re-calculer `trans`.
    c : np.ndarray (T,)
        Facteurs de normalisation (pour contrôler la stabilité numérique).
    """
    T = len(data)
    N = len(mu)
    alpha = np.zeros((T, N))
    beta = np.zeros((T, N))
    c = np.zeros(T)
    likelihoods = np.zeros((T, N))

    for j in range(N):
        likelihoods[0, j] = normal_pdf(data[0], mu[j], sigma[j])
        alpha[0, j] = pi[j] * likelihoods[0, j]
    c[0] = alpha[0].sum() or 1e-9
    alpha[0] /= c[0]

    for t in range(1, T):
        for j in range(N):
            likelihoods[t, j] = normal_pdf(data[t], mu[j], sigma[j])
            alpha[t, j] = likelihoods[t, j] * np.sum(alpha[t - 1] * trans[:, j])
        c[t] = alpha[t].sum() or 1e-9
        alpha[t] /= c[t]

    beta[-1] = 1.0 / c[-1]
    for t in range(T - 2, -1, -1):
        for i in range(N):
            beta[t, i] = np.sum(beta[t + 1] * trans[i, :] * likelihoods[t + 1, :])
        beta[t] /= c[t]

    gamma = alpha * beta
    gamma /= gamma.sum(axis=1, keepdims=True)

    xi = np.zeros((T - 1, N, N))
    for t in range(T - 1):
        denom = np.sum(
            alpha[t, :, None]
            * trans
            * likelihoods[t + 1, None, :]
            * beta[t + 1, None, :]
        ) or 1e-9
        xi[t] = (
            alpha[t, :, None]
            * trans
            * likelihoods[t + 1, None, :]
            * beta[t + 1, None, :]
        ) / denom

    return gamma, xi, c


def initialise_parameters(values: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Fournit des valeurs de départ raisonnables à l’algorithme EM :
    - les moyennes des régimes sont réparties sur les quantiles de la série
      (cela évite de démarrer tous les régimes au même niveau) ;
    - les variances sont égales ;
    - la matrice de transition a 0,85 sur la diagonale pour forcer la persistance ;
    - `pi` est uniforme par défaut.
    """
    quantiles = np.linspace(5, 95, K_REGIMES)
    mu = np.array([np.percentile(values, q) for q in quantiles])
    sigma = np.full(K_REGIMES, values.std() or 1.0)
    trans = np.full((K_REGIMES, K_REGIMES), 1 / K_REGIMES)
    np.fill_diagonal(trans, 0.85)
    for i in range(K_REGIMES):
        trans[i] /= trans[i].sum()
    pi = np.full(K_REGIMES, 1 / K_REGIMES)
    return mu, sigma, trans, pi


def estimate_markov_probs(gdp: pd.Series, max_iter: int = 200) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Estime le modèle de Markov sur la série de PIB (EM itératif).

    - Les régimes sont réordonnés par moyenne (low -> high) afin de
      les mapper systématiquement sur ["recession", "reprise", ...].
    - On renvoie les probabilités lissées pour chaque régime.
    """
    data = gdp.dropna().astype(float)
    if data.empty:
        raise ValueError("La série PIB est vide, impossible d'estimer le modèle.")
    values = data.values
    mu, sigma, trans, pi = initialise_parameters(values)

    for _ in range(max_iter):
        gamma, xi, _ = forward_backward(values, mu, sigma, trans, pi)

        for j in range(K_REGIMES):
            weight = gamma[:, j].sum()
            if weight <= 1e-9:
                continue
            mu[j] = np.sum(gamma[:, j] * values) / weight
            sigma[j] = math.sqrt(
                max(np.sum(gamma[:, j] * (values - mu[j]) ** 2) / weight, 1e-6)
            )

        for i in range(K_REGIMES):
            denom = gamma[:-1, i].sum() or 1e-9
            trans[i] = xi[:, i, :].sum(axis=0) / denom
        trans = np.clip(trans, 1e-5, 1 - 1e-5)
        trans /= trans.sum(axis=1, keepdims=True)
        pi = gamma[0]

    order = np.argsort(mu)
    ordered_mu = mu[order]
    ordered_gamma = gamma[:, order]

    regime_probs: Dict[str, pd.Series] = {}
    for idx, name in enumerate(REGIME_LABELS):
        regime_probs[name] = pd.Series(
            ordered_gamma[:, idx], index=data.index, name=f"{name}_prob"
        )

    regime_df = pd.concat(regime_probs.values(), axis=1)
    regime_df.attrs["ordered_mu"] = ordered_mu
    return regime_df, ordered_mu


def zscore(series: pd.Series) -> pd.Series:
    """Standardise une série (utilisé pour les indicateurs avancés)."""
    mean = series.mean()
    std = series.std()
    if std == 0 or math.isnan(std):
        std = 1.0
    return (series - mean) / std


def combine_indicators(panel: pd.DataFrame) -> pd.Series:
    """
    Construit un signal composite à partir des indicateurs avancés.

    Les séries retenues sont directement disponibles dans le panel :
    - `us_ism_manufacturing`
    - `us_michigan_sentiment`
    - `us_initial_claims` (que l’on inverse car une hausse = détérioration)
    - `us_nfp_change`

    Chaque composante est standardisée (z-score) puis on les moyenne.
    On retourne une série temporelle prête à passer dans le filtre de Kalman.
    """
    components = {
        "ism": panel.get("us_ism_manufacturing"),
        "sentiment": panel.get("us_michigan_sentiment"),
        "claims": panel.get("us_initial_claims"),
        "nfp": panel.get("us_nfp_change"),
    }
    df = pd.concat(components, axis=1)
    df = df.dropna(how="all")
    if df.empty:
        raise ValueError("Impossible de construire le panier (données manquantes).")

    df["claims"] = -df["claims"]  # plus de chômage -> signal négatif
    zdf = df.apply(zscore)
    combo = zdf.mean(axis=1)
    combo.name = "combo_signal"
    return combo.dropna()


def kalman_filter(observations: Iterable[float], q: float = 0.02, r: float = 0.15):
    """
    Filtre de Kalman scalaire avec état latent suivant une marche aléatoire.
    q : variance du bruit de processus (réactivité vs lissage)
    r : variance du bruit d’observation
    """
    x = 0.0  # estimate
    P = 1.0  # variance
    for y in observations:
        # prédiction
        P_pred = P + q
        x_pred = x
        # mise à jour
        K = P_pred / (P_pred + r)
        x = x_pred + K * (y - x_pred)
        P = (1 - K) * P_pred
        yield x


def build_kalman_prob(signal: pd.Series) -> pd.Series:
    """
    Applique le filtre de Kalman au signal composite et transforme l’état latent
    lissé en probabilité via une logistique. On obtient `kalman_prob`.
    """
    signal = signal.dropna()
    filt_values = list(kalman_filter(signal.values))
    state = pd.Series(filt_values, index=signal.index, name="kalman_state")
    state_norm = zscore(state)
    prob = 1 / (1 + np.exp(-state_norm))
    prob.name = "kalman_prob"
    return prob


def main() -> None:
    """
    Pipeline principal :
    1) Charge le panel
    2) Estime le Markov (4 régimes) et resample en fin de mois
    3) Calcule le Kalman
    4) Fusionne les probabilités (Markov/Kalman/blend)
    5) Exporte un CSV avec toutes les colonnes utiles
    """
    panel = load_panel()
    monthly = panel.resample("ME").last()

    # Markov sur PIB QoQ (quarterly)
    gdp = panel["us_gdp_qoq"].dropna()
    regime_probs, regime_mu = estimate_markov_probs(gdp)
    regime_monthly = regime_probs.resample("ME").ffill()
    cycle_phase = regime_monthly.idxmax(axis=1).rename("cycle_phase")
    recession_col = regime_monthly.get("recession_prob")
    if recession_col is None:
        recession_col = pd.Series(0.0, index=regime_monthly.index)
    ralentissement_col = regime_monthly.get("ralentissement_prob")
    if ralentissement_col is None:
        ralentissement_col = pd.Series(0.0, index=regime_monthly.index)
    # Probabilité “stress” = récession + moitié du ralentissement (croissance faible).
    markov_prob = (recession_col + 0.5 * ralentissement_col).rename("markov_prob")

    # Kalman sur signaux avancés
    combo = combine_indicators(monthly)
    kalman_prob = build_kalman_prob(combo)

    # Fusion des probabilités
    combined_index = monthly.index.union(markov_prob.index).union(kalman_prob.index)
    regime_aligned = regime_monthly.reindex(combined_index).ffill()
    cycle_aligned = cycle_phase.reindex(combined_index).ffill()
    markov_aligned = markov_prob.reindex(combined_index).ffill()
    kalman_aligned = kalman_prob.reindex(combined_index).ffill()
    # Blend : pondération 0,6/0,4 + terme d’interaction pour amplifier
    # lorsque les deux signaux s’allument simultanément.
    base = 0.6 * markov_aligned + 0.4 * kalman_aligned
    interaction = markov_aligned * kalman_aligned
    blended = (base + interaction).clip(0, 1)
    blended.name = "blended_prob"

    out_df = pd.concat(
        [
            regime_aligned,
            cycle_aligned,
            markov_aligned,
            kalman_aligned,
            blended,
        ],
        axis=1,
    ).dropna(subset=["markov_prob", "kalman_prob", "blended_prob"])
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUTPUT_PATH, index_label="date")
    print(f"Probabilités enregistrées dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

