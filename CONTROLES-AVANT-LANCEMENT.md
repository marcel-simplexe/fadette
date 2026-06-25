# Fadette — Contrôles avant lancement (1er juillet 2026)

Pré-vol à dérouler avant la naissance de la machine. Le plus court chemin pour la
plupart des points : `python tools/check_feeds.py` (teste endpoint + parsing d'un
coup). Tout doit passer en `[ ok ]`, **sauf TESS** qui reste à câbler.

---

## 0. Préalables — dépôt et secrets

- [ ] Dépôt GitHub **public** (Actions gratuites + Pages auto-hébergées).
- [ ] **GitHub Pages** activé, source = dossier `docs/`.
- [ ] **Secrets** définis : `INFOMANIAK_TOKEN`, `INFOMANIAK_PRODUCT_ID`.
- [ ] `pip install -r requirements.txt` (mido, ephem, PyYAML) sans erreur.

## 1. Captation des données — `python tools/check_feeds.py`

- [ ] **RTE solaire** : `national_mw` revient. (Champ `solaire` en MW, MAJ tous les ¼ h, quota 50 000 appels/mois — la machine en consomme ~1 400 sur deux mois.)
- [ ] **NOAA SWPC** (vent solaire / Kp / X-ray) : les valeurs reviennent.
- [ ] **METAR** : la chaîne LFLD → LFOA → LFLX répond.
- [ ] **Infomaniak** : `mistral24b` ET `swiss-ai/Apertus-70B-Instruct-2509` présents dans la liste des modèles ; une complétion d'un mot répond.
- [ ] **TESS** *(le seul vrai chantier)* : choisir une station de site sombre espagnol sur `tess.dashboards.stars4all.eu`, lire l'API réelle (`STARS4ALL/photometer-api`, docs `photometer.docs.apiary.io`) pour le vrai base URL + la route « dernière lecture » + les noms de champs, remplacer `STARS_TO_SET` dans `config.yaml`, ajuster `sky_brightness` si la route diffère.
      *Non bloquant — le filet calculé couvre la lunaire — mais requis pour l'empreinte **observée** du 28 août.*

## 2. Sensibilité aux éclipses

- [ ] **Filet calculé** (dans check_feeds) : `want ≈ 0,89` au 12 août 18:15 UTC.
- [ ] **Répétition à blanc** : rejouer `sky.state` + `tempo.how_many` sur le 12 août ~18:00 UTC → confirmer le **flot** (≈ 6 présages, contre 0-1 d'ordinaire) ; sur le 28 août ~04:42 UTC → constater que la lunaire reste marginale (lune à ~4°, aube).
- [ ] **Décision cadence** : garder « toutes les 2 h » (solaire capté à 18:00, lunaire ratée) **ou** resserrer (capte mieux le pic et la lunaire, mais casse le « toutes les deux heures » inscrit dans le récit). *À trancher.*
- [ ] **Calibration** : une fois RTE/TESS câblés, confronter les seuils (`×700` du solaire, `msas 19–22`, `want_surge 14`, `want_power 2`) aux vraies valeurs.

## 3. Fonctionnement technique

- [ ] `python -m py_compile src/*.py` → OK.
- [ ] `python -m src.render` → régénère `docs/` sans erreur (état vide avant le 1er juillet : normal).
- [ ] **Bout-en-bout** : un `workflow_dispatch` (onglet *Actions*) ou `python -m src.conductor` avec les secrets → un souffle réel. Vérifier qu'un **présage** + un **air** (.mid + lecture navigateur) + un **augure** sortent, et que le **commit** se fait.
- [ ] **Le son** : ouvrir `fadette-poc-standalone.html`, cliquer « hear the air » → ça joue (anches + bourdon tonique/quinte). *Invérifiable hors navigateur — à faire à la main.*

## 4. Identité, anonymat, cécité

- [ ] Nom « **Benjamin Gayte** » absent partout. *(vérifié : sources, texte et métadonnées PDF, git config, User-Agent)*
- [ ] **Pied de page** = « Fadette, Présages du Berry · Marcel Simplexe · 2026 » (site FR/EN + standalone).
- [ ] Aucune signature de l'outil de génération (nom de l'assistant ou de son éditeur) nulle part dans le dépôt. *(vérifié)*
- [ ] **Cécité** : aucune date ni le mot « eclipse » dans les prompts ; l'éphéméride ne livre que la phase. *(verrouillé)*

## 5. Pendant la vie de la machine

- [ ] **1er juillet** : premier souffle — vérifier le premier commit et le site en ligne.
- [ ] **12 août** (éclipse solaire) : surveiller le flot vers **18:00–18:30 UTC**.
- [ ] **28 août** (éclipse lunaire) : marginale depuis le Berry — ne pas s'étonner d'une réaction faible.
- [ ] **31 août** : la nouvelle (Apertus) se génère, puis la machine se tait.

---

## Commandes utiles

```bash
# Pré-vol complet (endpoint + parsing + Infomaniak + filet calculé)
python tools/check_feeds.py
INFOMANIAK_TOKEN=... INFOMANIAK_PRODUCT_ID=... python tools/check_feeds.py

# Test express des sens (une valeur = ok ; None = cassé)
python3 -c "from src import feeds, conductor as c; k=c.load_config(); [print(n, fn(k)) for n,fn in [('solaire',feeds.grid_solar),('kp',feeds.kp),('xray',feeds.xray),('metar',feeds.metar),('tess',feeds.sky_brightness)]]"

# Curl bruts
curl -s "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=1" | grep -i solaire
curl -s "https://aviationweather.gov/api/data/metar?ids=LFLD&format=raw&hours=2"
curl -s -H "Authorization: Bearer $INFOMANIAK_TOKEN" "https://api.infomaniak.com/2/ai/$INFOMANIAK_PRODUCT_ID/openai/v1/models" | python3 -c "import sys,json; print([m['id'] for m in json.load(sys.stdin)['data']])"
```
