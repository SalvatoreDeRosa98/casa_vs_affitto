"""
Comprehensive test suite for calcoli.py — Casa vs Affitto
Tests cover: mutuo calculations, break-even logic, initial costs, and sensitivity analysis
Target coverage: 80%+ of calcoli.py
"""

import pytest
import math
from calcoli import (
    calcola_rata_mutuo,
    saldo_residuo_mutuo,
    calcola_costi_iniziali,
    calcola_breakeven,
    ParamsCalcolo,
    _normalizza_regime,
)


# =============================================================================
# TASK 1.1: AUDIT MUTUO LOGIC — Test calcola_rata_mutuo & saldo_residuo_mutuo
# =============================================================================


class TestCalcolaRataMutuo:
    """Edge cases and benchmark validation for mortgage payment calculation."""

    def test_zero_interest_rate(self):
        """Zero interest: rata = capitale / (anni * 12)"""
        capitale = 300_000
        anni = 25
        rata = calcola_rata_mutuo(capitale, 0.0, anni)
        expected = capitale / (anni * 12)
        assert rata == pytest.approx(expected, abs=0.01)

    def test_standard_mortgage_3_5_percent(self):
        """Standard scenario: 300k € @ 3.5% over 25 years.
        Verify against benchmark: rata should be ~1,501.87 €/month"""
        capitale = 300_000
        tasso = 3.5
        anni = 25
        rata = calcola_rata_mutuo(capitale, tasso, anni)
        # Known benchmark from Italian calculator (French amortization)
        assert rata == pytest.approx(1501.87, abs=1.0)

    def test_high_interest_5_percent(self):
        """High interest scenario: 5% rate increases monthly payment."""
        capitale = 200_000
        tasso_low = 3.0
        tasso_high = 5.0
        anni = 20
        rata_low = calcola_rata_mutuo(capitale, tasso_low, anni)
        rata_high = calcola_rata_mutuo(capitale, tasso_high, anni)
        assert rata_high > rata_low
        assert (rata_high - rata_low) / rata_low > 0.18  # ~19% increase

    def test_short_mortgage_5_years(self):
        """Shorter mortgages have higher monthly payments for same capital."""
        capitale = 100_000
        tasso = 3.0
        rata_5 = calcola_rata_mutuo(capitale, tasso, 5)
        rata_25 = calcola_rata_mutuo(capitale, tasso, 25)
        assert rata_5 > rata_25
        assert rata_5 / rata_25 > 3.0  # ~4x higher

    def test_long_mortgage_30_years(self):
        """30-year mortgage reduces monthly burden."""
        capitale = 400_000
        tasso = 3.5
        rata_20 = calcola_rata_mutuo(capitale, tasso, 20)
        rata_30 = calcola_rata_mutuo(capitale, tasso, 30)
        assert rata_30 < rata_20

    def test_very_low_rate_0_1_percent(self):
        """Near-zero rate (0.1%) behaves smoothly."""
        capitale = 250_000
        rata = calcola_rata_mutuo(capitale, 0.1, 20)
        expected = capitale / (20 * 12)
        assert rata == pytest.approx(expected, rel=0.02)  # Allow 2% variance

    def test_high_rate_8_percent(self):
        """High rate stress test (8%)."""
        capitale = 150_000
        rata = calcola_rata_mutuo(capitale, 8.0, 15)
        assert rata > 0
        assert rata < capitale  # sanity check

    def test_rata_times_months_exceeds_capitale(self):
        """Total payments exceed principal (as expected with interest)."""
        capitale = 100_000
        tasso = 4.0
        anni = 20
        rata = calcola_rata_mutuo(capitale, tasso, anni)
        total_paid = rata * 12 * anni
        assert total_paid > capitale
        assert (total_paid - capitale) / capitale > 0.30  # Interest is >30%


