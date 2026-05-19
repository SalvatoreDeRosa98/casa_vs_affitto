# =============================================================================
# MOTORE DI CALCOLO — Casa vs Affitto  (v3 — confronto patrimoniale)
# =============================================================================
# Logica:
#
#   patrimonio_buy(t)  = equity_immobile(t) + investimenti_da_risparmi_buy(t)
#   patrimonio_rent(t) = capitale_iniziale_investito + investimenti_da_risparmi_rent(t)
#
#   dove equity(t) = valore_immobile(t) - saldo_residuo_mutuo(t)
#
#   Ogni anno si confrontano i flussi abitativi:
#     acquisto = rate + manutenzione + IMU
#     affitto  = canone annuo
#
#   Modello prudente:
#     - chi affitta investe capitale iniziale evitato e risparmi quando affittare costa meno
#     - chi compra non investe automaticamente il risparmio quando la rata/costi sono inferiori all'affitto
#   Break-even = primo anno in cui patrimonio_buy > patrimonio_rent.
# =============================================================================

from dataclasses import dataclass
import pandas as pd
from dati import PROVINCE


@dataclass
class ParamsCalcolo:
    mq: int
    anticipo_perc: float  # % del valore casa (es. 20)
    anni_mutuo: int  # durata mutuo (15/20/25/30)
    tasso_mutuo: float  # tasso annuo fisso % (es. 3.5)
    rendimento_etf: float  # rendimento annuo investimento % (es. 5.0)
    rivalutazione_immobile: float  # % rivalutazione annua immobile (es. 1.5)
    prima_casa: bool
    inflazione_affitti: float  # % crescita annua affitti (default 2.0)
    base_catastale_perc: float = 35.0  # % del prezzo usata come proxy del valore catastale
    regime_fiscale: str = "prima_casa"  # prima_casa, giovani, seconda_casa
    anni_max: int = 40
    manutenzione_perc: float = 1.5  # % annua del valore casa
    costo_vendita_perc: float = 4.0  # % del valore di vendita
    assicurazione_annua: float = 0.0
    condominio_extra_annuo: float = 0.0
    ristrutturazione_iniziale: float = 0.0
    inflazione_costi_annui: float = 2.0


# ── FUNZIONI BASE ─────────────────────────────────────────────────────────────


def calcola_rata_mutuo(capitale: float, tasso_annuo_perc: float, anni: int) -> float:
    """Rata mensile mutuo a tasso fisso — formula ammortamento francese."""
    r = tasso_annuo_perc / 100 / 12
    n = anni * 12
    if r == 0:
        return capitale / n
    return capitale * r * (1 + r) ** n / ((1 + r) ** n - 1)


def saldo_residuo_mutuo(
    capitale: float, tasso_annuo_perc: float, anni_totali: int, anni_trascorsi: int
) -> float:
    """
    Saldo residuo del mutuo dopo anni_trascorsi anni.
    Formula: C*(1+r)^k − rata*((1+r)^k − 1)/r
    """
    if anni_trascorsi >= anni_totali:
        return 0.0
    r = tasso_annuo_perc / 100 / 12
    n = anni_totali * 12
    k = anni_trascorsi * 12
    if r == 0:
        return max(0.0, capitale * (1 - k / n))
    rata = calcola_rata_mutuo(capitale, tasso_annuo_perc, anni_totali)
    saldo = capitale * (1 + r) ** k - rata * ((1 + r) ** k - 1) / r
    return max(0.0, saldo)


def _normalizza_regime(prima_casa: bool, regime_fiscale: str | None = None) -> str:
    if regime_fiscale:
        return regime_fiscale
    return "prima_casa" if prima_casa else "seconda_casa"


def calcola_costi_iniziali(
    valore_casa: float,
    prima_casa: bool,
    regime_fiscale: str | None = None,
    base_catastale_perc: float = 35.0,
) -> dict:
    """
    Costi una-tantum acquisto:
      - Imposta di registro: 2% prima casa, 9% seconda casa
      - Giovani/under 36: scenario separato, oggi trattato come prima casa ordinaria
        lato imposte; l'effetto principale e' sulla garanzia mutuo, non modellata qui.
      - Agenzia: ~3%
      - Notaio + spese: ~3.500 €
    """
    regime = _normalizza_regime(prima_casa, regime_fiscale)
    aliquota = 0.09 if regime == "seconda_casa" else 0.02
    base_catastale = valore_casa * base_catastale_perc / 100
    imposta = base_catastale * aliquota
    ipocatastali = 100
    agenzia = valore_casa * 0.03
    notaio = 3_500
    return {
        "base_catastale": base_catastale,
        "base_catastale_perc": base_catastale_perc,
        "imposta": imposta,
        "ipocatastali": ipocatastali,
        "agenzia": agenzia,
        "notaio": notaio,
        "totale": imposta + ipocatastali + agenzia + notaio,
    }


