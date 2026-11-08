# -*- coding: utf-8 -*-
"""Aide-mémoire A4 à poser sur la table (une page, deux au besoin) : mise en place, tour de jeu, fin de partie et
score…

    python -X utf8 aide_memoire.py "<Ludothèque>/_outils/<Jeu>/aide-memoire.json" "<sortie.pdf>"
        [--livret "<livret.pdf>"]   vignette de la couverture (page 1) en tête de page
        [--apercu "<image.png>"]    image de la page construite (la 2e page, s'il y en a une : <image>-2.png)
        [--une-page]                jamais de 2e page (texte réduit jusqu'à 7 pt)

aide-memoire.json (rédigé par Claude d'après le livret, voir references/aide-memoire.md) :
    {
      "titre": "CMYK",
      "infos": "Jeu de plis · 1 à 5 joueurs · 20-30 min",          facultatif
      "but": "Remporter les plis de la couleur de son objectif.",   une phrase
      "sections": [
        {"titre": "Mise en place", "etapes": ["…", "…"]},           liste numérotée
        {"titre": "Tour de jeu", "etapes": ["…"]},
        {"titre": "Fin de manche et score", "points": ["…"]},       liste à puces
        {"titre": "Cartes spéciales", "tableau": [["Joker", "…"]]}, une ligne « nom : effet » par carte
        {"titre": "À ne pas oublier", "points": ["…"], "accent": true}   encadré
      ],
      "source": "Livret CMYK_Rules_FR.pdf, p. 2-5"
    }
Dans les textes, **gras** met en gras. Les sections se suivent dans l'ordre, sur deux colonnes ; le texte est
réduit pas à pas jusqu'à tenir sur une page sans descendre sous 8,5 pt. Sinon l'aide-mémoire passe sur deux pages
(recto-verso), avec un texte plus grand (« TROP LONG » si même deux pages en 7 pt ne suffisent pas : raccourcir le
JSON).
"""
import html, io, json, os, re, sys

import pymupdf

A4 = pymupdf.paper_rect("a4")
MARGE, ENTRE_COLONNES, HAUT_TETE, HAUT_SUITE = 34, 22, 92, 30
TAILLE_MIN, PETIT = 7.0, 8.5  # PETIT : en dessous, une 2e page vaut mieux qu'un texte qu'on lit mal
POLICES = {  # polices de Windows ; à défaut, celles intégrées à pymupdf
    "corps": ("segoeui.ttf", "segoeuib.ttf", "segoeuii.ttf"),
    "titre": ("georgia.ttf", "georgiab.ttf", None),
}
ENCRE, GRIS, FILET, FOND = "#1d1d1f", "#5b5b63", "#c9c9cf", "#f1f1f3"


def _polices():
    dossier = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    css, archive = [], pymupdf.Archive()
    ok = all(os.path.isfile(os.path.join(dossier, f)) for fams in POLICES.values() for f in fams if f)
    if not ok:
        return "", None, "sans-serif", "serif"
    archive.add(pymupdf.Archive(dossier))
    for nom, (normal, gras, ital) in POLICES.items():
        css.append(f"@font-face {{ font-family: am-{nom}; src: url({normal}); }}")
        css.append(f"@font-face {{ font-family: am-{nom}; font-weight: bold; src: url({gras}); }}")
        if ital:
            css.append(f"@font-face {{ font-family: am-{nom}; font-style: italic; src: url({ital}); }}")
    return "\n".join(css), archive, "am-corps", "am-titre"


def _texte(t):
    """Échappe le texte, **gras** → <b>, typographie française (espace insécable avant ; : ! ? et dans « »)."""
    t = re.sub(r"\s*([;:!?])(?=\s|$|\*)", "\u00a0\\1", str(t).strip())  # avant l'échappement (« &gt; » finit par ;)
    t = re.sub(r"\s*»", "\u00a0»", re.sub(r"«\s*", "«\u00a0", t))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(t, quote=False))