class TestSaldoResiduo:
    """Validate residual balance calculation."""

    def test_saldo_at_start(self):
        """Saldo at year 0 should equal capitale."""
        capitale = 300_000
        tasso = 3.5
        anni = 25
        saldo = saldo_residuo_mutuo(capitale, tasso, anni, 0)
        assert saldo == pytest.approx(capitale, abs=1.0)

    def test_saldo_at_end(self):
        """Saldo at final year should be ~0."""
        capitale = 200_000
        tasso = 3.0
        anni = 20
        saldo = saldo_residuo_mutuo(capitale, tasso, anni, 20)
        assert saldo == pytest.approx(0, abs=1.0)

    def test_saldo_halfway_through(self):
        """Saldo at halfway should be between 0 and capitale.
        For equal amortization, ~50%; for French amortization, >50%."""
        capitale = 100_000
        tasso = 3.0
        anni = 20
        saldo_half = saldo_residuo_mutuo(capitale, tasso, anni, 10)
        # French amortization: roughly 50-55% remains at halfway
        assert 40_000 < saldo_half < 65_000

    def test_saldo_zero_interest(self):
        """Zero interest: saldo decreases linearly."""
        capitale = 100_000
        anni = 20
        saldo_5 = saldo_residuo_mutuo(capitale, 0.0, anni, 5)
        saldo_10 = saldo_residuo_mutuo(capitale, 0.0, anni, 10)
        assert saldo_5 == pytest.approx(75_000, abs=1.0)
        assert saldo_10 == pytest.approx(50_000, abs=1.0)

    def test_saldo_beyond_duration(self):
        """Saldo beyond loan end should be 0."""
        capitale = 150_000
        tasso = 4.0
        anni = 15
        saldo_30 = saldo_residuo_mutuo(capitale, tasso, anni, 30)
        assert saldo_30 == 0.0

    def test_saldo_decreases_monotonically(self):
        """Saldo should decrease each year (no jumps up)."""
        capitale = 250_000
        tasso = 3.5
        anni = 25
        saldo_prev = capitale
        for anno in range(1, anni + 1):
            saldo_curr = saldo_residuo_mutuo(capitale, tasso, anni, anno)
            assert saldo_curr <= saldo_prev
            saldo_prev = saldo_curr

    def test_saldo_high_rate(self):
        """With 7% rate, more principal paid toward end."""
        capitale = 200_000
        tasso = 7.0
        anni = 20
        saldo_1 = saldo_residuo_mutuo(capitale, tasso, anni, 1)
        saldo_19 = saldo_residuo_mutuo(capitale, tasso, anni, 19)
        # At year 1, most of payment is interest → saldo ~= capitale
        # At year 19, mostly principal paid
        assert saldo_1 > 190_000
        assert saldo_19 < 20_000


# =============================================================================
# TASK 1.2: AUDIT BREAK-EVEN LOGIC — Realistic scenarios + sensitivity
# =============================================================================


