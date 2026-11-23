# Livret scanné (pages-images sans texte)

`preparer.py` le détecte (« SCANNÉ ») et copie `scan.py`, `ocr.py`, `grille.py`, `bandes.py` et le modèle
`spec_scan_modele.py`. Il n'y a pas de texte à remplacer : `build.py` ne s'applique pas.
Sont aussi traités comme des scans : une page-image avec une **couche de texte OCR invisible** (police
« HiddenHorzOCR », Helvetica non embarquée, mode de rendu 3 : le texte se sélectionne mais l'image reste
affichée — Quino-Phex) et des **lettres en tracés vectoriels** (« texte en tracés vectoriels », `VECTEUR = True`
posé dans le spec — Koi Breeders, Tricks of the Engkantos). Si un tel livret a été préparé comme livret à
texte (ancienne version de `preparer.py`) : copier les scripts de scan et `spec_scan_modele.py` à la main et
retirer `build.py` (sinon `livrer.py` le prend pour moteur).

## Choisir le rendu (demander à l'utilisateur)
- **« recouvrir »** (ressemble à l'original) : chaque zone de texte de l'image est masquée par la couleur du fond
  mesurée autour, et le français est posé dedans, police réduite automatiquement pour tenir. Limites à
  annoncer : sur fond texturé ou dégradé le masque se voit (aplat), le texte écrit dans les illustrations reste
  en langue d'origine sauf zone dédiée, et le français est souvent très petit sur un livret dense.
  **Lettres en tracés vectoriels** (pas de texte, mais pas une image non plus : `page.get_drawings()` rend des
  centaines de petits tracés, cas de Bird Club) : `VECTEUR = True` dans le spec, les lettres sont supprimées
  au lieu d'être masquées et le fond reste intact (pas d'aplat visible).
- **« cote »** (le plus fiable) : chaque page d'origine à gauche, sa traduction complète à droite ; une page de
  plus si la traduction est longue (`PAGES[page] = "<h3>…</h3><p>…</p>"`).