# ── HELPER FUNCTIONS ────────────────────────────────────────────────────────────


def _calcola_costi_annuali(
    valore_attuale: float,
    abitazione_principale: bool,
    tasso_mutuo: float,
    anni_mutuo: int,
    capitale_mutuo: float,
    anno: int,
    manutenzione_perc: float = 1.0,
    assicurazione_annua: float = 0.0,
    condominio_extra_annuo: float = 0.0,
    inflazione_costi_annui: float = 2.0,
) -> float:
    """Calcola i costi annuali di mantenimento."""
    rata_mensile = calcola_rata_mutuo(capitale_mutuo, tasso_mutuo, anni_mutuo)
    rate_anno = rata_mensile * 12 if anno <= anni_mutuo else 0.0
    manutenzione = valore_attuale * manutenzione_perc / 100
    imu = valore_attuale * 0.005 if not abitazione_principale else 0.0
    crescita_costi = (1 + inflazione_costi_annui / 100) ** (anno - 1)
    costi_extra = (assicurazione_annua + condominio_extra_annuo) * crescita_costi
    return rate_anno + manutenzione + imu + costi_extra


# ── CALCOLO PRINCIPALE ────────────────────────────────────────────────────────


def calcola_breakeven(prezzo_mq: float, affitto_mensile: float, params: ParamsCalcolo) -> dict:
    """
    Calcola il break-even tra acquisto e affitto anno per anno.

    Il confronto e' patrimoniale: a parita' di capitale iniziale disponibile,
    comprare conviene quando il patrimonio netto del proprietario supera quello
    dell'inquilino che investe il capitale iniziale e i risparmi di cassa.

    Break-even = primo anno in cui patrimonio_buy > patrimonio_rent.
    """
    V = prezzo_mq * params.mq
    D = V * params.anticipo_perc / 100  # anticipo
    M = V - D  # capitale mutuo
    regime = _normalizza_regime(params.prima_casa, params.regime_fiscale)
    abitazione_principale = regime in ("prima_casa", "giovani")

    ci = calcola_costi_iniziali(V, params.prima_casa, regime, params.base_catastale_perc)
    rata = calcola_rata_mutuo(M, params.tasso_mutuo, params.anni_mutuo)
    totale_rate_mutuo = rata * 12 * params.anni_mutuo
    interessi_mutuo = totale_rate_mutuo - M

    g = params.rivalutazione_immobile / 100  # rivalutazione annua immobile
    r = params.rendimento_etf / 100  # rendimento ETF annuo
    inf_aff = params.inflazione_affitti / 100  # inflazione affitti

    capitale_iniziale = D + ci["totale"] + params.ristrutturazione_iniziale

    anni_list = []
    patrimoni_acquisto = []
    patrimoni_acquisto_netto_vendita = []
    patrimoni_affitto = []
    risparmi_cumulati = []
    breakeven = None
    breakeven_netto_vendita = None
    recupero_costi_iniziali = None
    risparmio_cumulato_nominale = 0.0

    # Chi affitta investe da subito la liquidita' che l'acquirente immobilizza.
    investimento_buy = 0.0
    investimento_rent = capitale_iniziale

    for anno in range(1, params.anni_max + 1):
        investimento_buy *= 1 + r
        investimento_rent *= 1 + r

        # ── ACQUISTO ─────────────────────────────────────────────────────────
        val_att = V * (1 + g) ** anno
        costo_buy_anno = _calcola_costi_annuali(
            val_att,
            abitazione_principale,
            params.tasso_mutuo,
            params.anni_mutuo,
            M,
            anno,
            params.manutenzione_perc,
            params.assicurazione_annua,
            params.condominio_extra_annuo,
            params.inflazione_costi_annui,
        )

        # Equity = valore rivalutato − saldo residuo mutuo
        saldo = saldo_residuo_mutuo(M, params.tasso_mutuo, params.anni_mutuo, anno)
        equity = val_att - saldo

        # ── AFFITTO ──────────────────────────────────────────────────────────
        # Affitto dell'anno corrente: il primo anno usa il canone attuale.
        costo_rent_anno = affitto_mensile * 12 * (1 + inf_aff) ** (anno - 1)

        differenza = costo_buy_anno - costo_rent_anno
        if differenza > 0:
            investimento_rent += differenza
        else:
            # Modello prudente: il risparmio di cassa del proprietario non viene
            # automaticamente reinvestito nel patrimonio. Lo tracciamo solo per
            # il grafico "recupero costi iniziali".
            risparmio_cumulato_nominale += -differenza

        if (
            recupero_costi_iniziali is None
            and risparmio_cumulato_nominale >= capitale_iniziale
        ):
            recupero_costi_iniziali = anno

        patrimonio_buy = equity + investimento_buy
        valore_netto_vendita = val_att * (1 - params.costo_vendita_perc / 100)
        patrimonio_buy_netto_vendita = valore_netto_vendita - saldo + investimento_buy
        patrimonio_rent = investimento_rent

        anni_list.append(anno)
        patrimoni_acquisto.append(patrimonio_buy)
        patrimoni_acquisto_netto_vendita.append(patrimonio_buy_netto_vendita)
        patrimoni_affitto.append(patrimonio_rent)
        risparmi_cumulati.append(risparmio_cumulato_nominale)

        if breakeven is None and patrimonio_buy > patrimonio_rent:
            breakeven = anno
        if (
            breakeven_netto_vendita is None
            and patrimonio_buy_netto_vendita > patrimonio_rent
        ):
            breakeven_netto_vendita = anno

    return {
        "breakeven_anno": breakeven,
        "breakeven_netto_vendita_anno": breakeven_netto_vendita,
        "anni": anni_list,
        "patrimonio_acquisto": patrimoni_acquisto,
        "patrimonio_acquisto_netto_vendita": patrimoni_acquisto_netto_vendita,
        "patrimonio_affitto": patrimoni_affitto,
        "risparmio_cumulato_nominale_anni": risparmi_cumulati,
        # Alias mantenuti per compatibilita' con eventuali chiamanti esterni.
        "costo_acquisto": patrimoni_acquisto,
        "costo_affitto": patrimoni_affitto,
        "rata_mensile": rata,
        "totale_rate_mutuo": totale_rate_mutuo,
        "interessi_mutuo": interessi_mutuo,
        "anticipo": D,
        "capitale_iniziale": capitale_iniziale,
        "recupero_costi_iniziali_anno": recupero_costi_iniziali,
        "anni_affitto_equivalenti": (
            capitale_iniziale / (affitto_mensile * 12) if affitto_mensile > 0 else None
        ),
        "risparmio_cumulato_nominale": risparmio_cumulato_nominale,
        "valore_casa": V,
        "costi_iniziali": ci,
        "ristrutturazione_iniziale": params.ristrutturazione_iniziale,
        "costo_vendita_perc": params.costo_vendita_perc,
        "manutenzione_perc": params.manutenzione_perc,
        "assicurazione_annua": params.assicurazione_annua,
        "condominio_extra_annuo": params.condominio_extra_annuo,
        "capitale_mutuo": M,
        "regime_fiscale": regime,
    }


def calcola_tutti_breakeven(params: ParamsCalcolo) -> pd.DataFrame:
    """Break-even per tutte le 107 province — usato da mappa e classifica."""
    righe = []
    for citta, dati in PROVINCE.items():
        affitto = dati["affitto_80mq"] * params.mq / 80
        res = calcola_breakeven(dati["prezzo_mq"], affitto, params)
        be = res["breakeven_anno"]
        righe.append(
            {
                "citta": citta,
                "regione": dati["regione"],
                "lat": dati["lat"],
                "lon": dati["lon"],
                "prezzo_mq": dati["prezzo_mq"],
                "affitto_mensile": affitto,
                "valore_casa": res["valore_casa"],
                "anticipo": res["anticipo"],
                "rata_mensile": res["rata_mensile"],
                "breakeven_anno": be if be else 99,
                "breakeven_label": f"{be} anni" if be else f">{params.anni_max} anni",
            }
        )
    return pd.DataFrame(righe).sort_values("breakeven_anno")
