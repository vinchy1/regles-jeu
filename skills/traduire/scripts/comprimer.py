# -*- coding: utf-8 -*-
"""Version allégée d'un livret traduit, pour l'envoyer sur Discord (10 Mo maximum par fichier).

Usage : python -X utf8 comprimer.py "<livret.pdf>" [--max 10] [--sortie "<fichier.pdf>"] [--remplacer]
Écrit `<nom>_light.pdf` À CÔTÉ du livret : le livret en pleine qualité n'est jamais touché ni remplacé, la
version allégée est un fichier de plus, à n'envoyer que sur Discord.

1. Les dessins vectoriels répétés à l'identique (fond copié sur chaque page, qui ne diffère que par sa position)
   sont ramenés à un seul dessin partagé : rendu identique, souvent plusieurs Mo de gagnés.
2. Les images sont recompressées en JPEG, et ramenées à un dpi plus bas si elles sont très fines, en s'arrêtant
   au premier essai qui passe sous la limite. Jamais en dessous d'un plancher (150 dpi, qualité 70) : plus bas,
   les images deviennent illisibles.
3. Si aucun essai lisible ne passe, le livret est coupé en parties de pages consécutives
   (`<nom>_light_partie1.pdf`, `…_partie2.pdf`…), chacune sous la limite et compressée le moins possible.
Le texte reste du texte (vectoriel), net à l'écran comme à l'impression ; le script vérifie qu'il n'a pas bougé.
Livret déjà sous la limite : il le dit et ne fait rien."""
import glob, hashlib, os, re, sys
import pymupdf

LIMITE = 10e6  # 10 Mo : taille maximale d'un envoi Discord (lecture la plus stricte du Mo)
MARGE = 0.98   # viser un peu en dessous plutôt que de jouer avec la limite
# essais successifs (dpi visé, qualité JPEG), du plus fin au plus serré ; None = nettoyage seul, images intactes.
# Le dernier est le plancher : plus bas, les images d'un livret ne se lisent plus (Uncharted Passage, 11/2026 :
# illustrations et icônes en bouillie dans une version poussée jusqu'à 72 dpi). Plutôt couper en parties.
PASSES = [(None, None), (300, 92), (300, 85), (220, 80), (170, 72), (150, 70)]
PLANCHER = "150 dpi, qualité 70"
BONNES = 4  # les 4 premiers essais (jusqu'à 220 dpi, qualité 80) gardent les images nettes : couper le livret en
            # parties qui passent ainsi vaut mieux qu'un seul fichier aux images abîmées ; le plancher ne sert
            # que si aucun découpage ne passe avec eux
MAX_PARTIES = 10    # Discord : 10 pièces jointes au plus par message
DESSIN_MIN = 10_000  # octets : un dessin plus petit ne vaut pas la peine d'être partagé
OPTIONS = {"--max", "--sortie"}  # options suivies d'une valeur


def fail(msg):
    sys.exit(f"ERREUR : {msg}")


def taille(n):
    return f"{n / 1e6:.1f} Mo" if n >= 1e5 else f"{n / 1e3:.0f} Ko"


