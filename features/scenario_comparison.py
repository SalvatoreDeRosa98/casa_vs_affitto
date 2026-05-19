# =============================================================================
# SCENARIO COMPARISON — Casa vs Affitto
# Salvataggio e confronto di scenari calcolati
# =============================================================================

import pandas as pd
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Scenario:
    """Rappresenta uno scenario salvato."""
    nome: str
    citta: str
    mq: int
    prezzo_mq: float
    affitto_mens: float
    tasso_mutuo: float
    anticipo_perc: float
    anni_mutuo: int
    rendimento_etf: float
    rivalutazione: float
    regime_label: str
    regime_fiscale: str
    breakeven_anno: int | None
    rata_mensile: float


def crea_scenario(
    nome: str,
    citta: str,
    mq: int,
    prezzo_mq: float,
    affitto_mens: float,
    tasso_mutuo: float,
    anticipo_perc: float,
    anni_mutuo: int,
    rendimento_etf: float,
    rivalutazione: float,
    regime_label: str,
    regime_fiscale: str,
    result: dict,
) -> Scenario:
    """
    Crea uno scenario dai parametri attuali.

    Args:
        nome: Nome descrittivo dello scenario
        citta: Città
        mq: Superficie
        prezzo_mq: Prezzo al mq
        affitto_mens: Affitto mensile
        tasso_mutuo: Tasso mutuo (%)
        anticipo_perc: Anticipo (%)
        anni_mutuo: Durata mutuo
        rendimento_etf: Rendimento ETF (%)
        rivalutazione: Rivalutazione immobile (%)
        regime_label: Etichetta regime fiscale
        regime_fiscale: Chiave regime fiscale
        result: Dizionario risultati calcolo

    Returns:
        Scenario: Oggetto scenario
    """
    return Scenario(
        nome=nome,
        citta=citta,
        mq=mq,
        prezzo_mq=prezzo_mq,
        affitto_mens=affitto_mens,
        tasso_mutuo=tasso_mutuo,
        anticipo_perc=anticipo_perc,
        anni_mutuo=anni_mutuo,
        rendimento_etf=rendimento_etf,
        rivalutazione=rivalutazione,
        regime_label=regime_label,
        regime_fiscale=regime_fiscale,
        breakeven_anno=result.get("breakeven_anno"),
        rata_mensile=result.get("rata_mensile"),
    )


def compare_scenarios(scenarios: List[Scenario]) -> pd.DataFrame:
    """
    Crea un dataframe di confronto tra scenari.

    Args:
        scenarios: Lista di scenari

    Returns:
        pd.DataFrame: Tabella comparativa
    """
    if not scenarios:
        return pd.DataFrame()

    data = []
    for s in scenarios:
        be_label = f"{s.breakeven_anno} anni" if s.breakeven_anno else ">40 anni"
        data.append({
            "Scenario": s.nome,
            "Città": s.citta,
            "mq": s.mq,
            "Prezzo €/mq": f"{s.prezzo_mq:,.0f}",
            "Affitto €/mese": f"{s.affitto_mens:,.0f}",
            "Rata €/mese": f"{s.rata_mensile:,.0f}",
            "Tasso mutuo": f"{s.tasso_mutuo}%",
            "Anticipo": f"{s.anticipo_perc}%",
            "Durata mutuo": f"{s.anni_mutuo} anni",
            "Rendimento ETF": f"{s.rendimento_etf}%",
            "Rivalutazione": f"{s.rivalutazione}%",
            "Break-even": be_label,
        })

    return pd.DataFrame(data)
