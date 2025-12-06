"""Applique des chocs prospectifs aux indicateurs et recalcule les probabilités.

Ce module lit un fichier YAML décrivant un scénario (nom, description,
liste d'overrides), projette le panel macroéconomique dans le futur
afin de couvrir l'horizon demandé, applique les chocs uniquement sur les
dates strictement postérieures à la dernière observation historique,
puis calcule de nouveau les probabilités de cycle.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import yaml
from pandas.tseries.frequencies import to_offset

from recession_indicator import compute_cycle_probabilities, load_panel

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "data" / "processed" / "recession_prob.csv"
SCENARIO_OUTPUT_DIR = ROOT / "data" / "processed" / "scenarios"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exécuter un scénario macro.")
    parser.add_argument(
        "--config",
        required=True,
        type=Path,
        help="Chemin vers le fichier YAML du scénario",
    )
    return parser.parse_args()


def load_config(config_path: Path) -> Dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not config or "name" not in config:
        raise ValueError("Le fichier de config doit contenir un champ 'name'.")
    config.setdefault("description", "")
    overrides = config.get("overrides", [])
    if not isinstance(overrides, list):
        raise ValueError("Le champ 'overrides' doit être une liste.")
    config["overrides"] = overrides
    return config


def infer_frequency(index: pd.DatetimeIndex) -> str:
    freq = pd.infer_freq(index)
    if freq:
        return freq
    # Par défaut on projette en fréquence mensuelle (month-start).
    return "MS"


def extend_panel_for_future(panel: pd.DataFrame, overrides: List[Dict[str, Any]]) -> pd.DataFrame:
    if not overrides:
        return panel
    max_target_date = max(
        pd.to_datetime(rule.get("end", rule["start"])) for rule in overrides
    )
    last_hist_date = panel.index.max()
    if max_target_date <= last_hist_date:
        return panel
    freq = infer_frequency(panel.index)
    offset = to_offset(freq)
    future_index = pd.date_range(
        start=last_hist_date + offset,
        end=max_target_date,
        freq=freq,
    )
    if future_index.empty:
        return panel
    extended = (
        panel.reindex(panel.index.union(future_index))
        .sort_index()
        .ffill()
    )
    return extended


def apply_overrides(
    panel: pd.DataFrame,
    overrides: List[Dict[str, Any]],
    last_hist_date: pd.Timestamp,
) -> pd.DataFrame:
    updated = panel.copy()
    for rule in overrides:
        column = rule["column"]
        if column not in updated.columns:
            raise KeyError(f"Colonne inconnue dans le scénario: {column}")
        start = pd.to_datetime(rule["start"])
        end = pd.to_datetime(rule.get("end", start))
        mask = (updated.index >= start) & (updated.index <= end) & (updated.index > last_hist_date)
        if not mask.any():
            continue  # Les chocs passés sont ignorés automatiquement.
        if "value" in rule:
            updated.loc[mask, column] = rule["value"]
        elif "delta_pct" in rule:
            updated.loc[mask, column] = updated.loc[mask, column] * (1 + rule["delta_pct"])
        else:
            raise ValueError(f"Aucun champ 'value' ou 'delta_pct' pour la colonne {column}")
    return updated


def ensure_output_horizon(
    probs: pd.DataFrame,
    overrides: List[Dict[str, Any]],
    freq: str,
) -> pd.DataFrame:
    if not overrides:
        return probs
    max_target_date = max(
        pd.to_datetime(rule.get("end", rule["start"])) for rule in overrides
    )
    if max_target_date <= probs.index.max():
        return probs
    offset = to_offset(freq)
    future_index = pd.date_range(
        start=probs.index.max() + offset,
        end=max_target_date,
        freq=freq,
    )
    extended = (
        probs.reindex(probs.index.union(future_index))
        .sort_index()
        .ffill()
    )
    return extended


def load_baseline_probs(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Charge le CSV historique si disponible, sinon le régénère et le sauvegarde.
    """
    if BASELINE_PATH.exists():
        df = pd.read_csv(BASELINE_PATH, parse_dates=["date"])
        return df.set_index("date")
    baseline = compute_cycle_probabilities(panel)
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    baseline.to_csv(BASELINE_PATH, index_label="date")
    return baseline


def run_scenario(config_path: Path) -> Path:
    print("[run_scenario] démarrage")
    config = load_config(config_path)
    print(f"[run_scenario] config chargée ({config['name']})")
    overrides = config["overrides"]
    panel = load_panel()
    print(f"[run_scenario] panel chargé ({len(panel)} lignes)")
    baseline_probs = load_baseline_probs(panel)
    print(f"[run_scenario] baseline chargée ({len(baseline_probs)} lignes)")
    last_hist_obs = panel.index.max()
    hist_cutoff = baseline_probs.index.max()
    panel = extend_panel_for_future(panel, overrides)
    print("[run_scenario] panel étendu")
    panel_override = apply_overrides(panel, overrides, last_hist_obs)
    print("[run_scenario] overrides appliqués")
    probs = compute_cycle_probabilities(panel_override)
    print("[run_scenario] probabilités recalculées")
    future_probs = probs.loc[probs.index > hist_cutoff]
    combined = pd.concat([baseline_probs, future_probs], axis=0)
    combined = combined[~combined.index.duplicated(keep="last")].sort_index()
    hist_mask = combined.index <= hist_cutoff
    if hist_mask.any():
        baseline_aligned = baseline_probs.reindex(combined.index).ffill()
        combined.loc[hist_mask] = baseline_aligned.loc[hist_mask]
    freq = infer_frequency(combined.index)
    combined = ensure_output_horizon(combined, overrides, freq)
    print("[run_scenario] horizon assuré")

    SCENARIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SCENARIO_OUTPUT_DIR / f"scenario_{config['name']}.csv"
    combined.to_csv(output_path, index=True)
    print(f"[run_scenario] CSV écrit ({len(combined)} lignes)")

    print(
        f"Scénario '{config['name']}' sauvegardé dans {output_path} "
        f"(hist jusqu'au {hist_cutoff.date()}, overrides futurs uniquement)."
    )
    return output_path


def main() -> None:
    args = parse_args()
    run_scenario(args.config)


if __name__ == "__main__":
    main()

