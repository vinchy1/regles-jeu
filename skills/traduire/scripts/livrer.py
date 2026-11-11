"""Livre une traduction terminée : un seul appel pour toutes les étapes de rangement.
Usage : python -X utf8 livrer.py "<Ludothèque>/_outils/<Jeu>" [--langue X] [--editeur Y] [--remplacer]
        python -X utf8 livrer.py "<Ludothèque>/_outils/<Jeu>" --original "<livret>" --pdf "<français.pdf>"
               [--pdf-en "<anglais.pdf>"] [--type "recréé (…)"] [--langue X] [--editeur Y] [--remplacer]

1. crée <Ludothèque>/<Jeu>/ et y déplace le livret d'origine (s'il est encore dans « A traduire ») ; s'il y est
   déjà à l'identique, la copie restée dans « A traduire » est simplement retirée ;
2. fait pointer SRC de spec.py sur son nouvel emplacement ;
3. range et allège le dossier d'outils (ranger.py), reconstruit avec les polices allégées (build.py ou scan.py) ;
4. copie la sortie en <Jeu>/<nom>_FR.pdf, mention de langue retirée (« Jeu_EN.pdf » → « Jeu_FR.pdf »,
   « Jeu ENG Rules.pdf » → « Jeu Rules_FR.pdf ») puis range de nouveau ;
   spec bilingue (LANGUE lu dans l'environnement, textes X("fr", "en")) : construit aussi l'anglais
   (LANGUE=en) et le copie en <Jeu>/<nom>_EN.pdf ;
Un livret livré qui atteint 10 Mo est signalé : au-delà, il ne passe pas sur Discord, et une version allégée est
à proposer à l'utilisateur (comprimer.py) — le livret en pleine qualité, lui, reste tel quel.
Après la construction, `origine.json` note le livret d'origine traduit (nom, taille, pages, empreinte SHA-256 et
liens de « Sources » de NOTES.md) : un ami qui suit ce dossier d'outils (app « Règles de jeu », traductions
partagées) reconnaît ainsi le même livret chez lui, même renommé, et sait où le télécharger.
5. ajoute ou met à jour la ligne du jeu dans l'index _outils/LISEZMOI.md (langue et éditeur : options, sinon lus
   dans NOTES.md) et signale un NOTES.md manquant.
Avec --encre : construit et livre en plus <nom>_FR_encre.pdf, version économe en encre à imprimer (fond sombre
retiré, couleurs claires foncées — build.py --fond-clair) ; seulement si l'utilisateur la demande, et seulement
pour un livret à texte.
Avec --pdf (traduction faite sans spec.py : page web recréée en HTML, livret recomposé à neuf…) : étapes 1, 4 et 5
seulement, avec les PDF donnés (--pdf-en : version anglaise, --pdf-encre : version économe en encre) et le Type
donné à l'index (défaut « recréé »).
N'écrase jamais un fichier existant dans le dossier du jeu sans --remplacer."""
import ast, datetime, filecmp, hashlib, json, os, re, shutil, subprocess, sys

HEADER = """# Index des livrets traduits (plugin regles-jeu, skill traduire)

Une ligne par jeu. Le détail de chaque jeu (polices, vocabulaire, choix, particularités) est dans
`_outils/<Jeu>/NOTES.md` ; les livrets (original et `_FR.pdf`) sont dans `<Jeu>/`.
Pour corriger : modifier `spec.py` dans `_outils/<Jeu>/`, vérifier avec `python -X utf8 build.py sortie.pdf`
(Type « texte ») ou `scan.py` (Type « scan »), puis `python -X utf8 livrer.py "_outils/<Jeu>" --remplacer`.
Chercher un jeu proche par éditeur ou par police : `grep -i "<éditeur ou police>" _outils/LISEZMOI.md`.

| Jeu | Langue | Éditeur | Type | Polices de remplacement | Date |
|---|---|---|---|---|---|
"""
LANG_SUFFIX = re.compile(r"[ _\-.](EN|ENG|JP|JA|JPN|DE|GER|ES|SP|IT|CN|ZH|KR|KO|PT|NL|PL|RU)$", re.I)
# au milieu du nom (« Man Eating House ENG Rules ») : seulement en capitales ou en toutes lettres, pour ne pas
# toucher un mot du titre (« Take It Easy »)
LANG_WORD = re.compile(r"(?<![^ _\-.])(?:EN|ENG|JP|JPN|DE|GER|ES|IT|CN|ZH|KR|PT|NL|PL|RU|"
                       r"(?i:english|englisch|japanese|german|deutsch|spanish|italian|chinese))(?=[ _\-.])")


