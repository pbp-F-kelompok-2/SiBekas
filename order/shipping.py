"""Shipping rate and location service using AgenWebsite Rate API."""

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

DEFAULT_LOCATIONS = [
    {"id": "16424", "postal_code": "16424", "label": "Depok, Beji, Pondok Cina (Kampus UI), 16424", "city": "Depok"},
    {"id": "16425", "postal_code": "16425", "label": "Depok, Beji, Kukusan (Area Kos UI), 16425", "city": "Depok"},
    {"id": "12620", "postal_code": "12620", "label": "Jakarta Selatan, Jagakarsa, Srengseng Sawah, 12620", "city": "Jakarta Selatan"},
    {"id": "10110", "postal_code": "10110", "label": "Jakarta Pusat, Gambir, 10110", "city": "Jakarta Pusat"},
    {"id": "12110", "postal_code": "12110", "label": "Jakarta Selatan, Kebayoran Baru, 12110", "city": "Jakarta Selatan"},
    {"id": "16111", "postal_code": "16111", "label": "Bogor, Bogor Tengah, 16111", "city": "Bogor"},
    {"id": "17111", "postal_code": "17111", "label": "Bekasi, Bekasi Barat, 17111", "city": "Bekasi"},
    {"id": "15111", "postal_code": "15111", "label": "Tangerang, Tangerang Kota, 15111", "city": "Tangerang"},
]

DEFAULT_QUOTES = [
    {
        "id": "jnt_ez",
        "courier": "J&T Express",
        "service": "Regular (EZ)",
        "cost": 9000,
        "cost_formatted": "Rp 9.000",
        "etd": "2-3 hari",
        "logo_url": "https://assets-agenwebsite.b-cdn.net/images/couriers/jnt.png",
        "code": "jnt_ez",
    },
    {
        "id": "sicepat_reg",
        "courier": "SiCepat",
        "service": "SiUntung / Reguler",
        "cost": 10000,
        "cost_formatted": "Rp 10.000",
        "etd": "1-2 hari",
        "logo_url": "https://assets-agenwebsite.b-cdn.net/images/couriers/sicepat.png",
        "code": "sicepat_reg",
    },
    {
        "id": "pos_reg",
        "courier": "POS Indonesia",
        "service": "Pos Nextday / Reguler",
        "cost": 12000,
        "cost_formatted": "Rp 12.000",
        "etd": "1-2 hari",
        "logo_url": "https://assets-agenwebsite.b-cdn.net/images/couriers/pos.png",
        "code": "pos_reg",
    },
]


def search_destinations(query=""):
    query_clean = (query or "").strip().lower()
    if not query_clean:
        return DEFAULT_LOCATIONS

    cache_key = f"agenwebsite:loc:{query_clean}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    base_url = getattr(settings, "AGENWEBSITE_BASE_URL", "https://api.agenwebsite.com/v1").rstrip("/")
    api_key = getattr(settings, "AGENWEBSITE_API_KEY", "awk_live_e6e09877d20c7e20409c3c486a979577")
    params = urllib.parse.urlencode({"q": query_clean})
    url = f"{base_url}/locations/search?{params}"

    headers = {
        "x-api-key": api_key,
        "User-Agent": "SiBekas/1.0",
        "Accept": "application/json",
    }

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = []
            for item in data.get("data", []):
                postal_code = item.get("postal_code") or ""
                label = item.get("label") or f"{item.get('subdistrict', '')}, {item.get('city', '')} {postal_code}".strip(", ")
                if postal_code and label:
                    results.append({
                        "id": postal_code,
                        "postal_code": postal_code,
                        "label": label,
                        "city": item.get("city", ""),
                    })
            if results:
                cache.set(cache_key, results, timeout=86400)
                return results
    except Exception as exc:
        logger.warning("Gagal memanggil API lokasi AgenWebsite: %s", exc)

    # Fallback to filtering local locations
    filtered = [
        loc for loc in DEFAULT_LOCATIONS
        if query_clean in loc["label"].lower() or query_clean in loc["postal_code"]
    ]
    return filtered or DEFAULT_LOCATIONS


def get_shipping_quotes(destination_postal_code, weight_grams=1000):
    destination = str(destination_postal_code or "").strip()
    if not destination or not destination.isdigit():
        return []

    weight = max(int(weight_grams or 1000), 100)
    cache_key = f"agenwebsite:rates:{destination}:{weight}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    base_url = getattr(settings, "AGENWEBSITE_BASE_URL", "https://api.agenwebsite.com/v1").rstrip("/")
    api_key = getattr(settings, "AGENWEBSITE_API_KEY", "awk_live_e6e09877d20c7e20409c3c486a979577")
    origin_postal_code = getattr(settings, "AGENWEBSITE_ORIGIN_POSTAL_CODE", "16424")

    payload = {
        "shipper": {"zipcode": origin_postal_code},
        "destination": {"zipcode": destination},
        "weight": weight,
        "couriers": ["jnt", "pos", "sicepat"],
    }

    req = urllib.request.Request(
        f"{base_url}/rates",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "SiBekas/1.0",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_rates = data.get("data", {}).get("rates", [])
            quotes = []
            for rate in raw_rates:
                service_name = rate.get("service_name", "")
                service_type = rate.get("service_type", "")
                cost = rate.get("cost", 0)

                # Skip cargo motor or hazardous goods
                if "motor" in service_name.lower() or "dangerous" in service_name.lower() or cost > 100000:
                    continue

                quote_id = f"{rate.get('courier_code')}_{rate.get('service_code')}"
                cost_int = int(cost)
                cost_fmt = rate.get("cost_formatted") or f"Rp {cost_int:,.0f}".replace(",", ".")
                quotes.append({
                    "id": quote_id,
                    "courier": rate.get("courier_name", "Kurir"),
                    "service": service_name,
                    "cost": cost_int,
                    "cost_formatted": cost_fmt,
                    "etd": rate.get("etd_text") or f"{rate.get('etd_min_days', 1)}-{rate.get('etd_max_days', 3)} hari",
                    "logo_url": rate.get("courier_logo_url", ""),
                    "code": rate.get("service_code", ""),
                })

            if quotes:
                quotes.sort(key=lambda x: x["cost"])
                cache.set(cache_key, quotes, timeout=3600)
                return quotes
    except Exception as exc:
        logger.warning("Gagal memanggil API rates AgenWebsite: %s", exc)

    # Fallback quotes
    return DEFAULT_QUOTES
