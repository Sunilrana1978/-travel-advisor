"""
tools.py — FunctionTools for the Travel Advisor multi-agent system.

Each plain Python function becomes an ADK FunctionTool.
Gemini reads the docstring + type hints to know when and how to call each tool.
No API keys required — Open-Meteo and CoinCap are both free & public.
"""

import json
import urllib.request
from typing import Optional

# ── Geocoding table ────────────────────────────────────────────────────────────
CITY_COORDS: dict[str, dict] = {
    "london":      {"lat": 51.5074,  "lon": -0.1278,  "country": "UK"},
    "tokyo":       {"lat": 35.6762,  "lon": 139.6503, "country": "Japan"},
    "paris":       {"lat": 48.8566,  "lon": 2.3522,   "country": "France"},
    "new york":    {"lat": 40.7128,  "lon": -74.0060, "country": "USA"},
    "dubai":       {"lat": 25.2048,  "lon": 55.2708,  "country": "UAE"},
    "sydney":      {"lat": -33.8688, "lon": 151.2093, "country": "Australia"},
    "rome":        {"lat": 41.9028,  "lon": 12.4964,  "country": "Italy"},
    "barcelona":   {"lat": 41.3851,  "lon": 2.1734,   "country": "Spain"},
    "amsterdam":   {"lat": 52.3676,  "lon": 4.9041,   "country": "Netherlands"},
    "singapore":   {"lat": 1.3521,   "lon": 103.8198, "country": "Singapore"},
    "bangkok":     {"lat": 13.7563,  "lon": 100.5018, "country": "Thailand"},
    "berlin":      {"lat": 52.5200,  "lon": 13.4050,  "country": "Germany"},
    "toronto":     {"lat": 43.6532,  "lon": -79.3832, "country": "Canada"},
    "istanbul":    {"lat": 41.0082,  "lon": 28.9784,  "country": "Turkey"},
    "mexico city": {"lat": 19.4326,  "lon": -99.1332, "country": "Mexico"},
    "cape town":   {"lat": -33.9249, "lon": 18.4241,  "country": "South Africa"},
    "mumbai":      {"lat": 19.0760,  "lon": 72.8777,  "country": "India"},
    "seoul":       {"lat": 37.5665,  "lon": 126.9780, "country": "South Korea"},
}

WMO_CODES: dict[int, str] = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️", 2: "Partly cloudy ⛅", 3: "Overcast ☁️",
    45: "Foggy 🌫️", 48: "Icy fog 🌫️",
    51: "Light drizzle 🌦️", 53: "Moderate drizzle 🌦️", 55: "Dense drizzle 🌧️",
    61: "Slight rain 🌧️", 63: "Moderate rain 🌧️", 65: "Heavy rain 🌧️",
    71: "Slight snow 🌨️", 73: "Moderate snow 🌨️", 75: "Heavy snow ❄️",
    80: "Rain showers 🌦️", 81: "Moderate showers 🌦️", 82: "Violent showers ⛈️",
    95: "Thunderstorm ⛈️", 96: "Thunderstorm w/ hail ⛈️", 99: "Heavy thunderstorm ⛈️",
}


def _outfit_advice(temp_c: float, wmo: int) -> str:
    rainy = wmo in {51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99}
    snowy = wmo in {71, 73, 75}
    if snowy:
        return "Heavy winter coat, thermal layers, waterproof boots, and gloves are essential."
    if temp_c < 5:
        return "Bundle up: heavy coat, scarf, and gloves — it's very cold."
    if temp_c < 12:
        return "Warm jacket or heavy sweater recommended." + (" Bring an umbrella." if rainy else "")
    if temp_c < 18:
        return "Light jacket or cardigan will keep you comfortable." + (" Rain jacket advised." if rainy else "")
    if temp_c < 24:
        return "T-shirts and light trousers are perfect." + (" Pack a compact umbrella." if rainy else "")
    if temp_c < 30:
        return "Light, breathable clothing — shorts and a tee will do nicely."
    return "Very hot! Lightweight, loose clothing, sunscreen, and stay hydrated."