def fr_stem(stem):
    """Nom du livret sans sa mention de langue : « Jeu_EN » et « Jeu ENG Rules » → « Jeu », « Jeu Rules »."""
    s = LANG_SUFFIX.sub("", stem) or stem
    s = LANG_WORD.sub("", s)
    s = re.sub(r"([ _\-.])[ _\-.]+", r"\1", s).strip(" _-.")
    return s or stem


DISCORD = 10e6  # au-dessus, un fichier ne passe pas sur Discord : une version allégée est à proposer


def signaler_poids(path):
    """Livret trop lourd pour Discord : le dire, pour qu'une version allégée soit proposée à l'utilisateur."""
    n = os.path.getsize(path)
    if n >= DISCORD:
        print(f"ATTENTION : {os.path.basename(path)} fait {n / 1e6:.1f} Mo, au-dessus des 10 Mo de Discord — "
              f'proposer une version allégée : python -X utf8 comprimer.py "{path}"')


def fail(msg):
    sys.exit(f"ERREUR : {msg}")


def opt(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def run(args, cwd, langue=None):
    env = dict(os.environ)
    env.pop("LANGUE", None)
    if langue:
        env["LANGUE"] = langue
    r = subprocess.run([sys.executable, "-X", "utf8"] + args, cwd=cwd, capture_output=True, text=True,
                       encoding="utf8", env=env)
    return r.returncode, (r.stdout + r.stderr).strip()


def bilingue(spec_path):
    """spec.py qui appelle X("fr", "en") : version anglaise à construire aussi (la ligne LANGUE et la fonction X
    du modèle, restées sans usage, ne suffisent pas)."""
    tree = ast.parse(open(spec_path, encoding="utf8").read())
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "X"
               for n in ast.walk(tree))


def identiques(a, b):
    return os.path.isfile(a) and os.path.isfile(b) and filecmp.cmp(a, b, shallow=False)


def deplacer_original(src, target, replace):
    os.makedirs(target, exist_ok=True)
    dest = os.path.join(target, os.path.basename(src))
    if os.path.normcase(os.path.dirname(src)) != os.path.normcase(target) and not identiques(src, dest):
        if os.path.exists(dest) and not replace:
            fail(f"{dest} existe déjà, différent du livret traduit — relancer avec --remplacer")
        shutil.move(src, dest)
        print(f"livret d'origine déplacé -> {dest}")
    # copie identique restée à traiter (livret envoyé à traduire depuis le dossier du jeu) : sans cela il resterait
    # proposé à la traduction. Seule une copie exacte est retirée : l'exemplaire du dossier du jeu reste.
    depot = os.path.join(os.path.dirname(target), "A traduire", os.path.basename(dest))
    if identiques(depot, dest):
        os.remove(depot)
        print(f"copie identique retirée de « A traduire » : {os.path.basename(dest)}")
    return dest


def indexer(ludo, jeu, tools, typ):
    notes = os.path.join(tools, "NOTES.md")
    langue = opt("--langue") or from_notes(notes, "Langue d'origine") or "?"
    editeur = opt("--editeur") or from_notes(notes, "Éditeur") or "?"
    row = (f"| {jeu} | {langue} | {editeur} | {typ} | "
           f"{font_families(os.path.join(tools, 'ff')) or '—'} | {datetime.date.today().isoformat()} |")
    index = os.path.join(ludo, "_outils", "LISEZMOI.md")
    text = open(index, encoding="utf8").read() if os.path.isfile(index) else HEADER
    lines = text.rstrip("\n").split("\n")
    rows = [i for i, l in enumerate(lines) if l.startswith(f"| {jeu} |")]
    table = [i for i, l in enumerate(lines) if l.startswith("|")]
    if rows:
        lines[rows[0]] = row
    elif table:  # new row right after the table's last row, not after the notes that follow it
        lines.insert(table[-1] + 1, row)
    else:
        lines.append(row)
    open(index, "w", encoding="utf8").write("\n".join(lines) + "\n")
    print(f"index : {row}")
    if not os.path.isfile(notes):
        print(f"ATTENTION : {notes} manque — l'écrire (langue, éditeur, polices, vocabulaire, choix, compromis)")


