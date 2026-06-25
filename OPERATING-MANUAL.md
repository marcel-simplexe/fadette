# Fadette — Operating Manual

About thirty minutes, all clicks. The goal: a permanent public URL you can send to
the biennale **before 26 June**, which shows *“Marcel Simplexe — absent until 1
July”* now and comes alive on its own on **1 July**.

> **The one rule, above all:** never write a **date**, nor the word **eclipse**, into
> a prompt. Fadette is built blind on purpose; the eclipse must enter only as an
> observed anomaly. Section 7 says where every prompt is and how to change it safely.

---

## 0. What you need

- A GitHub account (free).
- An Infomaniak **AI Services** product: a **token** and a **product id**.
- Five minutes in `config.yaml`.

## 1. Put Fadette on GitHub (5 min)

1. Create a repository, e.g. `fadette` (public, so Pages is free).
2. Upload the whole contents of this folder (or `git push` it).
3. Confirm: `config.yaml`, `src/`, `docs/`, `journal/`, `history/`, and
   `.github/workflows/fadette.yml` are present.

## 2. The two secrets (3 min)

Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Name | Value |
|---|---|
| `INFOMANIAK_TOKEN` | your Infomaniak AI Services token |
| `INFOMANIAK_PRODUCT_ID` | your AI Services product id |

They are read from the environment; they never appear in the code or the archive.

## 3. Confirm the night station (5 min)

One thing must match your chosen station:

1. **The night station (the lunar eclipse).** In `config.yaml`, set
   `feeds.tess_station` to a real **Spanish dark-site** TESS / STARS4ALL station
   (see the IoT-EELab dashboard at `tess.stars4all.eu`), and confirm the per-station
   reading path in `src/feeds.py:sky_brightness`. *Until set, a harmless fallback is
   used and the computed gift covers the 28th.*

The text endpoint needs no change (Infomaniak's standard OpenAI-compatible one). Set the two
model ids to models your product exposes: `infomaniak.text_model` (the daily voice) and
`finale.model` (the nouvelle — Apertus by default, the Swiss sovereign model). Both run on the
same sovereign host; confirm their ids via the models endpoint. Everything else in `config.yaml`
— the Berry, 1 July–31 August, the schedule — is correct.

## 4. Turn on GitHub Pages (3 min)

**Settings → Pages** → Source: **Deploy from a branch** → Branch **main**, folder
**/docs** → Save. After a minute you get a URL like
`https://<you>.github.io/fadette/`. Open it: the **“absent until 1 July”** sign and
the schedule. **This is the link to send to the biennale** — you never send another;
the same URL opens on its own.

## 5. Test one breath now, then undo (5 min)

The machine is silent outside its window, so to see a real breath before July:

1. In `config.yaml`, **temporarily** set `window.birth` to **today's date**.
2. Commit. **Actions → fadette → Run workflow**.
3. After ~1 minute, a commit *“breath …”* appears, with a `journal/<today>.json`, a
   `.mid` under `docs/work/`, and the two pages regenerated. Reload your URL: the
   **living journal** — the day's gazes, each with a playable air (no number, no augury).
4. **Undo step 1** (set `window.birth` back to `2026-07-01`) and commit. The pages
   return to the “absent” sign until July.

If a breath fails, the run log shows where — almost always a secret or an Infomaniak
model/endpoint to adjust.

## 6. From 1 July it runs itself

No further action. Each breath is a commit; the page updates within a minute or two.

| What | UTC | Paris (summer) |
|---|---|---|
| a breath (the heartbeat) | every 2 h | every 2 h |
| the lens is refined | 23:30 | 01:30 |

Each heartbeat utters as many omens as the sky stirs: one (or none) on a still night,
several when it is troubled, a crowd when the light fails. The cadence is set by
`tempo` in `config.yaml`.

The **finale** — one dense nouvelle of about twenty pages, written by Apertus — lands in the small hours of
**1 September** (the 23:30 UTC run of 31 August). Then Fadette falls silent; the page
stays up, the journal closed by the finale.

---

## 7. Acting on the prompts

Every instruction the language model receives lives in **`config.yaml`**, under
`prompts:`. Edit them there — no code to touch.

> **The rule, again:** never write a **date**, nor the word **eclipse**, into any
> prompt. That blindness is the work.

The seven prompts, what each does, and when it fires:

| key in `config.yaml` | what it does | when |
|---|---|---|
| `prompts.system` | the persona — a scribe of the Berry in George Sand's voice. Used by **every** text call; change it to change the voice everywhere. | every call |
| `prompts.presage` | turns the sky into the day's **fragment** (the omen). | every breath |
| `prompts.air` | turns the fragment into a **score** of notes. Keep it asking for a bare JSON list `[{"note":…,"start":…,"duration":…,"force":…}]`. | every breath |
| `prompts.refiner` | the daily **re-prompt** — rewrites `presage` and `air` one notch. Fires only if `lens.drift` is true. | once a day |
| `prompts.finale.matter` | distils the month's omens into the **matter** of a tale. | the last day |
| `prompts.finale.frame` | lays the **frame** of the nouvelle in `finale.movements` titled movements (nine by default). | the last day |
| `prompts.finale.movement` | writes **each movement**, upon the last. Keep `{n}`, `{total}`, `{frame}`, `{written}` — the machine fills them in. | the last day (one call each) |

Two levers that govern *how* the prompts are used, also in `config.yaml`:

- **`lens.drift`** — whether the lens refines itself daily.
  - `true` (default): the machine rewrites `presage` / `air` one notch a day; the
    **live** prompt then lives in `history/lens.json`. To change the live prompt
    mid-run, edit `history/lens.json` (its `text` / `score` fields); to start over from
    your `config.yaml` seeds, delete `history/lens.json`.
  - `false`: the machine never refines — **`config.yaml` is authoritative.** Edit
    `prompts.presage` / `prompts.air` and they take effect on the next breath. Use this
    to keep the voice fixed exactly as written.
- **`infomaniak.text_model`** — which model writes the daily text (the presages and the
  airs); **`finale.model`** — which model writes the closing nouvelle (Apertus by default). Not
  prompts, but the other half of the voice.

One more thing you can shape, in **`src/lens.py`**, the function **`say_the_sky`**: it
turns the measured numbers into the bare **sensations** the model is shown (“a hard,
hurrying wind from on high”, “the brightness fails as if evening were falling before
its hour”). Editing those phrasings changes *what the model sees* before it writes —
the transcription itself. Same rule: sensations only, never a date or “eclipse”.

That is the full inventory.

## 8. Good to know

- **The cron is best-effort.** GitHub Actions can start a few minutes late, sometimes
  more under load. The page says so.
- **The served files** (`.mid`) live under `docs/work/` so Pages serves
  them. Don't move them out of `docs/`.
- **The archive is the truth.** `journal/` and `history/` hold every breath and every
  state of the lens, dated. The two pages — `index.html` (English, the default landing, translated from the French) and
  `fr.html` (French, the source) — under `docs/` are regenerated from it at every
  breath.

*Marcel Simplexe, 2026.*
