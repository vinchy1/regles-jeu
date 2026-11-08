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


def check_text(out_path, src_path, names, log):
    """Livret à texte : français qui chevauche une image, un autre texte français, du texte d'origine resté en
    place, ou qui sort de la page."""
    out, src = pymupdf.open(out_path), pymupdf.open(src_path)
    issues = []
    for page, orig in zip(out, src):
        pa = _area(page.rect)
        spans = _spans(page)
        fr = [s for s in spans if s[1] in names]
        rest = [s for s in spans if s[1] not in names and s[2] != "¤"]
        orig_text = [pymupdf.Rect(s[0]) for s in _spans(orig)]
        imgs = [pymupdf.Rect(i["bbox"]) for i in page.get_image_info()
                if _area(pymupdf.Rect(i["bbox"])) < 0.35 * pa
                and not (i["bbox"][2] - i["bbox"][0] < 22 and i["bbox"][3] - i["bbox"][1] < 16)]
        seen = set()

        def add(r, msg):
            key = (round(r.x0 / 20), round(r.y0 / 10), msg[:20])
            if key not in seen:
                seen.add(key)
                issues.append(f"  page {page.number} ({r.x0:.0f}, {r.y0:.0f}) : {msg}")

        for i, (r, _, t) in enumerate(fr):
            if not page.rect.contains(r):
                add(r, f"sort de la page — « {t[:40]} »")
            for im in imgs:
                inter = r & im
                if _area(inter) > 0.3 * _area(r) and not any(_area(o & inter) > 0.3 * _area(inter) for o in orig_text):
                    add(r, f"chevauche une image — « {t[:40]} »")
                    break
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
