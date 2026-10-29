"""Server-side RajaOngkir Shipping Cost integration (Komerce direct search API)."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core import signing

BASE_URL = "https://rajaongkir.komerce.id/api/v1/"
QUOTE_MAX_AGE = 15 * 60


class ShippingError(ValueError):
    pass


def is_configured():
    origin = str(settings.RAJAONGKIR_ORIGIN_ID).strip()
    return bool(settings.RAJAONGKIR_API_KEY and origin.isdigit() and int(origin) > 0 and settings.RAJAONGKIR_COURIERS.strip())


def _request(endpoint, data=None):
    if not settings.RAJAONGKIR_API_KEY:
        raise ShippingError("Pengiriman kurir belum tersedia. Silakan pilih ambil di kampus UI.")
    encoded = urlencode(data).encode() if data is not None else None
    request = Request(BASE_URL + endpoint, data=encoded, headers={
        "key": settings.RAJAONGKIR_API_KEY,
        "Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded",
    })
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read(1_000_000))
        if not isinstance(payload, dict) or not isinstance(payload.get("meta"), dict) or payload["meta"].get("code") != 200 or not isinstance(payload.get("data"), list):
            raise ShippingError("Layanan pengiriman tidak tersedia untuk tujuan ini.")
        return payload["data"]
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, TypeError) as exc:
        raise ShippingError("Ongkir belum dapat dimuat. Coba lagi atau pilih ambil di kampus UI.") from exc


def get_destinations(query):
    """Look up IDs for either the collection point or a buyer's destination."""
    rows = _request("destination/domestic-destination?" + urlencode({"search": query, "limit": 10, "offset": 0}))
    try:
        destinations = [{"id": int(row["id"]), "label": str(row["label"])[:300]} for row in rows]
        if any(row["id"] <= 0 or not row["label"].strip() for row in destinations):
            raise ValueError
        return destinations
    except (KeyError, TypeError, ValueError) as exc:
        raise ShippingError("Data tujuan pengiriman tidak valid. Silakan coba lagi.") from exc


def search_destinations(query, user_id):
    return [{
        "label": row["label"],
        "token": signing.dumps({**row, "user": user_id}, salt="order.destination"),
    } for row in get_destinations(query)]


def calculate_quotes(destination_token, summary, user_id):
    if not is_configured():
        raise ShippingError("Pengiriman kurir belum tersedia. Silakan pilih ambil di kampus UI.")
    try:
        destination = signing.loads(destination_token, salt="order.destination", max_age=QUOTE_MAX_AGE)
        if destination["user"] != user_id:
            raise ValueError
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise ShippingError("Tujuan pengiriman kedaluwarsa. Cari kembali tujuanmu.") from exc
    rows = _request("calculate/domestic-cost", {
        "origin": settings.RAJAONGKIR_ORIGIN_ID, "destination": destination["id"],
        "weight": summary["weight_grams"], "courier": settings.RAJAONGKIR_COURIERS, "price": "lowest",
    })
    quotes = []
    try:
        for row in rows:
            cost = int(row["cost"])
            if cost < 0:
                raise ValueError
            quote = {
                "cost": cost, "service": f"{row['name']} · {row['service']}"[:150],
                "etd": str(row.get("etd", ""))[:100], "destination_id": destination["id"],
                "destination": destination["label"], "user": user_id,
                "fingerprint": summary["fingerprint"], "weight": summary["weight_grams"],
            }
            quotes.append({**quote, "token": signing.dumps(quote, salt="order.shipping")})
    except (KeyError, TypeError, ValueError) as exc:
        raise ShippingError("Data ongkir tidak valid. Silakan coba lagi.") from exc
    if not quotes:
        raise ShippingError("Belum ada kurir yang melayani tujuan ini.")
    return quotes


def validate_quote(token, summary, user_id):
    try:
        quote = signing.loads(token, salt="order.shipping", max_age=QUOTE_MAX_AGE)
        if quote["user"] != user_id or quote["fingerprint"] != summary["fingerprint"] or quote["weight"] != summary["weight_grams"]:
            raise ValueError
        return quote
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise ShippingError("Ongkir kedaluwarsa atau keranjang berubah. Hitung ongkir kembali.") from exc
