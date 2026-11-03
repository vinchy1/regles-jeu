# Jeu japonais introuvable par son nom en lettres latines

Cas fréquent pour un jeu du Game Market en cours ou tout juste passé : la fiche n'a que le titre japonais
(« Cosmo Chauffeur » → コスモ・ショーファー) et les moteurs de recherche ne connaissent pas encore le jeu.
Avant de conclure « aucun résultat » :

1. **Index du Game Market** : s'il existe, regarder d'abord
   `<Ludothèque>/_outils/game-market-<année>-<printemps|automne>.md` (`grep -i "<nom>"`).
2. **Vidéos et listes de nouveautés** : chercher le nom **entre guillemets sur YouTube** dans Chrome
   (`https://www.youtube.com/results?search_query=%22<nom>%22`). Les vidéos « Tokyo Game Market preview /
   anticipated » (ThinkerThemer, Crash Octopus…) ont un chapitre par jeu. Aussi : listes BGG « Tokyo Game
   Market preview » (geeklists), blogs de boutiques (Red Goose Games…).
   **Lire les résultats en texte, sans capture d'écran** (JavaScript dans la page : texte des blocs
   `ytd-video-renderer`, chapitres compris) : le titre du chapitre contient souvent le titre japonais
   (« Kubaru Te Miru Me (配る手見る目) »), ce qui évite d'ouvrir la vidéo. Il compte comme « lu sur une source ».
   **Chapitres = index du Game Market** : la description d'une vidéo « top 20 / anticipated » (lue une fois,
   en texte) donne les titres de tous ses jeux. Les garder dans le fichier d'index ci-dessus (tableau : titre
   latin, titre japonais, chapitre, fiche, règles récupérées) ; quand un jeu de l'index est trouvé, compléter
   sa ligne.
3. **Transcription de la vidéo** (texte, bien moins cher qu'une capture) : un jeu cité en passant n'a pas
   de chapitre (« Escape to Cosmos » : second jeu de l'auteur de Cosmo Chauffeur, dans le même chapitre).
   Ouvrir la vidéo, puis (JavaScript) mettre en pause, déplier la description (`#expand`), cliquer le bouton
   dont le texte contient « transcription » / « transcript », attendre ~3 s, et chercher le nom (regex,
   orthographes proches) dans le texte des blocs `ytd-transcript-segment-renderer,
   transcript-segment-view-model`, en renvoyant la ligne d'avant et d'après. Ce qui y est dit (auteur,
   cercle, type de jeu) donne la piste, pas le titre japonais.
4. **Même auteur ou même cercle** : une piste « du même auteur / cercle que X » (transcription, BGG, X) →
   `fiche_gm.py cercle <numéro du cercle de X>` liste tous ses jeux, titres japonais compris ; le nouveau jeu
   est le plus souvent en tête. Nom romanisé donné par l'utilisateur avec le cercle (« Kajitsu Tobu de
   Mashikamaru ») : lister le cercle et retrouver le titre dont la lecture correspond (果実飛ぶ).
   **Habitudes du cercle** : regarder où ses jeux précédents publient leurs règles (blog du cercle, billets
   « 【PRODUCT】 » avec lien Drive, page note.com, message épinglé du X avec les pages en images) —
   `fiche_gm.py page "<lien>"` sur ces pages. Rien encore pour le nouveau jeu : le dire (les règles arrivent
   souvent quelques jours après le Game Market) et proposer de relancer plus tard.
5. **Lire le titre sur la boîte** (seulement si rien de ce qui précède ne le donne) : ouvrir la vidéo au chapitre,
   puis (JavaScript) `v=document.querySelector('video'); v.muted=true; v.currentTime=<secondes>; v.pause()`,
   **une** capture, zoom sur la boîte. Titre, auteur et illustrateur (souvent imprimés en bas) comptent comme
   « lus sur une source ».
6. **Game Market avec ce titre** : chercher aussi un **mot seul et distinctif** du titre, sans `・` ni espaces
   (`ショーファー` plutôt que `コスモ・ショーファー`). Un mot trop courant (`パレード`, `コスモ`) donne trop de
   résultats.
7. Toujours rien : dire où et avec quels noms on a cherché, et proposer d'écrire à l'auteur
   (`ecrire-auteur.md`) ou demander une piste (titre de la boîte,
   éditeur, auteur, lien, vidéo où le jeu apparaît).
