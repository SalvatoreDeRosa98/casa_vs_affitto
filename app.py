# =============================================================================
# APP STREAMLIT — "Casa o affitto? Il calcolatore della verità"
# Redesigned with modern dark UI + mobile responsiveness
# Autore: Salvatore De Rosa · 2026
# =============================================================================

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from dati import PROVINCE, get_lista_citta, get_market_data_meta
from calcoli import ParamsCalcolo, calcola_breakeven, calcola_tutti_breakeven
from features.export_pdf import genera_report_pdf
from features.scenario_comparison import crea_scenario, compare_scenarios

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Casa o affitto? — Il calcolatore della verità",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SESSION STATE INITIALIZATION ──────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "scenarios" not in st.session_state:
    st.session_state.scenarios = []

if "scenario_name_input" not in st.session_state:
    st.session_state.scenario_name_input = ""

# ── COLOR PALETTE (MODERN DARK + LIGHT) ───────────────────────────────────────
# Dark mode
C_DARK_BG      = "#0B1F33"
C_DARK_CARD    = "#102A43"
C_DARK_TEXT    = "#F8FAFC"
C_ACCENT_GOLD  = "#0A66C2"
C_SUCCESS      = "#16803C"
C_DANGER       = "#D93025"
C_WARNING      = "#F5A623"
C_BORDER_DARK  = "#26445F"

# Legacy color aliases (for compatibility with plot code)
C_DARK         = "#111827"  # Dark
C_RED          = "#D93025"  # Red/danger
C_GREEN        = "#16803C"  # Green/success
C_AMBER        = C_WARNING
C_WHITE        = "#FFFFFF"  # White
C_CREAM        = "#F3F6F8"  # LinkedIn-like page background

# Light mode (secondary)
C_LIGHT_BG     = "#F3F6F8"
C_LIGHT_CARD   = "#FFFFFF"
C_LIGHT_TEXT   = "#172B4D"
C_BORDER_LIGHT = "#D9E2EC"

REGIMI_FISCALI = {
    "Prima casa ordinaria": {
        "key": "prima_casa",
        "prima_casa": True,
        "note": "Registro stimato al 2%, nessuna IMU se abitazione principale non di lusso.",
    },
    "Prima casa giovani": {
        "key": "giovani",
        "prima_casa": True,
        "note": "Nel 2026 le imposte sono simulate come prima casa ordinaria; la garanzia mutuo under 36 non e' modellata.",
    },
    "Seconda casa / investimento": {
        "key": "seconda_casa",
        "prima_casa": False,
        "note": "Registro stimato al 9% e IMU annua stimata allo 0,5% del valore rivalutato.",
    },
}

# ── THEME-AWARE COLORS ────────────────────────────────────────────────────────
def get_colors():
    """Returns color scheme based on dark_mode state."""
    if st.session_state.dark_mode:
        return {
            "bg": C_DARK_BG,
            "card": C_DARK_CARD,
            "text": C_DARK_TEXT,
            "text_muted": "rgba(230, 237, 243, 0.6)",
            "border": C_BORDER_DARK,
            "accent": C_ACCENT_GOLD,
        }
    else:
        return {
            "bg": C_LIGHT_BG,
            "card": C_LIGHT_CARD,
            "text": C_LIGHT_TEXT,
            "text_muted": "rgba(31, 41, 55, 0.6)",
            "border": C_BORDER_LIGHT,
            "accent": C_ACCENT_GOLD,
        }

# ── MODERN CSS ─────────────────────────────────────────────────────────────────
colors = get_colors()
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=Crimson+Pro:ital,wght@0,700;1,400;1,700&display=swap');

* {{ box-sizing: border-box; }}

#MainMenu, footer, header {{ visibility: hidden; }}

