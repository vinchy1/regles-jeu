# Pièges rencontrés et solutions

La plupart sont déjà gérés par `scripts/build.py` ; ce qui reste à faire dans le spec est indiqué.

- **Texte imprimé deux fois** (faux gras / surimpression) : lignes identiques au même endroit → dédoublonnées
  automatiquement.
- **Calques cachés** (version dans une autre langue, texte tourné d0,-1) : ne pas les mettre dans le spec.
  Vérifier sur le rendu ce qui est réellement visible (couverture : « Regras » invisible, « Rules » visible).
- **Icônes dans le texte** : petites images (<22×16) ou grappes de tracés vectoriels (<14×14) sur la bande d'une
  ligne traduite → retirées puis replacées sur `{}`. Le nombre de `{}` doit égaler le nombre d'icônes (le build
  signale tout écart). Lettres cerclées A/B/C (cercle vectoriel + lettre texte) : voir la version de
  `_outils/Dr_Science/build.py`.
- **Puces dans le texte** (« •\t », « 1.\t » dans la même span) : `bullet="•"` ou `bullet="1."`, le retrait
  est conservé. Puces des livrets japonais (●, 〇, ・, ■, ◆, ▶, ①…⑳, ❶…❿) aussi : `L(src, html, bullet="●")`,
  le français commence après la puce et son blanc (un 「 collé à la puce est pris en compte) ; inutile de
  donner `x0` à la main.
- **Étiquettes penchées** (« Connected! » en biais sur une illustration, ligne de direction non horizontale) :
  `INCLINEES = [(page, "texte exact de la ligne", "français"), …]` dans le spec. Le moteur efface la ligne
  et pose le français au même angle, même couleur, même police (`CODE`), centré sur l'original, réduit s'il
  dépasse de plus de 20 %. Ne pas les mettre dans un flux ni dans `IGNORE`. Journal : « étiquette inclinée »
  (ou « introuvable » si le texte ne correspond pas exactement à la ligne de `blocks.txt`).
- **Lettres doublées d'un contour** (titres décoratifs : le texte est imprimé, puis chaque lettre redessinée
  en tracé avec un contour blanc ou coloré ; après traduction il reste des lettres fantômes) :
  `CONTOURS = {page: [(x0, y0, x1, y1), …]}` = rectangles des titres concernés. Le moteur garde ces tracés
  mais ne les peint plus. Ne pas les effacer par une redaction (`REMOVE_IF_TOUCHED`) : elle emporte aussi
  les dégradés et motifs voisins (vagues de Hyakuju Parade). Le contour d'origine n'est pas recréé autour du
  français (compromis à signaler). Journal : « N contour(s) de lettres effacé(s) » ; 0 = lettres dessinées
  autrement, à regarder de près.
- **Numéros dans des pastilles** dessinées à gauche (étapes 1-5) : un flux par étape, ancré à sa position
  d'origine (maxy = début de l'étape suivante), sinon les pastilles ne suivent plus le texte.
