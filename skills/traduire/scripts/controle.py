"""Contrôles automatiques de mise en page, appelés en fin de build.py et de scan.py (à copier avec eux).
Ils signalent les endroits à regarder, pour ne relire en images que ceux-là (plus une planche rapide)."""
import pymupdf

MAX = 25  # lignes de signalement au plus


def _font_name(path):
    try:
        return pymupdf.Font(fontfile=path).name.split("+")[-1]
    except Exception:
        return None


def our_names(font_files):
    return {n for n in (_font_name(f) for f in font_files) if n}


def _spans(page):
    """Boîte « utile » de chaque span : du haut des capitales à la ligne de base (sans interligne ni jambages),
    pour ne pas confondre deux lignes serrées avec un chevauchement."""
    out = []
    for b in page.get_text("dict", flags=pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES)["blocks"]:  # sans les images (très lent sur un livret riche en images)
        for l in b.get("lines", []):
            if abs(l["dir"][0] - 1) > 0.01:
                continue
            for s in l["spans"]:
                if s["text"].strip():
                    y = s["origin"][1]
                    r = pymupdf.Rect(s["bbox"][0], y - 0.68 * s["size"], s["bbox"][2], y)
                    out.append((r, s["font"].split("+")[-1], s["text"].strip()))
    return out


def _area(r):
    return max(r.width, 0) * max(r.height, 0)


def _inter(a, b):
    return _area(pymupdf.Rect(a) & b)


class _Dessin:
    """Ce qu'il y a sous le texte français, d'après les pixels de la page construite dont tout le texte a été retiré
    (décor seul, icônes déplacées comprises) : fond uni (papier, même texturé, aplat d'encadré) ou dessin (photo,
    tuile, carte, flèche, icône). Les rectangles d'images ne suffisent pas : bien des livrets ont un fond fait de
    grandes images (des centaines de fausses alertes, qui noient les vraies), et une légende plus longue que
    l'anglais ne mord parfois que de quelques points sur l'illustration ou la flèche voisine."""
    K = 2  # pixels par point

    def __init__(self, page):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(self.K, self.K), colorspace=pymupdf.csGRAY)
        self.w, self.h, self.px = pix.width, pix.height, pix.samples

    def _px(self, r):
        k = self.K
        return (max(0, int(r.x0 * k)), max(0, int(r.y0 * k)), min(self.w, int(r.x1 * k) + 1), min(self.h, int(r.y1 * k) + 1))

    def sous(self, r, orig_text=()):
        """Largeur (pt) de dessin sous la ligne r : colonnes de pixels dont un quart au moins s'écarte nettement du
        fond de la ligne (sa valeur médiane). Les colonnes où l'original avait déjà du texte à cette hauteur ne
        comptent pas (étiquette posée sur une carte, encadré, fond bois : voulu par l'original) ; seul compte ce que
        le français ajoute. 0 si moins de 2 pt : bord de cadre effleuré, grain du papier."""
        x0, y0, x1, y1 = self._px(r)
        if x1 - x0 < 2 or y1 - y0 < 2:
            return 0
        deja = [(o.x0 - 1, o.x1 + 1) for o in orig_text if min(o.y1, r.y1) - max(o.y0, r.y0) > 0.5 * r.height]
        fond = sorted(self.px[y * self.w + x] for y in range(y0, y1) for x in range(x0, x1))[(x1 - x0) * (y1 - y0) // 2]
        larg = sum(1 for x in range(x0, x1)
                   if not any(a <= x / self.K <= b for a, b in deja)
                   and sum(1 for y in range(y0, y1) if abs(self.px[y * self.w + x] - fond) > 60) >= max(2, (y1 - y0) / 4))
        larg /= self.K
        return larg if larg >= 2 else 0


def _decor(out_path):
    """Le PDF construit sans aucun texte (images et tracés gardés), pour _Dessin."""
    doc = pymupdf.open(out_path)
    for page in doc:
        page.add_redact_annot(page.rect, fill=False)
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                              text=getattr(pymupdf, "PDF_REDACT_TEXT_REMOVE", 0))
    return doc