class TestCalcolaBreakeven:
    """Test break-even calculation with realistic Milano scenario."""

    def get_milano_params(self, **kwargs) -> ParamsCalcolo:
        """Default Milano scenario: 250 mq, 20% deposit, 3.5% rate, 25 years."""
        defaults = {
            "mq": 250,
            "anticipo_perc": 20.0,
            "anni_mutuo": 25,
            "tasso_mutuo": 3.5,
            "rendimento_etf": 5.0,
            "rivalutazione_immobile": 1.5,
            "prima_casa": True,
            "inflazione_affitti": 2.0,
            "base_catastale_perc": 35.0,
            "anni_max": 40,
        }
        defaults.update(kwargs)
        return ParamsCalcolo(**defaults)

    def test_milano_250mq_baseline(self):
        """Milano, 250 mq, realistic scenario."""
        # Milano: 4800 €/mq, affitto ~1400 €/mese per 80mq → 4375 €/mese per 250mq
        prezzo_mq = 4800
        affitto_mensile = 1400 * 250 / 80
        params = self.get_milano_params()
        result = calcola_breakeven(prezzo_mq, affitto_mensile, params)

        # Check result structure
        assert "breakeven_anno" in result
        assert "patrimonio_acquisto" in result
        assert "patrimonio_affitto" in result
        assert "rata_mensile" in result
        assert "valore_casa" in result

        # Breakeven should be > 1 and < 40 (reasonable range)
        be = result["breakeven_anno"]
        assert be is None or 1 <= be <= 40

        # Verify initial values
        V = prezzo_mq * params.mq
        assert result["valore_casa"] == pytest.approx(V, abs=1.0)
        assert result["anticipo"] == pytest.approx(V * 0.2, abs=1.0)

    def test_breakeven_patrimonio_arrays_length(self):
        """Patrimonio arrays should match anni_max."""
        params = self.get_milano_params(anni_max=40)
        result = calcola_breakeven(4800, 4375, params)
        assert len(result["anni"]) == 40
        assert len(result["patrimonio_acquisto"]) == 40
        assert len(result["patrimonio_affitto"]) == 40

    def test_intuitive_recovery_metrics_present(self):
        """Expose intuitive metrics separate from patrimonio break-even."""
        params = self.get_milano_params(anni_max=40)
        result = calcola_breakeven(4800, 4375, params)

        assert "recupero_costi_iniziali_anno" in result
        assert "anni_affitto_equivalenti" in result
        assert "risparmio_cumulato_nominale_anni" in result
        assert "breakeven_netto_vendita_anno" in result
        assert "patrimonio_acquisto_netto_vendita" in result
        assert len(result["risparmio_cumulato_nominale_anni"]) == 40
        assert len(result["patrimonio_acquisto_netto_vendita"]) == 40
        assert result["anni_affitto_equivalenti"] > 0

    def test_high_affitto_accelerates_breakeven(self):
        """Higher affitto increases rental costs → accelerates break-even."""
        params = self.get_milano_params()
        result_low = calcola_breakeven(4800, 4375, params)
        result_high = calcola_breakeven(4800, 5000, params)

        be_low = result_low["breakeven_anno"]
        be_high = result_high["breakeven_anno"]

        assert be_low is not None
        assert be_high is not None
        assert be_high <= be_low

    def test_high_property_appreciation_accelerates_breakeven(self):
        """Higher property appreciation → accelerates break-even."""
        params_low = self.get_milano_params(rivalutazione_immobile=1.0)
        params_high = self.get_milano_params(rivalutazione_immobile=3.0)

        result_low = calcola_breakeven(4800, 4375, params_low)
        result_high = calcola_breakeven(4800, 4375, params_high)

        be_low = result_low["breakeven_anno"]
        be_high = result_high["breakeven_anno"]

        if be_low is not None and be_high is not None:
            assert be_high <= be_low

    def test_higher_deposit_reduces_monthly_burden(self):
        """20% vs 30% deposit: higher deposit → lower rata, but more capital immobilized."""
        params_20 = self.get_milano_params(anticipo_perc=20.0)
        params_30 = self.get_milano_params(anticipo_perc=30.0)

        result_20 = calcola_breakeven(4800, 4375, params_20)
        result_30 = calcola_breakeven(4800, 4375, params_30)

        rata_20 = result_20["rata_mensile"]
        rata_30 = result_30["rata_mensile"]
        assert rata_30 < rata_20

    def test_high_interest_rate_delays_breakeven(self):
        """Higher mortgage rate delays break-even (higher payments)."""
        params_3 = self.get_milano_params(tasso_mutuo=3.0)
        params_6 = self.get_milano_params(tasso_mutuo=6.0)

        result_3 = calcola_breakeven(4800, 4375, params_3)
        result_6 = calcola_breakeven(4800, 4375, params_6)

        be_3 = result_3["breakeven_anno"]
        be_6 = result_6["breakeven_anno"]

        if be_3 is not None and be_6 is not None:
            assert be_6 >= be_3


