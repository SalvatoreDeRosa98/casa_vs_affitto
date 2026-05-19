"""Pytest configuration and fixtures for casa_vs_affitto tests."""
import sys
from pathlib import Path

# Add parent directory to path so we can import calcoli, dati, etc.
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from calcoli import ParamsCalcolo


@pytest.fixture
def params_default() -> ParamsCalcolo:
    """Default parameters for testing."""
    return ParamsCalcolo(
        mq=80,
        anticipo_perc=20.0,
        anni_mutuo=25,
        tasso_mutuo=3.5,
        rendimento_etf=5.0,
        rivalutazione_immobile=1.5,
        prima_casa=True,
        inflazione_affitti=2.0,
        base_catastale_perc=35.0,
        regime_fiscale="prima_casa",
        anni_max=40,
    )


@pytest.fixture
def provincia_milano() -> dict:
    """Milano province data fixture."""
    return {
        "prezzo_mq": 7500.0,
        "affitto_80mq": 800.0,
        "regione": "Lombardia",
        "lat": 45.4642,
        "lon": 9.1900,
    }


@pytest.fixture
def params_giovani(params_default: ParamsCalcolo) -> ParamsCalcolo:
    """Parameters for young homebuyers (under 36)."""
    return ParamsCalcolo(
        mq=params_default.mq,
        anticipo_perc=params_default.anticipo_perc,
        anni_mutuo=params_default.anni_mutuo,
        tasso_mutuo=params_default.tasso_mutuo,
        rendimento_etf=params_default.rendimento_etf,
        rivalutazione_immobile=params_default.rivalutazione_immobile,
        prima_casa=True,
        inflazione_affitti=params_default.inflazione_affitti,
        base_catastale_perc=params_default.base_catastale_perc,
        regime_fiscale="giovani",
        anni_max=params_default.anni_max,
    )


@pytest.fixture
def params_seconda_casa(params_default: ParamsCalcolo) -> ParamsCalcolo:
    """Parameters for second home / investment."""
    return ParamsCalcolo(
        mq=params_default.mq,
        anticipo_perc=params_default.anticipo_perc,
        anni_mutuo=params_default.anni_mutuo,
        tasso_mutuo=params_default.tasso_mutuo,
        rendimento_etf=params_default.rendimento_etf,
        rivalutazione_immobile=params_default.rivalutazione_immobile,
        prima_casa=False,
        inflazione_affitti=params_default.inflazione_affitti,
        base_catastale_perc=params_default.base_catastale_perc,
        regime_fiscale="seconda_casa",
        anni_max=params_default.anni_max,
    )
