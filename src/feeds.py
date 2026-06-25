# -*- coding: utf-8 -*-
"""
feeds.py — the machine's senses. No model here: we read, we do not think.

Four families:
  1. cosmic texture  — NOAA SWPC (solar wind, Bz, Kp, X-ray). BLIND to the eclipse.
  2. daylight        — RTE eCO2mix (solar power). Catches the SOLAR eclipse.
  3. nightlight      — TESS / STARS4ALL (sky brightness). Catches the LUNAR eclipse.
  4. the Berry's sky — METAR chain (the Berry -> Avord -> Chateauroux).

Every function is fault-tolerant: a feed that does not answer returns None, never
an exception that would kill the breath.
"""
from __future__ import annotations
import json
import urllib.request
import urllib.error

_UA = {"User-Agent": "fadette/1.0 (Marcel Simplexe; watching the sky over the Berry)"}
_TIMEOUT = 20


def _get_json(url: str):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=_TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return None


def _get_text(url: str):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=_TIMEOUT) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


# ---------------------------------------------------------------- 1. cosmic
def solar_wind(conf: dict) -> dict | None:
    plasma = _get_json(conf["feeds"]["solar_wind_plasma"])
    mag = _get_json(conf["feeds"]["solar_wind_mag"])
    out = {}
    if plasma and len(plasma) > 1:
        cols, *rows = plasma
        d = dict(zip(cols, rows[-1]))
        out["speed_km_s"] = _f(d.get("speed"))
        out["density"] = _f(d.get("density"))
    if mag and len(mag) > 1:
        cols, *rows = mag
        d = dict(zip(cols, rows[-1]))
        out["bz_nT"] = _f(d.get("bz_gsm"))
    return out or None


def kp(conf: dict):
    data = _get_json(conf["feeds"]["planetary_kp"])
    if data and len(data) > 1:
        return _f(data[-1][1])
    return None


def xray(conf: dict):
    data = _get_json(conf["feeds"]["xray_goes"])
    if isinstance(data, list) and data:
        return _f(data[-1].get("flux"))
    return None


# ------------------------------------------------------- 2. daylight (the sun)
def grid_solar(conf: dict) -> dict | None:
    """Solar power on the French grid (RTE eCO2mix), in MW. On 12 August at dusk
    this collapses toward zero before the ordinary nightfall: the measured
    fingerprint of the solar eclipse."""
    out = {}
    nat = _get_json(conf["feeds"]["rte_national"])
    if nat and nat.get("results"):
        for rec in nat["results"]:
            if rec.get("solaire") is not None:
                out["national_mw"] = _f(rec["solaire"])
                out["instant"] = rec.get("date_heure")
                break
    reg = _get_json(conf["feeds"]["rte_region"])
    if reg and reg.get("results"):
        for rec in reg["results"]:
            if rec.get("solaire") is not None:
                out["berry_mw"] = _f(rec["solaire"])
                break
    return out or None


# ------------------------------------------------------- 3. nightlight (the moon)
def sky_brightness(conf: dict) -> dict | None:
    """Night-sky brightness (mag/arcsec2) of a Spanish dark-site TESS station,
    with a cloud estimate. On the night of 28 August, over the full moon, this
    brightness drops: the (partial, from Europe) fingerprint of the lunar eclipse.
    First version: read the station's last reading. The exact per-station JSON
    endpoint is to confirm when wiring, on the IoT-EELab dashboard."""
    base, station = conf["feeds"]["tess_base"], conf["feeds"]["tess_station"]
    if station == "STARS_TO_SET":
        return {"_fallback": "TESS station not yet set — see config.yaml"}
    data = _get_json(f"{base}/api/readings/{station}/last")   # path to confirm
    if isinstance(data, dict):
        return {"mag_arcsec2": _f(data.get("magnitude") or data.get("msas")),
                "clouds_pct": _f(data.get("cloud") or data.get("clouds"))}
    return None


# ------------------------------------------------------- 4. the Berry's sky
def metar(conf: dict) -> dict | None:
    """The first station in the chain that answers with a fresh reading.
    the Berry (LFLD) -> Avord (LFOA) -> Chateauroux (LFLX). All in the Berry."""
    base = conf["feeds"]["metar_base"]
    for icao in conf["feeds"]["metar_chain"]:
        txt = _get_text(f"{base}?ids={icao}&format=raw&hours=2")
        if txt and txt.strip() and icao in txt:
            return {"station": icao, "metar": txt.strip().splitlines()[0]}
    return None


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None