html, body, .stApp {{
    background-color: {C_CREAM};
    color: {colors['text']};
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

.block-container {{
    max-width: 1180px;
    padding-top: 1.25rem;
}}

/* Hero Section — Modern Gradient + Typography */
.hero {{
    background: {C_WHITE};
    color: {C_DARK};
    padding: 2.4rem 2.2rem;
    margin: 0 0 1.5rem;
    border-radius: 8px;
    border: 1px solid {C_BORDER_LIGHT};
    border-top: 5px solid {C_ACCENT_GOLD};
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
    position: relative;
    overflow: hidden;
}}

.hero::before {{
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 38%;
    height: 100%;
    background: linear-gradient(135deg, rgba(10, 102, 194, 0.10), rgba(10, 102, 194, 0.02));
    pointer-events: none;
}}

.hero-content {{
    position: relative;
    z-index: 1;
}}

.hero-tag {{
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {C_ACCENT_GOLD};
    margin-bottom: 0.9rem;
}}

.hero-h1 {{
    font-size: clamp(2rem, 4vw, 3.4rem);
    font-weight: 900;
    line-height: 1.05;
    margin: 0 0 1rem;
    color: {C_DARK};
    letter-spacing: 0;
}}

.hero-h1 em {{
    font-family: 'Crimson Pro', Georgia, serif;
    font-style: italic;
    font-weight: 700;
    color: {C_ACCENT_GOLD};
    font-size: 1.05em;
}}

.hero-sub {{
    font-size: 1rem;
    color: #43566B;
    margin: 0 0 1.5rem;
    line-height: 1.65;
    max-width: 780px;
}}

.hero-brand {{
    font-size: 0.9rem;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    font-style: normal;
    color: {C_ACCENT_GOLD};
    display: inline-block;
}}

.sb-logo {{
    color: {C_DARK};
    font-size: 1.45rem;
    font-weight: 900;
    line-height: 1;
    margin: 0.25rem 0 0.35rem;
}}

.sb-logo span {{
    color: {C_ACCENT_GOLD};
}}

.sec-h {{
    color: {C_DARK};
    font-size: clamp(1.35rem, 2.3vw, 2rem);
    font-weight: 900;
    line-height: 1.12;
    margin: 1.8rem 0 0.25rem;
    letter-spacing: 0;
}}

.sec-h em {{
    color: {C_ACCENT_GOLD};
    font-family: 'Crimson Pro', Georgia, serif;
    font-style: italic;
    font-weight: 700;
}}

.sec-sub {{
    color: #61758A;
    display: block;
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
    text-transform: uppercase;
}}

.mc {{
    background: {C_WHITE};
    border: 1px solid {C_BORDER_LIGHT};
    border-radius: 8px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    min-height: 138px;
    padding: 1rem;
}}

.mc-lbl {{
    color: #61758A;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    margin: 0 0 0.55rem;
    text-transform: uppercase;
}}

.mc-val {{
    color: {C_DARK};
    font-size: clamp(1.35rem, 2vw, 1.85rem);
    font-weight: 900;
    line-height: 1.08;
    margin: 0 0 0.45rem;
}}

.mc-sub {{
    color: #61758A;
    font-size: 0.78rem;
    line-height: 1.35;
    margin: 0;
}}

.mc-green .mc-val {{ color: {C_GREEN}; }}
.mc-amber .mc-val {{ color: {C_WARNING}; }}
.mc-red .mc-val {{ color: {C_RED}; }}

.driver-grid {{
    display: grid;
    gap: 0.75rem;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    margin: 0.8rem 0 1.1rem;
}}

.driver-card {{
    background: {C_WHITE};
    border: 1px solid {C_BORDER_LIGHT};
    border-radius: 8px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
    min-height: 118px;
    padding: 1rem;
}}

.driver-card strong {{
    color: {C_DARK};
    display: block;
    font-size: 0.86rem;
    font-weight: 900;
    margin-bottom: 0.4rem;
}}

.driver-card p {{
    color: #61758A;
    font-size: 0.82rem;
    line-height: 1.45;
    margin: 0;
}}

.driver-buy {{
    border-top: 3px solid {C_GREEN};
}}

.driver-rent {{
    border-top: 3px solid {C_RED};
}}

.driver-neutral {{
    border-top: 3px solid {C_ACCENT_GOLD};
}}

.cfr-wrap {{
    align-items: stretch;
    display: grid;
    gap: 0.8rem;
    grid-template-columns: 1fr auto 1fr;
    margin: 1rem 0 0.4rem;
}}

.cfr-card {{
    border-radius: 8px;
    padding: 1.35rem;
    min-height: 190px;
}}

.cfr-dark {{
    background: {C_DARK};
    color: {C_WHITE};
    border: 1px solid {C_DARK};
}}

.cfr-light {{
    background: {C_WHITE};
    color: {C_DARK};
    border: 1px solid {C_BORDER_LIGHT};
}}

.cfr-city {{
    color: {C_ACCENT_GOLD};
    font-size: 0.72rem;
    font-weight: 900;
    letter-spacing: 0.1em;
    margin: 0 0 0.55rem;
    text-transform: uppercase;
}}

.cfr-val {{
    font-size: clamp(2rem, 3vw, 3rem);
    font-weight: 900;
    line-height: 1;
    margin: 0 0 0.9rem;
}}

.cfr-sub {{
    color: inherit;
    font-size: 0.84rem;
    line-height: 1.5;
    margin: 0.25rem 0;
    opacity: 0.78;
}}

.cfr-arrow {{
    align-self: center;
    background: {C_ACCENT_GOLD};
    border-radius: 999px;
    color: {C_WHITE};
    font-weight: 900;
    height: 34px;
    line-height: 34px;
    text-align: center;
    width: 34px;
}}

/* Metric Cards — Clean & Modern */
.metric-card {{
    background: {colors['card']};
    border: 1px solid {colors['border']};
    border-radius: 12px;
    padding: 1.5rem;
    height: 100%;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}}

.metric-card:hover {{
    border-color: {C_ACCENT_GOLD};
    box-shadow: 0 4px 12px rgba(242, 193, 78, 0.1);
    transform: translateY(-2px);
}}

.metric-label {{
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: {colors['text_muted']};
    margin-bottom: 0.8rem;
}}

.metric-value {{
    font-size: clamp(1.5rem, 3vw, 2.2rem);
    font-weight: 900;
    color: {colors['text']};
    line-height: 1.2;
    margin-bottom: 0.5rem;
}}

.metric-sub {{
    font-size: 12px;
    color: {colors['text_muted']};
    font-weight: 500;
}}

.metric-card.success .metric-value {{ color: {C_SUCCESS}; }}
.metric-card.warning .metric-value {{ color: {C_WARNING}; }}
.metric-card.danger .metric-value {{ color: {C_DANGER}; }}

/* Section Headers */
.section-title {{
    font-size: clamp(1.5rem, 3vw, 2rem);
    font-weight: 800;
    color: {colors['text']};
    margin: 2.5rem 0 0.5rem;
    line-height: 1.2;
}}

.section-title em {{
    font-family: 'Crimson Pro', Georgia, serif;
    font-style: italic;
    font-weight: 400;
    color: {C_ACCENT_GOLD};
}}

.section-subtitle {{
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {colors['text_muted']};
    margin-bottom: 1.5rem;
    display: block;
}}

/* Input Card Container */
.input-card {{
    background: {colors['card']};
    border: 1px solid {colors['border']};
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}}

.input-section-title {{
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {colors['text']};
    margin-bottom: 1rem;
    display: block;
}}

/* Comparison Cards */
.comparison-wrap {{
    display: flex;
    align-items: stretch;
    gap: 1.5rem;
    margin: 2rem 0;
    flex-wrap: wrap;
}}

.comparison-card {{
    flex: 1;
    min-width: 280px;
    border-radius: 12px;
    padding: 2rem;
    border: 1px solid {colors['border']};
}}

.comparison-card.primary {{
    background: linear-gradient(135deg, {C_DARK_BG} 0%, {C_DARK_CARD} 100%);
    color: {colors['text']};
}}

.comparison-card.secondary {{
    background: {colors['card']};
    color: {colors['text']};
}}

.comparison-city {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: {C_ACCENT_GOLD};
    margin-bottom: 0.5rem;
}}

.comparison-value {{
    font-size: 2.5rem;
    font-weight: 900;
    line-height: 1.1;
    margin: 0.5rem 0 1rem;
}}

.comparison-sub {{
    font-size: 13px;
    color: {colors['text_muted']};
    line-height: 1.6;
    margin-bottom: 0.5rem;
}}

/* Chart Container */
.chart-container {{
    background: {colors['card']};
    border: 1px solid {colors['border']};
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
}}

/* Sidebar Styling */
[data-testid="stSidebar"] {{
    background-color: {C_WHITE};
    border-right: 1px solid {C_BORDER_LIGHT};
}}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    color: {C_DARK};
}}

.sidebar-brand {{
    font-size: 1.6rem;
    font-weight: 900;
    font-family: 'Crimson Pro', Georgia, serif;
    font-style: italic;
    color: {colors['text']};
    margin-bottom: 0.3rem;
}}

.sidebar-brand span {{ color: {C_ACCENT_GOLD}; }}

/* Tabs */
.stTabs [data-baseweb="tab"] {{
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {colors['text_muted']};
}}

.stTabs [aria-selected="true"] {{
    color: {C_ACCENT_GOLD};
}}

.stButton > button,
.stDownloadButton > button {{
    background: {C_WHITE};
    border-radius: 999px;
    border: 1px solid {C_ACCENT_GOLD};
    color: {C_DARK};
    font-weight: 800;
}}

.stButton > button:hover,
.stDownloadButton > button:hover {{
    background: {C_ACCENT_GOLD};
    border-color: {C_ACCENT_GOLD};
    color: {C_WHITE};
}}

.stButton > button *,
.stDownloadButton > button * {{
    color: inherit;
}}

/* Expander */
.streamlit-expanderHeader {{
    background-color: {C_WHITE};
    color: {C_DARK};
    font-weight: 800;
}}

[data-testid="stExpander"] {{
    background: {C_WHITE};
    border: 1px solid {C_BORDER_LIGHT};
    border-radius: 8px;
}}

[data-testid="stExpander"] [data-testid="stMarkdownContainer"],
[data-testid="stExpander"] p,
[data-testid="stExpander"] label,
[data-testid="stExpander"] span {{
    color: {C_DARK};
}}

[data-testid="stExpander"] [data-testid="stWidgetLabel"] p {{
    color: {C_DARK};
    font-weight: 800;
}}

[data-testid="stExpander"] [data-baseweb="select"] > div {{
    background-color: {C_WHITE};
    border-color: {C_BORDER_LIGHT};
    color: {C_DARK};
}}

[data-testid="stExpander"] [data-baseweb="select"] span {{
    color: {C_DARK};
}}

/* Info boxes */
.info-box {{
    background: {colors['card']};
    border-left: 4px solid {C_ACCENT_GOLD};
    border-radius: 8px;
    padding: 1.2rem;
    margin: 1.5rem 0;
}}