# ── Tool 1: get_current_weather ────────────────────────────────────────────────
def get_current_weather(city: str) -> dict:
    """
    Fetches live weather conditions for a travel destination city.

    Use this tool when the user asks about:
    - Current weather at their destination
    - What clothes or items to pack
    - Whether to bring an umbrella or raincoat
    - Temperature, wind, or precipitation conditions

    Args:
        city: The destination city name (e.g., 'London', 'Tokyo', 'Paris').
              Supported: London, Tokyo, Paris, New York, Dubai, Sydney, Rome,
              Barcelona, Amsterdam, Singapore, Bangkok, Berlin, Toronto,
              Istanbul, Mexico City, Cape Town, Mumbai, Seoul.

    Returns:
        A dict with temperature_c, temperature_f, condition, wind_kmh,
        precipitation_chance, outfit_advice, and city/country info.
    """
    key = city.strip().lower()
    if key not in CITY_COORDS:
        supported = ", ".join(c.title() for c in sorted(CITY_COORDS))
        return {
            "status": "error",
            "message": f"City '{city}' is not in the supported list. Supported cities: {supported}.",
        }

    coord = CITY_COORDS[key]
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={coord['lat']}&longitude={coord['lon']}"
        f"&current_weather=true"
        f"&hourly=precipitation_probability"
        f"&forecast_days=1"
    )

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TravelAdvisorADK/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        cw = data.get("current_weather", {})
        temp_c = cw.get("temperature")
        wind = cw.get("windspeed")
        wmo = cw.get("weathercode", 0)
        condition = WMO_CODES.get(wmo, "Unknown")
        precip_prob = data.get("hourly", {}).get("precipitation_probability", [None])[0]

        return {
            "status": "ok",
            "city": city.title(),
            "country": coord["country"],
            "temperature_c": temp_c,
            "temperature_f": round(temp_c * 9 / 5 + 32, 1) if temp_c is not None else None,
            "wind_kmh": wind,
            "condition": condition,
            "precipitation_chance_pct": precip_prob,
            "outfit_advice": _outfit_advice(temp_c, wmo) if temp_c is not None else "N/A",
        }
    except Exception as exc:
        return {"status": "error", "message": f"Weather API error: {exc}"}


# ── Tool 2: get_exchange_rate ──────────────────────────────────────────────────
def get_exchange_rate(base_currency: str, target_currency: str) -> dict:
    """
    Fetches the live currency exchange rate between two fiat currencies.

    Use this tool when the user asks about:
    - Currency conversion or exchange rates
    - How far their money will go at a destination
    - Spending power, budget, or price comparisons between currencies
    - Converting a specific amount from one currency to another

    Args:
        base_currency: The source currency ISO code (e.g., 'USD', 'GBP', 'EUR').
        target_currency: The destination currency ISO code (e.g., 'EUR', 'JPY', 'AED').

    Returns:
        A dict with the exchange rate, inverse rate, and example conversion
        amounts (10, 50, 100, 500, 1000 units of the base currency).
    """
    url = "https://api.coincap.io/v2/rates"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TravelAdvisorADK/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        rates: dict[str, float] = {}
        for item in data.get("data", []):
            sym = item.get("symbol", "").lower()
            try:
                rates[sym] = float(item.get("rateUsd", 0))
            except (ValueError, TypeError):
                pass

        b = base_currency.strip().lower()
        t = target_currency.strip().lower()

        if b not in rates:
            return {"status": "error", "message": f"Currency '{base_currency.upper()}' not found."}
        if t not in rates:
            return {"status": "error", "message": f"Currency '{target_currency.upper()}' not found."}

        # 1 base = (base_usd_rate / target_usd_rate) target
        rate = rates[b] / rates[t]
        examples = {str(amt): round(amt * rate, 2) for amt in [10, 50, 100, 500, 1000]}

        return {
            "status": "ok",
            "base_currency": base_currency.upper(),
            "target_currency": target_currency.upper(),
            "exchange_rate": round(rate, 6),
            "inverse_rate": round(1 / rate, 6),
            "example_conversions": examples,
        }
    except Exception as exc:
        return {"status": "error", "message": f"Currency API error: {exc}"}


# ── Tool 3: list_supported_cities ──────────────────────────────────────────────
def list_supported_cities() -> dict:
    """
    Returns the list of cities supported by the weather tool.

    Use this tool when the user asks which cities or destinations are available,
    or when you need to check whether a city is supported before fetching weather.

    Returns:
        A dict with a list of supported city names and their countries.
    """
    return {
        "supported_cities": [
            {"city": city.title(), "country": info["country"]}
            for city, info in sorted(CITY_COORDS.items())
        ]
    }
