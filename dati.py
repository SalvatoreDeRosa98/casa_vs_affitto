# =============================================================================
# DATI IMMOBILIARI — 107 Province Italiane
# Progetto: "Casa o affitto? Il calcolatore della verità"
# Fonte fallback originaria: OMI Agenzia delle Entrate, Immobiliare.it, Idealista 2024
# I valori statici sotto sono usati solo se non esiste una cache online aggiornata.
# La cache generata da scripts/update_market_data.py usa prezzi richiesti reali
# pubblicati online da Immobiliare.it; vedi data/market_data_immobiliare.json.
# =============================================================================
# prezzo_mq     : prezzo medio al mq per acquisto (€/mq)
# affitto_80mq  : affitto mensile medio per appartamento da 80mq (€/mese)
# lat, lon      : coordinate capoluogo per la mappa

import json
from pathlib import Path

PROVINCE = {
    # ── LOMBARDIA ──────────────────────────────────────────────────────────────
    "Milano":            {"regione": "Lombardia",             "prezzo_mq": 4800, "affitto_80mq": 1400, "lat": 45.4654, "lon":  9.1866},
    "Monza":             {"regione": "Lombardia",             "prezzo_mq": 2800, "affitto_80mq":  950, "lat": 45.5845, "lon":  9.2744},
    "Como":              {"regione": "Lombardia",             "prezzo_mq": 2500, "affitto_80mq":  850, "lat": 45.8081, "lon":  9.0852},
    "Varese":            {"regione": "Lombardia",             "prezzo_mq": 1900, "affitto_80mq":  700, "lat": 45.8207, "lon":  8.8257},
    "Bergamo":           {"regione": "Lombardia",             "prezzo_mq": 2200, "affitto_80mq":  800, "lat": 45.6983, "lon":  9.6773},
    "Brescia":           {"regione": "Lombardia",             "prezzo_mq": 1900, "affitto_80mq":  750, "lat": 45.5416, "lon": 10.2118},
    "Lecco":             {"regione": "Lombardia",             "prezzo_mq": 2000, "affitto_80mq":  750, "lat": 45.8566, "lon":  9.3970},
    "Lodi":              {"regione": "Lombardia",             "prezzo_mq": 1600, "affitto_80mq":  650, "lat": 45.3143, "lon":  9.5034},
    "Pavia":             {"regione": "Lombardia",             "prezzo_mq": 1700, "affitto_80mq":  650, "lat": 45.1847, "lon":  9.1582},
    "Cremona":           {"regione": "Lombardia",             "prezzo_mq": 1400, "affitto_80mq":  600, "lat": 45.1327, "lon": 10.0227},
    "Mantova":           {"regione": "Lombardia",             "prezzo_mq": 1500, "affitto_80mq":  620, "lat": 45.1564, "lon": 10.7914},
    "Sondrio":           {"regione": "Lombardia",             "prezzo_mq": 1300, "affitto_80mq":  580, "lat": 46.1698, "lon":  9.8727},
    # ── PIEMONTE ───────────────────────────────────────────────────────────────
    "Torino":            {"regione": "Piemonte",              "prezzo_mq": 2200, "affitto_80mq":  800, "lat": 45.0703, "lon":  7.6869},
    "Cuneo":             {"regione": "Piemonte",              "prezzo_mq": 1400, "affitto_80mq":  580, "lat": 44.3908, "lon":  7.5488},
    "Novara":            {"regione": "Piemonte",              "prezzo_mq": 1500, "affitto_80mq":  600, "lat": 45.4455, "lon":  8.6203},
    "Asti":              {"regione": "Piemonte",              "prezzo_mq": 1200, "affitto_80mq":  550, "lat": 44.9003, "lon":  8.2064},
    "Alessandria":       {"regione": "Piemonte",              "prezzo_mq": 1100, "affitto_80mq":  520, "lat": 44.9124, "lon":  8.6151},
    "Biella":            {"regione": "Piemonte",              "prezzo_mq":  900, "affitto_80mq":  480, "lat": 45.5659, "lon":  8.0537},
    "Vercelli":          {"regione": "Piemonte",              "prezzo_mq": 1000, "affitto_80mq":  490, "lat": 45.3204, "lon":  8.4232},
    "Verbania":          {"regione": "Piemonte",              "prezzo_mq": 1800, "affitto_80mq":  680, "lat": 45.9235, "lon":  8.5519},
    # ── LIGURIA ────────────────────────────────────────────────────────────────
    "Genova":            {"regione": "Liguria",               "prezzo_mq": 1900, "affitto_80mq":  750, "lat": 44.4056, "lon":  8.9463},
    "La Spezia":         {"regione": "Liguria",               "prezzo_mq": 2000, "affitto_80mq":  750, "lat": 44.1024, "lon":  9.8240},
    "Imperia":           {"regione": "Liguria",               "prezzo_mq": 2200, "affitto_80mq":  800, "lat": 43.8886, "lon":  8.0306},
    "Savona":            {"regione": "Liguria",               "prezzo_mq": 1800, "affitto_80mq":  700, "lat": 44.3074, "lon":  8.4823},
    # ── VALLE D'AOSTA ──────────────────────────────────────────────────────────
    "Aosta":             {"regione": "Valle d'Aosta",         "prezzo_mq": 2200, "affitto_80mq":  800, "lat": 45.7370, "lon":  7.3150},
    # ── TRENTINO-ALTO ADIGE ────────────────────────────────────────────────────
    "Bolzano":           {"regione": "Trentino-Alto Adige",   "prezzo_mq": 4500, "affitto_80mq": 1300, "lat": 46.4982, "lon": 11.3548},
    "Trento":            {"regione": "Trentino-Alto Adige",   "prezzo_mq": 2800, "affitto_80mq":  900, "lat": 46.0664, "lon": 11.1257},
    # ── VENETO ─────────────────────────────────────────────────────────────────
    "Venezia":           {"regione": "Veneto",                "prezzo_mq": 3500, "affitto_80mq": 1050, "lat": 45.4408, "lon": 12.3155},
    "Verona":            {"regione": "Veneto",                "prezzo_mq": 2500, "affitto_80mq":  850, "lat": 45.4384, "lon": 10.9916},
    "Padova":            {"regione": "Veneto",                "prezzo_mq": 2300, "affitto_80mq":  820, "lat": 45.4064, "lon": 11.8768},
    "Vicenza":           {"regione": "Veneto",                "prezzo_mq": 1900, "affitto_80mq":  720, "lat": 45.5455, "lon": 11.5353},
    "Treviso":           {"regione": "Veneto",                "prezzo_mq": 2000, "affitto_80mq":  750, "lat": 45.6669, "lon": 12.2430},
    "Belluno":           {"regione": "Veneto",                "prezzo_mq": 1500, "affitto_80mq":  620, "lat": 46.1433, "lon": 12.2169},
    "Rovigo":            {"regione": "Veneto",                "prezzo_mq": 1100, "affitto_80mq":  520, "lat": 45.0712, "lon": 11.7901},
    # ── FRIULI-VENEZIA GIULIA ──────────────────────────────────────────────────
    "Trieste":           {"regione": "Friuli-Venezia Giulia", "prezzo_mq": 2200, "affitto_80mq":  800, "lat": 45.6495, "lon": 13.7768},
    "Udine":             {"regione": "Friuli-Venezia Giulia", "prezzo_mq": 1700, "affitto_80mq":  650, "lat": 46.0748, "lon": 13.2351},
    "Pordenone":         {"regione": "Friuli-Venezia Giulia", "prezzo_mq": 1500, "affitto_80mq":  620, "lat": 45.9564, "lon": 12.6619},
    "Gorizia":           {"regione": "Friuli-Venezia Giulia", "prezzo_mq": 1300, "affitto_80mq":  580, "lat": 45.9411, "lon": 13.6206},
    # ── EMILIA-ROMAGNA ─────────────────────────────────────────────────────────
    "Bologna":           {"regione": "Emilia-Romagna",        "prezzo_mq": 3000, "affitto_80mq": 1000, "lat": 44.4949, "lon": 11.3426},
    "Modena":            {"regione": "Emilia-Romagna",        "prezzo_mq": 2000, "affitto_80mq":  780, "lat": 44.6471, "lon": 10.9252},
    "Parma":             {"regione": "Emilia-Romagna",        "prezzo_mq": 2200, "affitto_80mq":  800, "lat": 44.8015, "lon": 10.3279},
    "Reggio Emilia":     {"regione": "Emilia-Romagna",        "prezzo_mq": 1800, "affitto_80mq":  720, "lat": 44.6989, "lon": 10.6297},
    "Ferrara":           {"regione": "Emilia-Romagna",        "prezzo_mq": 1300, "affitto_80mq":  580, "lat": 44.8381, "lon": 11.6198},
    "Ravenna":           {"regione": "Emilia-Romagna",        "prezzo_mq": 1600, "affitto_80mq":  650, "lat": 44.4151, "lon": 12.2011},
    "Forlì":             {"regione": "Emilia-Romagna",        "prezzo_mq": 1400, "affitto_80mq":  600, "lat": 44.2227, "lon": 12.0407},
    "Rimini":            {"regione": "Emilia-Romagna",        "prezzo_mq": 2200, "affitto_80mq":  800, "lat": 44.0595, "lon": 12.5650},
    "Piacenza":          {"regione": "Emilia-Romagna",        "prezzo_mq": 1500, "affitto_80mq":  620, "lat": 45.0526, "lon":  9.6930},
    # ── TOSCANA ────────────────────────────────────────────────────────────────
    "Firenze":           {"regione": "Toscana",               "prezzo_mq": 3800, "affitto_80mq": 1100, "lat": 43.7696, "lon": 11.2558},
    "Prato":             {"regione": "Toscana",               "prezzo_mq": 1900, "affitto_80mq":  750, "lat": 43.8777, "lon": 11.1023},
    "Siena":             {"regione": "Toscana",               "prezzo_mq": 2500, "affitto_80mq":  850, "lat": 43.3188, "lon": 11.3307},
    "Lucca":             {"regione": "Toscana",               "prezzo_mq": 2300, "affitto_80mq":  820, "lat": 43.8429, "lon": 10.5027},
    "Pisa":              {"regione": "Toscana",               "prezzo_mq": 2200, "affitto_80mq":  800, "lat": 43.7228, "lon": 10.4017},
    "Arezzo":            {"regione": "Toscana",               "prezzo_mq": 1600, "affitto_80mq":  650, "lat": 43.4633, "lon": 11.8797},
    "Livorno":           {"regione": "Toscana",               "prezzo_mq": 1700, "affitto_80mq":  660, "lat": 43.5485, "lon": 10.3106},
    "Pistoia":           {"regione": "Toscana",               "prezzo_mq": 1500, "affitto_80mq":  620, "lat": 43.9330, "lon": 10.9173},
    "Grosseto":          {"regione": "Toscana",               "prezzo_mq": 1400, "affitto_80mq":  600, "lat": 42.7602, "lon": 11.1128},
    "Massa":             {"regione": "Toscana",               "prezzo_mq": 1600, "affitto_80mq":  640, "lat": 44.0352, "lon": 10.1413},
    # ── UMBRIA ─────────────────────────────────────────────────────────────────
    "Perugia":           {"regione": "Umbria",                "prezzo_mq": 1600, "affitto_80mq":  650, "lat": 43.1122, "lon": 12.3888},
    "Terni":             {"regione": "Umbria",                "prezzo_mq": 1200, "affitto_80mq":  560, "lat": 42.5636, "lon": 12.6430},
    # ── MARCHE ─────────────────────────────────────────────────────────────────
    "Ancona":            {"regione": "Marche",                "prezzo_mq": 1600, "affitto_80mq":  650, "lat": 43.6158, "lon": 13.5189},
    "Pesaro":            {"regione": "Marche",                "prezzo_mq": 1500, "affitto_80mq":  620, "lat": 43.9105, "lon": 12.9138},
    "Macerata":          {"regione": "Marche",                "prezzo_mq": 1200, "affitto_80mq":  560, "lat": 43.2988, "lon": 13.4527},
    "Fermo":             {"regione": "Marche",                "prezzo_mq": 1100, "affitto_80mq":  530, "lat": 43.1604, "lon": 13.7157},
    "Ascoli Piceno":     {"regione": "Marche",                "prezzo_mq": 1100, "affitto_80mq":  520, "lat": 42.8534, "lon": 13.5746},
    # ── LAZIO ──────────────────────────────────────────────────────────────────
    "Roma":              {"regione": "Lazio",                 "prezzo_mq": 3500, "affitto_80mq": 1100, "lat": 41.9028, "lon": 12.4964},
    "Latina":            {"regione": "Lazio",                 "prezzo_mq": 1400, "affitto_80mq":  600, "lat": 41.4676, "lon": 12.9037},
    "Frosinone":         {"regione": "Lazio",                 "prezzo_mq": 1100, "affitto_80mq":  520, "lat": 41.6402, "lon": 13.3436},
    "Viterbo":           {"regione": "Lazio",                 "prezzo_mq": 1300, "affitto_80mq":  580, "lat": 42.4175, "lon": 12.1048},
    "Rieti":             {"regione": "Lazio",                 "prezzo_mq": 1000, "affitto_80mq":  490, "lat": 42.4015, "lon": 12.8573},
    # ── ABRUZZO ────────────────────────────────────────────────────────────────
    "L'Aquila":          {"regione": "Abruzzo",               "prezzo_mq": 1100, "affitto_80mq":  520, "lat": 42.3498, "lon": 13.3995},
    "Pescara":           {"regione": "Abruzzo",               "prezzo_mq": 1500, "affitto_80mq":  620, "lat": 42.4612, "lon": 14.2160},
    "Chieti":            {"regione": "Abruzzo",               "prezzo_mq": 1100, "affitto_80mq":  510, "lat": 42.3510, "lon": 14.1673},
    "Teramo":            {"regione": "Abruzzo",               "prezzo_mq": 1000, "affitto_80mq":  490, "lat": 42.6589, "lon": 13.6944},
    # ── MOLISE ─────────────────────────────────────────────────────────────────
    "Campobasso":        {"regione": "Molise",                "prezzo_mq":  900, "affitto_80mq":  450, "lat": 41.5603, "lon": 14.6564},
    "Isernia":           {"regione": "Molise",                "prezzo_mq":  800, "affitto_80mq":  420, "lat": 41.5941, "lon": 14.2330},
    # ── CAMPANIA ───────────────────────────────────────────────────────────────
    "Napoli":            {"regione": "Campania",              "prezzo_mq": 2500, "affitto_80mq":  900, "lat": 40.8518, "lon": 14.2681},
    "Salerno":           {"regione": "Campania",              "prezzo_mq": 1500, "affitto_80mq":  620, "lat": 40.6824, "lon": 14.7681},
    "Caserta":           {"regione": "Campania",              "prezzo_mq": 1300, "affitto_80mq":  570, "lat": 41.0761, "lon": 14.3328},
    "Avellino":          {"regione": "Campania",              "prezzo_mq": 1000, "affitto_80mq":  490, "lat": 40.9145, "lon": 14.7893},
    "Benevento":         {"regione": "Campania",              "prezzo_mq":  900, "affitto_80mq":  450, "lat": 41.1297, "lon": 14.7819},
    # ── PUGLIA ─────────────────────────────────────────────────────────────────
    "Bari":              {"regione": "Puglia",                "prezzo_mq": 1800, "affitto_80mq":  700, "lat": 41.1171, "lon": 16.8719},
    "Lecce":             {"regione": "Puglia",                "prezzo_mq": 1500, "affitto_80mq":  620, "lat": 40.3520, "lon": 18.1750},
    "Taranto":           {"regione": "Puglia",                "prezzo_mq": 1000, "affitto_80mq":  490, "lat": 40.4640, "lon": 17.2470},
    "Brindisi":          {"regione": "Puglia",                "prezzo_mq": 1000, "affitto_80mq":  480, "lat": 40.6366, "lon": 17.9472},
    "Foggia":            {"regione": "Puglia",                "prezzo_mq":  900, "affitto_80mq":  450, "lat": 41.4621, "lon": 15.5444},
    "Barletta":          {"regione": "Puglia",                "prezzo_mq": 1100, "affitto_80mq":  510, "lat": 41.3156, "lon": 16.2803},
    # ── BASILICATA ─────────────────────────────────────────────────────────────
    "Potenza":           {"regione": "Basilicata",            "prezzo_mq":  900, "affitto_80mq":  450, "lat": 40.6420, "lon": 15.7990},
    "Matera":            {"regione": "Basilicata",            "prezzo_mq": 1400, "affitto_80mq":  580, "lat": 40.6664, "lon": 16.6043},
    # ── CALABRIA ───────────────────────────────────────────────────────────────
    "Catanzaro":         {"regione": "Calabria",              "prezzo_mq":  900, "affitto_80mq":  440, "lat": 38.9098, "lon": 16.5873},
    "Reggio Calabria":   {"regione": "Calabria",              "prezzo_mq": 1000, "affitto_80mq":  470, "lat": 38.1113, "lon": 15.6476},
    "Cosenza":           {"regione": "Calabria",              "prezzo_mq":  900, "affitto_80mq":  440, "lat": 39.2999, "lon": 16.2527},
    "Crotone":           {"regione": "Calabria",              "prezzo_mq":  800, "affitto_80mq":  420, "lat": 39.0808, "lon": 17.1288},
    "Vibo Valentia":     {"regione": "Calabria",              "prezzo_mq":  750, "affitto_80mq":  400, "lat": 38.6750, "lon": 16.1019},
    # ── SICILIA ────────────────────────────────────────────────────────────────
    "Palermo":           {"regione": "Sicilia",               "prezzo_mq": 1500, "affitto_80mq":  620, "lat": 38.1157, "lon": 13.3615},
    "Catania":           {"regione": "Sicilia",               "prezzo_mq": 1300, "affitto_80mq":  570, "lat": 37.5079, "lon": 15.0830},
    "Messina":           {"regione": "Sicilia",               "prezzo_mq": 1100, "affitto_80mq":  520, "lat": 38.1938, "lon": 15.5540},
    "Agrigento":         {"regione": "Sicilia",               "prezzo_mq":  900, "affitto_80mq":  440, "lat": 37.3111, "lon": 13.5765},
    "Siracusa":          {"regione": "Sicilia",               "prezzo_mq": 1200, "affitto_80mq":  550, "lat": 37.0755, "lon": 15.2866},
    "Trapani":           {"regione": "Sicilia",               "prezzo_mq": 1000, "affitto_80mq":  480, "lat": 38.0176, "lon": 12.5365},
    "Ragusa":            {"regione": "Sicilia",               "prezzo_mq": 1100, "affitto_80mq":  510, "lat": 36.9249, "lon": 14.7151},
    "Caltanissetta":     {"regione": "Sicilia",               "prezzo_mq":  800, "affitto_80mq":  420, "lat": 37.4903, "lon": 14.0514},
    "Enna":              {"regione": "Sicilia",               "prezzo_mq":  750, "affitto_80mq":  400, "lat": 37.5637, "lon": 14.2789},
    # ── SARDEGNA ───────────────────────────────────────────────────────────────
    "Cagliari":          {"regione": "Sardegna",              "prezzo_mq": 2000, "affitto_80mq":  780, "lat": 39.2238, "lon":  9.1217},
    "Sassari":           {"regione": "Sardegna",              "prezzo_mq": 1300, "affitto_80mq":  570, "lat": 40.7259, "lon":  8.5556},
    "Nuoro":             {"regione": "Sardegna",              "prezzo_mq":  900, "affitto_80mq":  440, "lat": 40.3219, "lon":  9.3310},
    "Oristano":          {"regione": "Sardegna",              "prezzo_mq": 1000, "affitto_80mq":  470, "lat": 39.9057, "lon":  8.5875},
    "Sud Sardegna":      {"regione": "Sardegna",              "prezzo_mq":  950, "affitto_80mq":  450, "lat": 39.3143, "lon":  9.3000},
}