/* Responsive Design */
@media (max-width: 1200px) {{
    .hero {{ padding: 3rem 1.5rem; }}
    .hero-h1 {{ font-size: clamp(1.7rem, 3vw, 2.5rem); }}
    .comparison-wrap {{ gap: 1rem; }}
}}

@media (max-width: 768px) {{
    .driver-grid {{
        grid-template-columns: 1fr;
    }}

    .hero {{ padding: 2rem 1rem; margin: 0 0 1.25rem; border-radius: 8px; }}
    .hero-h1 {{ font-size: clamp(1.5rem, 2.5vw, 2rem); }}
    .hero-sub {{ font-size: 0.95rem; }}
    .section-title {{ font-size: clamp(1.2rem, 2.5vw, 1.6rem); }}
    .metric-value {{ font-size: clamp(1.3rem, 2.5vw, 1.8rem); }}
    .comparison-wrap {{ flex-direction: column; gap: 1rem; }}
    .comparison-card {{ min-width: 100%; }}
    .comparison-value {{ font-size: 2rem; }}
    .cfr-wrap {{ grid-template-columns: 1fr; }}
    .cfr-arrow {{ justify-self: center; transform: rotate(90deg); }}
}}

@media (max-width: 600px) {{
    .hero {{ padding: 2rem 1rem; }}
    .hero::before {{ width: 300px; height: 300px; }}
    .hero-h1 {{ font-size: 1.4rem; margin-bottom: 0.8rem; }}
    .hero-sub {{ font-size: 0.9rem; margin-bottom: 1rem; }}
    .hero-tag {{ margin-bottom: 1rem; }}
    .metric-card {{ padding: 1.2rem; }}
    .metric-value {{ font-size: 1.5rem; }}
    .input-card {{ padding: 1rem; }}
    .section-title {{ font-size: 1.3rem; margin: 2rem 0 0.5rem; }}
}}

</style>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown('<div class="sb-logo">città<span>.</span></div>', unsafe_allow_html=True)
    st.caption("Casa o affitto? Il calcolatore della verità.")
    st.divider()

    citta_list = get_lista_citta()
    default_idx = citta_list.index("Milano") if "Milano" in citta_list else 0
    citta = st.selectbox("📍 La tua città", citta_list, index=default_idx)

    mq = st.slider("📐 Superficie (mq)", 40, 200, 80, 5)
    dati_default_sidebar = PROVINCE[citta]

    st.divider()
    st.markdown("**🏷️ Valori immobile**")
    usa_valori_manual = st.toggle(
        "Uso prezzo e affitto reali",
        value=False,
        help="Attiva se conosci il prezzo della casa e/o l'affitto mensile reale. Il calcolo usera' questi valori invece della media della citta'.",
    )
    prezzo_mq_manual = None
    affitto_mens_manual = None
    if usa_valori_manual:
        prezzo_totale_default = int(dati_default_sidebar["prezzo_mq"] * mq)
        affitto_default = int(dati_default_sidebar["affitto_80mq"] * mq / 80)
        prezzo_totale_manual = st.number_input(
            "Prezzo casa (€)",
            min_value=10_000,
            max_value=5_000_000,
            value=prezzo_totale_default,
            step=5_000,
            help="Prezzo totale richiesto o offerto per l'immobile.",
        )
        affitto_mens_manual = st.number_input(
            "Affitto mensile (€)",
            min_value=100,
            max_value=20_000,
            value=affitto_default,
            step=50,
            help="Canone mensile reale per un immobile comparabile.",
        )
        prezzo_mq_manual = prezzo_totale_manual / mq
        st.caption(f"Valori usati: {prezzo_mq_manual:,.0f} €/mq acquisto · {affitto_mens_manual / mq:,.2f} €/mq/mese affitto")

    st.divider()
    st.markdown("**💰 Parametri mutuo**")
    anticipo_perc = st.slider("Anticipo (%)", 10, 50, 20, 5)
    anni_mutuo    = st.select_slider("Durata mutuo (anni)", [15, 20, 25, 30], value=25)
    tasso_mutuo   = st.slider("Tasso fisso (%)", 1.0, 7.0, 3.5, 0.1)
    regime_label  = st.selectbox("Regime fiscale", list(REGIMI_FISCALI.keys()), index=0)
    regime_info   = REGIMI_FISCALI[regime_label]
    regime_fiscale = regime_info["key"]
    prima_casa    = regime_info["prima_casa"]
    st.caption(regime_info["note"])
    base_catastale_default = 40 if regime_fiscale == "seconda_casa" else 35
    base_catastale_perc = st.slider(
        "Base catastale stimata (% del prezzo)",
        15,
        90,
        base_catastale_default,
        5,
        help="Proxy del valore catastale usato per stimare l'imposta di registro. Per precisione reale serve la rendita catastale dell'immobile.",
    )

    st.divider()
    st.markdown("**🧾 Costi realistici proprietario**")
    manutenzione_perc = st.slider(
        "Manutenzione annua (% valore casa)",
        0.0,
        4.0,
        1.5,
        0.1,
        help="NerdWallet indica spesso 1%-2% come accantonamento manutenzione; case vecchie o lavori straordinari possono richiedere di piu'.",
    )
    costo_vendita_perc = st.slider(
        "Costo vendita futura (%)",
        0.0,
        8.0,
        4.0,
        0.5,
        help="Agenzia, trattativa, costi amministrativi e frizione di mercato. Serve per il grafico 'se vendo in quell'anno'.",
    )
    assicurazione_annua = st.number_input(
        "Assicurazione casa annua (€)",
        min_value=0,
        max_value=10_000,
        value=0,
        step=50,
    )
    condominio_extra_annuo = st.number_input(
        "Spese extra proprietario annue (€)",
        min_value=0,
        max_value=30_000,
        value=0,
        step=100,
        help="Quota di spese condominiali/lavori che non pagheresti da inquilino.",
    )
    ristrutturazione_iniziale = st.number_input(
        "Ristrutturazione iniziale (€)",
        min_value=0,
        max_value=500_000,
        value=0,
        step=1_000,
    )

    st.divider()
    st.markdown("**📈 Parametri investimento**")
    rendimento_etf = st.slider("Rendimento alternativo (%/anno)", 2.0, 10.0, 5.0, 0.5,
                                help="Rendimento annuo applicato al capitale iniziale non usato per comprare e alle differenze annuali di cassa.")
    rivalutazione  = st.slider("Rivalutazione immobile (%/anno)", 0.0, 4.0, 1.5, 0.5)

    st.divider()
    citta_cfr_list = [c for c in citta_list if c != citta]
    citta_cfr      = st.selectbox("🔀 Confronta con", citta_cfr_list,
                                   index=citta_cfr_list.index("Roma") if "Roma" in citta_cfr_list else 0)

    st.divider()
    st.markdown("**📊 Strumenti**")

    # Scenario save section
    st.markdown("**Salva Scenario**")
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        scenario_name = st.text_input(
            "Nome scenario",
            placeholder="es. Milano base",
            key="scenario_name_input",
            label_visibility="collapsed"
        )
    with col_s2:
        save_scenario_btn = st.button("💾 Salva", use_container_width=True)

    if save_scenario_btn and scenario_name:
        scenario_dati = PROVINCE[citta]
        scenario_prezzo_mq = prezzo_mq_manual if usa_valori_manual else scenario_dati["prezzo_mq"]
        scenario_affitto = affitto_mens_manual if usa_valori_manual else scenario_dati["affitto_80mq"] * mq / 80
        scenario_params = ParamsCalcolo(
            mq=mq,
            anticipo_perc=anticipo_perc,
            anni_mutuo=anni_mutuo,
            tasso_mutuo=tasso_mutuo,
            rendimento_etf=rendimento_etf,
            rivalutazione_immobile=rivalutazione,
            prima_casa=prima_casa,
            inflazione_affitti=2.0,
            base_catastale_perc=base_catastale_perc,
            regime_fiscale=regime_fiscale,
            anni_max=40,
            manutenzione_perc=manutenzione_perc,
            costo_vendita_perc=costo_vendita_perc,
            assicurazione_annua=assicurazione_annua,
            condominio_extra_annuo=condominio_extra_annuo,
            ristrutturazione_iniziale=ristrutturazione_iniziale,
        )
        scenario_res = calcola_breakeven(
            scenario_prezzo_mq,
            scenario_affitto,
            scenario_params,
        )
        new_scenario = crea_scenario(
            nome=scenario_name,
            citta=f"{citta} (manuale)" if usa_valori_manual else citta,
            mq=mq,
            prezzo_mq=scenario_prezzo_mq,
            affitto_mens=scenario_affitto,
            tasso_mutuo=tasso_mutuo,
            anticipo_perc=anticipo_perc,
            anni_mutuo=anni_mutuo,
            rendimento_etf=rendimento_etf,
            rivalutazione=rivalutazione,
            regime_label=regime_label,
            regime_fiscale=regime_fiscale,
            result=scenario_res,
        )
        st.session_state.scenarios.append(new_scenario)
        st.session_state.scenario_name_input = ""
        st.success(f"✓ Scenario '{scenario_name}' salvato!")

    # Show saved scenarios count
    if st.session_state.scenarios:
        st.caption(f"📌 {len(st.session_state.scenarios)} scenario(i) salvato(i)")

        # Delete scenario selector
        if len(st.session_state.scenarios) > 0:
            scenario_names = [s.nome for s in st.session_state.scenarios]
            scenario_to_delete = st.selectbox(
                "Elimina scenario",
                scenario_names,
                key="scenario_delete_selector",
                label_visibility="collapsed"
            )
            if st.button("🗑️ Elimina", use_container_width=True):
                st.session_state.scenarios = [s for s in st.session_state.scenarios if s.nome != scenario_to_delete]
                st.success("Scenario eliminato!")
                st.rerun()

    st.divider()
    market_meta = get_market_data_meta()
    fonte_label = market_meta["source"]
    periodo_label = market_meta["period"] or "periodo non disponibile"
    records_count = market_meta["records_count"]
    if records_count:
        st.caption(
            f"Prezzi e affitti: {fonte_label}, {periodo_label}. "
            f"Cache locale con {records_count} localita'. Calcoli a fini illustrativi."
        )
    else:
        st.caption(
            "Prezzi e affitti: fallback interno indicativo. "
            "Esegui `python scripts/update_market_data.py` per generare la cache da Immobiliare.it. "
            "Calcoli a fini illustrativi."
        )