- **Texte qui contourne une image** (lignes à côté d'une carte, puis pleine largeur) : couper le français en
  deux paragraphes (`b3:0-1` à côté, `b3:2` dessous) en choisissant la coupure pour que la 1re partie remplisse
  ses lignes ; le premier paragraphe pleine largeur après l'image prend `fix=True` pour ne pas remonter dessus.
- **Paragraphe en double dans l'original** : fusionner les sources dans un seul paragraphe (`lead=` pour forcer
  l'interligne) et le signaler.
- **Mini-cartes illustrées** (texte de 1 à 4 pt) : table `CARDS` + `CARD_PAGES` ; ne traduire que les cartes
  dont le texte est visible (cartes empilées : seulement celle de devant), sinon le français s'affiche
  par-dessus. Les styles qui distinguent numéro / ambiance / effet se
  règlent dans `CARD_STYLE` (voir `spec_modele.py`).
- **Mots soulignés** (traits dessinés sous la ligne, pas du texte) : le build retire ceux qui sont sous une
  ligne remplacée (journal : « soulignement(s) d'origine retiré(s) ») ; souligner le français avec
  `<u>…</u>` et `u {text-decoration:underline;}` dans le CSS du spec. Un trait qui dépasse le texte de la ligne
  (ligne d'un tableau, bord d'un cadre) n'est pas un soulignement et reste en place ; si un tableau perd quand
  même des lignes, ce message dans le journal en est la cause.
- **Polices du livret complètes** : si `polices.py glyphes` ne signale aucun manque (police embarquée en
  entier), copier simplement l'originale dans `ff/`.
- **Plusieurs colonnes par page** : détectées seules (blancs verticaux à la hauteur du paragraphe, texte de la
  colonne voisine jusqu'à 150 pt plus haut ou plus bas) ; si un paragraphe déborde quand même (signalé « À
  VÉRIFIER »), lui donner `x1=` ou `COLUMNS`.
- **Étapes numérotées sur pastilles** : le moteur ancre seul un paragraphe dont le premier caractère est posé
  sur une petite forme pleine (`fix=True` implicite, `fix=False` pour l'empêcher) et réduit le texte qui
  précéderait trop bas. Le chiffre, s'il est du texte (blanc), reste à réécrire au début du français avec un
  retrait suspendu (`<div style="margin-left:8pt;text-indent:-8pt">`).
- **Bouts d'illustration pris pour des icônes** (journal : « {} pour N icône(s) » sur un paragraphe sans
  icône) : `noicons=True` sur le paragraphe.
- **Insécables** : « Bleu 19 », « joueur A », « page 3 », « étape 2 » sont protégés par le moteur (mot à
  majuscule + nombre, et joueur / page / étape / manche / carte… + nombre ou lettre). Autre cas : `&#160;`.
- **Glyphe spécial pour un chiffre** (« Ä » ou � qui s'affiche « 0 ») : écrire simplement « 0 ».
- **Coupures indésirables** : le build met une insécable avant `{}` et après un nombre suivi d'un mot ; pour
  « p. 8 » ou « 1 - 2 = -1 » écrire `&#160;` dans le spec.
- **Titres longs** (nom d'origine + français) : `T(...)` les garde sur une ligne ; s'ils touchent une image,
  raccourcir le français ou passer `size=`.
- **Anglais qui réapparaît ailleurs, images cachées qui ressortent** (livrets InDesign japonais, Fagioli) : les
  redactions de MuPDF décalent ou effacent les lignes voisines quand le texte passe à la ligne par `T*`, `'`
  ou `"`, et suppriment les masques vides `0 0 m W n` qui cachent des images en double (jetons de travers
  par-dessus les vrais). Géré par `build.py` (`protect_content`, avant les redactions) : réécriture en
  `0 -TL Td` et en `0 0 0 0 re W n`, annulée si le texte de la page bouge (journal : « flux protégé… » ou
  « réécriture du flux annulée »). Si l'anglais revient malgré tout : vérifier `page.search_for()` avant et
  après une redaction isolée sur une seule ligne.
- **Retraits en espaces pleine chasse** (livrets japonais : « 　　　Texte » à côté d'une mini-carte dessinée,
  Bell Peppers) : la ligne commence sous la carte, et l'effacer sur toute sa largeur emportait les chiffres
  et lettres de la carte. `build.py` n'efface que les caractères imprimés de la ligne (`ink_rect` : sans les
  blancs de tête et de fin, demi-largeur pour les parenthèses pleine chasse （）「」). Le texte français, lui,
  se place avec `x0` = début de ligne + n × la taille de police (une espace pleine chasse = 1 em).
- **Marges de paragraphe ignorées** (livret composé avec `pymupdf.Story`) : MuPDF donne à `<p>` une marge
  par défaut de 1em en haut et en bas, que `* {margin:0}` ne remet pas à zéro. Une règle qui ne fixe qu'un
  côté (`p {margin-bottom:6pt}`) laisse l'autre à 1em, qui l'emporte (marges fusionnées) : l'écart reste
  d'une ligne entière, sans message. Toujours donner les quatre côtés dans la règle du paragraphe ou de sa
  classe : `p {margin: 0 0 6pt 0;}`, `.memo {margin: 0 0 3pt 0;}`. Symptôme : listes ou paragraphes
  anormalement espacés, page qui déborde alors qu'elle devrait tenir. `margin-left` seul fonctionne.
- **Titres, bulles et légendes en caractères-images** (PDF « Microsoft Print to PDF » d'un fichier Illustrator :
  chaque kanji d'un titre est une petite image, les renvois « p8 » ou « 〜 » de petits dessins ; rien dans
  `blocks.txt`) : couche « scan » dans `AVANT_TEXTE` du spec — liste de rectangles, aplat de la couleur
  mesurée autour (médiane d'un anneau de 1,5 pt sur la page déjà nettoyée) ou donnée, puis `insert_htmlbox`
  du français (poser soi-même les insécables ; `html=None` = simple masque ; police : `pymupdf.Archive("ff")`
  et le `CSS` du spec). Cellules de tableau dont la redaction mangerait les chiffres voisins : `IGNORE` +
  recouvrement dans la même couche. Noter dans `NOTES.md` du jeu que cette couche existe.
- **Police sans gras** (Marcellus…) : MuPDF ne fabrique pas de faux gras, `<b>` sort en maigre. Déclarer une
  police grasse voisine dans la même famille (`@font-face{font-family:Mc;font-weight:bold;src:url(...)}`).
- **Espace insécable trop large** : Arial Narrow Bold de Windows (ARIALNB.TTF) dessine U+00A0 deux fois plus
  large que l'espace (trous dans « « cartes » », « Obligation de suivre : »). Corriger la copie de `ff/` avec
  fontTools : U+00A0 → glyphe de l'espace dans toutes les tables `cmap`. Contrôle : `hmtx` de U+00A0 = celui
  de U+0020.
- **Modifier spec/build par script** : écrire le script Python dans le scratchpad avec l'outil Write ; les `\1`,
  `\'` et apostrophes dans un heredoc bash se corrompent facilement.
- **Gras et italique invisibles** (une seule police variable embarquée, Noto Sans KR « Thin » : `blocks.txt` et
  `get_texttrace` ne montrent aucune différence) : les repérer sur un agrandissement et les remettre à la main
  (`<b>`, `<i>`) ; il faut alors des fichiers gras / italique dans `ff/` (polices.md).
- **Plusieurs couleurs dans un paragraphe** (une ligne rouge puis du noir) : le moteur prend la couleur la plus
  présente pour tout le paragraphe ; marquer l'autre partie `<span style="color:#000000">…</span>` (taille
  différente : `font-size:11pt` dans le même style).
- **Titres d'étapes soulignés** (① ② ③) : `u {text-decoration:underline;}` dans le CSS et `<u>…</u>`, sinon le
  soulignement d'origine est retiré sans être remplacé (journal : « soulignement(s) d'origine retiré(s) »).
- **Paragraphe court qui garde la largeur d'un caractère** (titre d'un seul kanji, « 例 » → « Exemple » minuscule) :
  `x1=` sur le paragraphe.
- **Texte japonais gardé** (titre, noms des crédits) dans une police de remplacement réduite au latin : il
  disparaît (carrés) ; le laisser dans `IGNORE` ou le romaniser.
- **Icône rattachée à la mauvaise ligne** (lignes hautes qui se chevauchent) : le moteur la rattache à la ligne
  dont le milieu est le plus proche ; si une icône sort encore décalée d'une ligne, vérifier `blocks.txt`.

## Drapeau de la langue d'origine
Beaucoup de livrets affichent la langue par un drapeau (Royaume-Uni, États-Unis, moitié des deux, Japon…), souvent
dans un rond près du titre ou du nombre de joueurs. Dans la version française, il devient le drapeau français :
`DRAPEAUX = [(page, (x0, y0, x1, y1), "rond")]` (ou `"rect"` pour un drapeau rectangulaire).
- Relever le rectangle : dessin vectoriel → `page.get_drawings()` sur la zone ; s'il y a un **liseré** (trait
  fermé autour du drapeau : `color` et `width` renseignés), prendre **son** rectangle : il est retrouvé et
  redessiné par-dessus le drapeau français (journal : « liseré redessiné »). Sinon le rectangle du drapeau ; image
  → `page.get_image_info()`. Un zoom à 200-300 dpi sur la zone confirme le résultat.
- Un bout d'ancien drapeau qui dépasse (liseré peint en aplat, pas en trait) : agrandir le rectangle d'un point.
- Un drapeau qui fait partie du jeu (pays, faction, carte) n'est pas un drapeau de langue : ne pas le toucher.
