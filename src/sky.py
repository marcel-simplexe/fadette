# -*- coding: utf-8 -*-
"""
sky.py — "what the sky is doing", at an instant, seen from the Berry.

We gather the cosmic texture, the daylight (RTE), the nightlight (TESS), the
Berry's sky (METAR), and the computed context (ephemeris: phase, altitudes). Then
we decide on an OBSERVED "want of light": by day from the RTE solar collapse, by
night from the TESS brightness drop.

The gift (calculation) only steps in as a FALLBACK: if the observation is mute or
ambiguous (a missing feed, clouds, a low moon), we take the computed value so the
eclipse is not missed. The provenance is traced ("observed" / "fallback-gift") in
the archive — but the lens itself receives only a state, never a date.
"""
from __future__ import annotations
import datetime as dt
from . import feeds, ephemeris, gift


def _safe(fn, *a):
    """A sense that fails returns nothing, never an exception that kills the breath."""
    try:
        return fn(*a)
    except Exception:
        return None


def state(conf: dict, when_utc: dt.datetime | None = None) -> dict:
    when_utc = when_utc or dt.datetime.now(dt.timezone.utc)
    lat, lon = conf["place"]["latitude"], conf["place"]["longitude"]

    eph = ephemeris.read(lat, lon, when_utc)
    cosmic = {"solar_wind": _safe(feeds.solar_wind, conf), "kp": _safe(feeds.kp, conf), "xray": _safe(feeds.xray, conf)}
    day_light = _safe(feeds.grid_solar, conf)
    night_light = _safe(feeds.sky_brightness, conf)
    berry = _safe(feeds.metar, conf)

    want_obs, source = _observed_want(eph, day_light, night_light)

    computed = gift.want_of_light(lat, lon, when_utc) if conf["gift"]["active"] else {}
    want, prov = want_obs, source
    if conf["gift"]["active"]:
        trig = conf["gift"].get("trigger", 0.15)
        if want_obs is None or (computed.get("want_of_light", 0) - (want_obs or 0)) > trig:
            want = computed.get("want_of_light", want_obs)
            prov = "fallback-gift"

    return {
        "instant_utc": when_utc.isoformat(timespec="minutes"),
        "ephemeris": eph,
        "cosmic": cosmic,
        "day_light": day_light,
        "night_light": night_light,
        "berry": berry,
        "want_of_light": round(want, 3) if want is not None else None,
        "want_source": prov,                 # observed | fallback-gift | undetermined
        "_computed_fallback": computed,       # traced, never handed to the lens
    }


def _observed_want(eph: dict, day_light, night_light):
    """Deduce the want of light from MEASURED feeds only, with the ephemeris for
    context (where the light ought to be). First-version thresholds; calibrate
    against the chosen station when wiring."""
    if eph["day"] and eph["sun_alt_deg"] > 2 and day_light and day_light.get("national_mw") is not None:
        expected = max(1.0, eph["sun_alt_deg"] * 700.0)   # MW, order of magnitude
        miss = 1.0 - min(1.0, day_light["national_mw"] / expected)
        return max(0.0, round(miss, 3)), "observed"
    if eph["night"] and eph["moon_illum"] > 0.8 and night_light and night_light.get("mag_arcsec2") is not None:
        msas = night_light["mag_arcsec2"]                 # ~19 full-moon-clear ; ~22 dark
        miss = min(1.0, max(0.0, (msas - 19.0) / 3.0))
        return round(miss, 3), "observed"
    return None, "undetermined"
