# Changelog

Toutes les évolutions notables du plugin. Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
numérotation [sémantique](https://semver.org/lang/fr/).

## [1.7.5] — 2026-11-22
### Ajouté
- `fiche-discord` : un jeu déjà posté à la main, ou par un autre membre, peut être noté (lien du post collé dans
  l'app Règles de jeu, gardé dans `fiche/envoye.txt` avec `"a_la_main": true`, comme après un envoi par webhook) ;
  la skill le respecte même sans fiche préparée : elle donne le lien au lieu de refaire une fiche.

## [1.7.4] — 2026-11-22
### Ajouté
- `bgg.py` : **formats des cartes** relevés par la communauté de BoardGameGeek (page « Sleeves » du jeu), lus par
  l'adresse JSON de cette page (`api.geekdo.com/api/cardsetsbygame`, sans clé ni Cloudflare). `bgg.py fiche` les
  ajoute (ligne `Cartes :`), `bgg.py cartes <identifiant>` les donne seuls. Tous les formats de la boîte, avec leur
  nom quand BGG en a un (`73 cartes (44 x 68 mm : Age Cards), 13 cartes (65 x 100 mm : Wonder Cards)`) ; promos et
  ajouts écartés ; plusieurs éditions relevées : la première, les autres signalées. Sur 250 jeux d'une ludothèque,
  la plupart des jeux édités en Occident sont renseignés, peu des jeux récents du Game Market.
- `fiche-discord` : ligne `Cartes :` remplie par BGG quand le Game Market ne la donne pas, avec tous les formats.

## [1.7.3] — 2026-11-21
### Ajouté
- `build.py` : contrôle **« TEXTE GARDÉ EFFACÉ »**. Effacer une ligne traduite retire aussi toute lettre gardée
  (titre du jeu, lettre d'un pion) dont la boîte de police touche la zone, alors que la lettre elle-même en est loin :
  « SHUFFLE » de Shuffle and Swing avait perdu U F F sous « RULEBOOK », réparé à la main après coup. Le journal liste
  maintenant ces lettres (boîte dans une zone effacée, lettre dehors, disparition visible : l'original et le français
  diffèrent à son endroit) ; sur 15 livrets reconstruits, seule alerte en plus : les lettres A, B, C des pions
  d'Escape to Cosmo, effacées sans que personne l'ait vu. Correction (`AVANT_TEXTE`) dans `references/pieges.md`.

## [1.7.2] — 2026-11-16
### Corrigé
- `controle.py` : le contrôle « chevauche une image » ne regarde plus les rectangles des images mais les pixels du
  décor sous chaque ligne française (page construite sans son texte) : papier, fonds et aplats sont ignorés, une
  légende qui mord de quelques points sur une illustration, une flèche ou une icône est signalée (« chevauche un
  dessin (N pt) »), et ce que l'original pose déjà sur un dessin ne compte pas. Sur OSTIA (fond fait de grandes
  images), 340 alertes presque toutes fausses, qui noyaient les légendes posées sur la tuile de ville et une
  remarque débordant sur la carte, deviennent 9 alertes, toutes vraies.
- Relecteur visuel : zoom sur chaque légende placée autour d'une illustration (étendue comparée à l'original), et
  sur toute alerte « chevauche un dessin » ; jusqu'à 12 zooms.

## [1.7.1] — 2026-11-11
### Corrigé
- `rechercher` : BoardGameGeek n'est plus ouvert dans le navigateur piloté (bloqué par la vérification anti-robots de
  Cloudflare) : le jeu est trouvé par l'API officielle (`scripts/bgg.py`, déplacé de `fiche-discord`, qui l'utilise
  toujours) ; l'onglet « Files » passe par le Chrome de l'utilisateur, sinon son lien lui est donné.

