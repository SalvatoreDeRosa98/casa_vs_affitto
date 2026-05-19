"""Integration tests for casa_vs_affitto calculator."""
from calcoli import (
    ParamsCalcolo,
    calcola_breakeven,
    calcola_tutti_breakeven,
    calcola_costi_iniziali,
    calcola_rata_mutuo,
    saldo_residuo_mutuo,
)


class TestCalcolaRataMutuo:
    """Test mortgage payment calculation."""

    def test_rata_mutuo_positive_rate(self):
        """Test monthly payment with positive interest rate."""
        # 100k loan, 3% annual, 20 years = ~554 EUR/month
        rata = calcola_rata_mutuo(100_000, 3.0, 20)
        assert 550 < rata < 560
        assert rata > 0

    def test_rata_mutuo_zero_rate(self):
        """Test monthly payment with zero interest (installment only)."""
        # 100k loan, 0% annual, 20 years = 100000 / 240 = 416.67
        rata = calcola_rata_mutuo(100_000, 0.0, 20)
        assert abs(rata - 100_000 / 240) < 0.01

    def test_rata_mutuo_high_rate(self):
        """Test monthly payment with high interest rate."""
        rata_3pct = calcola_rata_mutuo(100_000, 3.0, 20)
        rata_5pct = calcola_rata_mutuo(100_000, 5.0, 20)
        assert rata_5pct > rata_3pct


class TestSaldoResiduoMutuo:
    """Test remaining mortgage balance calculation."""

    def test_saldo_residuo_initially_full(self):
        """After 0 years, saldo = total loan."""
        saldo = saldo_residuo_mutuo(100_000, 3.0, 20, 0)
        assert abs(saldo - 100_000) < 1

    def test_saldo_residuo_after_completion(self):
        """After 20 years, saldo = 0."""
        saldo = saldo_residuo_mutuo(100_000, 3.0, 20, 20)
        assert saldo < 1

    def test_saldo_residuo_beyond_duration(self):
        """After duration exceeded, saldo = 0."""
        saldo = saldo_residuo_mutuo(100_000, 3.0, 20, 25)
        assert saldo == 0.0

    def test_saldo_residuo_after_completion_zero_rate(self):
        """After duration, saldo = 0 (zero rate case)."""
        saldo = saldo_residuo_mutuo(100_000, 0.0, 20, 20)
        assert saldo <= 0.01

    def test_saldo_residuo_midway(self):
        """After 10 years of 20-year loan, saldo is between 0 and initial."""
        saldo = saldo_residuo_mutuo(100_000, 3.0, 20, 10)
        assert 0 < saldo < 100_000

    def test_saldo_residuo_monotonic_decrease(self):
        """Remaining balance decreases over time."""
        balances = [saldo_residuo_mutuo(100_000, 3.0, 20, year) for year in range(0, 21)]
        for i in range(len(balances) - 1):
            assert balances[i] >= balances[i + 1]


class TestCalcolaCostiIniziali:
    """Test initial purchase costs calculation."""

    def test_costi_iniziali_prima_casa(self):
        """Test costs for primary residence."""
        costi = calcola_costi_iniziali(300_000, prima_casa=True)
        assert costi["totale"] > 0
        assert costi["imposta"] > 0
        assert costi["agenzia"] == 300_000 * 0.03
        assert costi["base_catastale"] == 300_000 * 0.35

    def test_costi_iniziali_seconda_casa(self):
        """Test costs for second home (higher tax)."""
        costi_prima = calcola_costi_iniziali(300_000, prima_casa=True)
        costi_seconda = calcola_costi_iniziali(300_000, prima_casa=False)
        # Second home has higher tax (9% vs 2%)
        assert costi_seconda["totale"] > costi_prima["totale"]
        assert costi_seconda["imposta"] > costi_prima["imposta"]

    def test_costi_iniziali_regime_giovani(self):
        """Test costs with giovani (young) regime."""
        costi = calcola_costi_iniziali(300_000, prima_casa=True, regime_fiscale="giovani")
        # Giovani has same tax as prima_casa ordinaria (2%)
        costi_ordinaria = calcola_costi_iniziali(300_000, prima_casa=True)
        assert abs(costi["totale"] - costi_ordinaria["totale"]) < 1