def opt(name, defaut=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else defaut


def fichiers():
    """Arguments qui ne sont ni une option ni la valeur d'une option."""
    out, i = [], 1
    while i < len(sys.argv):
        if sys.argv[i] in OPTIONS:
            i += 2
            continue
        if not sys.argv[i].startswith("--"):
            out.append(sys.argv[i])
        i += 1
    return out


def texte(path):
    """Texte de chaque page, pour vérifier que la compression ne touche qu'aux images."""
    doc = pymupdf.open(path)
    out = [p.get_text() for p in doc]
    doc.close()
    return out


NOMS = {1: "/DeviceGray", 3: "/DeviceRGB", 4: "/DeviceCMYK"}


def composantes_jpeg(raw):
    """Nombre de composantes d'un JPEG (1 gris, 3 RVB, 4 CMJN), lu dans son en-tête SOF ; None si illisible."""
    i = 2
    while i + 9 < len(raw) and raw[i] == 0xFF:
        marque, long = raw[i + 1], int.from_bytes(raw[i + 2:i + 4], "big")
        if 0xC0 <= marque <= 0xCF and marque not in (0xC4, 0xC8, 0xCC):
            return raw[i + 9]
        i += 2 + long
    return None


def composantes_espace(doc, xref):
    """Nombre de composantes de l'espace de couleur d'une image (ICCBased : son /N) ; None si inconnu."""
    t, v = doc.xref_get_key(xref, "ColorSpace")
    if t == "name":
        return {"/DeviceGray": 1, "/DeviceRGB": 3, "/DeviceCMYK": 4, "/CalRGB": 3, "/CalGray": 1}.get(v)
    if t == "xref":
        objet = doc.xref_object(int(v.split()[0]), compressed=True)
    elif t == "array":
        objet = v
    else:
        return None
    if "/ICCBased" in objet:
        icc = re.search(r"/ICCBased\s+(\d+)\s+0\s+R", objet)
        n = icc and doc.xref_get_key(int(icc.group(1)), "N")
        return int(n[1]) if n and n[0] == "int" else None
    for nom, k in (("/DeviceRGB", 3), ("/DeviceCMYK", 4), ("/DeviceGray", 1)):
        if objet.strip("[] ").startswith(nom):
            return k
    return None


def accorder_couleurs(doc, corriger=True):
    """Après rewrite_images : une image passée en JPEG RVB peut garder l'espace de couleur de l'original (profil
    ICC CMJN d'imprimeur, 4 composantes). Acrobat refuse alors le fichier et les navigateurs peignent l'image en
    noir. Chaque JPEG reçoit l'espace qui correspond à ses vraies composantes, sans /Decode de l'ancien espace.
    Rend le nombre d'images corrigées."""
    n = 0
    for xref in range(1, doc.xref_length()):
        if doc.xref_get_key(xref, "Subtype")[1] != "/Image" or "DCTDecode" not in doc.xref_get_key(xref, "Filter")[1]:
            continue
        reel = composantes_jpeg(doc.xref_stream_raw(xref) or b"")
        if reel in NOMS and composantes_espace(doc, xref) != reel:
            if corriger:
                doc.xref_set_key(xref, "ColorSpace", NOMS[reel])
                doc.xref_set_key(xref, "Decode", "null")
            n += 1
    return n


def partager_dessins(doc):
    """Motifs (PatternType 1) et formes (XObject Form) au dessin identique octet pour octet, mêmes ressources et
    même cadre, mais à une position (/Matrix) différente : garbage=4 ne peut pas les fusionner et chaque copie pèse
    son poids (Uncharted Passage : 25 copies de fonds de 350 à 400 Ko, 9,5 Mo sur 27). Le dessin passe dans une
    seule forme partagée ; chaque copie garde sa position et son cadre et ne fait plus qu'appeler cette forme.
    Rendu identique. Rend le nombre de copies remplacées."""
    groupes = {}
    for x in range(1, doc.xref_length()):
        try:
            if not doc.xref_is_stream(x):
                continue
            if doc.xref_get_key(x, "PatternType")[1] != "1" and doc.xref_get_key(x, "Subtype")[1] != "/Form":
                continue
            raw = doc.xref_stream_raw(x) or b""
        except Exception:
            continue
        if len(raw) < DESSIN_MIN:
            continue
        cle = (hashlib.sha1(raw).hexdigest(), doc.xref_get_key(x, "Resources"), doc.xref_get_key(x, "BBox")[1],
               doc.xref_get_key(x, "Filter")[1], doc.xref_get_key(x, "DecodeParms")[1])
        groupes.setdefault(cle, []).append(x)
    n = 0
    for (_, res, bbox, _, _), xs in groupes.items():
        if len(xs) < 2 or not bbox.startswith("["):
            continue
        try:
            dessin = doc.xref_stream(xs[0])
        except Exception:
            continue
        ressources = res[1] if res[0] in ("dict", "xref") else "<<>>"
        forme = doc.get_new_xref()
        doc.update_object(forme, f"<</Type/XObject/Subtype/Form/BBox{bbox}/Resources {ressources}>>")
        doc.update_stream(forme, dessin)
        for x in xs:
            doc.xref_set_key(x, "Resources", f"<</XObject<</FmPartage {forme} 0 R>>>>")
            doc.xref_set_key(x, "DecodeParms", "null")
            doc.update_stream(x, b"/FmPartage Do")
            n += 1
    return n


def essai(src, dst, dpi, qual, pages=None):
    """Une passe de compression, sur tout le livret ou une suite de pages ; rend la taille obtenue."""
    doc = pymupdf.open(src)
    if pages is not None:
        doc.select(list(pages))
    partager_dessins(doc)
    if dpi:  # images plus fines que dpi ramenées à dpi et recompressées (le trait pur est laissé tranquille)
        doc.rewrite_images(dpi_threshold=dpi + 1, dpi_target=dpi, quality=qual, bitonal=False)
        accorder_couleurs(doc)
    try:
        doc.subset_fonts()
    except Exception:
        pass
    doc.save(dst, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True, clean=True)
    doc.close()
    return os.path.getsize(dst)


def comprimer(src, tmp, cible, pages=None, passes=PASSES):
    """Passes du plus doux au plus serré, arrêtées à la première sous la cible. Rend (taille, essai retenu) ;
    essai None si même la dernière dépasse (tmp est alors la version la plus serrée)."""
    for dpi, qual in passes:
        n = essai(src, tmp, dpi, qual, pages)
        if n <= cible:
            return n, ("nettoyage seul, images intactes" if not dpi else
                       f"images en JPEG qualité {qual}, au plus {dpi} dpi")
    return n, None


def decouper(nb_pages, k):
    """k suites de pages consécutives, aussi égales que possible."""
    bornes = [round(i * nb_pages / k) for i in range(k + 1)]
    return [range(bornes[i], bornes[i + 1]) for i in range(k)]


def verifier(tmp, ref):
    if texte(tmp) != ref:
        fail("le texte du livret a changé pendant la compression — version allégée abandonnée")
    verif = pymupdf.open(tmp)
    faux = accorder_couleurs(verif, corriger=False)
    verif.close()
    if faux:
        fail(f"{faux} image(s) aux couleurs incohérentes (illisibles dans Acrobat) — version allégée abandonnée")


def main():
    args = fichiers()
    if not args:
        sys.exit(__doc__)
    src = os.path.abspath(args[0])
    if not os.path.isfile(src):
        fail(f"livret introuvable : {src}")
    limite = float(opt("--max", LIMITE / 1e6)) * 1e6
    n0 = os.path.getsize(src)
    if n0 < limite:
        print(f"{os.path.basename(src)} fait {taille(n0)}, déjà sous {limite / 1e6:.0f} Mo : rien à faire")
        return
    dst = os.path.abspath(opt("--sortie") or os.path.splitext(src)[0] + "_light.pdf")
    if os.path.normcase(dst) == os.path.normcase(src):
        fail("la sortie remplacerait le livret d'origine — donner un autre nom avec --sortie")
    racine = os.path.splitext(dst)[0]
    anciens = ([dst] if os.path.exists(dst) else []) + sorted(glob.glob(glob.escape(racine) + "_partie*.pdf"))
    if anciens and "--remplacer" not in sys.argv:
        fail(f"{anciens[0]} existe déjà — relancer avec --remplacer pour l'écraser")

    ref = texte(src)
    cible = limite * MARGE
    kmax = max(1, min(MAX_PARTIES, len(ref)))
    print(f"{os.path.basename(src)} : {taille(n0)} à ramener sous {limite / 1e6:.0f} Mo par fichier")
    faits = []  # (fichier d'essai, fichier final, taille, essai retenu ou None, pages ou None)
    try:
        essais = [(k, PASSES[:BONNES]) for k in range(1, kmax + 1)] + [(k, PASSES) for k in range(1, kmax + 1)]
        for j, (k, passes) in enumerate(essais):
            dernier = j == len(essais) - 1
            for f in faits:
                os.remove(f[0])
            faits = []
            for i, pages in enumerate(decouper(len(ref), k) if k > 1 else [None], 1):
                final = dst if k == 1 else f"{racine}_partie{i}.pdf"
                n, comment = comprimer(src, final + ".essai", cible, pages, passes)
                faits.append((final + ".essai", final, n, comment, pages))
                if not comment and not dernier:
                    break  # cette partie ne passe pas : essayer en plus de parties
            if all(f[3] for f in faits):
                break
            if passes is PASSES or k == kmax:
                print(f"  en {k} fichier{'s' * (k > 1)} : trop lourd "
                      + (f"même au plancher lisible ({PLANCHER})" if passes is PASSES else
                         "sans abîmer les images, quel que soit le découpage — essais jusqu'au plancher"))
        for tmp, final, n, comment, pages in faits:
            verifier(tmp, [ref[p] for p in pages] if pages is not None else ref)
        for vieux in anciens:  # ancienne version allégée (un fichier ou des parties) : remplacée en entier
            os.remove(vieux)
        for tmp, final, *_ in faits:
            os.replace(tmp, final)
    finally:
        for f in faits:
            if os.path.exists(f[0]):
                os.remove(f[0])
    if len(faits) > 1:
        print(f"livret coupé en {len(faits)} parties de moins de {limite / 1e6:.0f} Mo (en un seul fichier, il aurait fallu "
              f"abîmer les images) — à poster en messages séparés :")
    for tmp, final, n, comment, pages in faits:
        quoi = f"pages {pages.start + 1} à {pages.stop}, " if pages is not None else ""
        print(f"version allégée -> {final}  ({quoi}{taille(n)}, {comment or 'plancher : ' + PLANCHER})")
    print(f"le livret en pleine qualité reste {os.path.basename(src)} ({taille(n0)}), inchangé")
    trop = [f for f in faits if f[2] > limite]
    if trop:
        print(f"ATTENTION : {len(trop)} fichier(s) restent au-dessus de {limite / 1e6:.0f} Mo, même coupés en "
              f"{len(faits)} — mettre plutôt le lien du livret dans le message.")


if __name__ == "__main__":
    main()
