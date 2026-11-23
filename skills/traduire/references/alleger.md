# Version allégée pour Discord (10 Mo par fichier)

Discord refuse un fichier de plus de 10 Mo, et c'est là que les livrets traduits sont publiés la plupart du
temps. Un livret riche en images dépasse vite cette limite.

**À proposer, jamais à faire d'office.** `livrer.py` signale lui-même le cas, avec la commande toute prête :

```
ATTENTION : <nom>_FR.pdf fait 14.2 Mo, au-dessus des 10 Mo de Discord — proposer une version allégée :
python -X utf8 comprimer.py "<chemin>"
```

Sous 10 Mo, rien n'est signalé et il n'y a rien à proposer.

**Poser la question, pas l'écrire dans le bilan** : AskUserQuestion « Le livret fait 23 Mo, trop pour Discord.
Faire une version allégée ? » (Oui / Non), avant le bilan final. Une phrase en fin de bilan (« je peux faire une
version allégée si… ») passe inaperçue. L'app Règles de jeu propose aussi un bouton qui lance `comprimer.py`
elle-même.

## Construire
```
python -X utf8 comprimer.py "<livret.pdf>" [--max 10] [--sortie "<fichier.pdf>"] [--remplacer]
```
Écrit `<nom>_light.pdf` à côté du livret — ou, s'il ne passe pas en un fichier aux images nettes,
`<nom>_light_partie1.pdf`, `<nom>_light_partie2.pdf`… (voir plus bas). Une ancienne version allégée (en un fichier
ou en parties) est remplacée en entier avec `--remplacer`. Les images recompressées en JPEG reçoivent l'espace de couleur de leurs
vraies composantes (une image d'un profil CMJN d'imprimeur devient RVB) : sinon Acrobat refuse le fichier et les
navigateurs peignent ces images en noir ; le script le vérifie avant d'enregistrer. **Le livret en pleine qualité n'est jamais touché ni remplacé** : la
version allégée est un fichier de plus, à n'envoyer que sur Discord. C'est le livret normal qui reste la
référence, qu'on archive et qu'on imprime.

## Ce que fait la compression
0. **Dessins répétés partagés** (à chaque essai) : un fond vectoriel copié sur chaque page, identique mais placé
   ailleurs, pèse son poids à chaque copie (Uncharted Passage : 25 copies de 350 à 400 Ko, 9,5 Mo sur 27). Le
   dessin est gardé une fois et chaque page l'appelle : rendu identique, rien n'est abîmé.

Puis essais successifs, du plus doux au plus serré, **arrêtés au premier qui passe sous la limite** pour abîmer
les images le moins possible :
1. nettoyage seul (objets inutiles retirés, polices réduites) — images intactes ;
2. images recompressées en JPEG, qualité 92, puis 85, 80 ;
3. et, pour les images très fines (scans à 300 dpi et plus), résolution ramenée à 300, 220 dpi ;
4. **couper plutôt qu'abîmer** : si aucun de ces essais ne passe, le livret est coupé en 2 parties de pages
   consécutives (puis 3, 4… jusqu'à 10), chacune compressée le moins possible, en reprenant les mêmes essais ;
5. seulement si aucun découpage ne passe ainsi : essais plus serrés (170 dpi qualité 72, puis **plancher**
   150 dpi qualité 70), d'abord en un fichier, puis en parties.

**Jamais en dessous du plancher** (150 dpi, qualité 70) : plus bas, illustrations et icônes ne se lisent plus. La
première version allégée d'Uncharted Passage était descendue jusqu'à 72 dpi, puis coupée en deux fichiers de 6 Mo
illisibles ; la bonne réponse était deux fichiers de 9,6 et 8,5 Mo aux images intactes.

**Ne pas improviser de découpage** à côté du script (compresser tout le livret au plus serré puis le couper en
deux) : c'est `comprimer.py` qui décide du nombre de parties, et chaque partie est compressée seule.

Le **texte reste du texte** : il est vectoriel, la compression ne le touche pas, il est aussi net que dans le
livret d'origine à l'écran comme à l'impression. Le script le vérifie page par page après coup et abandonne la
version allégée si le texte a bougé.

Le journal donne l'essai retenu pour chaque fichier :
`version allégée -> …_light_partie1.pdf  (pages 1 à 10, 9.6 Mo, nettoyage seul, images intactes)`. Coupé en
parties, le livret se poste en **messages séparés** (Discord : 10 Mo en tout par message sans boost).

## Limites
- Une page seule plus lourde que 10 Mo même au plancher (très rare) reste au-dessus : le script le dit ; mettre
  alors le lien du livret dans le message.
- Un livret allégé peut prendre une ou deux minutes (chaque essai réécrit tout le livret).
- Les images au trait en noir et blanc pur ne sont pas converties en JPEG (elles y perdraient beaucoup pour un
  gain nul).
- `--max 8` permet de viser une autre limite (ancien quota Discord, pièce jointe d'un courriel).