def _section(s):
    h = f'<h2>{_texte(s["titre"])}</h2>'
    if s.get("etapes"):
        h += "<ol>" + "".join(f"<li>{_texte(x)}</li>" for x in s["etapes"]) + "</ol>"
    if s.get("points"):
        h += "<ul>" + "".join(f"<li>{_texte(x)}</li>" for x in s["points"]) + "</ul>"
    if s.get("tableau"):  # une ligne « Nom : effet » par entrée (les <table> de MuPDF font chevaucher les colonnes)
        h += "".join(f'<p class="def"><b>{_texte(a)}</b> : {_texte(b)}</p>' for a, b in s["tableau"])
    if s.get("texte"):
        h += f"<p>{_texte(s['texte'])}</p>"
    return f'<div class="sec{" accent" if s.get("accent") else ""}">{h}</div>'


def _css(polices, corps, titre, taille):
    return polices + f"""
    body, div, p, h2, ol, ul, li {{ margin: 0; padding: 0; }}  /* MuPDF ignore « * » : marges par défaut sinon */
    body {{ font-family: {corps}; font-size: {taille}pt; line-height: 1.3; color: {ENCRE}; }}
    .sec {{ margin-bottom: {taille * 0.9}pt; }}
    .accent {{ background-color: {FOND}; padding: {taille * 0.6}pt {taille * 0.8}pt; }}
    h2 {{ font-family: {titre}; font-size: {taille * 1.3}pt; font-weight: bold; margin-bottom: {taille * 0.35}pt;
          padding-bottom: {taille * 0.15}pt; border-bottom: 0.6pt solid {FILET}; }}
    ol, ul {{ padding-left: {taille * 1.6}pt; }}
    li {{ margin-bottom: {taille * 0.25}pt; }}
    p {{ margin-bottom: {taille * 0.3}pt; }}
    p.def {{ padding-bottom: {taille * 0.25}pt; border-bottom: 0.4pt solid {FILET}; }}
    b {{ font-weight: bold; }}
    """


def _colonnes(pages):
    """Colonnes à remplir dans l'ordre : deux par page ; la 1re page sous l'en-tête, la 2e sous son rappel du titre."""
    largeur = (A4.width - 2 * MARGE - ENTRE_COLONNES) / 2
    bas, cols = A4.height - MARGE - 16, []
    for p in range(pages):
        haut = MARGE + (HAUT_TETE if p == 0 else HAUT_SUITE)
        cols += [(p, pymupdf.Rect(MARGE, haut, MARGE + largeur, bas)),
                 (p, pymupdf.Rect(MARGE + largeur + ENTRE_COLONNES, haut, A4.width - MARGE, bas))]
    return cols


def _poser(sections, taille, css, archive, w, dev, pages):
    """Pose les sections l'une sous l'autre sur deux colonnes, chacune d'un seul bloc : une section qui ne tient
    pas dans le reste d'une colonne passe en haut de la suivante (coupée seulement si elle dépasse une colonne
    entière). dev : la 1re page, déjà commencée dans w ; la 2e est commencée au besoin. Rend le nombre de pages
    utilisées, ou 0 si tout ne tient pas dans `pages` pages."""
    cols, gap = _colonnes(pages), taille * 0.3  # en plus de la marge basse de .sec, comprise dans la zone remplie
    c, y, page = 0, cols[0][1].y0, 0
    for html_sec in sections:
        story = pymupdf.Story(html=html_sec, user_css=css, archive=archive)
        while True:
            if c >= len(cols):
                return 0
            p, col = cols[c]
            if p > page:  # première colonne de la page suivante
                w.end_page()
                dev, page = w.begin_page(A4), p
            reste, rempli = story.place(pymupdf.Rect(col.x0, y, col.x1, col.y1))
            if reste and y > col.y0:  # pas la place ici : la section repart en haut de la colonne suivante
                c += 1
                y = cols[c][1].y0 if c < len(cols) else 0
                story = pymupdf.Story(html=html_sec, user_css=css, archive=archive)
                continue
            story.draw(dev)
            if not reste:
                y = rempli[3] + gap  # bas de la zone remplie
                break
            c += 1  # plus haute qu'une colonne : la suite en face
            y = cols[c][1].y0 if c < len(cols) else 0
    return page + 1


