# Aide-mémoire (une page, deux au besoin)

Une page A4 à poser sur la table pendant la partie (deux, en recto-verso, quand le jeu le demande) : mise en place, déroulement d'un tour, fin de partie et
score, points qu'on oublie. **À la demande seulement**, jamais d'office : pour un jeu déjà traduit, un jeu
livré en français, ou juste après une traduction si l'utilisateur le demande. Toujours **en français**, quelle
que soit la langue du livret.

## 1. Lire les règles (texte, pas d'images)
Dans l'ordre de préférence :
- le livret français du jeu (`<Ludothèque>/<Jeu>/<nom>_FR.pdf`, ou un livret français livré par l'éditeur) :
  `python -X utf8 -c "import pymupdf; [print('=== p', i + 1, p.get_text()) for i, p in enumerate(pymupdf.open(r'<livret>'))]"` ;
- sinon le `spec.py` du dossier d'outils (textes français déjà écrits) ;
- sinon le livret d'origine (même commande) ; scan sans texte : `blocks.txt` / `zones.py` s'ils existent,
  sinon une planche à 70 dpi puis des zooms sur les zones utiles, comme pour une traduction.
`NOTES.md` du dossier d'outils : vocabulaire choisi et noms de cartes à reprendre tels quels.

## 2. Écrire `_outils/<Jeu>/aide-memoire.json`
Format dans l'en-tête de `scripts/aide_memoire.py`. Sections habituelles, dans cet ordre, à adapter au jeu :
1. **Mise en place** (`etapes`) — matériel à distribuer selon le nombre de joueurs, premier joueur ;
2. **Tour de jeu** ou **Un pli** (`etapes`) — l'enchaînement, dans l'ordre où on le fait ;
3. actions ou pouvoirs particuliers (`points`, ou `tableau` nom → effet pour des cartes spéciales) ;
4. **Fin de manche** / **Score** (`points` ; `tableau` pour un barème) ;
5. **Fin de partie** (`points`) — condition de fin, vainqueur, départage ;
6. **À ne pas oublier** (`points`, `"accent": true`) — 2 à 4 pièges qu'on rate à la première partie.

Règles d'écriture :
- **Rien d'inventé** : chaque phrase vient du livret. Une règle ambiguë ou absente n'y entre pas (la signaler).
- Phrases courtes à l'infinitif ou à l'impératif, chiffres en chiffres ; une idée par ligne.
- **350 à 500 mots** pour une page. Un jeu riche (nombreuses cartes à effet, plusieurs phases, barème détaillé)
  peut aller **jusqu'à 900 mots** : l'aide-mémoire passe alors sur deux pages, à imprimer en recto-verso. Ne pas
  allonger pour remplir : garder ce qui sert pendant la partie ; laisser l'ambiance, le matériel détaillé, les
  exemples longs, les variantes (une ligne au plus pour une variante).
- `**gras**` pour les mots-clés qu'on cherche des yeux (nombres de cartes, conditions de victoire, interdits).
- Vocabulaire de `references/glossaire.md` et de la traduction du jeu ; noms de cartes et de variantes comme dans
  le livret français (préférences de l'utilisateur).
- **Titres et phrases toujours en français**, même quand le livret traduit a gardé un titre en anglais (titre
  décoratif dessiné, noté « non traduit » dans `NOTES.md`) : « Haggis (3-Player) » s'écrit « Haggis à 3 joueurs »,
  « Setup » « Mise en place ». Seuls restent tels quels les noms propres (jeu, variante comme « Haggis and
  Tatties », cartes), avec au besoin une précision en français entre parenthèses. `aide_memoire.py` signale les
  restes repérés (« À VÉRIFIER : anglais ») : les corriger dans le JSON et reconstruire.
- `infos` : type de jeu, joueurs, durée, âge, tels qu'imprimés sur le livret (ou `_outils/bgg.json` s'il y est).
- `source` : le livret lu et ses pages (« CMYK_Rules_FR.pdf, p. 1-12 »).

## 3. Construire et regarder
```
python -X utf8 <skill>/scripts/aide_memoire.py "<Ludothèque>/_outils/<Jeu>/aide-memoire.json" \
    "<Ludothèque>/<Jeu>/<nom>_aide-memoire.pdf" --livret "<livret d'origine.pdf>" --apercu "<scratchpad>/am.png"
```
- `--livret` : la couverture (page 1) en vignette dans l'en-tête — le livret d'origine, reconnaissable sur la table.
- Le texte est réduit pas à pas pour tenir sur une page, sans descendre sous 8,5 pt ; sinon l'aide-mémoire passe
  sur **deux pages** (la 2e rappelle le titre, pages numérotées), avec un texte plus grand. Le journal donne la
  taille et le nombre de pages. « TROP LONG » (même deux pages en 7 pt) : raccourcir le JSON, pas les marges.
  `--une-page` interdit la 2e page (texte réduit jusqu'à 7 pt), si l'utilisateur la refuse.
- Regarder **une fois** l'aperçu à 80 dpi (`am.png`, et `am-2.png` pour une 2e page) : sections dans l'ordre, rien
  de coupé ; puis des zooms seulement là où un doute reste. Corrections : dans le JSON, puis reconstruire.

`<nom>` : celui du livret français (`CMYK_Rules` pour `CMYK_Rules_FR.pdf`), suffixe `_aide-memoire.pdf`, rangé
avec les livrets du jeu. L'app de la ludothèque le reconnaît à ce suffixe et l'ouvre depuis la fiche du jeu.
Ajouter une ligne « Aide-mémoire : fait le <date> » à la fin de `NOTES.md` avec l'outil d'édition (pas `printf` ni `echo`). Résumer à l'utilisateur : fichier, nombre
de pages (deux : à imprimer en recto-verso), taille du texte, ce qui a été laissé de côté.