def check_text(out_path, src_path, names, log):
    """Livret à texte : français qui chevauche une image, un autre texte français, du texte d'origine resté en
    place, ou qui sort de la page."""
    out, src, decor = pymupdf.open(out_path), pymupdf.open(src_path), _decor(out_path)
    issues = []
    for page, orig, nu in zip(out, src, decor):
        spans = _spans(page)
        fr = [s for s in spans if s[1] in names]
        rest = [s for s in spans if s[1] not in names and s[2] != "¤"]
        orig_text = [pymupdf.Rect(s[0]) for s in _spans(orig)]
        dessin = _Dessin(nu)
        seen = set()

        def add(r, msg):
            key = (round(r.x0 / 20), round(r.y0 / 10), msg[:20])
            if key not in seen:
                seen.add(key)
                issues.append(f"  page {page.number} ({r.x0:.0f}, {r.y0:.0f}) : {msg}")

        for i, (r, _, t) in enumerate(fr):
            if not page.rect.contains(r):
                add(r, f"sort de la page — « {t[:40]} »")
            large = dessin.sous(r, orig_text)
            if large:
                add(r, f"chevauche un dessin ({large:.0f} pt) — « {t[:40]} »")
            for r2, f2, t2 in rest:
                if _inter(r, r2) > 0.15 * min(_area(r), _area(r2)):
                    add(r, f"touche du texte d'origine « {t2[:20]} » — « {t[:30]} »")
                    break
            for r2, _, t2 in fr[i + 1:]:
                if abs(r.y0 - r2.y0) > 1 and _inter(r, r2) > 0.2 * min(_area(r), _area(r2)):
                    add(r, f"chevauche un autre texte français « {t2[:20]} » — « {t[:30]} »")
                    break
    _report(issues, log)


def _bands(page, rect, k=8):
    """Lignes d'encre (y0, y1) dans rect — même règle que bandes.py."""
    r = pymupdf.Rect(rect) & page.rect
    if r.is_empty:
        return []
    pix = page.get_pixmap(matrix=pymupdf.Matrix(k, k), clip=r, colorspace=pymupdf.csGRAY)
    w, h, s = pix.width, pix.height, pix.samples
    rows = []
    for y in range(h):
        line = s[y * w:(y + 1) * w]
        mid = sorted(line)[len(line) // 2]
        rows.append(sum(1 for v in line if abs(v - mid) > 90) / w > 0.01)
    out, start = [], None
    for y, on in enumerate(rows + [False]):
        if on and start is None:
            start = y
        elif not on and start is not None:
            if (y - start) / k >= 1.2:
                out.append((r.y0 + start / k, r.y0 + y / k))
            start = None
    return out


def check_scan(src_doc, zones, log):
    """Livret scanné : une ligne d'encre de l'original qui entre dans un masque et en ressort (texte d'origine
    coupé par le bord du masque, donc en partie visible)."""
    issues = []
    for i, z in enumerate(zones, 1):
        if z.get("bg", "auto") is None:
            continue
        page = src_doc[z["page"]]
        r = pymupdf.Rect(z["rect"])
        bands = _bands(page, (r.x0, r.y0 - 5, r.x1, r.y1 + 5))
        if not bands:
            continue
        typical = sorted(b - a for a, b in bands)[len(bands) // 2]
        for a, b in bands:
            if b - a > 2.2 * typical:  # trait de dessin, fond, bulle : pas une ligne de texte
                continue
            if a <= r.y0 - 4.8 or b >= r.y1 + 4.8:  # encre jusqu'au bord de la fenêtre : illustration
                continue
            out_top, out_bot = r.y0 - a, b - r.y1
            if a < r.y1 and b > r.y0 and (out_top > 0.6 or out_bot > 0.6):
                side = "haut" if out_top > out_bot else "bas"
                issues.append(f"  page {z['page']} zone {i} {tuple(round(v) for v in z['rect'])} : une ligne "
                              f"d'origine dépasse du masque en {side} ({max(out_top, out_bot):.1f} pt)")
                break
    _report(issues, log)


def _report(issues, log):
    log.append("")
    if issues:
        log.append(f"À VÉRIFIER ({len(issues)}) — regarder ces endroits en priorité :")
        log += issues[:MAX]
        if len(issues) > MAX:
            log.append(f"  … et {len(issues) - MAX} de plus")
    else:
        log.append("Contrôles de mise en page : rien à signaler.")
