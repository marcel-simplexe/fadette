# -*- coding: utf-8 -*-
"""
tempo.py - the tempo of the machine is the tempo of the sky.

The scribe speaks when the sky moves him. Each breath (the cron heartbeat) the BODY
weighs how far the sky departs from calm - the troubled north (Kp), a solar flare, a
hurrying wind, and ABOVE ALL a failing of light - and that decides how many omens the
breath utters: one or none when the sky is still, several in a storm, a flood when the
light fails. The machine never knows it is an eclipse: the flood is only its answer to
the want of light, the same answer it would give to a freak aurora.

Like everything in the body, this reads numbers; the EYE never does. No date, no
learned name, never the word "eclipse" enters here either.
"""
from __future__ import annotations


def _flare_num(xray) -> float:
    """Turn a solar X-ray reading into 0 (quiet) / 1 (M) / 2 (X), defensively."""
    if not xray:
        return 0.0
    cls = None
    if isinstance(xray, dict):
        cls = xray.get("class") or xray.get("flare_class") or xray.get("level")
        if cls is None:
            flux = xray.get("flux_w_m2") or xray.get("flux")
            try:
                f = float(flux)
                if f >= 1e-4:
                    return 2.0
                if f >= 1e-5:
                    return 1.0
            except (TypeError, ValueError):
                return 0.0
            return 0.0
    elif isinstance(xray, str):
        cls = xray
    if isinstance(cls, str) and cls[:1].upper() in ("M", "X"):
        return 2.0 if cls[:1].upper() == "X" else 1.0
    return 0.0


def agitation(sky: dict, conf: dict) -> float:
    """How far the sky departs from calm, measured in omens. 0 = perfectly still."""
    c = conf.get("tempo", {})
    cosmic = sky.get("cosmic") or {}
    kp = cosmic.get("kp") or 0.0
    wind = ((cosmic.get("solar_wind") or {}).get("speed_km_s")) or 0.0
    flare = _flare_num(cosmic.get("xray"))
    want = sky.get("want_of_light") or 0.0
    return (c.get("per_kp", 0.5) * max(0.0, float(kp) - c.get("calm_kp", 2))
            + c.get("per_wind", 1.0) * max(0.0, (float(wind) - c.get("calm_wind", 450)) / c.get("wind_span", 130))
            + c.get("per_flare", 1.5) * flare
            + c.get("want_surge", 11.0) * (float(want) ** c.get("want_power", 2)))


def how_many(sky: dict, conf: dict, is_vespers: bool = False) -> int:
    """How many omens this breath should utter, given the sky's agitation."""
    c = conf.get("tempo", {})
    floor = c.get("vespers_floor", 1) if is_vespers else 0
    n = round(floor + agitation(sky, conf))
    return max(0, min(int(n), int(c.get("cap", 12))))
