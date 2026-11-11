"""BoardGameGeek par son API XML officielle (pas de navigateur : la page du site est protégée par Cloudflare).

    python -I -X utf8 bgg.py chercher "<nom du jeu>"        jeux trouvés : identifiant, nom, année
    python -I -X utf8 bgg.py fiche <identifiant ou lien BGG>  titre exact, autres noms, année, joueurs, auteurs,
                                                              illustrateurs, éditeurs, mécaniques, image, lien

L'API demande une clé personnelle (token BGG) : variable d'environnement BGG_TOKEN, sinon celle de l'app Règles de
jeu (%APPDATA%/regles-jeu/config.json, « bgg_cle »). Elle n'est jamais affichée. Sans clé : le dire, et lire BGG dans
le navigateur en dernier recours.
"""
import json, os, re, ssl, sys, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

API = "https://boardgamegeek.com/xmlapi2/"
TLS = ssl.create_default_context()
TLS.verify_flags &= ~ssl.VERIFY_X509_STRICT  # certains proxys d'entreprise : chaîne valide mais non « stricte »


def cle():
    c = os.environ.get("BGG_TOKEN", "").strip()
    if not c:
        try:
            with open(os.path.join(os.environ.get("APPDATA", ""), "regles-jeu", "config.json"), encoding="utf-8") as f:
                c = str(json.load(f).get("bgg_cle") or "").strip()
        except (OSError, ValueError):
            pass
    if not c:
        sys.exit("ERREUR : pas de clé BoardGameGeek (BGG_TOKEN, ou « Clé et infos BoardGameGeek » dans l'app).")
    return c


def get(fonction, **params):
    url = API + fonction + "?" + urllib.parse.urlencode(params)
    for essai in range(5):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {cle()}", "User-Agent": "regles-jeu"})
        try:
            with urllib.request.urlopen(req, timeout=30, context=TLS) as r:
                if r.status == 202:  # mise en file par BGG
                    time.sleep(3 + 2 * essai)
                    continue
                return ET.fromstring(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 401:
                sys.exit("ERREUR : clé BoardGameGeek refusée.")
            if e.code in (429, 500, 502, 503):
                time.sleep(8 * (essai + 1))
                continue
            sys.exit(f"ERREUR BGG {e.code}")
    sys.exit("ERREUR : BoardGameGeek ne répond pas.")


def chercher(nom):
    items = get("search", query=nom, type="boardgame").findall("item")
    if not items:
        print(f"Recherche « {nom} » : aucun jeu.")
    vus = set()
    for i in items:
        if i.get("id") in vus:
            continue
        vus.add(i.get("id"))
        n = i.find("name")
        an = i.find("yearpublished")
        print(f"- {i.get('id')} : {n.get('value') if n is not None else '?'}"
              f" ({an.get('value') if an is not None else 'année ?'}) https://boardgamegeek.com/boardgame/{i.get('id')}")


def fiche(ref):
    m = re.search(r"boardgame(?:expansion)?/(\d+)", ref) or re.fullmatch(r"\s*(\d+)\s*", ref)
    if not m:
        sys.exit("ERREUR : donner un identifiant BGG ou un lien https://boardgamegeek.com/boardgame/…")
    item = get("thing", id=m.group(1)).find("item")
    if item is None:
        sys.exit(f"ERREUR : jeu {m.group(1)} introuvable sur BGG.")
    val = lambda tag: (item.find(tag).get("value") if item.find(tag) is not None else "")
    noms = lambda t: [l.get("value") for l in item.findall("link") if l.get("type") == t]
    print(f"Titre : {next((n.get('value') for n in item.findall('name') if n.get('type') == 'primary'), '?')}")
    autres = [n.get("value") for n in item.findall("name") if n.get("type") == "alternate"]
    if autres:
        print(f"Autres noms : {' | '.join(autres)}")
    print(f"Lien : https://boardgamegeek.com/boardgame/{item.get('id')}")
    print(f"Année : {val('yearpublished')}")
    print(f"Joueurs : {val('minplayers')} à {val('maxplayers')}")
    for titre, t in (("Auteurs", "boardgamedesigner"), ("Illustrateurs", "boardgameartist"),
                     ("Éditeurs", "boardgamepublisher"), ("Mécaniques", "boardgamemechanic"),
                     ("Catégories", "boardgamecategory")):
        print(f"{titre} : {', '.join(noms(t)) or '—'}")
    print(f"Image : {(item.findtext('image') or '').strip() or '—'}")


if __name__ == "__main__":
    actions = {"chercher": chercher, "fiche": fiche}
    if len(sys.argv) != 3 or sys.argv[1] not in actions:
        sys.exit(__doc__)
    actions[sys.argv[1]](sys.argv[2])