def _taille(d, polices, archive, corps, titre, une_page=False):
    """Nombre de pages et plus grande taille de texte (pas de 0,25 pt) : une page si le texte y tient sans
    descendre sous PETIT, sinon deux (recto-verso), plus lisibles qu'une page en tout petit."""
    sections = [_section(s) for s in d["sections"]]
    for pages, plancher in ((1, TAILLE_MIN),) if une_page else ((1, PETIT), (2, TAILLE_MIN)):
        taille = 11.0
        while taille >= plancher:
            w = pymupdf.DocumentWriter(io.BytesIO())  # essai dessiné à part, jeté ensuite
            n = _poser(sections, taille, _css(polices, corps, titre, taille), archive, w, w.begin_page(A4), pages)
            w.end_page()
            w.close()
            if n:
                return sections, taille, n
            taille = round(taille - 0.25, 2)
    raise SystemExit(f"TROP LONG : même en {TAILLE_MIN} pt le contenu ne tient pas sur "
                     f"{'une page' if une_page else 'deux pages'} — raccourcir le JSON")


def _tete_html(d, polices, corps, titre):
    tete = (f'<p class="eti">Aide-mémoire</p><h1>{_texte(d["titre"])}</h1>'
            + (f'<p class="infos">{_texte(d["infos"])}</p>' if d.get("infos") else "")
            + (f'<p class="but"><b>But du jeu.</b> {_texte(d["but"])}</p>' if d.get("but") else ""))
    css = polices + f"""
      body, p, h1 {{ margin: 0; padding: 0; }}
      body {{ font-family: {corps}; color: {ENCRE}; }}
      .eti {{ font-size: 7.5pt; font-weight: bold; color: {GRIS}; letter-spacing: 1pt; text-transform: uppercase; }}
      h1 {{ font-family: {titre}; font-size: 24pt; line-height: 1.1; margin: 1pt 0 2pt; }}
      .infos {{ font-size: 9pt; color: {GRIS}; margin-bottom: 4pt; }}
      .but {{ font-size: 10pt; line-height: 1.3; }}"""
    return tete, css


def _vignette(livret):
    """Taille de la vignette de couverture (largeur, hauteur) pour la hauteur de l'en-tête."""
    with pymupdf.open(livret) as src:
        r = src[0].rect
    h = HAUT_TETE - 14
    return h * r.width / r.height, h


# restes d'anglais à ne pas recopier du livret (titres décoratifs gardés en anglais dans la traduction, comme
# « Haggis (3-Player) ») : dans les titres de section, et « N-Player » partout ; les noms de cartes restent permis
ANGLAIS_TITRE = re.compile(r"\b(?:\d+-?players?|players?|setup|set-up|scoring|variants?|rules?|rounds?|game ?play|"
                           r"overview|turn order|end of (?:the )?game|components?|how to play|winning)\b", re.I)
ANGLAIS_PARTOUT = re.compile(r"\b\d+-players?\b", re.I)


def _anglais(d):
    """Restes d'anglais à traduire : [(où, texte)]."""
    out = []
    for s in d.get("sections", []):
        if ANGLAIS_TITRE.search(s.get("titre", "")):
            out.append(("titre", s["titre"]))
        for x in s.get("etapes", []) + s.get("points", []) + [" ".join(map(str, r)) for r in s.get("tableau", [])]:
            if ANGLAIS_PARTOUT.search(x):
                out.append((f"section « {s.get('titre', '')} »", x))
    return out


