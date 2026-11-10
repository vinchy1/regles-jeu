# Version allégée pour Discord (10 Mo)

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
Écrit `<nom>_light.pdf` à côté du livret. Les images recompressées en JPEG reçoivent l'espace de couleur de leurs
vraies composantes (une image d'un profil CMJN d'imprimeur devient RVB) : sinon Acrobat refuse le fichier et les
navigateurs peignent ces images en noir ; le script le vérifie avant d'enregistrer. **Le livret en pleine qualité n'est jamais touché ni remplacé** : la
version allégée est un fichier de plus, à n'envoyer que sur Discord. C'est le livret normal qui reste la
référence, qu'on archive et qu'on imprime.

## Ce que fait la compression
Essais successifs, du plus doux au plus serré, **arrêtés au premier qui passe sous la limite** pour abîmer les
images le moins possible :
1. nettoyage seul (objets inutiles retirés, polices réduites) — images intactes ;
2. images recompressées en JPEG, qualité 92, puis 85, 80, 72… ;
3. et, pour les images très fines (scans à 300 dpi et plus), résolution ramenée à 300, 220, 170 dpi…

Le **texte reste du texte** : il est vectoriel, la compression ne le touche pas, il est aussi net que dans le
livret d'origine à l'écran comme à l'impression. Le script le vérifie page par page après coup et abandonne la
version allégée si le texte a bougé.

Le journal donne l'essai retenu : `20.0 Mo -> 5.6 Mo, images en JPEG qualité 92, au plus 300 dpi`.

## Limites
- Un livret presque entièrement fait de grandes images peut rester au-dessus de 10 Mo même au dernier essai :
  le script le dit. Le plus simple est alors de l'envoyer en deux fichiers (deux moitiés de pages).
- Les images au trait en noir et blanc pur ne sont pas converties en JPEG (elles y perdraient beaucoup pour un
  gain nul).
- `--max 8` permet de viser une autre limite (ancien quota Discord, pièce jointe d'un courriel).