## [1.7.0] — 2026-11-11
### Ajouté
- Skill **`fiche-discord`** (reprise du dépôt `fiche-jeu-discord`) : fiche de présentation d'un jeu pour le salon
  forum *discussion-par-titre* du Discord Golden Meeple (auteurs, liens BGG / boutique / LEX PLI / Game Market, type,
  cartes, couverture), rangée avec les outils du jeu : `<Ludothèque>/_outils/<Jeu>/fiche/` (`titre.txt`,
  `message.txt`, `notes.txt`, `couverture.*`, `fiche.json`), synchronisée avec eux. Livrets pris dans le dossier du jeu, sans copie :
  anglais (ou VO) et français, tous joints au message du post ; BoardGameGeek lu par son API (`bgg.py`, clé BGG
  de l'app) et non par le navigateur, que Cloudflare bloque ; version allégée au-delà de 10 Mo. Publication à la main par
  défaut ; `webhook.py` prêt pour le jour où un admin crée un webhook (adresse dans
  `~/.claude/regles-jeu/discord-webhook.txt`, hors de la ludothèque synchronisée).

## [1.6.8] — 2026-11-11
### Corrigé
- `build.py` : les étapes lettrées en début de ligne (`A. `, `B. `, `C. `…, suivies d'une espace) sont reconnues
  comme des puces, comme `1.`, `2.` : la lettre est gardée et le texte traduit s'aligne après elle. `B.Placez`
  (sans espace), `A.B.C.` ou un mot ordinaire ne le sont pas.
- `controle.py` : la lecture du texte n'extrait plus les images (`TEXTFLAGS_DICT & ~TEXT_PRESERVE_IMAGES`) ; sur un
  livret riche en images, le contrôle était si lent qu'il semblait bloqué. Le texte lu est le même.

## [1.6.7] — 2026-11-11
### Corrigé
- `build.py` : une grande image posée à côté d'un paragraphe (plateau, illustration) le borne comme une colonne
  voisine. Avant, la recherche des colonnes ne voyait que le texte : un paragraphe tenu en colonne étroite à côté
  d'une image (Yunnan p. 4 : la mise en place à gauche du plateau) s'élargissait en français jusqu'au bord de la
  page, par-dessus l'image. Une image de fond, sous le texte, ne compte pas.

## [1.6.6] — 2026-11-11
### Ajouté
- `livrer.py` note le livret d'origine traduit dans `_outils/<Jeu>/origine.json` (nom, taille, pages, empreinte
  SHA-256, liens de « Sources ») : un ami qui suit ce dossier d'outils reconnaît le même livret chez lui, même
  renommé, et sait où le télécharger. Sans lien dans NOTES.md, la livraison le signale.
- `livrer.py` affiche aussi la ligne « TEXTE NON TRADUIT » de la construction (l'app s'en sert pour dire qu'un
  livret n'est pas tout à fait celui qu'un ami a traduit).
- La méthode demande de toujours garder dans « Sources » le lien direct vers le livret d'origine.

## [1.6.5] — 2026-11-10
### Corrigé
- `build.py` : la page de mesure du texte faisait 1000 pt de large ; sur un livret plus large (dépliant de 1612 pt
  de The Six Of VIII, livret paysage de 17 Dice Bets), un texte posé au-delà tombait hors de la page et la
  construction s'arrêtait (« le texte français ne produit rien à l'écran »). La page de mesure prend maintenant la
  largeur du cadre ; rien ne change pour les livrets de taille habituelle. Correctif d'abord fait à la main dans
  `_outils/The Six Of VIII/`, reporté ici.

## [1.6.4] — 2026-11-10
### Corrigé
- `comprimer.py` : la version allégée était illisible dans Acrobat, et ses images noires dans les navigateurs, quand
  le livret avait des images en profil CMJN d'imprimeur (ICC à 4 composantes) : `rewrite_images` les passait en JPEG
  RVB sans changer leur espace de couleur. Chaque JPEG reçoit maintenant l'espace de ses vraies composantes, et le
  script refuse d'enregistrer une version qui garderait une incohérence (The Six Of VIII : 73 images sur 75).
- Livret de plus de 10 Mo : la version allégée est proposée par une vraie question avant le bilan, plus par une
  phrase en fin de bilan qui passait inaperçue (SKILL.md, `references/alleger.md`).

## [1.6.3] — 2026-11-09
### Corrigé
- Aide-mémoire : les titres gardés en anglais dans le livret traduit (titres décoratifs, comme « Haggis
  (3-Player) ») ne sont plus recopiés tels quels ; la méthode demande de les écrire en français, et
  `aide_memoire.py` signale les restes (« À VÉRIFIER : anglais »).

## [1.6.2] — 2026-11-06
### Corrigé
- `build.py` : les lignes d'un tableau ou le bord d'un cadre qui passent juste sous une ligne traduite ne sont plus
  prises pour un soulignement et restent en place (Mini Express : table des matières et tableau de scores avaient
  perdu leurs lignes). Un trait qui dépasse le texte de la ligne, ou qui prolonge un trait plus long, est gardé ;
  `pieges.md` l'explique.

## [1.6.1] — 2026-11-04
### Corrigé
- `livrer.py` : un livret déjà rangé à l'identique dans le dossier du jeu ne reste plus dans `A traduire` après la
  livraison (il y restait proposé à la traduction). La copie exacte de `A traduire` est retirée, sans `--remplacer` ;
  un livret différent arrête toujours la livraison.

