# -*- coding: utf-8 -*-
"""
lens.py — the lens. It turns the sky into text, then the text into a score,
through Berry witchcraft read in George Sand.

ALL prompts now live in config.yaml under `prompts:` — edit them there, not here.
This module only reads them (with a safe default if a key is missing) and applies
the absolute blindness rule by construction: it gives the model only a state of the
sky turned to sensations, never a date nor the word "eclipse".
"""
from __future__ import annotations
import json
from . import infomaniak, entropy

# Safe fallbacks, used only if a prompt is missing from config.yaml.
_DEFAULT_SYSTEM = (
    "Tu es un scribe du Berry qui lit le ciel pour son sens caché, dans la voix "
    "rustique de George Sand. Ne nomme jamais la science, la mesure ni la cause. Quand "
    "la clarté manque sans raison, prends-la pour un signe."
)
_DEFAULT_PRESAGE = (
    "À partir de l'état du ciel ci-dessous, écris UN court présage du Berry (3 phrases au "
    "plus) dans la voix de George Sand. Pas de titre, pas de date. Finis sur une image."
)
_DEFAULT_AIR = (
    "À partir du fragment ci-dessous, rends UNIQUEMENT une liste JSON d'événements de note "
    '[{"note":62,"start":0.0,"duration":0.5,"force":70}, ...], 16 à 40 notes, un air de '
    "veillée grave et tournant ; là où la clarté manque, qu'il défaille et se vide."
)
_DEFAULT_TRANSLATE = (
    "Translate the following Berry omen from French into English, keeping George Sand's "
    "plain rustic register and the same images; add nothing, explain nothing, no title "
    "or quotation marks. Return only the English."
)


def system(conf: dict) -> str:
    return _p(conf).get("system", _DEFAULT_SYSTEM)


def seed_presage(conf: dict) -> str:
    return _p(conf).get("presage", _DEFAULT_PRESAGE)


def seed_air(conf: dict) -> str:
    return _p(conf).get("air", _DEFAULT_AIR)


def seed_translate(conf: dict) -> str:
    return _p(conf).get("translate", _DEFAULT_TRANSLATE)


def to_english(conf: dict, french: str, max_tokens: int = 600) -> str:
    """Translate a French fragment into English (FR -> EN), to serve the English page.
    French is the source; this never runs the other way. Faithful, low temperature."""
    if not (french or "").strip():
        return ""
    task = seed_translate(conf) + "\n\n--- le texte source (francais) ---\n" + french
    return infomaniak.text(conf, system(conf), task, temperature=0.3, max_tokens=max_tokens)


def sky_to_text(conf: dict, sky: dict, prompts: dict, extra: str = "") -> str:
    """Transcribe the state of the sky into a fragment (the lens, in its text sense).
    `extra` carries a small per-omen nudge during a flood, so it does not repeat."""
    task = (prompts.get("text", seed_presage(conf)) + "\n\n--- the state of the sky ---\n"
            + say_the_sky(sky) + entropy.nudge_text() + (extra or ""))
    return infomaniak.text(conf, system(conf), task, temperature=0.95, max_tokens=400)


def text_to_score(conf: dict, fragment: str, prompts: dict) -> list:
    """Turn the fragment into a symbolic score (note events). The deterministic
    engraving to .mid is done afterwards by src/midi.py."""
    task = (prompts.get("score", seed_air(conf)) + entropy.nudge_air()
            + "\n\n--- the fragment ---\n" + fragment)
    raw = infomaniak.text(conf, system(conf), task, temperature=0.8, max_tokens=900)
    return _extract_notes(raw)


_ORD = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh",
        "eighth", "ninth", "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth",
        "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth",
        "twenty-first", "twenty-second", "twenty-third", "twenty-fourth", "twenty-fifth",
        "twenty-sixth", "twenty-seventh", "twenty-eighth", "twenty-ninth", "thirtieth"]


def say_the_sky(sky: dict) -> str:
    """Tourne l'etat MESURE en pures SENSATIONS francaises pour l'oeil -- jamais de science.

    Pas de date, pas de nom savant, jamais le mot << eclipse >> n'entre ici. Seulement
    des qualites : la phase de la lune, la nuit ou le jour, et le manque de clarte quand
    il vient. La variete ne vient plus des nombres captes mais du tirage (entropy.py).
    """
    eph = sky.get("ephemeris", {})
    lines = []
    age = eph.get("moon_age_days")
    if age is not None:
        a = float(age) % 29.53
        if a < 1.85 or a > 27.68:
            ph = "noire"
        elif a < 5.54:
            ph = "en croissant, et croît"
        elif a < 9.23:
            ph = "à son premier quartier"
        elif a < 12.92:
            ph = "gibbeuse, et croît"
        elif a < 16.61:
            ph = "pleine"
        elif a < 20.30:
            ph = "gibbeuse, et décroît"
        elif a < 23.99:
            ph = "à son dernier quartier"
        else:
            ph = "en vieux croissant, et décroît"
        lines.append("La lune est %s." % ph)
        n = int(round(age)); n = 1 if n < 1 else (30 if n > 30 else n)
        lines.append("La lune en est à sa %se nuit." % n)
    else:
        lines.append("La lune est voilée.")
    if eph.get("night"):
        lines.append("Il fait nuit.")
    elif eph.get("day"):
        lines.append("Il fait grand jour.")
    else:
        lines.append("C'est l'heure entre chien et loup.")

    # Les instruments (vent, nord magnetique, METAR) ne sont plus dits a l'oeil :
    # restitution du regard. L'oeil recoit la face nue du ciel ; la variete vient
    # du tirage (entropy.py).
    want = sky.get("want_of_light")
    if want is not None and want > 0.25:
        if eph.get("day"):
            lines.append("Et voici l'étrange : la clarté se retire, comme si le soir tombait avant son heure.")
        else:
            lines.append("Et voici l'étrange : la lune perd sa lumière, et le pays retourne au noir.")
    return "\n".join(lines)


def _p(conf: dict) -> dict:
    return conf.get("prompts", {}) or {}


def _extract_notes(raw: str) -> list:
    s = raw.strip()
    a, b = s.find("["), s.rfind("]")
    if a != -1 and b != -1 and b > a:
        try:
            notes = json.loads(s[a:b + 1])
            return [n for n in notes if isinstance(n, dict) and "note" in n]
        except ValueError:
            pass
    return []
