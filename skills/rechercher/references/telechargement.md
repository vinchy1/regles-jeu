# Téléchargements difficiles

## BoardGameGeek
- Le jeu (identifiant, noms, éditeur) : `bgg.py` (API officielle, clé BGG de l'app ou `BGG_TOKEN`).
- Les pages du site : lecture simple refusée (403), et un navigateur piloté (outil de navigation de Claude Code)
  bute sur la vérification anti-robots de Cloudflare, même si l'utilisateur coche la case : ne pas insister ni
  chercher à la contourner. Seul le Chrome de l'utilisateur (extension Claude in Chrome) passe ; sans lui, donner à
  l'utilisateur le lien de l'onglet « Files » à ouvrir lui-même, et poursuivre avec les autres sources.
- Onglet « Files » : `/boardgame/NNN/<nom>/files`. Jeu du dernier Game Market souvent absent : une recherche
  vide suffit. Distinguer règles officielles et traductions / aides de fan (déposant, date ; plusieurs langues
  déposées ensemble le même jour = probablement l'équipe).
- Lien du fichier : sur la page du fichier, l'adresse `/file/download_redirect/…` (lue en JavaScript, sans la
  partie `?…`), à donner à `telecharger.py` : passe souvent sans connexion.
- Le compte X d'une équipe étrangère (coréenne…) mène souvent à BGG, avec des livrets en plusieurs langues.

## « REFUSÉ » ou « PAS UN PDF »
Connexion demandée : télécharger avec Chrome, sinon demander à l'utilisateur de le faire et de dire où il l'a mis.
Google Drive toujours bloqué : suivre `references/en-ligne.md` de la skill traduire (avec son accord).
Le fichier n'est jamais modifié.

## Fichier sur le Drive de l'utilisateur (son propre scan, lien privé)
Chrome sur `https://drive.usercontent.google.com/download?id=<id>&export=download`. Le fichier arrive dans
Téléchargements, parfois encore sous un nom provisoire (`<uuid>.tmp`, `.crdownload`) de la bonne taille : le
copier dans le dossier de travail et dire à l'utilisateur qu'il peut supprimer ce fichier provisoire.

## Règles en images
Donner tous les liens dans l'ordre de lecture : `telecharger.py "<image 1>" "<image 2>" … "<travail>"` → un seul
PDF, une image par page, sans modification ; « ALERTE : petite image » = le dire à l'utilisateur (vérifier sur un
agrandissement que le texte reste lisible). Ordre incertain (règles / histoire) : garder celui de la source et le
noter. Images ◆ d'une fiche (format d'une page, nom quelconque) : les regarder en petit pour confirmer.
