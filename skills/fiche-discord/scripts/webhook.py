"""Envoi de la fiche d'un jeu dans le salon forum Discord par un webhook du serveur.

    python -I -X utf8 webhook.py "<Ludothèque>/<Jeu>"                 ESSAI : contrôle tout, n'envoie rien
    python -I -X utf8 webhook.py "<Ludothèque>/<Jeu>" --envoyer       crée le post, en un seul message : titre,
                                                                      message, couverture et livrets de fiche.json

La fiche est avec les outils du jeu, <Ludothèque>/_outils/<Jeu>/fiche/ (titre.txt, message.txt, couverture.*,
fiche.json) ; les livrets restent dans le dossier du jeu, <Ludothèque>/<Jeu>/. Adresse du webhook : variable d'environnement DISCORD_WEBHOOK_FICHES, ou
fichier ~/.claude/regles-jeu/discord-webhook.txt (hors de la ludothèque, qui est synchronisée). Elle n'est jamais
affichée : c'est un secret. Après un envoi, fiche/envoye.txt garde le lien du post (empêche un second envoi).
"""
import json, mimetypes, os, re, sys, urllib.error, urllib.request, uuid
from pathlib import Path

MAX_MESSAGE = 2000          # caractères par message Discord
MAX_TITRE = 100             # caractères pour un titre de post
MAX_FICHIERS = 10           # pièces jointes par message
MAX_OCTETS = 10 * 1024 ** 2  # total des pièces jointes sans boost du serveur
FORME = re.compile(r"https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/\d+/[\w-]+")
SECRET = Path.home() / ".claude" / "regles-jeu" / "discord-webhook.txt"


def adresse():
    url = os.environ.get("DISCORD_WEBHOOK_FICHES") or (SECRET.read_text("utf-8").strip() if SECRET.exists() else "")
    if not url:
        sys.exit(f"ERREUR : pas d'adresse de webhook (ni {SECRET}, ni DISCORD_WEBHOOK_FICHES).")
    if not FORME.fullmatch(url):
        sys.exit("ERREUR : l'adresse du webhook n'a pas la forme https://discord.com/api/webhooks/<id>/<jeton>.")
    return url


def appel(url, donnees=None, entete=None):
    req = urllib.request.Request(url, data=donnees, headers={"User-Agent": "regles-jeu", **(entete or {})},
                                 method="POST" if donnees else "GET")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        sys.exit(f"ERREUR Discord {e.code} : {detail}")


def corps(payload, fichiers):
    """multipart/form-data : payload_json + files[n]."""
    borne = uuid.uuid4().hex
    parts = [f'--{borne}\r\nContent-Disposition: form-data; name="payload_json"\r\n'
             f"Content-Type: application/json\r\n\r\n".encode() + json.dumps(payload).encode() + b"\r\n"]
    for i, f in enumerate(fichiers):
        type_ = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        parts.append(f'--{borne}\r\nContent-Disposition: form-data; name="files[{i}]"; filename="{f.name}"\r\n'
                     f"Content-Type: {type_}\r\n\r\n".encode() + f.read_bytes() + b"\r\n")
    parts.append(f"--{borne}--\r\n".encode())
    return b"".join(parts), {"Content-Type": f"multipart/form-data; boundary={borne}"}


def lire(f):
    return f.read_text("utf-8").strip() if f.exists() else ""


def pieces(jeu, fiche, problemes):
    """Couverture et livrets nommés dans fiche.json (« livrets » ; anciennes fiches : « premier » puis « reponse »),
    pris à la racine du dossier du jeu."""
    try:
        info = json.loads(lire(fiche / "fiche.json") or "{}")
    except ValueError:
        info = {}
        problemes.append("fiche.json illisible")
    noms = info.get("livrets") or [*(info.get("premier") or []), *(info.get("reponse") or [])]
    out = sorted(f for f in fiche.glob("couverture.*") if f.is_file())[:1]
    for nom in dict.fromkeys(noms):
        f = jeu / os.path.basename(str(nom))
        leger = f.with_name(f.stem + "_light.pdf")  # trop lourd pour Discord : sa version allégée, si elle existe
        if f.is_file() and f.stat().st_size > MAX_OCTETS and leger.is_file():
            f = leger
        if f.is_file():
            out.append(f)
        else:
            problemes.append(f"livret absent du dossier du jeu : {nom}")
    return out