class TestCalcolaBreakeven:
    """Integration tests for full breakeven calculation."""

    def test_breakeven_basic_scenario(self, params_default: ParamsCalcolo, provincia_milano: dict):
        """Test basic buy vs rent scenario (Milano)."""
        prezzo_mq = provincia_milano["prezzo_mq"]
        affitto_mensile = provincia_milano["affitto_80mq"] * params_default.mq / 80

        result = calcola_breakeven(prezzo_mq, affitto_mensile, params_default)

        # Check structure
        assert "breakeven_anno" in result
        assert "anni" in result
        assert "patrimonio_acquisto" in result
        assert "patrimonio_affitto" in result
        assert "rata_mensile" in result
        assert "capitale_iniziale" in result

        # Check data validity
        assert len(result["anni"]) == params_default.anni_max
        assert len(result["patrimonio_acquisto"]) == params_default.anni_max
        assert len(result["patrimonio_affitto"]) == params_default.anni_max
        assert result["rata_mensile"] > 0
        assert result["capitale_iniziale"] > 0

    def test_breakeven_patrimonio_grows(
        self, params_default: ParamsCalcolo, provincia_milano: dict
    ):
        """Both patrimonio series should grow over time."""
        prezzo_mq = provincia_milano["prezzo_mq"]
        affitto_mensile = provincia_milano["affitto_80mq"] * params_default.mq / 80

        result = calcola_breakeven(prezzo_mq, affitto_mensile, params_default)

        patrimonio_buy = result["patrimonio_acquisto"]
        patrimonio_rent = result["patrimonio_affitto"]

        # Should be generally increasing (with possible small fluctuations)
        assert patrimonio_buy[-1] > patrimonio_buy[0]
        assert patrimonio_rent[-1] > patrimonio_rent[0]

    def test_breakeven_high_mortgage_rate(
        self, params_default: ParamsCalcolo, provincia_milano: dict
    ):
        """High mortgage rate delays breakeven."""
        prezzo_mq = provincia_milano["prezzo_mq"]
        affitto_mensile = provincia_milano["affitto_80mq"] * params_default.mq / 80

        # Normal scenario
        result_normal = calcola_breakeven(prezzo_mq, affitto_mensile, params_default)
        breakeven_normal = result_normal["breakeven_anno"] or params_default.anni_max + 1

        # High rate scenario
        params_high_rate = ParamsCalcolo(
            mq=params_default.mq,
            anticipo_perc=params_default.anticipo_perc,
            anni_mutuo=params_default.anni_mutuo,
            tasso_mutuo=5.5,  # Higher rate
            rendimento_etf=params_default.rendimento_etf,
            rivalutazione_immobile=params_default.rivalutazione_immobile,
            prima_casa=params_default.prima_casa,
            inflazione_affitti=params_default.inflazione_affitti,
        )
        result_high_rate = calcola_breakeven(prezzo_mq, affitto_mensile, params_high_rate)
        breakeven_high_rate = result_high_rate["breakeven_anno"] or params_default.anni_max + 1

        # Higher rate should delay or prevent breakeven
        assert breakeven_high_rate >= breakeven_normal

    def test_breakeven_low_rent_scenario(
        self, params_default: ParamsCalcolo, provincia_milano: dict
    ):
        """Test scenario where rent is better (very low affitto)."""
        prezzo_mq = provincia_milano["prezzo_mq"]
        # Artificially low rent
        affitto_mensile = 300.0

        result = calcola_breakeven(prezzo_mq, affitto_mensile, params_default)

        # With very low rent, breakeven might not occur within 40 years
        # or occur much later
        breakeven = result["breakeven_anno"]
        if breakeven:
            assert breakeven > 25  # Should be quite late

    def test_breakeven_risparmio_affitto(
        self, params_default: ParamsCalcolo, provincia_milano: dict
    ):
        """Test risparmio affitto scenario (rent much higher than purchase costs)."""
        prezzo_mq = provincia_milano["prezzo_mq"]
        # Very high rent (>80% more than normal)
        affitto_mensile = 1600.0

        result = calcola_breakeven(prezzo_mq, affitto_mensile, params_default)

        # With high rent, should reach breakeven earlier
        breakeven = result["breakeven_anno"]
        if breakeven:
            assert breakeven < 20

    def test_breakeven_regime_seconda_casa(
        self, params_seconda_casa: ParamsCalcolo, provincia_milano: dict
    ):
        """Test breakeven with second home regime (higher taxes/IMU)."""
        prezzo_mq = provincia_milano["prezzo_mq"]
        affitto_mensile = provincia_milano["affitto_80mq"] * params_seconda_casa.mq / 80

        result_prima = calcola_breakeven(
            prezzo_mq,
            affitto_mensile,
            ParamsCalcolo(
                mq=80,
                anticipo_perc=20,
                anni_mutuo=25,
                tasso_mutuo=3.5,
                rendimento_etf=5.0,
                rivalutazione_immobile=1.5,
                prima_casa=True,
                inflazione_affitti=2.0,
                regime_fiscale="prima_casa",
            ),
        )

        result_seconda = calcola_breakeven(prezzo_mq, affitto_mensile, params_seconda_casa)

        # Second home has higher initial costs and annual IMU
        assert result_seconda["capitale_iniziale"] > result_prima["capitale_iniziale"]

    def test_breakeven_different_mq(self, params_default: ParamsCalcolo, provincia_milano: dict):
        """Test breakeven scales with property size."""
        prezzo_mq = provincia_milano["prezzo_mq"]

        # 80 mq
        affitto_80 = provincia_milano["affitto_80mq"]
        result_80 = calcola_breakeven(prezzo_mq, affitto_80, params_default)

        # 100 mq
        params_100 = ParamsCalcolo(
            mq=100,
            anticipo_perc=params_default.anticipo_perc,
            anni_mutuo=params_default.anni_mutuo,
            tasso_mutuo=params_default.tasso_mutuo,
            rendimento_etf=params_default.rendimento_etf,
            rivalutazione_immobile=params_default.rivalutazione_immobile,
            prima_casa=params_default.prima_casa,
            inflazione_affitti=params_default.inflazione_affitti,
        )
        affitto_100 = provincia_milano["affitto_80mq"] * 100 / 80
        result_100 = calcola_breakeven(prezzo_mq, affitto_100, params_100)

        # Values should scale proportionally
        assert result_100["valore_casa"] > result_80["valore_casa"]
        assert result_100["rata_mensile"] > result_80["rata_mensile"]


