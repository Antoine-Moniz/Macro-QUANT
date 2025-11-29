"""
Ingestion des indicateurs Bloomberg exportés dans l'Excel
`Indices_Bloomberg_Macro données.xlsx`.

Sorties :
    - data/processed/macro_panel.parquet : panel temporel des séries.
    - data/processed/macro_metadata.csv : métadonnées (pilier, fréquence, etc.).

Hypothèses :
    - Chaque feuille (sauf 'Dashboard') contient deux colonnes (dates, valeurs).
    - Les données démarrent en ligne 3 avec dates en colonne A et valeurs en colonne B.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXCEL_PATH = ROOT / "Indices_Bloomberg_Macro données.xlsx"
PROCESSED_DIR = ROOT / "data" / "processed"


@dataclass
class SeriesMeta:
    sheet_name: str
    series_id: str
    description: str
    pillar: str
    frequency: str
    transformation: str = "niveau"
    source: str = "Bloomberg"


PILLAR_MAP: Dict[str, SeriesMeta] = {
    "ECB Main Refinancing Rate": SeriesMeta(
        sheet_name="ECB Main Refinancing Rate",
        series_id="ecb_main_refi",
        description="Taux directeur BCE principal",
        pillar="Politique monétaire",
        frequency="Mensuel",
    ),
    "Italy Manufacturing Confidence": SeriesMeta(
        sheet_name="Italy Manufacturing Confidence",
        series_id="it_manufacturing_confidence",
        description="Confiance manufacturière Italie",
        pillar="Entreprises",
        frequency="Mensuel",
    ),
    "France Manufacturing PMI": SeriesMeta(
        sheet_name="France Manufacturing PMI",
        series_id="fr_manufacturing_pmi",
        description="PMI manufacturier France",
        pillar="Entreprises",
        frequency="Mensuel",
    ),
    "Germany IFO Business Climate": SeriesMeta(
        sheet_name="Germany IFO Business Climate",
        series_id="de_ifo_business_climate",
        description="Climat des affaires IFO Allemagne",
        pillar="Entreprises",
        frequency="Mensuel",
    ),
    "Japan Jobless Rate": SeriesMeta(
        sheet_name="Japan Jobless Rate",
        series_id="jp_jobless_rate",
        description="Taux de chômage Japon",
        pillar="Consommateurs / Marché du travail",
        frequency="Mensuel",
    ),
    "US FOMC Rate Decision (Upper Bo": SeriesMeta(
        sheet_name="US FOMC Rate Decision (Upper Bo",
        series_id="us_fed_funds_upper",
        description="Fourchette haute Fed Funds",
        pillar="Politique monétaire",
        frequency="Mensuel",
    ),
    "US Univ. of Michigan Sentiment": SeriesMeta(
        sheet_name="US Univ. of Michigan Sentiment",
        series_id="us_michigan_sentiment",
        description="Sentiment des consommateurs (U. Michigan)",
        pillar="Consommateurs",
        frequency="Mensuel",
    ),
    "EC Economic Sentiment Indicator": SeriesMeta(
        sheet_name="EC Economic Sentiment Indicator",
        series_id="ea_economic_sentiment",
        description="Indice de sentiment économique zone euro",
        pillar="Entreprises",
        frequency="Mensuel",
    ),
    "France CPI YoY": SeriesMeta(
        sheet_name="France CPI YoY",
        series_id="fr_cpi_yoy",
        description="Inflation annuelle France",
        pillar="Inflation",
        frequency="Mensuel",
        transformation="variation annuelle",
    ),
    "US Change in Nonfarm Payrolls": SeriesMeta(
        sheet_name="US Change in Nonfarm Payrolls",
        series_id="us_nfp_change",
        description="Variation mensuelle des emplois NFP",
        pillar="Marché du travail",
        frequency="Mensuel",
    ),
    "Japan Industrial Production MoM": SeriesMeta(
        sheet_name="Japan Industrial Production MoM",
        series_id="jp_industrial_production_mom",
        description="Production industrielle Japon (MoM)",
        pillar="Entreprises",
        frequency="Mensuel",
        transformation="variation mensuelle",
    ),
    "US Initial Jobless Claims": SeriesMeta(
        sheet_name="US Initial Jobless Claims",
        series_id="us_initial_claims",
        description="Nouvelles demandes d'allocations chômage",
        pillar="Marché du travail",
        frequency="Hebdomadaire",
    ),
    "US CPI MoM": SeriesMeta(
        sheet_name="US CPI MoM",
        series_id="us_cpi_mom",
        description="Inflation mensuelle US",
        pillar="Inflation",
        frequency="Mensuel",
        transformation="variation mensuelle",
    ),
    "US ISM Manufacturing PMI": SeriesMeta(
        sheet_name="US ISM Manufacturing PMI",
        series_id="us_ism_manufacturing",
        description="PMI manufacturier ISM",
        pillar="Entreprises",
        frequency="Mensuel",
    ),
    "EA CPI YoY (HICP)": SeriesMeta(
        sheet_name="EA CPI YoY (HICP)",
        series_id="ea_cpi_yoy",
        description="Inflation harmonisée zone euro",
        pillar="Inflation",
        frequency="Mensuel",
        transformation="variation annuelle",
    ),
    "US GDP Annualized QoQ": SeriesMeta(
        sheet_name="US GDP Annualized QoQ",
        series_id="us_gdp_qoq",
        description="PIB annualisé QoQ US",
        pillar="Croissance",
        frequency="Trimestriel",
    ),
    "Germany ZEW Expectations": SeriesMeta(
        sheet_name="Germany ZEW Expectations",
        series_id="de_zew_expectations",
        description="Expectations ZEW Allemagne",
        pillar="Entreprises",
        frequency="Mensuel",
    ),
    "Japan GDP SA QoQ": SeriesMeta(
        sheet_name="Japan GDP SA QoQ",
        series_id="jp_gdp_qoq",
        description="PIB Japon (QoQ SA)",
        pillar="Croissance",
        frequency="Trimestriel",
    ),
}


def slugify(name: str) -> str:
    """Convertit un nom de feuille en identifiant snake_case."""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def load_sheet(xls: pd.ExcelFile, sheet: str) -> pd.Series:
    """Lit une feuille (dates en colonne A, valeurs en colonne B)."""
    df = xls.parse(
        sheet,
        skiprows=2,
        header=None,
        usecols="A:B",
        names=["date", "value"],
    )
    df = df.dropna(subset=["date"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    series = pd.to_numeric(df["value"], errors="coerce")
    return series


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable : {EXCEL_PATH}")

    xls = pd.ExcelFile(EXCEL_PATH)
    panel: List[pd.Series] = []
    metadata_rows: List[dict] = []

    for sheet in xls.sheet_names:
        if sheet.lower().startswith("dashboard"):
            continue
        series = load_sheet(xls, sheet)
        if series.empty:
            continue
        meta = PILLAR_MAP.get(
            sheet,
            SeriesMeta(
                sheet_name=sheet,
                series_id=slugify(sheet),
                description=sheet,
                pillar="Autre",
                frequency="Inconnue",
            ),
        )
        series.name = meta.series_id
        panel.append(series)
        metadata_rows.append(meta.__dict__)

    if not panel:
        raise RuntimeError("Aucune série valide détectée dans le classeur.")

    panel_df = pd.concat(panel, axis=1).sort_index()
    panel_df.to_parquet(PROCESSED_DIR / "macro_panel.parquet")
    pd.DataFrame(metadata_rows).to_csv(
        PROCESSED_DIR / "macro_metadata.csv", index=False
    )
    print(
        f"Ingestion terminée : {len(panel_df.columns)} séries, "
        f"{panel_df.shape[0]} dates."
    )


if __name__ == "__main__":
    main()