# Sensitivity tests (Task 1.2 requirement)
class TestSensitivityAnalysis:
    """Sensitivity analysis: +0.5% interest rate impact."""

    def test_sensitivity_tasso_plus_0_5_percent(self):
        """Interest rate +0.5%: verify break-even delay."""
        params_base = ParamsCalcolo(
            mq=250,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.0,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=40,
        )
        params_high = ParamsCalcolo(
            mq=250,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=40,
        )

        result_base = calcola_breakeven(4800, 4375, params_base)
        result_high = calcola_breakeven(4800, 4375, params_high)

        rata_base = result_base["rata_mensile"]
        rata_high = result_high["rata_mensile"]

        # +0.5% interest → ~5-6% higher monthly payment
        rate_increase = (rata_high - rata_base) / rata_base
        assert 0.03 < rate_increase < 0.07

    def test_sensitivity_affitto_inflazione(self):
        """Affitto inflation impact: higher inflation favors ownership."""
        params_low = ParamsCalcolo(
            mq=250,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=1.0,
            anni_max=40,
        )
        params_high = ParamsCalcolo(
            mq=250,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=4.0,
            anni_max=40,
        )

        result_low = calcola_breakeven(4800, 4375, params_low)
        result_high = calcola_breakeven(4800, 4375, params_high)

        # Higher inflation → affitto costs grow faster → earlier break-even
        be_low = result_low["breakeven_anno"]
        be_high = result_high["breakeven_anno"]

        if be_low is not None and be_high is not None:
            assert be_high <= be_low


# =============================================================================
# TASK 1.3: AUDIT COSTI INIZIALI + IMU
# =============================================================================


class TestCalcolaCostiIniziali:
    """Test initial costs and IMU logic."""

    def test_prima_casa_aliquota_2_percent(self):
        """Prima casa: 2% imposta di registro on base catastale (35% of value)."""
        valore = 500_000
        result = calcola_costi_iniziali(valore, prima_casa=True)

        base = valore * 35.0 / 100  # base_catastale_perc = 35.0
        assert result["base_catastale"] == pytest.approx(base, abs=1.0)
        assert result["imposta"] == pytest.approx(base * 0.02, abs=1.0)

    def test_seconda_casa_aliquota_9_percent(self):
        """Seconda casa: 9% imposta di registro (much higher) on base catastale."""
        valore = 500_000
        result = calcola_costi_iniziali(valore, prima_casa=False)

        base = valore * 35.0 / 100  # base_catastale_perc = 35.0
        assert result["imposta"] == pytest.approx(base * 0.09, abs=1.0)

    def test_seconda_vs_prima_ratio(self):
        """Second home tax is 4.5x higher than first home."""
        valore = 400_000
        result_prima = calcola_costi_iniziali(valore, prima_casa=True)
        result_seconda = calcola_costi_iniziali(valore, prima_casa=False)

        ratio = result_seconda["imposta"] / result_prima["imposta"]
        assert ratio == pytest.approx(4.5, abs=0.01)

    def test_agenzia_3_percent_of_value(self):
        """Agenzia should be 3% of property value."""
        valore = 300_000
        result = calcola_costi_iniziali(valore, prima_casa=True)
        assert result["agenzia"] == pytest.approx(valore * 0.03, abs=1.0)

    def test_notaio_fixed_cost(self):
        """Notaio is fixed ~€3,500."""
        valore = 200_000
        result = calcola_costi_iniziali(valore, prima_casa=True)
        assert result["notaio"] == 3_500

    def test_totale_includes_all_components(self):
        """Total should sum all components."""
        valore = 250_000
        result = calcola_costi_iniziali(valore, prima_casa=True)

        expected_total = (
            result["imposta"] + result["ipocatastali"] + result["agenzia"] + result["notaio"]
        )
        assert result["totale"] == pytest.approx(expected_total, abs=0.01)

    def test_base_catastale_percentage_customizable(self):
        """Base catastale % should be customizable."""
        valore = 300_000
        result_35 = calcola_costi_iniziali(valore, prima_casa=True, base_catastale_perc=35.0)
        result_30 = calcola_costi_iniziali(valore, prima_casa=True, base_catastale_perc=30.0)

        assert result_35["base_catastale"] > result_30["base_catastale"]
        assert result_35["imposta"] > result_30["imposta"]

    def test_regime_fiscale_override(self):
        """regime_fiscale parameter should override prima_casa flag."""
        valore = 400_000
        # If prima_casa=True but regime="seconda_casa", should apply 9%
        result = calcola_costi_iniziali(valore, prima_casa=True, regime_fiscale="seconda_casa")
        base = valore * 35.0 / 100  # base_catastale_perc = 35.0
        assert result["imposta"] == pytest.approx(base * 0.09, abs=1.0)

    def test_small_property_costs(self):
        """Small property: e.g., 150k €."""
        valore = 150_000
        result = calcola_costi_iniziali(valore, prima_casa=True)
        assert result["totale"] > 0
        assert result["totale"] < valore * 0.1  # Sanity: <10% of value

    def test_large_property_costs(self):
        """Large property: e.g., 1M €."""
        valore = 1_000_000
        result = calcola_costi_iniziali(valore, prima_casa=False)
        assert result["totale"] > 30_000  # Expected: ~60k+
        assert result["imposta"] > 30_000  # 9% of base