def noter_origine(tools, original):
    """origine.json : le livret d'origine traduit, pour le retrouver ailleurs (nom, taille, pages, empreinte, liens)."""
    h = hashlib.sha256()
    with open(original, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    try:
        import pymupdf
        with pymupdf.open(original) as d:
            pages = len(d)
    except Exception:
        pages = None
    notes = os.path.join(tools, "NOTES.md")
    texte = open(notes, encoding="utf8", errors="replace").read() if os.path.isfile(notes) else ""
    liens = []
    for u in re.findall(r"https?://[^\s)>\]»\"'`]+", texte):
        u = u.rstrip(".,;:")
        if u not in liens:
            liens.append(u)
    with open(os.path.join(tools, "origine.json"), "w", encoding="utf8") as f:
        json.dump({"fichier": os.path.basename(original), "taille": os.path.getsize(original), "pages": pages,
                   "sha256": h.hexdigest(), "sources": liens[:8]}, f, ensure_ascii=False, indent=1)
    if not liens:
        print("ATTENTION : aucun lien vers le livret d'origine dans NOTES.md (« Sources ») — l'ajouter, pour qu'un "
              "ami qui reprend cette traduction retrouve le même livret")


def livrer_pdf(tools, jeu, ludo, target, replace):
    """Traduction faite sans spec.py : PDF donnés, original déplacé, index."""
    src = os.path.abspath(opt("--original") or fail("--original \"<livret d'origine>\" manque"))
    pdfs = {"FR": opt("--pdf"), "EN": opt("--pdf-en"), "FR_encre": opt("--pdf-encre")}
    if not os.path.isfile(src):
        fail(f"livret d'origine introuvable : {src}")
    stem = fr_stem(os.path.splitext(os.path.basename(src))[0])
    for lg, f in pdfs.items():
        if f and not os.path.isfile(f):
            fail(f"PDF introuvable : {f}")
        if f and os.path.exists(os.path.join(target, f"{stem}_{lg}.pdf")) and not replace:
            fail(f"{os.path.join(target, f'{stem}_{lg}.pdf')} existe déjà — relancer avec --remplacer")
    noter_origine(tools, deplacer_original(src, target, replace))
    for lg, f in pdfs.items():
        if f:
            shutil.copy(f, os.path.join(target, f"{stem}_{lg}.pdf"))
            print(f"traduction -> {os.path.join(target, f'{stem}_{lg}.pdf')}")
            signaler_poids(os.path.join(target, f"{stem}_{lg}.pdf"))
    typ = opt("--type") or "recréé"
    indexer(ludo, jeu, tools, typ + (" (FR + EN)" if pdfs["EN"] else "") + (" + encre" if pdfs["FR_encre"] else ""))


def read_src(spec_path):
    """Valeur de SRC (chemin absolu) et lignes de l'affectation dans spec.py."""
    code = open(spec_path, encoding="utf8").read()
    for node in ast.parse(code).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "SRC" for t in node.targets):
            ns = {"__file__": spec_path}
            exec("import os\n" + "\n".join(code.splitlines()[:node.end_lineno]), ns)
            return os.path.abspath(ns["SRC"]), node.lineno, node.end_lineno
    fail(f"SRC introuvable dans {spec_path}")


def font_families(ff):
    from fontTools.ttLib import TTFont
    names = []
    for f in sorted(os.listdir(ff)) if os.path.isdir(ff) else []:
        if f.lower().endswith((".ttf", ".otf")):
            try:
                n = TTFont(os.path.join(ff, f))["name"].getBestFamilyName()
            except Exception:
                n = os.path.splitext(f)[0]
            n = re.sub(r"\s+(Regular|Bold|Italic|Medium|Light|Black|ExtraBold|SemiBold|Narrow)\b.*$", "", n)
            if n not in names:
                names.append(n)
    return ", ".join(names)


