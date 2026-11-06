# Changelog

Toutes les évolutions notables du plugin. Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
numérotation [sémantique](https://semver.org/lang/fr/).

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