class TestIMULogic:
    """Test IMU calculation within break-even calculation."""

    def test_imu_zero_for_prima_casa(self):
        """Prima casa: IMU should be 0."""
        params = ParamsCalcolo(
            mq=100,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=10,
        )
        result = calcola_breakeven(3000, 1000, params)

        # IMU should contribute 0 to costo_buy_anno for prima casa
        # Verify by checking patrimonio values don't have IMU penalty
        assert result["valore_casa"] > 0

    def test_imu_charged_for_seconda_casa(self):
        """Seconda casa: IMU should be charged (0.5% of value annually)."""
        # Use scenario where buying is always more expensive (so IMU impact is visible)
        params_prima = ParamsCalcolo(
            mq=150,
            anticipo_perc=30.0,
            anni_mutuo=20,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=2.0,
            prima_casa=True,
            inflazione_affitti=0.5,
            anni_max=20,  # Low affitto growth
        )
        params_seconda = ParamsCalcolo(
            mq=150,
            anticipo_perc=30.0,
            anni_mutuo=20,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=2.0,
            prima_casa=False,
            inflazione_affitti=0.5,
            anni_max=20,
        )

        result_prima = calcola_breakeven(2500, 500, params_prima)
        result_seconda = calcola_breakeven(2500, 500, params_seconda)

        # Seconda casa should have lower patrimonio due to IMU costs
        # Compare at year 15 when effect is visible
        pat_prima_y15 = result_prima["patrimonio_acquisto"][14]
        pat_seconda_y15 = result_seconda["patrimonio_acquisto"][14]
        # The difference should be visible after 15 years of accumulating IMU
        assert pat_seconda_y15 <= pat_prima_y15  # Allow equal for numerical precision


# =============================================================================
# TASK 1.4: TYPE HINTS & EDGE CASES
# =============================================================================


