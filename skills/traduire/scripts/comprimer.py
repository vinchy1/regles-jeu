# -*- coding: utf-8 -*-
"""Version allégée d'un livret traduit, pour l'envoyer sur Discord (10 Mo maximum).

Usage : python -X utf8 comprimer.py "<livret.pdf>" [--max 10] [--sortie "<fichier.pdf>"] [--remplacer]
Écrit `<nom>_light.pdf` À CÔTÉ du livret : le livret en pleine qualité n'est jamais touché ni remplacé, la
version allégée est un fichier de plus, à n'envoyer que sur Discord.
Seules les images sont recompressées en JPEG, et ramenées à un dpi plus bas si elles sont très fines ; le texte
reste du texte (vectoriel), donc net à l'écran comme à l'impression. Le script s'arrête au premier essai qui
passe sous la limite, pour abîmer les images le moins possible, et vérifie que le texte n'a pas bougé.
Livret déjà sous la limite : il le dit et ne fait rien."""
import os, re, sys
import pymupdf

LIMITE = 10e6  # 10 Mo : taille maximale d'un envoi Discord (lecture la plus stricte du Mo)
MARGE = 0.98   # viser un peu en dessous plutôt que de jouer avec la limite
# essais successifs (dpi visé, qualité JPEG), du plus fin au plus serré ; None = nettoyage seul, images intactes
PASSES = [(None, None), (300, 92), (300, 85), (220, 80), (170, 72), (140, 65), (110, 55), (85, 45), (72, 35)]
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


def essai(src, dst, dpi, qual):
    """Une passe de compression ; rend la taille obtenue."""
    doc = pymupdf.open(src)
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
    if os.path.exists(dst) and "--remplacer" not in sys.argv:
        fail(f"{dst} existe déjà — relancer avec --remplacer pour l'écraser")

    ref = texte(src)
    tmp = dst + ".essai"
    cible = limite * MARGE
    print(f"{os.path.basename(src)} : {taille(n0)} à ramener sous {limite / 1e6:.0f} Mo")
    n, comment = n0, ""
    try:
        for dpi, qual in PASSES:
            n = essai(src, tmp, dpi, qual)
            comment = ("nettoyage seul, images intactes" if not dpi else
                       f"images en JPEG qualité {qual}, au plus {dpi} dpi")
            print(f"  {comment} : {taille(n)}")
            if n <= cible:
                break
        if texte(tmp) != ref:
            fail("le texte du livret a changé pendant la compression — version allégée abandonnée")
        verif = pymupdf.open(tmp)
        faux = accorder_couleurs(verif, corriger=False)
        verif.close()
        if faux:
            fail(f"{faux} image(s) aux couleurs incohérentes (illisibles dans Acrobat) — version allégée abandonnée")
        if os.path.exists(dst):
            os.remove(dst)
        os.replace(tmp, dst)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    print(f"version allégée -> {dst}  ({taille(n0)} -> {taille(n)}, {comment})")
    print(f"le livret en pleine qualité reste {os.path.basename(src)}, inchangé")
    if n > limite:
        print(f"ATTENTION : {taille(n)} reste au-dessus de {limite / 1e6:.0f} Mo — livret très riche en images. "
              f"L'envoyer en deux fichiers (le couper en deux moitiés de pages) est le plus simple.")


if __name__ == "__main__":
    main()