def controler(message, fichiers, problemes):
    if not message and not fichiers:
        problemes.append("rien à envoyer")
    if len(message) > MAX_MESSAGE:
        problemes.append(f"message trop long : {len(message)} caractères (max {MAX_MESSAGE})")
    if len(fichiers) > MAX_FICHIERS:
        problemes.append(f"trop de pièces jointes : {len(fichiers)} (max {MAX_FICHIERS})")
    total = sum(f.stat().st_size for f in fichiers)
    if total > MAX_OCTETS:
        lourd = [f.name for f in fichiers if f.stat().st_size > MAX_OCTETS]
        problemes.append(f"pièces jointes trop lourdes pour un seul envoi : {total / 1024 ** 2:.1f} Mo en tout (max "
                         f"{MAX_OCTETS / 1024 ** 2:.0f} Mo sans boost du serveur) : "
                         + (f"faire la version allégée (_light.pdf) de {', '.join(lourd)}" if lourd else
                            "chaque livret passe seul, mais pas ensemble : poster à la main (Discord compte par fichier), "
                            "ou mettre le lien d'un livret dans le message"))


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-") or set(args[1:]) - {"--envoyer"}:
        sys.exit(__doc__)
    jeu, envoyer = Path(args[0]).resolve(), "--envoyer" in args
    if jeu.name == "fiche":  # dossier de la fiche donné : _outils/<Jeu>/fiche → <Ludothèque>/<Jeu>
        jeu = jeu.parent.parent.parent / jeu.parent.name if jeu.parent.parent.name == "_outils" else jeu.parent
    fiche = jeu.parent / "_outils" / jeu.name / "fiche"
    if not fiche.is_dir():
        sys.exit(f"ERREUR : pas de fiche pour {jeu.name} ({fiche} absent).")
    trace = fiche / "envoye.txt"
    deja = json.loads(trace.read_text("utf-8")) if trace.exists() else {}
    problemes = []

    if deja.get("post"):
        sys.exit(f"ERREUR : ce post a déjà été créé ({deja.get('lien', deja['post'])}). Rien envoyé.")
    titre, message = lire(fiche / "titre.txt"), lire(fiche / "message.txt")
    fichiers = pieces(jeu, fiche, problemes)
    if not titre:
        problemes.append("titre.txt manquant ou vide")
    elif len(titre) > MAX_TITRE:
        problemes.append(f"titre trop long : {len(titre)} caractères (max {MAX_TITRE})")
    controler(message, fichiers, problemes)

    print(f"Nouveau post : {titre}")
    print(f"Message ({len(message)} caractères) :\n{message}\n")
    for f in fichiers:
        print(f"Pièce jointe : {f.name} ({f.stat().st_size / 1024:.0f} Ko)")
    if problemes:
        sys.exit("\nPROBLÈMES (rien envoyé) :\n- " + "\n- ".join(problemes))
    url = adresse()
    info = appel(url)  # lecture seule : vérifie que le webhook existe et donne son salon
    print(f"\nWebhook « {info.get('name')} » → salon {info.get('channel_id')} (serveur {info.get('guild_id')})")
    if not envoyer:
        print("\nESSAI : tout est en ordre, rien n'a été envoyé.")
        return

    payload = {"content": message, "allowed_mentions": {"parse": []},
               "attachments": [{"id": i, "filename": f.name} for i, f in enumerate(fichiers)], "thread_name": titre}
    retour = appel(url + "?wait=true", *corps(payload, fichiers))
    lien = f"https://discord.com/channels/{info.get('guild_id')}/{retour['channel_id']}/{retour['id']}"
    deja.update(post=retour["channel_id"], lien=lien)
    trace.write_text(json.dumps(deja, ensure_ascii=False, indent=2), "utf-8")
    print(f"\nENVOYÉ : {lien}")


if __name__ == "__main__":
    main()
