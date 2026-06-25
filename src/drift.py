# -*- coding: utf-8 -*-
"""
drift.py — the lens drifts, one notch a day. This is the only re-prompting in the
machine: a single daily call rewrites the lens's own task prompt by one notch, on
that day's own fragments. The fragments themselves are never re-prompted - Fadette
keeps what the scribe says. Every state of the lens is historised.

Blind: the refiner is given neither date nor "eclipse". It looks at the day's
fragments and tightens the lens on its own matter - the witchcraft of the Berry.
"""
from __future__ import annotations
import datetime as dt
from . import memory, infomaniak
from . import lens

_DEFAULT_REFINER = (
    "Here is a scribe's current prompt, then the fragments he wrote today. Propose a "
    "slightly improved version: one notch closer to George Sand's voice and the "
    "witchcraft of the Berry. Tighten, sharpen, remove one softness. Return only the "
    "new prompt."
)


def one_notch(conf: dict, date: str | None = None) -> dict:
    cur = memory.read_lens()
    day = memory.read_day(date or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"))
    fragments = [b.get("presage", "") for b in day.get("breaths", []) if b.get("presage")]
    matter = "\n---\n".join(fragments) if fragments else "(no fragments today)"

    refiner = (conf.get("prompts", {}) or {}).get("refiner", _DEFAULT_REFINER)
    sys = lens.system(conf)
    new = dict(cur)
    new["notch"] = cur.get("notch", 0) + 1

    try:
        task = (refiner + "\n\n--- current prompt ---\n" + cur["text"]
                + "\n\n--- today's fragments ---\n" + matter)
        new["text"] = infomaniak.text(conf, sys, task, temperature=0.5, max_tokens=400)
    except Exception:
        pass   # a missed notch is no harm: the lens keeps its state

    try:
        task = (refiner + "\n\n--- current prompt (the air) ---\n" + cur["score"]
                + "\n\n--- today's fragments ---\n" + matter)
        new["score"] = infomaniak.text(conf, sys, task, temperature=0.4, max_tokens=400)
    except Exception:
        pass

    # traduire l'optique raffinee en anglais (affichage Original/Traduction) ; non bloquant
    try:
        new["text_en"] = lens.to_english(conf, new["text"])
    except Exception:
        pass
    try:
        new["score_en"] = lens.to_english(conf, new["score"])
    except Exception:
        pass

    memory.write_lens(new, date)
    return new