class TestCalcolaTuttiBreakveen:
    """Test multi-province calculation."""

    def test_calcola_tutti_breakeven(self, params_default: ParamsCalcolo):
        """Test calculation across all provinces."""
        df = calcola_tutti_breakeven(params_default)

        # Check structure
        assert len(df) > 0
        assert "citta" in df.columns
        assert "regione" in df.columns
        assert "breakeven_anno" in df.columns
        assert "prezzo_mq" in df.columns

        # Check data validity
        assert all(df["breakeven_anno"] > 0)
        assert all(df["prezzo_mq"] > 0)
        assert all(df["affitto_mensile"] > 0)
        assert all(df["rata_mensile"] > 0)

    def test_calcola_tutti_breakeven_sorted(self, params_default: ParamsCalcolo):
        """Result should be sorted by breakeven year."""
        df = calcola_tutti_breakeven(params_default)
        breakevens = df["breakeven_anno"].tolist()
        assert breakevens == sorted(breakevens)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_anticipo(self, provincia_milano: dict):
        """Test with 0% down payment (edge case)."""
        params = ParamsCalcolo(
            mq=80,
            anticipo_perc=0.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
        )
        result = calcola_breakeven(provincia_milano["prezzo_mq"], 800, params)
        assert result["anticipo"] == 0.0
        assert result["capitale_mutuo"] == result["valore_casa"]

    def test_100_anticipo(self, provincia_milano: dict):
        """Test with 100% down payment (no mortgage)."""
        params = ParamsCalcolo(
            mq=80,
            anticipo_perc=100.0,
            anni_mutuo=25,
            tasso_mutuo=3.5,
            rendimento_etf=5.0,
            rivalutazione_immobile=1.5,
            prima_casa=True,
            inflazione_affitti=2.0,
        )
        result = calcola_breakeven(provincia_milano["prezzo_mq"], 800, params)
        assert result["capitale_mutuo"] == 0.0
        assert result["rata_mensile"] == 0.0