## [1.6.0] — 2026-11-03
### Ajouté
- Livret introuvable (skill `rechercher`) : au lieu de seulement demander un autre nom ou un lien, la skill
  propose d'écrire à l'auteur. Elle cherche où le joindre (e-mail publié, formulaire, X…), rédige un court message
  en anglais demandant le livret en PDF, l'enregistre dans `_outils/<Jeu>/message_auteur.txt` et note le contact
  dans `NOTES.md` ; l'utilisateur l'envoie lui-même. Méthode : `skills/rechercher/references/ecrire-auteur.md`.

## [1.5.0] — 2026-11-01
### Ajouté
- Drapeau de la langue remplacé par le drapeau français : réglage `DRAPEAUX` du spec (`[(page, rect, "rond" |
  "rect")]`), peint par `drapeau.py` (nouveau) dans `build.py` et dans `scan.py` (mode « recouvrir ») ; version
  française seulement. La méthode demande de chercher ce drapeau sur la planche de chaque livret
  (`references/pieges.md`, « Drapeau de la langue d'origine »).

## [1.4.0] — 2026-11-01
### Modifié
- Aide-mémoire sur deux pages quand une seule ne suffit pas : plutôt que de réduire le texte sous 8,5 pt,
  `aide_memoire.py` le pose sur deux pages A4 à imprimer en recto-verso (la seconde rappelle le titre, pages
  numérotées « 1 / 2 », aperçu de la 2e page en `<aperçu>-2.png`) ; `--une-page` garde l'ancien comportement.
  Rédaction : 350 à 500 mots pour une page, jusqu'à 900 pour un jeu riche.

## [1.3.0] — 2026-10-28
### Ajouté
- Aide-mémoire d'une page d'un jeu, à la demande (skill `traduire`) : Claude résume en français, d'après le texte
  du livret, le but, la mise en place, le tour de jeu, la fin de manche et le score, la fin de partie et les pièges,
  dans `_outils/<Jeu>/aide-memoire.json` ; `aide_memoire.py` (nouveau) en fait une page A4 sur deux colonnes, la
  couverture du livret en vignette, texte réduit pas à pas pour tenir sur la page, rangée en
  `<Jeu>/<nom>_aide-memoire.pdf`. Documentation : `skills/traduire/references/aide-memoire.md`.

## [1.2.0] — 2026-10-28
### Ajouté
- Version allégée d'un livret pour Discord (10 Mo) : `livrer.py` signale tout livret livré qui atteint 10 Mo,
  et `comprimer.py` (nouveau) écrit `<nom>_light.pdf` à côté du livret, qui reste intact en pleine qualité.
  Essais du plus doux au plus serré, arrêtés au premier qui passe ; le texte, vectoriel, n'est pas touché et
  l'égalité du texte est vérifiée après coup. Documentation : `skills/traduire/references/alleger.md`.

## [1.1.0] — 2026-10-27
### Ajouté
- Version économe en encre d'un livret à fond sombre, à la demande de l'utilisateur : `build.py --fond-clair`
  (nouveau `encre.py`), `noir.py --clair` pour un livret recomposé, `livrer.py --encre` pour livrer
  `<nom>_FR_encre.pdf` à côté du livret normal. Documentation : `skills/traduire/references/encre.md`.
  Le fond (image ou aplat) est retiré, les autres couleurs voient leur clarté inverser à teinte constante,
  le texte est assombri jusqu'à rester lisible, les illustrations gardent leurs couleurs. Les livrets scannés
  ne sont pas couverts.

### Corrigé
- `livrer.py` : la version anglaise n'est construite que si le spec appelle vraiment `X()`, et ne peut plus
  écraser le livret d'origine (correctif repris de notoriousFabb).

## [1.0.0] — 2026-10-27
### Ajouté
- Plugin `regles-jeu` : réunion des skills `recherche-regles-jeu` (devenue `rechercher`) et
  `traduction-regles-jeu` (devenue `traduire`), avec tout leur historique.
- Agents relecteurs fournis avec le plugin : `regles-jeu:relecteur-texte` et `regles-jeu:relecteur-visuel`.
- Boutique d'installation (`/plugin marketplace add vinchy1/regles-jeu`).

### Changé
- Commandes directes : `/regles-jeu:rechercher` et `/regles-jeu:traduire`.
- La skill de traduction évolue indépendamment du dépôt de notoriousFabb.

### Contenu repris des anciennes skills
- Version anglaise des livrets (`_EN.pdf`) depuis une seule spec bilingue.
- Rendu « recomposer » pour les scans froissés, fond « dominant » des masques.
- Livraison d'une traduction faite sans spec (`livrer.py --pdf`).
- Fichiers de travail allégés (moins de jetons).
