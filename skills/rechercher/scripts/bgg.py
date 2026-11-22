"""BoardGameGeek par son API XML officielle (pas de navigateur : la page du site est protégée par Cloudflare).

    python -I -X utf8 bgg.py chercher "<nom du jeu>"        jeux trouvés : identifiant, nom, année
    python -I -X utf8 bgg.py fiche <identifiant ou lien BGG>  titre exact, autres noms, année, joueurs, auteurs,
                                                              illustrateurs, éditeurs, mécaniques, image, lien,
                                                              formats des cartes
    python -I -X utf8 bgg.py cartes <identifiant ou lien BGG> formats des cartes seuls (sans clé)

L'API demande une clé personnelle (token BGG) : variable d'environnement BGG_TOKEN, sinon celle de l'app Règles de
jeu (%APPDATA%/regles-jeu/config.json, « bgg_cle »). Elle n'est jamais affichée. Sans clé : le dire, et lire BGG dans
le navigateur en dernier recours.

Formats des cartes : relevés par la communauté de BGG (page « Sleeves » du jeu), lus par l'adresse JSON que cette page
utilise (api.geekdo.com, sans clé ni Cloudflare). Seul le jeu de cartes principal compte (pas les promos ni les ajouts) ;
plusieurs formats dans la boîte : tous donnés, avec leur nom quand BGG en a un. Plusieurs éditions relevées : la
première, les autres signalées. Une extension a sa propre fiche BGG : la lire par son identifiant.
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


def ident(ref):
    m = re.search(r"boardgame(?:expansion)?/(\d+)", ref) or re.fullmatch(r"\s*(\d+)\s*", ref)
    if not m:
        sys.exit("ERREUR : donner un identifiant BGG ou un lien https://boardgamegeek.com/boardgame/…")
    return m.group(1)


def mm(x):
    return f"{float(x):g}".replace(".", ",")


def formats_cartes(i):
    """Types de cartes du jeu de cartes principal : [(quantité, largeur, hauteur, nom)], et le nombre d'autres éditions."""
    url = "https://api.geekdo.com/api/cardsetsbygame?" + urllib.parse.urlencode({"objectid": i, "objecttype": "thing"})
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "regles-jeu"})
        with urllib.request.urlopen(req, timeout=30, context=TLS) as r:
            d = json.load(r) or {}
    except urllib.error.HTTPError as e:
        if e.code != 404:  # 404 : aucun relevé pour ce jeu
            return None, 0
        d = {}
    except (urllib.error.URLError, ValueError, TimeoutError):
        return None, 0  # pas de réponse : inconnu (à ne pas confondre avec « aucune carte relevée »)
    base = [s for s in d.get("cardSets") or [] if not s.get("addon")]
    if not base:
        return [], 0
    out = []
    for c in base[0].get("cardTypes") or []:
        try:
            out.append((int(c.get("quantity") or 0), c["width"], c["height"], (c.get("name") or "").strip()))
        except (KeyError, ValueError):
            continue
    return out, len(base) - 1


def ligne_cartes(i):
    types, autres = formats_cartes(i)
    if types is None:
        return "Cartes : ? (BGG ne répond pas)"
    if not types:
        return "Cartes : — (aucun format relevé sur BGG)"
    parts = [f"{n or '?'} cartes ({mm(l)} x {mm(h)} mm{f' : {nom}' if nom else ''})" for n, l, h, nom in types]
    note = f"   [+ {autres} autre(s) édition(s) relevée(s) sur BGG]" if autres else ""
    return "Cartes : " + ", ".join(parts) + note


def cartes(ref):
    print(ligne_cartes(ident(ref)))


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
    i = ident(ref)
    item = get("thing", id=i).find("item")
    if item is None:
        sys.exit(f"ERREUR : jeu {i} introuvable sur BGG.")
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
    print(ligne_cartes(i))


if __name__ == "__main__":
    actions = {"chercher": chercher, "fiche": fiche, "cartes": cartes}
    if len(sys.argv) != 3 or sys.argv[1] not in actions:
        sys.exit(__doc__)
    actions[sys.argv[1]](sys.argv[2])
