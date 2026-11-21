# traduire — skill du plugin regles-jeu

Traduit en français un livret de règles de jeu de société au format PDF, depuis **n'importe quelle langue**
(anglais, allemand, espagnol, italien, japonais…), **en gardant exactement la mise en page** : polices,
illustrations, icônes dans le texte, encadrés, cartes reproduites, positions. Le résultat est un `<nom>_FR.pdf`
prêt à imprimer, rangé à côté de l'original.

Il suffit de déposer le PDF dans un dossier et de demander à Claude Code « traduis-moi ce livret ». La skill fait
le reste : préparation, traduction, construction du PDF, contrôles, relecture, rangement.

Testée sur des livrets de jeux de plis et de cartes : Trick to the Future, Numberwang±, Fright Factor,
Dr. Science, Tricklings / Vazerneiros, Merge Take, Pack Tricks, The Good Farmer, Poker Avoces et Fagioli (anglais ;
Fagioli est un jeu japonais), This is from that customer over there (japonais), et quatre livrets **scannés** : Shinobi Blade (japonais),
After You Betobeto-san, The Final Bosses' Blues et Man Eating House (anglais).

---

## Sommaire
- [Ce qu'elle fait](#ce-quelle-fait)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Organisation des dossiers](#organisation-des-dossiers)
- [Déroulement d'une traduction](#déroulement-dune-traduction)
- [Livrets scannés](#livrets-scannés)
- [Règles sur une page web](#règles-sur-une-page-web)
- [Version économe en encre](#version-économe-en-encre)
- [Version allégée pour Discord](#version-allégée-pour-discord)
- [Aide-mémoire](#aide-mémoire)
- [Contrôles automatiques et relecture](#contrôles-automatiques-et-relecture)
- [Coût en jetons et modèles](#coût-en-jetons-et-modèles)
- [Corriger une traduction déjà faite](#corriger-une-traduction-déjà-faite)
- [Contenu du dépôt](#contenu-du-dépôt)
- [Limites connues](#limites-connues)
- [Remarques](#remarques)

---

## Ce qu'elle fait
- **Détecte la langue** du livret (pas besoin de la préciser) et l'annonce ; ne pose une question que si le
  livret est multilingue ou déjà en partie en français.
- **Retire le texte d'origine** du PDF sans toucher aux images ni aux dessins vectoriels (traits de
  soulignement compris), et sans décaler le texte voisin ni faire ressortir des images cachées (pièges de
  certains livrets InDesign, protégés automatiquement).
- **Pose le texte français au même endroit**, avec des polices libres proches de l'originale (les polices
  embarquées n'ont presque jamais tous les accents), et réduit légèrement la taille si le français est plus long.
- **Trouve seule la mise en page** : colonnes (jusqu'à 4 par page), étapes numérotées posées sur des pastilles,
  paragraphes qui reprennent sous une image.
- **Replace les icônes intégrées au texte** (symboles de couleur, étoiles, lettres cerclées…) au bon endroit
  dans la phrase française.
- **Traduit aussi le texte des cartes** reproduites dans le livret.
- **Respecte la typographie française** : « guillemets », espaces insécables avant ; : ! ?, décimales à virgule,
  pas de coupure dans « Bleu 19 », « joueur A », « page 3 ».
- **Garde un vocabulaire cohérent d'un jeu à l'autre** grâce à un glossaire (pli, entamer, fournir, atout,
  couleur demandée…).
- **Accepte les livrets scannés** (pages-images) : lecture automatique du texte, puis texte de l'image masqué et
  remplacé par le français, ou traduction placée à côté de chaque page.
- **Contrôle son propre travail** : texte oublié, chevauchements, débordements, fautes, termes du glossaire non
  respectés, paragraphes anormalement courts.
- **Signale un livret trop lourd pour Discord** (10 Mo) et propose une version allégée, en gardant le livret en
  pleine qualité intact.
- **Produit une version économe en encre** d'un livret à fond sombre, si on la demande : même mise en page, fond
  blanc, texte foncé, illustrations intactes.
- **Remplace le drapeau de la langue** (Royaume-Uni, États-Unis, Japon…) par le drapeau français dans le livret
  traduit.
- **Fait aussi la version anglaise** si on la demande (utile pour un livret japonais) : la même spec contient
  les deux textes, et la livraison produit `<nom>_FR.pdf` et `<nom>_EN.pdf`.
- **Fait l'aide-mémoire** d'un jeu, si on le demande : mise en place, tour de jeu, fin de partie et score,
  pièges, sur une feuille A4 à poser sur la table (deux pages en recto-verso pour un jeu riche).
- **Range tout** : livrets dans un dossier par jeu, outils allégés à part, index des jeux traduits.

Préférences de traduction appliquées :
- le titre du jeu et les noms de variantes ne sont jamais traduits ;
- les noms de cartes et de personnages restent dans la langue d'origine, avec le français entre parenthèses dans
  les titres (« The Bride (La Fiancée) ») ; pour un alphabet non latin, le nom imprimé en lettres latines, sinon
  le nom anglais officiel, sinon une romanisation ;
- les compromis sont toujours signalés (police réduite, phrase condensée, texte d'illustration non traduit).

---

## Installation
1. **Installer le plugin** `regles-jeu`, qui contient cette skill, la skill de traduction et les
   agents relecteurs : voir le [README du plugin](../../README.md#installation).
2. **Installer Python 3 et les bibliothèques** :
   ```
   pip install pymupdf fonttools pyspellchecker
   ```
   - `pymupdf` : lecture et écriture des PDF ; `fonttools` : polices ; `pyspellchecker` : dictionnaire français
     de la relecture (facultatif : sans lui, seul le contrôle d'orthographe est sauté).
   - Lecture automatique des livrets scannés (Windows uniquement, moteur de lecture intégré à Windows) :
     ```
     pip install winrt-runtime winrt-Windows.Media.Ocr winrt-Windows.Globalization winrt-Windows.Graphics.Imaging winrt-Windows.Storage.Streams winrt-Windows.Foundation winrt-Windows.Foundation.Collections
     ```
     Chaque langue à lire doit être installée dans Windows (Paramètres → Heure et langue → Langue → ajouter la
     langue avec la reconnaissance optique). Le japonais n'y est pas par défaut ; le plus simple est d'installer
     seulement son module de lecture, dans un terminal administrateur :
     ```
     dism /Online /Add-Capability /CapabilityName:Language.OCR~~~ja-JP~0.0.1.0
     ```
     (`Add-WindowsCapability` échoue sous PowerShell 7 avec « Classe non enregistrée »).
3. **Agents relecteurs** : installés avec le plugin (`regles-jeu:relecteur-texte` et
   `regles-jeu:relecteur-visuel`). La relecture est faite sur un modèle moins coûteux (voir
   [Coût en jetons et modèles](#coût-en-jetons-et-modèles)).
4. **Créer le dossier de dépôt** `A traduire` dans votre ludothèque.

Facultatif : un `CLAUDE.md` à la racine de la ludothèque peut noter le chemin exact de Python ou un autre nom
de dossier de dépôt. Les chemins propres à votre machine vont là, pas dans la skill.

---

## Utilisation
Déposer le PDF dans `A traduire/`, ouvrir Claude Code dans ce dossier et demander, par exemple :

> Traduis-moi ce livret de règles : MonJeu_rules.pdf

ou simplement « traduis la règle » s'il n'y a qu'un PDF. On peut aussi donner le chemin d'un PDF ou d'un dossier
situé ailleurs.

**Plusieurs PDF dans le dossier** : Claude les liste (en regroupant ceux d'un même jeu : règles et extension,
livret et aide de jeu), indique le coût estimé (environ 150 000 à 200 000 jetons par livret) et demande s'il faut
tout traduire ou un seul livret ; il ne commence rien avant la réponse. « Tout » : les livrets sont traduits un
par un, avec un court bilan après chacun ; un livret qui pose un vrai problème (police introuvable, scan
illisible…) est mis de côté et signalé, et les autres continuent.

Pour chaque livret, Claude annonce la langue, le nombre de pages et le type
de livret (à texte ou scanné), pose une question seulement si c'est nécessaire (par exemple le rendu d'un livret
scanné), traduit, vérifie, puis range. À la fin, il résume : fichier produit, choix de vocabulaire, compromis.

**Livret seulement consultable en ligne** (lien Google Drive sans téléchargement) : donner le lien à Claude. Le
blocage du téléchargement est un choix du propriétaire : Claude ne le contourne pas. Il cherche un PDF
téléchargeable (site de l'éditeur, BoardGameGeek) ; sinon, il vous propose de demander le fichier au
propriétaire, ou de lui fournir vos propres captures des pages, qu'il assemble en PDF et traite comme un livret
scanné (`references/en-ligne.md`).

**Jeu japonais** : Claude cherche toujours d'abord la fiche du jeu sur le Tokyo Game Market (gamemarket.jp)
et le manuel de l'auteur (titre officiel, noms en lettres latines, errata). Si le livret est lui-même une
traduction (règle anglaise d'un jeu japonais, aide de jeu de fan), il la compare à l'original, signale les écarts
et traduit en suivant l'original (`references/source.md`). Pour les autres langues, il le propose.

Pour corriger une traduction existante : « dans Merge Take, remplace "la plus forte" par "de plus haute
valeur" » (voir [plus bas](#corriger-une-traduction-déjà-faite)).

---

## Organisation des dossiers
```
<Ludothèque>/
├── A traduire/                  ← déposer ici les PDF à traduire
├── Merge Take/                  ← un dossier par jeu, créé à la livraison :
│   ├── MergeTake_EN.pdf             l'original
│   └── MergeTake_FR.pdf             la traduction
├── Pack Tricks/
│   └── …
└── _outils/
    ├── LISEZMOI.md              ← index : une ligne par jeu traduit
    ├── Merge Take/              ← outils du jeu, gardés pour les corrections futures :
    │   ├── spec.py                  la traduction et ses réglages
    │   ├── NOTES.md                 langue, éditeur, polices, vocabulaire, choix, compromis
    │   ├── ff/                      polices de remplacement, allégées
    │   └── build.py, …              scripts copiés de la skill
    └── …
```
- **Les dossiers de jeu ne contiennent que les livrets.** Rien n'y est écrasé sans votre accord.
- **Nom du dossier de jeu** : le titre imprimé en lettres latines (titre anglais officiel ou romanisation pour un
  titre japonais), nettoyé pour Windows : virgules, points d'exclamation et `\ / : * ? " < > |` sont retirés
  (« After You, Betobeto-san » → « After You Betobeto-san », « Dune: Imperium » → « Dune Imperium ») ; les noms
  réservés de Windows (`CON`, `NUL`…) reçoivent « (jeu) ». Si le dossier du jeu existe déjà, il est réutilisé tel
  quel.
- **Le dossier d'outils reste léger** (de l'ordre de 0,5 à 1,5 Mo par jeu) : à la livraison, les fichiers de travail
  sont supprimés et les polices réduites aux seuls caractères du français.
- **L'index `LISEZMOI.md`** reste court même avec des centaines de jeux (une ligne : Jeu | Langue | Éditeur |
  Type | Polices | Date). Claude y cherche par mot-clé (éditeur, police) au lieu de le lire en entier, et ne
  lit le `NOTES.md` que des jeux proches : un nouveau livret du même éditeur réutilise ses polices et son
  vocabulaire.
- **Nom du fichier traduit** : la mention de langue est retirée et `_FR` ajouté à la fin
  (« MergeTake_EN.pdf » → « MergeTake_FR.pdf », « Shinobi Blade.pdf » → « Shinobi Blade_FR.pdf »,
  « Man Eating House ENG Rules.pdf » → « Man Eating House Rules_FR.pdf »). Au milieu du nom, seules les
  abréviations en capitales (EN, ENG, JP…) et les noms de langue en toutes lettres (English, Japanese…) sont
  retirés, pour ne pas toucher un mot du titre (« Take It Easy »).
- **Livret nommé en japonais, chinois…** : il est d'abord renommé en lettres latines, titre anglais officiel
  de préférence et autres mots traduits en anglais (« 夜連_説明書.pdf » → « Who follows me_Rules.pdf »,
  « コスモショーファー_JP_Rule_v1.2.pdf » → « Cosmo Chauffeur_JP_Rule_v1.2.pdf »), ce qui donne un `_FR.pdf`
  lisible partout. L'ancien nom est noté dans `NOTES.md`.
- **Retraduction** d'un livret déjà rangé dans `<Jeu>/` : les outils vont dans `_outils/<Jeu>/` et rien n'est
  déplacé.
- Si le PDF n'est ni dans `A traduire/` ni dans un dossier de jeu, les outils sont créés à côté du PDF et rien
  n'est déplacé.

---

## Déroulement d'une traduction
1. **Préparer** (`preparer.py`) : nettoie le nom du jeu, crée `_outils/<Jeu>/`, détecte un livret scanné, copie
   les scripts utiles et un modèle de `spec.py` (chemin du livret déjà rempli), fait une planche d'aperçu des
   pages, l'inventaire du texte (`blocks.txt`, icônes comprises), extrait les polices et signale les accents qui
   leur manquent, devine la langue, lit le texte des scans, et liste les jeux déjà traduits qui utilisent les
   mêmes polices.
2. **Choisir les polices** (`polices.py`) : réutiliser celles d'un jeu proche, sinon trouver des polices libres
   de même allure (comparaison visuelle et de largeur), placées dans `ff/`. Les correspondances déjà trouvées
   sont dans `references/polices.md`.
3. **Traduire** : Claude écrit `spec.py`, qui associe chaque bloc de texte d'origine à sa traduction française.
   Exemple :
   ```python
   F(0, P("b18", "Cartes Slime (numérotées) : 46<br/>Remarque : en principe, chaque combinaison…"))
   #    page ↑   ↑ bloc 18 de l'inventaire     ↑ français (<b>, <i>, <br/>, {} = icône suivante)
   ```
   La mise en page (colonnes, pastilles, insécables) est trouvée par le moteur ; le spec ne contient des
   réglages (`x1=`, `fix=`, `COLUMNS`) que pour corriger un cas raté. Pour dessiner sous le français (élargir un
   bandeau de titre trop court, remplacer un drapeau), le spec peut fournir une fonction `AVANT_TEXTE`, appelée
   entre l'effacement de l'original et la pose du français.
4. **Construire** (`build.py`) : efface le texte d'origine, pose le français et les icônes, et écrit un journal :
   police réduite, débordement, icône non replacée, **texte non traduit**, **texte gardé effacé**, **à vérifier**
   (voir plus bas).
5. **Relire** : texte et mise en page, par deux agents relecteurs ; Claude vérifie chaque point signalé avant de
   corriger, reconstruit, et ne regarde que les pages modifiées.
6. **Livrer** (`livrer.py`) : Claude écrit `NOTES.md`, puis le script déplace l'original dans `<Jeu>/`, met à
   jour le chemin dans `spec.py`, allège le dossier d'outils (`ranger.py`), reconstruit le PDF final, le copie en
   `<nom>_FR.pdf` (refuse d'écraser un PDF existant sans accord) et ajoute ou met à jour la ligne de l'index.

---

## Livrets scannés
Un livret dont les pages sont des images (pas de texte sélectionnable) est détecté automatiquement. Trois rendus
au choix :
- **Recouvrir** (conseillé pour une image numérique propre) : chaque zone de texte de l'image est masquée par la
  couleur du fond mesurée autour (ou, pour des encadrés semi-transparents, la couleur dominante de la zone), et le
  français est posé dedans, la police étant réduite au besoin pour tenir.
- **Côte à côte** : chaque page d'origine reste intacte, sa traduction complète est placée à droite.
- **Recomposer** (conseillé pour un scan papier plié ou froissé) : le livret est réécrit à neuf, même découpage
  et mêmes couleurs, sans l'image du scan (`references/recomposer.md`, exemple dans `exemples/recomposer/`).

Le texte de l'image est lu automatiquement (`ocr.py`, moteur de Windows, résolution adaptée à celle du scan ;
japonais choisi seul quand le livret en contient) et regroupé en paragraphes
avec leur position (`zones.py`), ce qui évite de recopier le texte à la main. Sans la langue installée dans
Windows (souvent le cas du japonais), Claude lit les pages en images, ce qui coûte plus cher.

Pour le rendu « recouvrir », la skill sait aussi :
- poser les symboles ①❶◆★ avec une police de Windows (Segoe UI Symbol, copiée d'office) quand celle du texte
  ne les a pas ;
- découper une icône de l'original (`icone.py`) pour la remettre dans la phrase française ;
- refaire les titres sur bandeau ou sur pastille, en élargissant le bandeau si le français est plus long ;
- garder à leur taille les zones d'une seule ligne (interligne et marge resserrés d'office) ;
- poser une étiquette verticale (`rot`) ;
- sur un livret dont les lettres sont des tracés vectoriels (ni texte ni image), supprimer les lettres au lieu
  de poser un aplat (`VECTEUR = True`) : le fond d'origine reste intact sous le français.

Livrets à texte : les puces japonaises (●, 〇, ❶, ①…), les étiquettes penchées (`INCLINEES`) et les titres
aux lettres doublées d'un contour (`CONTOURS`) sont gérés par `build.py` (voir `references/pieges.md`).

Détails : `references/scan.md`.

---

## Règles sur une page web
Quand les règles ne sont publiées que sur une page web (Google Sites, Notion, site de l'éditeur), le PDF fait
par la skill [rechercher](../rechercher/README.md) n'est pas recouvert : la
page elle-même est traduite (`page_web.py` liste ses morceaux de texte dans l'ordre d'affichage, puis remet le
français à leur place), et remise en PDF avec le même script (`page_pdf.py --garder` garde la page et ses
images). Le livret français a exactement la présentation du site, sans police réduite ni texte condensé.
Le texte dessiné dans les images reste dans la langue d'origine. Détails : `references/page-web.md`.

---

## Version économe en encre
Un livret à fond noir ou très sombre vide une cartouche à l'impression. Sur demande — jamais d'office — la
skill construit **en plus** du livret normal un second PDF prêt à imprimer, même mise en page, fond blanc :
`<nom>_FR_encre.pdf`. Le livret normal reste la référence.

Page sombre par page sombre (une page déjà claire est laissée telle quelle) :
- l'image ou l'aplat qui couvre la page n'est plus peint : le papier blanc reste ;
- les autres couleurs voient leur **clarté inverser à teinte constante** : filet clair → filet foncé, pastille
  sombre → pastille claire ;
- les couleurs de **texte** sont en plus assombries tant que le contraste sur blanc est insuffisant, sinon un
  titre clair resterait pâle et illisible une fois le fond blanc ;
- les **images gardent leurs couleurs** : illustrations, logos et pictogrammes sont imprimés tels quels. Une
  illustration sombre reste sombre — c'est voulu, l'économie vient du fond.

Le texte français est posé dans la couleur inversée de l'original : un texte blanc sur fond noir devient noir sur
blanc sans rien changer au `spec.py`. Un livret recomposé à neuf a son propre mode clair (`noir.py --clair`).
Les livrets scannés ne sont pas couverts. Détails : `references/encre.md`.

---

## Version allégée pour Discord
Discord refuse un fichier de plus de 10 Mo, et c'est là que les livrets sont publiés la plupart du temps. À la
livraison, un livret qui atteint 10 Mo est signalé ; la skill **propose** alors une version allégée, sans jamais
la faire d'office. Sous 10 Mo, rien n'est signalé.

`comprimer.py` écrit `<nom>_FR_light.pdf` à côté du livret. **Le livret en pleine qualité n'est ni touché ni
remplacé** : la version allégée est un fichier de plus, à n'envoyer que sur Discord. Les essais vont du plus
doux au plus serré et s'arrêtent au premier qui passe sous la limite : nettoyage seul, puis images recompressées
en JPEG (qualité 92, 85, 80…), puis résolution des images très fines ramenée à 300, 220, 170 dpi…

Le **texte reste du texte** : vectoriel, il n'est jamais touché et reste net à l'écran comme à l'impression. Le
script le vérifie page par page après coup. Détails : `references/alleger.md`.

---

## Aide-mémoire
« Fais l'aide-mémoire de CMYK » : Claude lit le texte du livret (le français s'il existe, sinon l'original) et
écrit un résumé en français qui tient sur **une page A4**, ou deux en recto-verso pour un jeu riche : but du jeu, mise en place, tour de jeu, fin de manche
et score, fin de partie, et un encadré « À ne pas oublier ». Rien n'y est inventé : chaque ligne vient du livret,
dont les pages sont citées en bas de la feuille.

`aide_memoire.py` met la page en forme : en-tête avec la couverture du livret en vignette, sections sur deux
colonnes, chacune d'un seul bloc, texte réduit pas à pas pour tenir sur la page. Plutôt que de descendre sous
8,5 pt, il passe sur deux pages numérotées (la seconde rappelle le titre), avec un texte plus grand ; `--une-page`
l'en empêche. Fond blanc, à imprimer. Le contenu est rangé dans `_outils/<Jeu>/aide-memoire.json`, la feuille dans
`<Jeu>/<nom>_aide-memoire.pdf`, à côté des livrets. Détails : `references/aide-memoire.md`.

---

## Contrôles automatiques et relecture
**Pendant la construction** (`build.py`, `scan.py`, `controle.py`) :
- **TEXTE NON TRADUIT** : toute ligne d'origine ni remplacée ni volontairement ignorée (`IGNORE`) est listée.
- **TEXTE GARDÉ EFFACÉ** : texte gardé tel quel (titre du jeu, lettre sur un pion) emporté par l'effacement
  d'une ligne voisine traduite : le PDF efface toute lettre dont la boîte touche la zone, et une grande police a
  des boîtes bien plus hautes que ses lettres. Seules les lettres dont la disparition se voit sont signalées.
- **À VÉRIFIER** : français qui chevauche une image, un autre texte ou un reste de texte d'origine, ou qui sort
  de la page ; sur un scan, ligne d'origine qui dépasse d'un masque.
- **DÉBORDE / police réduite** : le français ne tient pas à la taille d'origine.
- **flux protégé / réécriture du flux annulée** : avant d'effacer le texte d'origine, `build.py` réécrit
  certaines pages (livrets InDesign japonais) pour éviter que des lignes voisines se décalent ou disparaissent,
  ou que des images cachées réapparaissent ; si cela fait bouger le moindre mot, la réécriture est annulée et
  la page est à regarder de près.

**Relecture du texte** (`relecture.py`) : écrit `texte_fr.txt` (original et français, paragraphe par paragraphe)
et signale les mots inconnus du dictionnaire, les fautes de typographie, l'anglais resté, les termes du glossaire
non respectés (« trump » sans « atout ») et les paragraphes anormalement courts ou longs (signe d'un oubli).
Avec `LANGUE=en`, elle relit la version anglaise (`texte_en.txt`, orthographe anglaise).

**Deux agents relecteurs** (`agents/`), lancés en parallèle :
- **relecteur-texte** lit tout le texte et rend les contresens, oublis, incohérences de vocabulaire et fautes,
  et dit pour chaque alerte automatique si elle est vraie ou fausse ;
- **relecteur-visuel** compare chaque page à l'original, agrandit les endroits signalés et rend les défauts
  localisés (page et coordonnées).

Les agents ne modifient rien : leurs rapports sont des propositions, que le modèle principal vérifie avant de
corriger.

---

## Coût en jetons et modèles
Une traduction consomme beaucoup de jetons, surtout à cause des images : compter environ 150 000 à 200 000
jetons pour un livret de quelques pages, davantage pour un scan ou un long livret. La skill limite ce coût de plusieurs
façons :
- **les scripts font le travail mécanique** : préparation, inventaire, construction, contrôles, rangement ;
- **les images ne servent qu'à bon escient** : planches à faible résolution, agrandissements seulement sur ce qui
  est signalé, texte lu dans des fichiers plutôt que sur des images ;
- **la relecture est confiée à un modèle moins coûteux.** Le modèle que vous avez choisi dans Claude Code dirige
  le travail : il traduit, écrit le spec et prend les décisions, car c'est ce qui fait la qualité. Les deux
  relectures, longues et gourmandes en images, tournent sur **Sonnet** dans des agents séparés : leurs images et
  leur lecture du texte complet n'alourdissent pas la conversation principale, qui ne reçoit qu'un rapport de
  quelques lignes. À titre d'exemple, sur un livret de 2 pages en 4 colonnes, chaque relecteur a pris environ
  25 secondes.
- Les tâches courtes ne sont **pas** déléguées : démarrer un agent a un coût fixe qui dépasserait le gain.

Pour changer le modèle des relecteurs, modifier la ligne `model:` en tête des fichiers de `agents/` (par
exemple `haiku`, moins cher mais moins sûr pour juger une traduction).

---

## Corriger une traduction déjà faite
Demander la correction à Claude (« dans <Jeu>, page 2, remplace … par … »). Il lit `_outils/<Jeu>/NOTES.md`,
modifie `spec.py`, reconstruit, regarde la page, puis remplace `<nom>_FR.pdf` **après votre accord**
(`livrer.py --remplacer`). Le dossier d'outils de chaque jeu est conservé pour cela.

---

## Contenu du dépôt
- `SKILL.md` — la méthode suivie par Claude et les préférences de traduction
- `../../agents/` (à la racine du plugin) — `relecteur-texte.md` et `relecteur-visuel.md` (Sonnet), installés avec
  le plugin
- `references/`
  - `dossiers.md` : organisation des dossiers, noms de jeux, index et notes ;
  - `langues.md` : langue de départ, livrets multilingues, longueur du français selon la langue, texte vertical ;
  - `scan.md` : livrets scannés (lecture automatique, zones, rendus) ;
  - `recomposer.md` : livret recomposé à neuf, sans l'image du scan ;
  - `encre.md` : version économe en encre d'un livret à fond sombre, à imprimer (sur demande seulement) ;
  - `alleger.md` : version allégée sous 10 Mo pour Discord (sur proposition, livret d'origine conservé) ;
  - `page-web.md` : règles publiées sur une page web (page traduite puis remise en PDF ; page bilingue,
    version anglaise) ;
  - `en-ligne.md` : livret seulement consultable en ligne (Google Drive) : où chercher le PDF, captures de
    l'utilisateur ;
  - `source.md` : vérifier une règle traduite contre l'original (Tokyo Game Market pour les jeux japonais) ;
  - `glossaire.md` : vocabulaire de jeu commun à tous les jeux, avec équivalences par langue ;
  - `polices.md` : polices de remplacement déjà trouvées pour des polices de livrets ;
  - `pieges.md` : cas difficiles rencontrés et leurs solutions (texte en double, calques cachés, icônes,
    mini-cartes, soulignements, marges de paragraphe, lignes décalées ou images cachées qui ressortent à
    l'effacement…).
- `scripts/`
  - `preparer.py` : démarre un livret (voir plus haut) ;
  - `build.py` : moteur des livrets à texte ; `scan.py` : moteur des livrets scannés ; `commun.py` : fonctions
    communes ; `controle.py` : contrôles automatiques de mise en page ;
  - `spec_modele.py` / `spec_scan_modele.py` : modèles de `spec.py`, avec la description de toutes les options ;
  - `dump.py` : inventaire du texte (`blocks.txt`) ; `polices.py` : extraction, contrôle des accents,
    comparaison et largeur des polices ; `ocr.py` : lecture du texte des scans ;
  - `grille.py` / `bandes.py` : mesures de position sur les scans ;
  - `icone.py` : découpe une icône d'un scan pour la remettre dans le texte français ;
  - `sheet.py` / `side.py` : planche d'aperçu et images côte à côte original / français ;
  - `relecture.py` : relecture du texte seul ; `encre.py` : version économe en encre d'un livret à fond sombre ;
    `comprimer.py` : version allégée sous 10 Mo pour Discord ;
    `aide_memoire.py` : aide-mémoire (une page, deux au besoin) ;
  - `page_web.py` : texte d'une page web à traduire, et page française reconstruite ;
  - `livrer.py` : livraison (version anglaise comprise ; `--encre` pour la version économe en encre ; `--pdf`
    pour une traduction faite sans spec) ;
    `ranger.py` : allègement du dossier d'outils.
- `exemples/recomposer/` : `noir.py` et `textes.py`, moteur et texte d'un livret recomposé à neuf (CMYK), à copier
  et adapter (`noir.py --clair` : version économe en encre).

---

## Limites connues
- **Texte vertical** (japonais) : le français est posé à l'horizontale dans la même zone si la place le permet,
  sinon c'est signalé.
- **Japonais, chinois, coréen** : le français prend beaucoup plus de place (souvent 1,5 à 2 fois en largeur) ; la
  traduction est plus concise et la police plus réduite, ce qui est signalé.
- **Texte dessiné dans les illustrations** (logos, onomatopées) : laissé tel quel, et signalé.
- **Lecture automatique des scans** : Windows uniquement ; ailleurs, Claude lit les pages en images (plus cher).
- **Livrets très longs** : la traduction se fait page par page dans une même session, ce qui reste coûteux ;
  mieux vaut le savoir avant de commencer un livret de 40 pages.
- **Version allégée** : un livret presque entièrement fait de grandes images peut rester au-dessus de 10 Mo même
  au dernier essai ; il faut alors l'envoyer en deux fichiers.
- **Version économe en encre** : pas pour les livrets scannés, où le fond EST l'image scannée. Un fond fait de
  nombreux petits pavés, ou posé avec une matrice tournée, est signalé dans le journal plutôt que forcé.

---

## Remarques
- **Usage personnel** : ne diffusez les livrets traduits qu'avec l'accord de l'éditeur du jeu.
- Skill initiée par [notoriousFabb](https://github.com/notoriousFabb/traduction-regles-jeu), optimisée et complétée par
  [vinchy1](https://github.com/vinchy1/traduction-regles-jeu) ; cette version par vinchy1 y ajoute la traduction depuis
  toutes les langues, les livrets scannés, l'organisation en dossiers, les contrôles automatiques, la relecture du texte et les agents relecteurs.
- Ce dépôt évolue désormais de façon indépendante. Le dépôt d'origine reste noté comme source facultative
  (`git fetch notoriousfabb`) : ses nouveautés ne sont reprises qu'à la demande.