def construire(json_path, sortie, livret=None, apercu=None, une_page=False):
    with open(json_path, encoding="utf-8") as f:
        d = json.load(f)
    for ou, t in _anglais(d):
        print(f"À VÉRIFIER : anglais dans {ou} : « {t[:80]} » — l'écrire en français (ex. « à 3 joueurs »)")
    polices, archive, corps, titre = _polices()
    sections, taille, pages = _taille(d, polices, archive, corps, titre, une_page)
    livret = livret if livret and os.path.isfile(livret) else None
    vw, vh = _vignette(livret) if livret else (0, 0)
    x_tete = MARGE + (vw + 14 if livret else 0)

    # texte : en-tête puis sections sur deux colonnes (sur la 2e page, s'il y en a une, sous le rappel du titre)
    tampon = io.BytesIO()
    w = pymupdf.DocumentWriter(tampon)
    dev = w.begin_page(A4)
    tete, css_tete = _tete_html(d, polices, corps, titre)
    st = pymupdf.Story(html=tete, user_css=css_tete, archive=archive)
    if st.place(pymupdf.Rect(x_tete, MARGE, A4.width - MARGE, MARGE + HAUT_TETE - 8))[0]:
        print("ATTENTION : en-tête trop long, la fin est coupée — raccourcir « infos » ou « but »")
    st.draw(dev)

    _poser(sections, taille, _css(polices, corps, titre, taille), archive, w, dev, pages)
    w.end_page()
    w.close()

    # dessins : vignette, filet sous l'en-tête, pied de page
    doc = pymupdf.open("pdf", tampon.getvalue())
    page = doc[0]
    if livret:
        r = pymupdf.Rect(MARGE, MARGE, MARGE + vw, MARGE + vh)
        with pymupdf.open(livret) as src:  # en image : la page en vecteurs emporte toutes ses polices (8 Mo)
            pix = src[0].get_pixmap(dpi=round(3 * 72 * vh / src[0].rect.height))  # ~3 px par point
        page.insert_image(r, stream=pix.tobytes("jpeg", jpg_quality=85))
        page.draw_rect(r, color=(0.8, 0.8, 0.82), width=0.5)
    pied = " · ".join(x for x in (d.get("source") and f"D'après le livret : {d['source']}",
                                  "aide-mémoire : les règles complètes font foi") if x)
    for n, pg in enumerate(doc):
        y = MARGE + (HAUT_TETE if n == 0 else HAUT_SUITE) - 4
        pg.draw_line((MARGE, y), (A4.width - MARGE, y), color=(0.25, 0.25, 0.28), width=1.2 if n == 0 else 0.6)
        if n:  # rappel du titre en haut de la 2e page (réduit au besoin pour tenir sur sa ligne)
            pg.insert_htmlbox(pymupdf.Rect(MARGE, MARGE, A4.width - MARGE, y - 3),
                              f'<p class="t2">{_texte(d["titre"])} <span class="eti2">Aide-mémoire · suite</span></p>',
                              css=css_tete + f" .t2 {{ font-family: {titre}; font-size: 13pt; font-weight: bold; }}"
                              f" .eti2 {{ font-family: {corps}; font-size: 7.5pt; color: {GRIS}; font-weight: normal; }}",
                              archive=archive, scale_low=0)
        numero = f"{n + 1} / {len(doc)} · " if len(doc) > 1 else ""
        pg.insert_text((MARGE, A4.height - MARGE + 6), numero + pied, fontsize=6.5, color=(0.45, 0.45, 0.5))
    doc.set_metadata({"title": f"{d['titre']} — aide-mémoire", "creator": "regles-jeu"})
    os.makedirs(os.path.dirname(os.path.abspath(sortie)), exist_ok=True)
    doc.subset_fonts()  # polices entières sinon (1 Mo pour une page)
    doc.save(sortie, garbage=3, deflate=True)
    if apercu:
        for n, pg in enumerate(doc):
            racine, ext = os.path.splitext(apercu)
            pg.get_pixmap(dpi=80).save(apercu if n == 0 else f"{racine}-{n + 1}{ext}")
    doc.close()
    print(f"OK : {sortie} (texte en {taille} pt, {'2 pages : à imprimer en recto-verso' if pages > 1 else '1 page'}"
          f"{' — petit : envisager de raccourcir' if taille < PETIT else ''})")


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = lambda n: a[a.index(n) + 1] if n in a else None
    pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] not in ("--livret", "--apercu"))]
    if len(pos) != 2:
        raise SystemExit(__doc__)
    construire(pos[0], pos[1], opt("--livret"), opt("--apercu"), "--une-page" in a)
