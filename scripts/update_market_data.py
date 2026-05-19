"""Aggiorna prezzi vendita/affitto da Immobiliare.it.

Il comando genera data/market_data_immobiliare.json. L'app usa quel file come
fonte primaria, mantenendo dati.py come fallback se il download fallisce.
"""

from __future__ import annotations

import html
import json
import re
import sys
import random
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    from curl_cffi import requests
    IMPERSONATE = "chrome120"
except ImportError:
    import requests  # type: ignore[no-redef]
    IMPERSONATE = None

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dati import PROVINCE  # noqa: E402


OUT_PATH = ROOT / "data" / "market_data_immobiliare.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.immobiliare.it/",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

REGION_SLUGS = {
    "Abruzzo": "abruzzo",
    "Basilicata": "basilicata",
    "Calabria": "calabria",
    "Campania": "campania",
    "Emilia-Romagna": "emilia-romagna",
    "Friuli-Venezia Giulia": "friuli-venezia-giulia",
    "Lazio": "lazio",
    "Liguria": "liguria",
    "Lombardia": "lombardia",
    "Marche": "marche",
    "Molise": "molise",
    "Piemonte": "piemonte",
    "Puglia": "puglia",
    "Sardegna": "sardegna",
    "Sicilia": "sicilia",
    "Toscana": "toscana",
    "Trentino-Alto Adige": "trentino-alto-adige",
    "Umbria": "umbria",
    "Valle d'Aosta": "valle-d-aosta",
    "Veneto": "veneto",
}

CITY_SLUG_OVERRIDES = {
    "Bolzano": "bolzano-bozen",
    "Forli": "forli",
    "Forlì": "forli",
    "La Spezia": "la-spezia",
    "Massa": "massa",
    "Monza": "monza",
    "Pesaro": "pesaro",
    "Reggio Emilia": "reggio-nell-emilia",
    "Sud Sardegna": "carbonia",
    "Verbania": "verbania",
}


@dataclass(frozen=True)
class MarketRecord:
    city: str
    prezzo_mq: int
    affitto_mq_mese: float
    period: str
    url: str


def slugify(value: str) -> str:
    value = CITY_SLUG_OVERRIDES.get(value, value)
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value


def parse_italian_number(value: str) -> float:
    cleaned = value.replace(".", "").replace(",", ".").replace(" ", "")
    return float(cleaned)


def extract_market_values(page: str, city: str, url: str) -> MarketRecord:
    text = html.unescape(page)
    period_match = re.search(r"A ([A-ZÀ-Ù][a-zà-ù]+ \d{4})", text)
    period = period_match.group(1) if period_match else "periodo non rilevato"

    sale_match = re.search(
        r"immobili residenziali in vendita.*?<strong>€\s*([\d.]+)\s+al metro quadro",
        text,
        flags=re.S,
    )
    rent_match = re.search(
        r"immobili residenziali in affitto.*?<strong>€\s*([\d.,]+)\s+al mese per metro quadro",
        text,
        flags=re.S,
    )
    if not sale_match or not rent_match:
        raise ValueError("prezzi vendita/affitto non trovati nella pagina")

    return MarketRecord(
        city=city,
        prezzo_mq=round(parse_italian_number(sale_match.group(1))),
        affitto_mq_mese=round(parse_italian_number(rent_match.group(1)), 2),
        period=period,
        url=url,
    )


def candidate_urls(city: str, region: str) -> Iterable[str]:
    region_slug = REGION_SLUGS[region]
    city_slug = slugify(city)
    yield f"https://www.immobiliare.it/mercato-immobiliare/{region_slug}/{city_slug}/"


def fetch_city(session, city: str, region: str) -> MarketRecord:
    errors = []
    for url in candidate_urls(city, region):
        try:
            kwargs = {"timeout": 25}
            if IMPERSONATE:
                kwargs["impersonate"] = IMPERSONATE
            response = session.get(url, **kwargs)
            if response.status_code == 403:
                errors.append(f"{url}: 403 bloccato")
                continue
            if response.status_code == 404:
                errors.append(f"{url}: 404")
                continue
            response.raise_for_status()
            return extract_market_values(response.text, city, url)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{url}: {exc}")
    raise RuntimeError("; ".join(errors))


def main() -> int:
    if IMPERSONATE:
        print(f"Modalità: curl_cffi (impersonate={IMPERSONATE}) — bypass bot detection attivo")
    else:
        print("Modalità: requests standard (installa curl_cffi per bypass bot detection)")
    session = requests.Session()
    session.headers.update(HEADERS)
    # Visita la homepage per ottenere cookies validi prima di iniziare
    try:
        session.get("https://www.immobiliare.it/", timeout=15, **({"impersonate": IMPERSONATE} if IMPERSONATE else {}))
        time.sleep(random.uniform(2, 4))
    except Exception:
        pass

    records: dict[str, dict] = {}
    failures: dict[str, str] = {}
    periods: dict[str, int] = {}

    cities = sorted(PROVINCE.items())
    for index, (city, data) in enumerate(cities, start=1):
        try:
            record = fetch_city(session, city, data["regione"])
            records[city] = {
                "prezzo_mq": record.prezzo_mq,
                "affitto_mq_mese": record.affitto_mq_mese,
                "affitto_80mq": round(record.affitto_mq_mese * 80),
                "period": record.period,
                "source": "Immobiliare.it - mercato immobiliare",
                "url": record.url,
            }
            periods[record.period] = periods.get(record.period, 0) + 1
            print(f"[{index:03d}] OK {city}: {record.prezzo_mq} €/mq, {record.affitto_mq_mese} €/mq/mese")
        except Exception as exc:  # noqa: BLE001
            failures[city] = str(exc)
            print(f"[{index:03d}] FAIL {city}: {exc}")
        time.sleep(random.uniform(1.8, 3.8))

    period = max(periods, key=periods.get) if periods else None
    min_required = max(10, int(len(cities) * 0.75))
    if len(records) < min_required:
        print(
            f"\nDataset incompleto: {len(records)}/{len(cities)} record. "
            "Non sovrascrivo la cache usata dall'app."
        )
        return 1

    payload = {
        "source": "Immobiliare.it - mercato immobiliare",
        "source_note": "Prezzi richiesti per immobili residenziali pubblicati nelle pagine Mercato immobiliare.",
        "period": period,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "records": records,
        "failures": failures,
    }

    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nScritti {len(records)} record in {OUT_PATH}")
    if failures:
        print(f"Falliti {len(failures)} record: {', '.join(sorted(failures))}")
    return 0 if records else 1


if __name__ == "__main__":
    raise SystemExit(main())
