# fiche-discord — skill du plugin regles-jeu

Prépare la **fiche de présentation d'un jeu** pour un salon forum Discord — par défaut *discussion-par-titre* du
serveur **Golden Meeple**, au format de son post épinglé « Bibliothèque ». La fiche est rangée dans la ludothèque, à
côté des livrets du jeu, prête à coller dans « Nouveau post ».

Il suffit de demander à Claude Code « fais la fiche Discord de The Good Farmer », ou d'appuyer sur **Préparer la
fiche Discord** dans la fiche du jeu de l'app Règles de jeu.

---

## Sommaire
- [Ce qu'elle fait](#ce-quelle-fait)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Le format du post](#le-format-du-post)
- [D'où viennent les infos](#doù-viennent-les-infos)
- [Le dossier fiche/](#le-dossier-fiche)
- [Publier](#publier)
- [Contenu de la skill](#contenu-de-la-skill)
- [Limites connues](#limites-connues)

---

## Ce qu'elle fait
- Rassemble les infos du jeu sur BoardGameGeek (par son API), la boutique Golden Meeple, le Tokyo Game Market et la
  chaîne YouTube Golden Meeple (vidéos de règles LEX PLI), **sans rien inventer** : une info introuvable est laissée
  vide (ou sa ligne omise) et signalée.
- Récupère la couverture du jeu.
- Joint les livrets **déjà présents dans le dossier du jeu** : anglais (ou VO s'il n'y a pas d'anglais), puis
  français, tous dans le même message. Un livret de plus de 10 Mo est remplacé par sa version allégée (`_light.pdf`),
  faite au besoin sans toucher au livret d'origine.
- Pas de livret dans le dossier : la skill `rechercher` le cherche et l'y enregistre. Pas de français : c'est
  signalé, rien n'est traduit sans votre demande (une traduction coûte cher en quota).
- Range la fiche avec les outils du jeu, dans `<Ludothèque>/_outils/<Jeu>/fiche/`, sans recopier les livrets.
- **N'ouvre jamais Discord** et ne publie rien avec votre compte : c'est vous qui postez (ou, plus tard, un webhook du
  serveur). Vérifier que le jeu n'a pas déjà son post est donc à votre charge.

---

## Installation
1. **Installer le plugin** `regles-jeu`, qui contient cette skill : voir le [README du plugin](../../README.md#installation).
2. **Python 3 et `lxml`** (lecture de la boutique) : `pip install lxml`.
3. **Clé de l'API BoardGameGeek** : BGG bloque les navigateurs pilotés (page « Vérification de sécurité » de
   Cloudflare) ; la skill passe donc par son API, qui demande une clé personnelle gratuite (compte BGG → *API
   applications*). Elle est lue, sans jamais être affichée :
   - dans la configuration de l'app Règles de jeu (« Clé et infos BoardGameGeek… » : rien d'autre à faire) ;
   - sinon dans la variable d'environnement `BGG_TOKEN`.
   Sans clé, la ligne `BGG :` reste vide et c'est signalé.
4. **Un navigateur piloté** (extension Claude in Chrome, ou l'outil de navigation de Claude Code) : seulement pour
   chercher la vidéo LEX PLI sur YouTube, sans connexion.
5. **Ancienne skill** `fiche-jeu-discord` encore dans `~/.claude/skills/` : la supprimer, celle-ci la remplace.

---

## Utilisation
| Vous dites | Ce qui se passe |
|---|---|
| « Fais la fiche Discord de The Good Farmer » | fiche complète dans `_outils/The Good Farmer/fiche/`, bilan de ce qui manque |
| `/regles-jeu:fiche-discord Trick of Fixer, 6 Forces` | une fiche par jeu, un seul bilan |
| « Refais la fiche de 6 Forces » | fiche remplacée (la trace d'un envoi par webhook est gardée) |
| Bouton **Préparer la fiche Discord** (app Règles de jeu) | même chose, en tâche suivie dans « Tâches » ; la fiche s'affiche ensuite dans l'app |

Le bilan donne, par jeu, le titre, ce qui manque, les réserves et le chemin du dossier `_outils/<Jeu>/fiche/`, puis rappelle comment
poster.

---

## Le format du post
Celui des fiches déjà postées dans le salon :

```
<Auteur> / <Illustrateur> / <Éditeur> / <a à b> joueurs / <année>

BGG : <lien>

GM : <lien de la boutique Golden Meeple>

LEX PLI : <lien youtu.be>            (seulement si la vidéo existe)

Game Market : <lien>                 (seulement pour un jeu japonais)

[<Type>]                             (mécanique principale en anglais : [Trick-Taking], [Ladder Climbing]…)

Cartes : <nombre> cartes (<l> x <h> mm)   (seulement si connu)
```

- **Titre du post** : le titre BGG exact (règle du « Guide des posts » du salon) ; sans BGG, celui de la boutique.
- **Noms** : romanisation puis original entre parenthèses quand une source le donne — `Kentaro Yazawa (矢沢 賢太郎)`.
  L'écriture japonaise n'est jamais devinée.
- **Pièces jointes** : couverture, livret anglais (ou VO), livret français.

---

## D'où viennent les infos
| Info | Source |
|---|---|
| Titre exact, année, joueurs, auteurs, illustrateurs, éditeurs, mécaniques, image | BoardGameGeek, par l'API (`bgg.py` de la skill `rechercher`) ; identifiant déjà connu par `_outils/bgg.json` de l'app quand il y est |
| Lien boutique, noms, image de secours | boutique goldenmeeple.be (`scripts/boutique_gm.py`) |
| Noms japonais, nombre et format des cartes | fiche du Tokyo Game Market (`fiche_gm.py` de la skill `rechercher`) |
| Vidéo de règles | chaîne YouTube Golden Meeple, vidéos « <Jeu> \| LA REGLE » |
| Livrets | dossier du jeu dans la ludothèque |

Sources en désaccord : BGG l'emporte, l'écart est noté dans `notes.txt`.

---

## Le dossier fiche/
```
<Ludothèque>/
├── <Jeu>/                      les livrets, à leur place habituelle (<livret>_EN.pdf, <livret>_FR.pdf…)
└── _outils/<Jeu>/              outils du jeu (traduction : spec.py, NOTES.md… s'il a été traduit)
    └── fiche/
        ├── titre.txt        titre du post
        ├── message.txt      message à coller tel quel
        ├── notes.txt        sources, manques, écarts, doutes (jamais collé sur Discord)
        ├── couverture.jpg   image jointe au post
        ├── fiche.json       livrets à joindre (noms de fichiers du dossier du jeu), salon, date
        └── envoye.txt       lien du post, après un envoi par webhook
```

`fiche.json` :
```json
{"livrets": ["The_Good_Farmer_EN.pdf", "The_Good_Farmer_FR.pdf"],
 "salon": "https://discord.com/channels/…", "maj": "2026-11-11"}
```
Les livrets y sont nommés, pas copiés : la fiche reste légère et suit les livrets si une traduction est refaite. Leur
version `_light.pdf` est prise d'elle-même au-delà de 10 Mo. Rangée dans `_outils/`, la fiche voyage d'un PC à
l'autre avec la synchronisation GitHub de l'app (comme les outils de traduction, jamais les PDF) ; une fiche seule
ne fait pas passer le jeu pour traduit. Une fiche d'une version précédente (`<Jeu>/fiche/`) est déplacée ici par
l'app ou la skill.

---

## Publier
**À la main** (par défaut) :
1. Dans le salon, chercher le titre (« Recherche ou création d'un post… ») : le jeu a peut-être déjà son post.
2. « Nouveau post » → coller `titre.txt` dans **Titre**, `message.txt` dans le message, joindre la couverture et
   les livrets, **tout dans ce même message**.
3. Une fois le post créé, l'épingler (il contient les règles : Guide des posts).

Dans l'app Règles de jeu, la section **Fiche Discord** de la fiche du jeu fait tout cela en quelques clics : **Titre**
et **Message** copiés, **Pièces jointes** mises dans le presse-papiers (un Ctrl+V dans Discord les joint),
**Ouvrir le salon**.

**Par webhook** (quand un admin du serveur en aura créé un) : voir [references/webhook.md](references/webhook.md).
L'adresse se range dans `~/.claude/regles-jeu/discord-webhook.txt` (hors de la ludothèque, qui peut être
synchronisée sur GitHub) ; toujours un essai d'abord, et rien n'est envoyé sans votre accord explicite.

---

## Contenu de la skill
| Fichier | Rôle |
|---|---|
| `SKILL.md` | la méthode suivie par Claude |
| `references/webhook.md` | mise en place et utilisation d'un webhook (lu seulement dans ce cas) |
| `scripts/boutique_gm.py` | boutique Golden Meeple : `chercher "<nom>"`, `fiche <lien>` |
| `scripts/webhook.py` | essai (contrôle du titre, du message, des pièces jointes et de l'adresse), puis `--envoyer` |

Elle s'appuie aussi sur `fiche_gm.py` et `bgg.py` (skill `rechercher`) et `comprimer.py` (skill `traduire`).

---

## Limites connues
- **Doublons non vérifiés** : Claude n'ouvre pas Discord (le navigateur piloté n'y est pas connecté, et un programme
  qui se sert d'un compte personnel est interdit par Discord). À vérifier par vous avant de poster.
- **Webhook en attente** : il faut qu'un admin du serveur le crée. Il ne sait ni épingler le post ni poser les
  étiquettes du forum ; sans boost du serveur, Discord limite un envoi à 10 Mo en tout (livrets compris).
- **Jeux récents du Game Market** : souvent absents de BGG ; la ligne `BGG :` reste alors vide.
- **Salon par défaut** : celui de Golden Meeple. Pour un autre salon, donner son modèle à Claude.