def get_lista_citta():
    return sorted(PROVINCE.keys())


def get_dati_citta(citta: str) -> dict:
    return PROVINCE[citta]


def _applica_cache_mercato_online() -> None:
    """Sostituisce prezzi/affitti fallback con la cache online se disponibile."""
    cache_path = Path(__file__).parent / "data" / "market_data_immobiliare.json"
    if not cache_path.exists():
        return

    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return

    records = payload.get("records", {})
    for citta, valori in records.items():
        if citta not in PROVINCE:
            continue
        prezzo_mq = valori.get("prezzo_mq")
        affitto_mq_mese = valori.get("affitto_mq_mese")
        if not prezzo_mq or not affitto_mq_mese:
            continue
        PROVINCE[citta]["prezzo_mq"] = prezzo_mq
        PROVINCE[citta]["affitto_80mq"] = affitto_mq_mese * 80
        PROVINCE[citta]["fonte_dati"] = valori.get("source", payload.get("source"))
        PROVINCE[citta]["periodo_dati"] = valori.get("period", payload.get("period"))
        PROVINCE[citta]["url_dati"] = valori.get("url")


def get_market_data_meta() -> dict:
    cache_path = Path(__file__).parent / "data" / "market_data_immobiliare.json"
    if not cache_path.exists():
        return {
            "source": "Fallback interno indicativo",
            "period": "stima originaria 2024",
            "updated_at": None,
            "records_count": 0,
        }
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "source": "Fallback interno indicativo",
            "period": "cache non leggibile",
            "updated_at": None,
            "records_count": 0,
        }
    return {
        "source": payload.get("source", "Immobiliare.it"),
        "period": payload.get("period"),
        "updated_at": payload.get("updated_at"),
        "records_count": len(payload.get("records", {})),
    }


_applica_cache_mercato_online()