- **« recomposer »** (page propre, sans l'image) : tout le livret réécrit à neuf, même découpage et mêmes
  couleurs, sans aucune image du scan — `recomposer.md`. **À recommander pour un scan papier** (plié, froissé,
  photographié) : recouvrir y laisse plis et aplats visibles. « Recouvrir » reste le bon choix pour une image
  numérique propre (livret publié en images par l'auteur).
- **Version anglaise** demandée aussi : la même spec, textes `X("français", "english")` (voir l'en-tête de
  `spec_scan_modele.py`) ; `LANGUE=en python -X utf8 scan.py sortie_en.pdf`, livrée par `livrer.py`.

## Méthode « recouvrir »
1. **Lecture automatique** : `preparer.py` lance `ocr.py` (reconnaissance de texte de Windows), qui écrit
   `zones.py` : un `Z(page, (x0, y0, x1, y1), "texte d'origine")` par paragraphe, la taille du texte et, en
   commentaire, le haut et le bas de chaque ligne. Langue de lecture : choisie seule (japonais si Windows sait
   le lire et que le livret en contient, sinon anglais, et à défaut une autre langue à alphabet latin
   installée, par ex. `fr-FR` : elle lit bien l'anglais, à quelques confusions l/I près) ; autre langue : `--langue-ocr de-DE`, `fr-FR`… ;
   `python -X utf8 ocr.py --langues` liste celles installées. Japonais, chinois… : module OCR de Windows à
   installer par l'utilisateur (terminal administrateur :
   `dism /Online /Add-Capability /CapabilityName:Language.OCR~~~ja-JP~0.0.1.0`) ; sinon, méthode manuelle
   ci-dessous. L'OCR japonais confond souvent les petits caractères (ボ/ポ, ソ/リ, げ/け, kanji rares) :
   corriger d'après le sens et vérifier les mots douteux sur la planche.
2. **Écrire `spec.py`** à partir de `zones.py` : traduire chaque texte, **élargir `x1` jusqu'au bord de la
   colonne** (l'OCR donne la largeur du texte anglais, le français est plus long), couper une zone qui mélange
   titre et paragraphe (repères y en commentaire), régler `size` (≈ celle indiquée), `bold`, `align`, `color`.
   Garder l'original dans la zone pour la relecture : `Z(page, rect, "français", en="texte de zones.py")`.
   Vérifier sur la planche que l'OCR n'a rien oublié (petits textes, texte sur fond coloré, titres décoratifs)
   et ne pas traduire le texte des illustrations sauf demande.
3. **Méthode manuelle** (langue non lisible par l'OCR) : lire sur des agrandissements
   (`grille.py livret.pdf <page> x0,y0,x1,y1 300`) ; ne pas déduire les hauteurs à l'œil (erreurs de plusieurs
   points) : mesurer les lignes avec `bandes.py livret.pdf <page> x0,y0,x1,y1` (fond clair, sombre ou coloré) ;
   pour couper une ligne en deux zones (étiquette + nom), mesurer les blancs horizontaux. Si l'image est trop
   floue pour lire sans deviner, le dire plutôt que d'inventer.
4. **Construire** : `python -X utf8 scan.py sortie.pdf`. Réglages utiles :
   - livret dense : `pad=-0.5` (le texte peut dépasser un peu du masque) et `lead=1.0` ;
   - zone d'une seule ligne : `lead=1.0` et `pad=-0.6` posés d'office ;
   - symboles ①❶◆★ : `S("①")` (Segoe UI Symbol, copiée dans `ff/` par `preparer.py`) ; icône dans le texte :
     `icone.py livret.pdf <page> x0,y0,x1,y1 nom` puis `I("nom")` ; titre sur aplat : `BANNER(...)` (rectangle
     plus large que l'original pour un titre français plus long), `PILL(...)` (pastille arrondie) ;
   - agrandir chaque masque d'environ 1,5 pt vers le bas (jambages du texte d'origine) ; commencer les listes
     numérotées assez à gauche pour couvrir les numéros d'origine ;
   - **puce en tête de ligne** (●, ■, ◆) : mesurer sur l'image le bord gauche de la puce d'origine et y faire
     commencer la zone. CGOB : zone à x = 34 pour un ● qui commençait à 32,1, un bout du ● japonais restait
     visible à gauche du ● français ;
   - **étiquette dans un petit rond clair à contour** (表 / 裏 posés sur une illustration de cartes) : ni aplat
     `"auto"` (l'anneau mesuré autour attrape l'illustration et le contour : carré terne) ni zone carrée autour du
     rond (elle mord le contour). Mesurer le centre et le rayon intérieur du rond, puis `M(...)` carré **inscrit**
     (demi-côté ≈ 0,7 × rayon) de la couleur mesurée à l'intérieur, et `Z(..., bg=None)` dans une bande d'une
     ligne centrée sur le rond : le texte se cale toujours **en haut** de sa zone, une zone haute le décentre
     (CGOB, `RONDS` dans son spec) ;
   - fond sombre ou coloré mal deviné (bulle, encadré) : `bg="#rrggbb"` mesuré sur l'original ; `M(...)` pour
     effacer sans remplacer ;
   - **encadrés semi-transparents sur fond texturé** (ciel étoilé, photo) : l'anneau mesuré autour de la zone
     attrape le fond derrière l'encadré, aplats trop sombres : `BG = "dominant"` en tête de spec (couleur la plus
     fréquente DANS la zone), et zones gardées strictement à l'intérieur des encadrés (Hit and Win) ;
   - titre souligné d'un filet (vert, couleur) juste dessous : arrêter le bas du masque au-dessus du filet, mesuré
     sur l'image (pixels de la couleur du filet), sinon il disparaît ;
   - nom japonais dans une police de remplacement sans kanji : le romaniser (ou garder la zone d'origine).
   Journal : « police réduite à … (N pt) », « DÉBORDE » (raccourcir ou agrandir la zone) ; en dessous de
   ~4,5 pt imprimé, prévenir l'utilisateur. **« À VÉRIFIER »** : masques d'où une ligne d'origine dépasse
   (fausses alertes possibles sur les bulles et les dessins).
5. **Relire** : comme pour un livret à texte, avec les deux agents relecteurs (SKILL.md, étape 5) ; dire au
   relecteur visuel que c'est un scan (masques visibles, texte d'origine qui dépasse) et lui donner les endroits
   signalés. Le texte oublié ne se détecte pas seul : comparer avec `zones.py`.
Coût : plus élevé qu'un livret à texte ; le dire avant de commencer un long livret.