def from_notes(notes, key):
    if not os.path.isfile(notes):
        return None
    m = re.search(key + r"\s*:\s*([^.\n(]+)", open(notes, encoding="utf8").read())
    return m.group(1).strip() if m else None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tools = os.path.abspath(sys.argv[1])
    spec_path = os.path.join(tools, "spec.py")
    jeu = os.path.basename(tools)
    ludo = os.path.dirname(os.path.dirname(tools))
    target = os.path.join(ludo, jeu)
    replace = "--remplacer" in sys.argv
    if "--pdf" in sys.argv:
        return livrer_pdf(tools, jeu, ludo, target, replace)
    if not os.path.isfile(spec_path):
        fail(f"{tools} n'est pas un dossier d'outils (pas de spec.py) — traduction faite autrement : --pdf")
    scan = os.path.isfile(os.path.join(tools, "scan.py")) and not os.path.isfile(os.path.join(tools, "build.py"))
    engine = "scan.py" if scan else "build.py"
    en = bilingue(spec_path)
    encre = "--encre" in sys.argv  # version économe en encre, en plus du livret normal
    if encre and scan:
        fail("--encre ne vaut que pour un livret à texte : sur un scan, le fond EST l'image scannée")

    src, l0, l1 = read_src(spec_path)
    if not os.path.isfile(src):
        fail(f"livret d'origine introuvable : {src}")
    stem = os.path.splitext(os.path.basename(src))[0]
    fr_name = fr_stem(stem) + "_FR.pdf"
    fr_path = os.path.join(target, fr_name)
    en_path = os.path.join(target, fr_stem(stem) + "_EN.pdf")
    encre_path = os.path.join(target, fr_stem(stem) + "_FR_encre.pdf")
    if en and os.path.normcase(en_path) == os.path.normcase(os.path.join(target, os.path.basename(src))):
        fail(f"la version anglaise écraserait le livret d'origine ({en_path}) — renommer l'original, "
             "par exemple « <nom>_EN_original.pdf », puis relancer")
    for p in [fr_path] + ([en_path] if en else []) + ([encre_path] if encre else []):
        if os.path.exists(p) and not replace:
            fail(f"{p} existe déjà — relancer avec --remplacer pour l'écraser")

    # 1-2. dossier du jeu, livret d'origine, SRC
    dest = deplacer_original(src, target, replace)
    rel = os.path.relpath(dest, tools).replace("\\", "/").split("/")
    new = "SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), " + \
          ", ".join('"' + x + '"' for x in rel) + ")"
    lines = open(spec_path, encoding="utf8").read().splitlines()
    lines[l0 - 1:l1] = [new]
    open(spec_path, "w", encoding="utf8").write("\n".join(lines) + "\n")

    # 3-4. ranger, reconstruire, copier, ranger
    print(run(["ranger.py", tools], tools)[1].splitlines()[-1])
    code, out = run([engine, "sortie.pdf"], tools)
    if code or "ERREUR" in out:
        fail("la reconstruction a échoué :\n" + out[-2000:])
    tail = out[out.find("À VÉRIFIER"):] if "À VÉRIFIER" in out else ""
    # lignes d'origine sans traduction : dites aussi à l'app (reprise d'une traduction d'ami sur un autre livret)
    non_traduit = next((l for l in out.splitlines() if l.startswith("TEXTE NON TRADUIT")), "")
    if non_traduit:
        tail = non_traduit + "\n" + tail
    noter_origine(tools, dest)
    shutil.copy(os.path.join(tools, "sortie.pdf"), fr_path)
    print(f"traduction -> {fr_path}")
    signaler_poids(fr_path)
    if en:  # même spec, textes anglais : X("fr", "en") avec LANGUE=en
        code, out = run([engine, "sortie_en.pdf"], tools, langue="en")
        if code or "ERREUR" in out:
            fail("la reconstruction anglaise a échoué :\n" + out[-2000:])
        shutil.move(os.path.join(tools, "sortie_en.pdf"), en_path)
        for f in ("sortie_en_journal.txt",):
            if os.path.exists(os.path.join(tools, f)):
                os.remove(os.path.join(tools, f))
        print(f"version anglaise -> {en_path}")
        signaler_poids(en_path)
    if encre:  # même spec, fond sombre retiré : version à imprimer
        code, out = run([engine, "sortie_encre.pdf", "--fond-clair"], tools)
        if code or "ERREUR" in out:
            fail("la version économe en encre a échoué :\n" + out[-2000:])
        shutil.move(os.path.join(tools, "sortie_encre.pdf"), encre_path)
        if os.path.exists(os.path.join(tools, "sortie_encre_journal.txt")):
            os.remove(os.path.join(tools, "sortie_encre_journal.txt"))
        print(f"version économe en encre -> {encre_path}")
        signaler_poids(encre_path)
    print(run(["ranger.py", tools], tools)[1].splitlines()[-1])

    # 5. index
    indexer(ludo, jeu, tools, ("scan" if scan else "texte") + (" (FR + EN)" if en else "")
            + (" + encre" if encre else ""))
    if tail:
        print("\n" + tail)


if __name__ == "__main__":
    main()
