# Fadette

*A machine that watches the sky over the Berry, through a lens of Berry
witchcraft, through July and August 2026. On the 31st it writes a last story and
falls silent.*

By **Marcel Simplexe** — a name borne in honour of the Berry draughtsman **Marcel
Bascoulard** (1913–1978), the soil this work grew from: the justness of his gaze on the Berry,
and his greatness of spirit. Fadette is not the homage, but the occasion of one; it leans on no
part of his work. The machine's own name is George Sand's: *La Petite Fadette*, the little
village sorceress. Fadette is its own work — it carries its own theory.

---

## What it does

Through the day, Fadette captures the state of the sky over the Berry — the cosmic
texture (solar wind, the north, the sun's fire), the light reaching the ground by
day and the moon's light by night — and renders it in **three voices**:

1. **the presage** — a short Berry omen, written by a language model in George
   Sand's voice (rustic, measured, never naming a cause);
2. **the air** — a short veillée melody for bagpipe and hurdy-gurdy, composed by the
   model and engraved, note by note, into a `.mid` file by plain code;
3. **the augury** — a deterministic reading of the figures through a fixed table of
   signs (no model): *the Wild Hunt rides hard*, *a hand passes over the lamp*… It is
   still cast and archived, but — to restore the **regard** — no longer shown.

Each gaze is **drawn** fresh (`src/entropy.py`): where it falls, which of the Berry's
night-people may show (or none), in what musical colour — so no two repeat, even under
the same sky, and the captured numbers no longer drive the variety.

Once a day the **lens drifts one notch**: a single call rewrites its own prompt on
that day's fragments, and every state is archived. On **31 August** it composes a
single **nouvelle** of about twenty pages (a legend of the Berry), written by Apertus, the
Swiss sovereign model, in George Sand's manner — then it is done. The bare page is how it honours
Bascoulard now — his spirit, not his work, and never a generated image.

## The doctrine: blindness

The **body** of the machine (the scheduler) knows the calendar — the birth, the
death. The **eye** (the lens) never does. No prompt is given a date, nor the word
*eclipse*. The local ephemeris hands over only **phase** — never the geometry that
would betray an eclipse in advance.

So the two eclipses of August 2026 — the sun deeply bitten on the **12th**, the full
moon taken by shadow on the **28th** — cannot enter as announced facts. They enter
only as an **observed anomaly**: the light leaves, measured from the ground (the
grid's solar power by day, a dark-site photometer by night), and the lens writes a
day going out, for no reason it can name. The final nouvelle makes a **legend** of
it. The astronomical event becomes folklore. That is the whole point.

## How it runs

- **GitHub Actions** is the body: a cron fires the heartbeat every two hours — each
  beat uttering as many omens as the sky stirs, from one (or none) on a still night
  to a crowd when the light fails — and refines the lens nightly (23:30 UTC),
  committing the archive.
- **GitHub Pages** serves the site (`docs/`): **two static pages** titled *Présages du
  Berry* — English (`index.html`, the page a visitor meets first, **translated from
  the French at generation**) and French (`fr.html`, **the source**, never the other way), with a FR|EN toggle. Each is a
  deliberately **raw web 1.0** page (no CSS, web-safe palette, Times New Roman, a
  horizontal menu under the title that swaps the visible panel without scrolling, with
  prev/next to step between them — where a browser runs no script the panels stack and the
  menu jumps by anchor, the plain fallback) laid out as: the day's gazes, an earlier-days
  history (each gaze keeping its air), the drift of the prompts, and an *about*. They show
  only the **regard** — no captured number and no augury — and never part an air from its
  fragment. Before the first breath: *“Marcel Simplexe — absent until 1 July”*; at the
  first breath, the living journal.
- **Infomaniak AI Services** (sovereign, EU) provides the daily text (the lens) **and**
  the closing nouvelle, written by **Apertus**, the Swiss sovereign model, on the same
  host. Everything stays sovereign — one host, one token.

## Setup

See **OPERATING-MANUAL.md** — about thirty minutes, all clicks. One thing must be
confirmed against the live services: the **TESS station** (`config.yaml`). Infomaniak
carries both the daily text and the nouvelle (Apertus); confirm the model id once.

## Layout

```
config.yaml              the seed: place, window, schedule, feeds, blindness
src/                     the machine
  conductor.py           entry point — one breath (the body knows the calendar)
  sky.py / feeds.py      the senses (observation first)
  ephemeris.py           the local ephemeris (PHASE only — blind)
  gift.py                the computed "want of light" (a silent fallback net)
  lens.py                the prompts (system + seeds), the bare-sky transcription
  entropy.py             the per-gaze draw — variety, freed from the numbers
  infomaniak.py          the sovereign call (the daily text, and the finale)
  midi.py                the deterministic engraving of the score
  augury.py              the table of signs (deterministic, no model)
  drift.py               the daily re-prompting of the lens
  finale.py              the closing nouvelle (a chain, by Apertus)
  memory.py              the archive (nothing is erased)
  render.py              regenerates the two static web 1.0 pages (FR + EN) from the archive
docs/                    the web 1.0 site (index.html EN default + fr.html FR source + work/ + images/)
journal/ history/        the archive (source of truth; the lens snapshots)
```

*Marcel Simplexe, 2026. No date is spoken to the lens; what it sees, it takes for a sign.*

## License

The machine's **code** is under the **MIT License** (`LICENSE`). The **works** it
produces -- fragments, airs, the finale nouvelle, the plates -- together with the
page, the prompts and the theory of Fadette, are under **CC BY-NC-ND 4.0**
(`LICENSE-ART`): (c) Marcel Simplexe 2026. Read, copy, run; do not erase its signature.