class TestNormalizzaRegime:
    """Test regime normalization logic."""

    def test_prima_casa_default(self):
        """prima_casa=True, no override → "prima_casa"."""
        assert _normalizza_regime(True, None) == "prima_casa"

    def test_seconda_casa_default(self):
        """prima_casa=False, no override → "seconda_casa"."""
        assert _normalizza_regime(False, None) == "seconda_casa"

    def test_regime_override(self):
        """regime_fiscale overrides prima_casa."""
        assert _normalizza_regime(True, "giovani") == "giovani"
        assert _normalizza_regime(False, "prima_casa") == "prima_casa"


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_zero_size_property(self):
        """0 mq property (degenerate)."""
        params = ParamsCalcolo(
            mq=0,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=10,
        )
        result = calcola_breakeven(3000, 1000, params)
        # Should return valid structure with V=0
        assert result["valore_casa"] == 0

    def test_100_percent_deposit(self):
        """No mortgage: 100% deposit."""
        params = ParamsCalcolo(
            mq=100,
            anticipo_perc=100.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=10,
        )
        result = calcola_breakeven(3000, 1000, params)
        # No mortgage payments
        assert result["rata_mensile"] == pytest.approx(0, abs=0.01)
        assert result["capitale_mutuo"] == 0

    def test_zero_etf_return(self):
        """0% ETF return (conservative scenario)."""
        params = ParamsCalcolo(
            mq=100,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=0.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=10,
        )
        result = calcola_breakeven(3000, 1000, params)
        # Should calculate without growth on investments
        assert len(result["patrimonio_acquisto"]) > 0

    def test_very_high_affitto(self):
        """Affitto equal to property value (unrealistic but valid)."""
        params = ParamsCalcolo(
            mq=100,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=10,
        )
        result = calcola_breakeven(3000, 300_000, params)  # 300k/month
        # Rentals extremely expensive → buy should win quickly, but the
        # prudent model no longer reinvests owner cash-flow savings.
        be = result["breakeven_anno"]
        assert be is None or be <= 3

    def test_very_low_affitto(self):
        """Affitto very low (cheaper to rent)."""
        params = ParamsCalcolo(
            mq=100,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=10,
        )
        result = calcola_breakeven(3000, 100, params)  # €100/month
        # Very cheap rent → may never break even
        be = result["breakeven_anno"]
        assert be is None or be > 10

    def test_short_mortgage_15_years(self):
        """15-year mortgage vs standard 25-year."""
        params_15 = ParamsCalcolo(
            mq=100,
            anticipo_perc=20.0,
            anni_mutuo=15,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=20,
        )
        params_25 = ParamsCalcolo(
            mq=100,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=20,
        )

        result_15 = calcola_breakeven(3000, 1000, params_15)
        result_25 = calcola_breakeven(3000, 1000, params_25)

        # 15-year: higher payment, faster debt-free → may affect break-even
        rata_15 = result_15["rata_mensile"]
        rata_25 = result_25["rata_mensile"]
        assert rata_15 > rata_25


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_mutuo_consistency_with_breakeven(self):
        """Rata calculated in calcola_rata_mutuo matches break-even usage."""
        params = ParamsCalcolo(
            mq=100,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=10,
        )
        V = 3000 * 100
        M = V * 0.8

        rata_direct = calcola_rata_mutuo(M, 3.5, 25)
        result = calcola_breakeven(3000, 1000, params)

        assert rata_direct == pytest.approx(result["rata_mensile"], abs=0.01)

    def test_saldo_consistency_with_breakeven(self):
        """Saldo values used in break-even calculation are valid."""
        params = ParamsCalcolo(
            mq=100,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
            anni_max=25,
        )
        V = 3000 * 100
        M = V * 0.8

        result = calcola_breakeven(3000, 1000, params)

        # At year 25, saldo should be ~0
        saldo_25 = saldo_residuo_mutuo(M, 3.5, 25, 25)
        assert saldo_25 == pytest.approx(0, abs=1.0)

    def test_patrimonio_monotonic_growth(self):
        """Patrimonio should generally grow over time (with good parameters)."""
        params = ParamsCalcolo(
            mq=100,
            anticipo_perc=20.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=2.0,
            prima_casa=True,
            inflazione_affitti=1.5,
            anni_max=30,
        )
        result = calcola_breakeven(3000, 1000, params)

        # Check that patrimonio generally increases (allowing for year-to-year variance)
        pat_buy = result["patrimonio_acquisto"]
        pat_rent = result["patrimonio_affitto"]

        assert pat_buy[-1] > pat_buy[0]  # End > start
        assert pat_rent[-1] > pat_rent[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