# =============================================================================
# CALCOLI
# =============================================================================
params = ParamsCalcolo(
    mq=mq,
    anticipo_perc=anticipo_perc,
    anni_mutuo=anni_mutuo,
    tasso_mutuo=tasso_mutuo,
    rendimento_etf=rendimento_etf,
    rivalutazione_immobile=rivalutazione,
    prima_casa=prima_casa,
    inflazione_affitti=2.0,
    base_catastale_perc=base_catastale_perc,
    regime_fiscale=regime_fiscale,
    anni_max=40,
    manutenzione_perc=manutenzione_perc,
    costo_vendita_perc=costo_vendita_perc,
    assicurazione_annua=assicurazione_annua,
    condominio_extra_annuo=condominio_extra_annuo,
    ristrutturazione_iniziale=ristrutturazione_iniziale,
)

dati_citta   = PROVINCE[citta]
prezzo_mq    = prezzo_mq_manual if usa_valori_manual else dati_citta["prezzo_mq"]
affitto_mens = affitto_mens_manual if usa_valori_manual else dati_citta["affitto_80mq"] * mq / 80
fonte_valori = "Valori manuali inseriti dall'utente" if usa_valori_manual else dati_citta.get("fonte_dati", "Dataset città")

res = calcola_breakeven(prezzo_mq, affitto_mens, params)
be  = res["breakeven_anno"]
be_vendita = res["breakeven_netto_vendita_anno"]

# Confronto
dati_cfr     = PROVINCE[citta_cfr]
affitto_cfr  = dati_cfr["affitto_80mq"] * mq / 80
res_cfr      = calcola_breakeven(dati_cfr["prezzo_mq"], affitto_cfr, params)
be_cfr       = res_cfr["breakeven_anno"]

# =============================================================================
# HERO
# =============================================================================
if be_vendita is not None:
    hero_h1 = f"A <em>{citta}</em> conviene comprare solo se resti almeno {be_vendita} anni."
    hero_sub = (
        "Questo e' il verdetto piu' prudente: considera anche una vendita futura, "
        f"con costo di uscita al <strong>{costo_vendita_perc:.1f}%</strong>. "
        f"La rata stimata e' <strong>{res['rata_mensile']:,.0f} euro/mese</strong>, "
        f"l'affitto e' <strong>{affitto_mens:,.0f} euro/mese</strong>."
    )
elif be is not None:
    hero_h1 = f"A <em>{citta}</em> affittare resta competitivo se investi il capitale."
    hero_sub = (
        f"Il patrimonio teorico dell'acquisto supera l'affitto al <strong>anno {be}</strong>, "
        "ma se simuli la vendita la casa non recupera lo scenario affitto entro 40 anni. "
        "La liquidita' iniziale e il costo di uscita pesano molto."
    )
else:
    hero_h1 = f"A <em>{citta}</em> affittare resta piu' forte sull'orizzonte analizzato."
    hero_sub = (
        "Con questi parametri, affitto piu' investimento del capitale iniziale non viene superato "
        "dall'acquisto entro 40 anni. Risultato molto sensibile a rendimento alternativo, anticipo e rivalutazione casa."
    )

