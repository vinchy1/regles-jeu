"""Boutique Golden Meeple (goldenmeeple.be) : recherche et lecture d'une page produit, depuis le contenu brut.

    python -I -X utf8 boutique_gm.py chercher "<nom du jeu>"    produits trouvés (lien, stock)
    python -I -X utf8 boutique_gm.py fiche <lien produit>        nom, image, auteurs, éditeur, joueurs, année…

Une recherche qui ne trouve qu'un produit arrive directement sur sa page : la fiche est alors affichée.
"""
import json, re, sys, urllib.parse, urllib.request

import lxml.html

SITE = "https://www.goldenmeeple.be"


def page(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.geturl(), lxml.html.fromstring(r.read(), base_url=r.geturl())


def produit_ld(d):
    for s in d.xpath('//script[@type="application/ld+json"]'):
        try:
            data = json.loads(s.text_content())
        except ValueError:
            continue
        for el in (data.get("@graph", [data]) if isinstance(data, dict) else data):
            if isinstance(el, dict) and el.get("@type") == "Product":
                return el
    return None


def afficher(url, d):
    p = produit_ld(d)
    if not p:
        sys.exit(f"ERREUR : pas de fiche produit lisible sur {url}")
    offres = p.get("offers") or [{}]
    offre = offres[0] if isinstance(offres, list) else offres
    image = p.get("image")
    image = image[0] if isinstance(image, list) else image
    if isinstance(image, dict):
        image = image.get("url")
    print(f"Produit : {p.get('name')}\nLien : {url}\nImage : {image}")
    print(f"Stock : {(offre.get('availability') or '?').rsplit('/', 1)[-1]}")
    for prop in p.get("additionalProperty", []):
        nom = prop.get("name", "").removeprefix("pa_")
        print(f"- {nom} : {prop.get('value')}")


def chercher(mot):
    url, d = page(f"{SITE}/?s={urllib.parse.quote_plus(mot)}&post_type=product")
    if "/produit/" in url:
        print("Un seul produit trouvé :\n")
        afficher(url, d)
        return
    # Vignettes des résultats (le menu du site contient aussi des liens /produit/, sans cette classe)
    liens = dict.fromkeys(a.get("href") for a in d.xpath('//a[contains(@class,"pushed") and contains(@href,"/produit/")]'))
    if not liens:
        print(f"Recherche « {mot} » : aucun produit.")
    for lien in liens:
        print(f"- {lien}")


def fiche(lien):
    if not re.match(r"https?://(www\.)?goldenmeeple\.be/produit/", lien):
        sys.exit("ERREUR : donner un lien https://www.goldenmeeple.be/produit/…")
    afficher(*page(lien))


if __name__ == "__main__":
    actions = {"chercher": chercher, "fiche": fiche}
    if len(sys.argv) != 3 or sys.argv[1] not in actions:
        sys.exit(__doc__)
    actions[sys.argv[1]](sys.argv[2])