st.markdown(f"""
<div class="hero">
    <p class="hero-tag">città. · 2026</p>
    <h1 class="hero-h1">{hero_h1}</h1>
    <p class="hero-sub">{hero_sub}</p>
    <em class="hero-brand">città.</em>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# METRIC CARDS
# =============================================================================
col1, col2, col3, col4, col5 = st.columns(5)

be_label = f"{be} anni" if be else ">40 anni"
be_class = "mc-green" if (be and be <= 15) else ("mc-amber" if (be and be <= 25) else "mc-red")

with col1:
    st.markdown(f"""
    <div class="mc">
        <p class="mc-lbl">Valore immobile</p>
        <p class="mc-val">€ {res['valore_casa']:,.0f}</p>
        <p class="mc-sub">{mq} mq · {prezzo_mq:,.0f} €/mq</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="mc">
        <p class="mc-lbl">Anticipo richiesto</p>
        <p class="mc-val">€ {res['anticipo']:,.0f}</p>
        <p class="mc-sub">{anticipo_perc}% + costi ({res['costi_iniziali']['totale']:,.0f} €)</p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="mc">
        <p class="mc-lbl">Rata mensile</p>
        <p class="mc-val">€ {res['rata_mensile']:,.0f}</p>
        <p class="mc-sub">interessi tot. {res['interessi_mutuo']:,.0f} €</p>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="mc">
        <p class="mc-lbl">Affitto mensile</p>
        <p class="mc-val">€ {affitto_mens:,.0f}</p>
        <p class="mc-sub">{"valore manuale" if usa_valori_manual else f"stima per {mq} mq"}</p>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="mc {be_class}">
        <p class="mc-lbl">Break-even</p>
        <p class="mc-val">{be_label}</p>
        <p class="mc-sub">dopo, comprare batte l'affitto</p>
    </div>""", unsafe_allow_html=True)

st.write("")
st.caption(f"Fonte valori acquisto/affitto: {fonte_valori}.")

recupero_costi = res["recupero_costi_iniziali_anno"]
recupero_label = f"{recupero_costi} anni" if recupero_costi else ">40 anni"
affitti_equiv = res["anni_affitto_equivalenti"]
affitti_equiv_label = f"{affitti_equiv:.1f} anni" if affitti_equiv else "n.d."
be_vendita_label = f"{be_vendita} anni" if be_vendita else ">40 anni"

rent_yield_lordo = (affitto_mens * 12 / res["valore_casa"] * 100) if res["valore_casa"] else 0
gap_cassa_mese = affitto_mens - res["rata_mensile"]
driver_cards = []

if anticipo_perc >= 30 or (affitti_equiv and affitti_equiv >= 5):
    driver_cards.append((
        "driver-rent",
        "Anticipo alto",
        f"Stai immobilizzando {res['capitale_iniziale']:,.0f} euro all'inizio. Nel modello prudente chi affitta li investe subito.",
    ))
elif anticipo_perc <= 15:
    driver_cards.append((
        "driver-buy",
        "Anticipo leggero",
        "Il capitale iniziale bloccato nell'acquisto e' piu' contenuto: questo aiuta il lato proprietario.",
    ))

if rendimento_etf >= 7:
    driver_cards.append((
        "driver-rent",
        "Rendimento alternativo alto",
        f"Il {rendimento_etf:.1f}% annuo rende forte lo scenario affitto + investimento, soprattutto nei primi anni.",
    ))
elif rendimento_etf <= 3:
    driver_cards.append((
        "driver-buy",
        "Rendimento alternativo basso",
        "Se il capitale investito rende poco, l'affitto perde una delle sue difese principali.",
    ))

if rent_yield_lordo >= 5:
    driver_cards.append((
        "driver-buy",
        "Affitto caro",
        f"L'affitto vale circa il {rent_yield_lordo:.1f}% lordo del prezzo casa all'anno: questo spinge verso l'acquisto.",
    ))
elif rent_yield_lordo <= 3.5:
    driver_cards.append((
        "driver-rent",
        "Affitto competitivo",
        f"L'affitto pesa solo il {rent_yield_lordo:.1f}% lordo del prezzo casa all'anno: comprare e' meno immediato.",
    ))

if gap_cassa_mese > 0:
    driver_cards.append((
        "driver-neutral",
        "La rata e' piu' bassa, ma l'anticipo pesa",
        f"La rata e' circa {gap_cassa_mese:,.0f} euro/mese sotto l'affitto, pero' il capitale iniziale resta il vero costo opportunita'.",
    ))
else:
    driver_cards.append((
        "driver-rent",
        "La rata non batte l'affitto",
        f"La rata supera l'affitto di circa {abs(gap_cassa_mese):,.0f} euro/mese, prima ancora di manutenzione e altri costi.",
    ))

if costo_vendita_perc >= 4:
    driver_cards.append((
        "driver-rent",
        "Costo vendita alto",
        f"Il {costo_vendita_perc:.1f}% sottratto in uscita rende piu' severo il break-even se vendi.",
    ))

if manutenzione_perc >= 1.5:
    driver_cards.append((
        "driver-rent",
        "Manutenzione alta",
        f"La manutenzione al {manutenzione_perc:.1f}% vale circa {res['valore_casa'] * manutenzione_perc / 100:,.0f} euro il primo anno.",
    ))
elif manutenzione_perc <= 0.5:
    driver_cards.append((
        "driver-buy",
        "Manutenzione leggera",
        "Costi di proprieta' contenuti rendono piu' facile recuperare l'acquisto.",
    ))

if rivalutazione <= 0.5:
    driver_cards.append((
        "driver-rent",
        "Rivalutazione bassa",
        f"Con casa a +{rivalutazione:.1f}% annuo, l'equity cresce lentamente e l'investimento alternativo resta competitivo.",
    ))
elif rivalutazione >= 2:
    driver_cards.append((
        "driver-buy",
        "Rivalutazione alta",
        f"Una crescita casa del {rivalutazione:.1f}% annuo accorcia il tempo necessario per superare l'affitto.",
    ))

if not driver_cards:
    driver_cards.append((
        "driver-neutral",
        "Risultato bilanciato",
        "Nessun parametro domina da solo: il risultato nasce dalla combinazione tra prezzo, affitto, anticipo e rendimento alternativo.",
    ))

col_extra1, col_extra2, col_extra3 = st.columns(3)
with col_extra1:
    st.markdown(f"""
    <div class="mc">
        <p class="mc-lbl">Break-even se vendi</p>
        <p class="mc-val">{be_vendita_label}</p>
        <p class="mc-sub">con costo vendita futuro al {costo_vendita_perc:.1f}% sottratto dal valore casa</p>
    </div>""", unsafe_allow_html=True)

with col_extra2:
    st.markdown(f"""
    <div class="mc">
        <p class="mc-lbl">Recupero costi iniziali</p>
        <p class="mc-val">{recupero_label}</p>
        <p class="mc-sub">anni necessari per recuperare anticipo + imposte + notaio + agenzia con il risparmio annuo rispetto all'affitto</p>
    </div>""", unsafe_allow_html=True)

with col_extra3:
    st.markdown(f"""
    <div class="mc">
        <p class="mc-lbl">Affitti equivalenti</p>
        <p class="mc-val">{affitti_equiv_label}</p>
        <p class="mc-sub">quanti anni di affitto attuale equivalgono alla liquidita' iniziale richiesta per comprare</p>
    </div>""", unsafe_allow_html=True)

driver_html = "".join(
    f'<div class="driver-card {driver_class}"><strong>{title}</strong><p>{body}</p></div>'
    for driver_class, title, body in driver_cards[:6]
)

st.markdown(f"""
<p class="sec-h">Cosa guida <em>il risultato.</em></p>
<span class="sec-sub">Verdetto piu' onesto: permanenza, capitale investito e costi di uscita</span>
<div class="driver-grid">{driver_html}</div>
""", unsafe_allow_html=True)

# =============================================================================
# PDF EXPORT
# =============================================================================
col_pdf1, col_pdf2 = st.columns([2, 1])
with col_pdf2:
    pdf_buffer = genera_report_pdf(
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
        result=res,
    )
    st.download_button(
        label="📄 Scarica PDF",
        data=pdf_buffer,
        file_name=f"città_analisi_{citta}_{mq}mq.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# =============================================================================
# SCENARIO COMPARISON
# =============================================================================
if st.session_state.scenarios:
    st.divider()
    st.markdown("""
    <p class="sec-h">Confronto <em>scenari</em> salvati</p>
    <span class="sec-sub">Comparazione tra scenari · modificabili dalla sidebar</span>
    """, unsafe_allow_html=True)

    df_comparison = compare_scenarios(st.session_state.scenarios)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)

# =============================================================================
# CONFRONTO CITTÀ
# =============================================================================
be_cfr_label = f"{be_cfr} anni" if be_cfr else ">40 anni"
delta_be = (be_cfr - be) if (be and be_cfr) else None
delta_str = ""
if delta_be is not None:
    if delta_be > 0:
        delta_str = f"A {citta} l'acquisto supera l'affitto {delta_be} anni prima."
    elif delta_be < 0:
        delta_str = f"A {citta_cfr} l'acquisto supera l'affitto {abs(delta_be)} anni prima."
    else:
        delta_str = "Break-even identico nelle due città."

st.markdown(f"""
<p class="sec-h">Il confronto <em>che conta.</em></p>
<span class="sec-sub">{citta} vs {citta_cfr} · modifica le città nella sidebar</span>
<div class="cfr-wrap">
    <div class="cfr-card cfr-dark">
        <p class="cfr-city">{citta}</p>
        <p class="cfr-val">{be_label}</p>
        <p class="cfr-sub">break-even · casa {res['valore_casa']:,.0f} € · {prezzo_mq:,.0f} €/mq</p>
        <p class="cfr-sub">rata {res['rata_mensile']:,.0f} €/mese · affitto {affitto_mens:,.0f} €/mese</p>
    </div>
    <div class="cfr-arrow">↔</div>
    <div class="cfr-card cfr-light">
        <p class="cfr-city">{citta_cfr}</p>
        <p class="cfr-val">{be_cfr_label}</p>
        <p class="cfr-sub">break-even · casa {res_cfr['valore_casa']:,.0f} € · {dati_cfr['prezzo_mq']:,.0f} €/mq</p>
        <p class="cfr-sub">rata {res_cfr['rata_mensile']:,.0f} €/mese · affitto {affitto_cfr:,.0f} €/mese</p>
    </div>
</div>
<p style="font-size:0.85rem;color:#666;margin-top:0.5rem;">{delta_str}</p>
""", unsafe_allow_html=True)

st.divider()

# =============================================================================
# TABS
# =============================================================================
tab1, tab2, tab3 = st.tabs(["📈 Grafico break-even", "🗺️ Mappa Italia", "🏆 Classifica"])

# ── TAB 1: GRAFICO CUMULATIVO ─────────────────────────────────────────────────
with tab1:
    st.markdown(f"""
    <p class="sec-h">Patrimonio netto: <em>acquisto vs affitto</em></p>
    <span class="sec-sub">{citta} · orizzonte 40 anni · valori stimati in €</span>
    """, unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=res["anni"], y=res["patrimonio_acquisto"],
        name="Comprare (patrimonio)",
        line=dict(color=C_DARK, width=2.5),
        fill="none",
    ))
    fig.add_trace(go.Scatter(
        x=res["anni"], y=res["patrimonio_affitto"],
        name="Affittare (patrimonio)",
        line=dict(color=C_RED, width=2.5, dash="dash"),
        fill="none",
    ))

    if be:
        fig.add_vline(x=be, line=dict(color=C_GREEN, width=1.5, dash="dot"))
        fig.add_annotation(
            x=be, y=res["patrimonio_acquisto"][be - 1],
            text=f"  Break-even\n  anno {be}",
            showarrow=False,
            font=dict(color=C_GREEN, size=11),
            xanchor="left",
        )

    fig.update_layout(
        plot_bgcolor=C_WHITE,
        paper_bgcolor=C_CREAM,
        font=dict(family="Inter, sans-serif", color=C_DARK),
        xaxis=dict(
            title=dict(text="Anno", font=dict(size=11, color="#999")),
            gridcolor="rgba(0,0,0,0.05)",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title=dict(text="Patrimonio netto stimato (€)", font=dict(size=11, color="#999")),
            gridcolor="rgba(0,0,0,0.05)",
            tickfont=dict(size=10),
            tickformat=",.0f",
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=11),
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <p class="sec-h">Se vendi: <em>netto reale</em></p>
    <span class="sec-sub">Valore casa meno mutuo residuo e costo vendita vs affitto + investimento</span>
    """, unsafe_allow_html=True)

    fig_sell = go.Figure()
    fig_sell.add_trace(go.Scatter(
        x=res["anni"], y=res["patrimonio_acquisto_netto_vendita"],
        name="Comprare e vendere in quell'anno",
        line=dict(color=C_ACCENT_GOLD, width=3),
    ))
    fig_sell.add_trace(go.Scatter(
        x=res["anni"], y=res["patrimonio_affitto"],
        name="Affittare + investire",
        line=dict(color=C_RED, width=2.5, dash="dash"),
    ))
    if be_vendita:
        fig_sell.add_vline(x=be_vendita, line=dict(color=C_GREEN, width=1.5, dash="dot"))
        fig_sell.add_annotation(
            x=be_vendita,
            y=res["patrimonio_acquisto_netto_vendita"][be_vendita - 1],
            text=f"  Netto vendita\n  anno {be_vendita}",
            showarrow=False,
            font=dict(color=C_GREEN, size=11),
            xanchor="left",
        )
    fig_sell.update_layout(
        plot_bgcolor=C_WHITE,
        paper_bgcolor=C_CREAM,
        font=dict(family="Inter, sans-serif", color=C_DARK),
        xaxis=dict(
            title=dict(text="Anno di vendita", font=dict(size=11, color="#999")),
            gridcolor="rgba(0,0,0,0.05)",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title=dict(text="Patrimonio netto liquidabile (€)", font=dict(size=11, color="#999")),
            gridcolor="rgba(0,0,0,0.05)",
            tickfont=dict(size=10),
            tickformat=",.0f",
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=11),
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=390,
    )
    st.plotly_chart(fig_sell, use_container_width=True)

    st.markdown(f"""
    <div style="background:{C_WHITE};color:{C_DARK};padding:1rem 1.4rem;border:1px solid {C_BORDER_LIGHT};border-radius:8px;font-size:0.85rem;line-height:1.6;">
    <strong>Perche' questo e' piu' prudente:</strong> qui immaginiamo di vendere casa in ciascun anno.
    Dal valore stimato vengono sottratti mutuo residuo e costo vendita del {costo_vendita_perc:.1f}%.
    Questo evita di contare come ricchezza tutta l'equity teorica senza considerare il costo di trasformarla in liquidita'.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <p class="sec-h">Recupero <em>costi iniziali</em></p>
    <span class="sec-sub">Risparmio annuo nominale accumulato vs anticipo + costi di acquisto</span>
    """, unsafe_allow_html=True)

    soglia_costi = res["capitale_iniziale"]
    fig_recovery = go.Figure()
    fig_recovery.add_trace(go.Scatter(
        x=res["anni"],
        y=res["risparmio_cumulato_nominale_anni"],
        name="Risparmio cumulato",
        line=dict(color=C_ACCENT_GOLD, width=3),
        fill="tozeroy",
        fillcolor="rgba(10, 102, 194, 0.12)",
    ))
    fig_recovery.add_trace(go.Scatter(
        x=res["anni"],
        y=[soglia_costi] * len(res["anni"]),
        name="Anticipo + costi iniziali",
        line=dict(color=C_RED, width=2, dash="dash"),
    ))

    if recupero_costi:
        fig_recovery.add_vline(x=recupero_costi, line=dict(color=C_GREEN, width=1.5, dash="dot"))
        fig_recovery.add_annotation(
            x=recupero_costi,
            y=soglia_costi,
            text=f"  Recupero\n  anno {recupero_costi}",
            showarrow=False,
            font=dict(color=C_GREEN, size=11),
            xanchor="left",
            yanchor="bottom",
        )

    fig_recovery.update_layout(
        plot_bgcolor=C_WHITE,
        paper_bgcolor=C_CREAM,
        font=dict(family="Inter, sans-serif", color=C_DARK),
        xaxis=dict(
            title=dict(text="Anno", font=dict(size=11, color="#999")),
            gridcolor="rgba(0,0,0,0.05)",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title=dict(text="Euro cumulati", font=dict(size=11, color="#999")),
            gridcolor="rgba(0,0,0,0.05)",
            tickfont=dict(size=10),
            tickformat=",.0f",
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=11),
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=360,
    )
    st.plotly_chart(fig_recovery, use_container_width=True)

    st.markdown(f"""
    <div style="background:{C_WHITE};color:{C_DARK};padding:1rem 1.4rem;border:1px solid {C_BORDER_LIGHT};border-radius:8px;font-size:0.85rem;line-height:1.6;">
    <strong>Come leggere questo grafico:</strong> la linea blu somma solo il risparmio nominale degli anni in cui comprare costa meno dell'affitto.
    La linea rossa e' la liquidita' iniziale richiesta per comprare: anticipo piu' costi iniziali.
    Quando la linea blu supera la rossa, quei costi sono recuperati con il risparmio di cassa.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{C_DARK};color:{C_WHITE};padding:1rem 1.4rem;border-radius:10px;font-size:0.85rem;line-height:1.6;">
    <strong>Come leggere il grafico:</strong> la linea acquisto mostra l'equity della casa, al netto del debito residuo.
    Per prudenza non reinvestiamo automaticamente l'eventuale risparmio mensile del proprietario.
    La linea affitto mostra anticipo e costi iniziali evitati, piu' gli eventuali risparmi annuali,
    investiti in ETF al {rendimento_etf}%/anno.
    Quando la linea scura supera quella rossa: comprare conviene.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Cosa entra davvero nel confronto"):
        st.markdown(f"""
        - **Regime fiscale selezionato:** {regime_label}. {regime_info["note"]}
        - **Imposte iniziali:** registro stimato su una base catastale pari al {base_catastale_perc}% del prezzo, non sul prezzo pieno. Qui la base catastale stimata e' {res['costi_iniziali']['base_catastale']:,.0f} €, l'imposta di registro {res['costi_iniziali']['imposta']:,.0f} €, ipotecaria/catastale fisse {res['costi_iniziali']['ipocatastali']:,.0f} €.
        - **Acquisto:** anticipo, imposte iniziali, agenzia, notaio, ristrutturazione iniziale ({ristrutturazione_iniziale:,.0f} €), rate mutuo, manutenzione annua al {manutenzione_perc:.1f}% del valore casa rivalutato, assicurazione ({assicurazione_annua:,.0f} €/anno), spese extra proprietario ({condominio_extra_annuo:,.0f} €/anno) e, solo per seconda casa/investimento, IMU annua stimata allo 0,5%.
        - **Mutuo:** il capitale finanziato e' {res['capitale_mutuo']:,.0f} €. Con rata {res['rata_mensile']:,.0f} €/mese per {anni_mutuo} anni, il totale rate e' {res['totale_rate_mutuo']:,.0f} €, di cui {res['interessi_mutuo']:,.0f} € sono interessi. Nel grafico questi interessi pesano perche' la rata intera esce ogni anno dal cashflow dell'acquisto, mentre solo la quota capitale aumenta l'equity riducendo il debito residuo.
        - **Affitto:** canone annuo con crescita del 2% e investimento del capitale che non viene immobilizzato nell'acquisto.
        - **Investimento alternativo:** lato affitto non e' solo "l'anticipo"; include anche i costi iniziali evitati e, anno per anno, la differenza quando affittare costa meno del comprare. In modalita' prudente, se comprare costa meno dell'affitto, quella differenza non viene reinvestita automaticamente lato acquisto.
        - **Recupero costi iniziali:** misura diversa dal break-even patrimoniale. Somma solo il risparmio annuo nominale quando comprare costa meno dell'affitto e verifica quando recupera anticipo + costi iniziali.
        - **Affitti equivalenti:** divide anticipo + costi iniziali per l'affitto annuo attuale. Non considera mutuo, manutenzione, rivalutazione o investimenti: e' una misura rapida di liquidita' iniziale.
        - **Netto se vendi:** sottrae un costo vendita futuro del {costo_vendita_perc:.1f}% dal valore casa stimato prima di confrontare acquisto e affitto.
        """)

# ── TAB 2: MAPPA ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <p class="sec-h">La mappa <em>del break-even.</em></p>
    <span class="sec-sub">107 province italiane · anni necessari per superare lo scenario affitto</span>
    """, unsafe_allow_html=True)

    @st.cache_data(show_spinner="Calcolo in corso per 107 province…")
    def get_df_mappa(mq, anticipo_perc, anni_mutuo, tasso_mutuo,
                     rendimento_etf, rivalutazione, prima_casa, base_catastale_perc,
                     regime_fiscale, manutenzione_perc, costo_vendita_perc,
                     assicurazione_annua, condominio_extra_annuo, ristrutturazione_iniziale):
        p = ParamsCalcolo(
            mq=mq, anticipo_perc=anticipo_perc, anni_mutuo=anni_mutuo,
            tasso_mutuo=tasso_mutuo, rendimento_etf=rendimento_etf,
            rivalutazione_immobile=rivalutazione, prima_casa=prima_casa,
            inflazione_affitti=2.0, base_catastale_perc=base_catastale_perc,
            regime_fiscale=regime_fiscale, anni_max=40,
            manutenzione_perc=manutenzione_perc, costo_vendita_perc=costo_vendita_perc,
            assicurazione_annua=assicurazione_annua, condominio_extra_annuo=condominio_extra_annuo,
            ristrutturazione_iniziale=ristrutturazione_iniziale,
        )
        return calcola_tutti_breakeven(p)

    df_mappa = get_df_mappa(mq, anticipo_perc, anni_mutuo, tasso_mutuo,
                            rendimento_etf, rivalutazione, prima_casa,
                            base_catastale_perc, regime_fiscale, manutenzione_perc,
                            costo_vendita_perc, assicurazione_annua,
                            condominio_extra_annuo, ristrutturazione_iniziale)

    fig_map = go.Figure(go.Scattermapbox(
        lat=df_mappa["lat"],
        lon=df_mappa["lon"],
        mode="markers",
        marker=dict(
            size=12,
            color=df_mappa["breakeven_anno"].clip(0, 40),
            colorscale=[[0, C_GREEN], [0.5, C_AMBER], [1, C_RED]],
            cmin=5, cmax=40,
            colorbar=dict(
                title=dict(text="Anni", font=dict(size=11)),
                thickness=12,
                len=0.6,
            ),
            opacity=0.85,
        ),
        text=df_mappa.apply(
            lambda r: f"<b>{r['citta']}</b><br>Break-even: {r['breakeven_label']}<br>"
                      f"Prezzo: {r['prezzo_mq']:,} €/mq<br>Affitto: {r['affitto_mensile']:,.0f} €/mese",
            axis=1,
        ),
        hoverinfo="text",
    ))
    fig_map.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=42.5, lon=12.5), zoom=4.5),
        margin=dict(l=0, r=0, t=0, b=0),
        height=520,
        paper_bgcolor=C_CREAM,
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ── TAB 3: CLASSIFICA ────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <p class="sec-h">La classifica <em>completa.</em></p>
    <span class="sec-sub">107 province · ordinate per break-even crescente</span>
    """, unsafe_allow_html=True)

    @st.cache_data(show_spinner=False)
    def get_df_rank(mq, anticipo_perc, anni_mutuo, tasso_mutuo,
                    rendimento_etf, rivalutazione, prima_casa, base_catastale_perc,
                    regime_fiscale, manutenzione_perc, costo_vendita_perc,
                    assicurazione_annua, condominio_extra_annuo, ristrutturazione_iniziale):
        p = ParamsCalcolo(
            mq=mq, anticipo_perc=anticipo_perc, anni_mutuo=anni_mutuo,
            tasso_mutuo=tasso_mutuo, rendimento_etf=rendimento_etf,
            rivalutazione_immobile=rivalutazione, prima_casa=prima_casa,
            inflazione_affitti=2.0, base_catastale_perc=base_catastale_perc,
            regime_fiscale=regime_fiscale, anni_max=40,
            manutenzione_perc=manutenzione_perc, costo_vendita_perc=costo_vendita_perc,
            assicurazione_annua=assicurazione_annua, condominio_extra_annuo=condominio_extra_annuo,
            ristrutturazione_iniziale=ristrutturazione_iniziale,
        )
        return calcola_tutti_breakeven(p)

    df_rank = get_df_rank(mq, anticipo_perc, anni_mutuo, tasso_mutuo,
                          rendimento_etf, rivalutazione, prima_casa,
                          base_catastale_perc, regime_fiscale, manutenzione_perc,
                          costo_vendita_perc, assicurazione_annua,
                          condominio_extra_annuo, ristrutturazione_iniziale)

    df_display = df_rank[["citta", "regione", "prezzo_mq", "affitto_mensile",
                           "rata_mensile", "breakeven_label"]].copy()
    df_display.columns = ["Città", "Regione", "€/mq", "Affitto €/mese",
                          "Rata €/mese", "Break-even"]
    df_display["€/mq"]          = df_display["€/mq"].map("{:,.0f}".format)
    df_display["Affitto €/mese"] = df_display["Affitto €/mese"].map("{:,.0f}".format)
    df_display["Rata €/mese"]   = df_display["Rata €/mese"].map("{:,.0f}".format)
    df_display.index = range(1, len(df_display) + 1)

    st.dataframe(df_display, use_container_width=True, height=500)

# =============================================================================
# SENSITIVITY ANALYSIS
# =============================================================================
st.divider()
with st.expander("🔬 Analisi Sensibilità — Come cambiano i risultati al variare dei parametri", expanded=False):
    st.markdown("""
    Esplora come il break-even cambia quando modifichiamo uno specifico parametro.
    Seleziona il parametro da analizzare e osserva il grafico interattivo.
    """)

    sensitivity_param = st.selectbox(
        "Parametro da analizzare",
        ["Tasso Mutuo (%)", "Rendimento ETF (%)", "Rivalutazione Immobile (%)"],
        key="sensitivity_param_selector"
    )

    # Define ranges for sensitivity analysis
    sensitivity_ranges = {
        "Tasso Mutuo (%)": (1.0, 6.0, 0.1),
        "Rendimento ETF (%)": (1.0, 10.0, 0.25),
        "Rivalutazione Immobile (%)": (0.0, 4.0, 0.1),
    }

    param_min, param_max, param_step = sensitivity_ranges[sensitivity_param]

    # Generate sensitivity data
    sensitivity_values = []
    sensitivity_breakevens = []

    for param_value in np.arange(param_min, param_max + param_step, param_step):
        # Create modified parameters
        test_params = ParamsCalcolo(
            mq=mq,
            anticipo_perc=anticipo_perc,
            anni_mutuo=anni_mutuo,
            tasso_mutuo=tasso_mutuo if sensitivity_param != "Tasso Mutuo (%)" else param_value,
            rendimento_etf=rendimento_etf if sensitivity_param != "Rendimento ETF (%)" else param_value,
            rivalutazione_immobile=rivalutazione if sensitivity_param != "Rivalutazione Immobile (%)" else param_value,
            prima_casa=prima_casa,
            inflazione_affitti=2.0,
            base_catastale_perc=base_catastale_perc,
            regime_fiscale=regime_fiscale,
            anni_max=40,
            manutenzione_perc=manutenzione_perc,
            costo_vendita_perc=costo_vendita_perc,
            assicurazione_annua=assicurazione_annua,
            condominio_extra_annuo=condominio_extra_annuo,
            ristrutturazione_iniziale=ristrutturazione_iniziale,
        )

        test_result = calcola_breakeven(prezzo_mq, affitto_mens, test_params)
        be_test = test_result["breakeven_anno"]

        sensitivity_values.append(param_value)
        sensitivity_breakevens.append(be_test if be_test else 40)

    # Create sensitivity chart
    fig_sensitivity = go.Figure()

    fig_sensitivity.add_trace(go.Scatter(
        x=sensitivity_values,
        y=sensitivity_breakevens,
        mode='lines+markers',
        name='Break-even (anni)',
        line=dict(color='#F2C14E', width=3),
        marker=dict(size=6, color='#F2C14E'),
        fill='tozeroy',
        fillcolor='rgba(242, 193, 78, 0.1)',
    ))

    # Add current value line
    current_param_value = {
        "Tasso Mutuo (%)": tasso_mutuo,
        "Rendimento ETF (%)": rendimento_etf,
        "Rivalutazione Immobile (%)": rivalutazione,
    }[sensitivity_param]

    fig_sensitivity.add_vline(
        x=current_param_value,
        line=dict(color='#3A8C52', width=2, dash='dash'),
        annotation_text="  Valore attuale",
        annotation_position="top right",
    )

    fig_sensitivity.update_layout(
        plot_bgcolor='#EDE8DC',
        paper_bgcolor='#EDE8DC',
        font=dict(family='Inter, sans-serif', color='#0F0C08', size=11),
        xaxis=dict(
            title=dict(text=sensitivity_param, font=dict(size=12)),
            gridcolor='rgba(0,0,0,0.05)',
        ),
        yaxis=dict(
            title=dict(text='Break-even (anni)', font=dict(size=12)),
            gridcolor='rgba(0,0,0,0.05)',
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=400,
        hovermode='x unified',
    )

    st.plotly_chart(fig_sensitivity, use_container_width=True)

    # Summary statistics
    col_sens1, col_sens2, col_sens3 = st.columns(3)
    with col_sens1:
        st.metric(
            "Break-even minimo",
            f"{min(sensitivity_breakevens):.0f} anni",
            delta=f"a {sensitivity_values[sensitivity_breakevens.index(min(sensitivity_breakevens))]:.2f}" if min(sensitivity_breakevens) < 40 else None,
        )
    with col_sens2:
        st.metric(
            "Break-even massimo",
            f"{max(sensitivity_breakevens):.0f} anni",
        )
    with col_sens3:
        current_be_idx = min(range(len(sensitivity_values)), key=lambda i: abs(sensitivity_values[i] - current_param_value))
        st.metric(
            "Break-even attuale",
            f"{sensitivity_breakevens[current_be_idx]:.0f} anni",
        )
