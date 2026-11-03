# Écrire à l'auteur quand aucun livret n'est en ligne

Choix « Écrire à l'auteur » de l'étape 3. Claude **rédige** le message ; c'est l'utilisateur qui l'envoie
(jamais d'envoi par Claude : message, formulaire, commentaire, X).

## 1. Trouver où écrire
Dans les pages déjà lues, puis seulement si besoin : fiche Game Market, site ou blog de l'auteur / du cercle
(pages « contact », « about », profil), boutique BOOTH, fiche BGG (éditeur, auteur), bio du X.
Par ordre de préférence : adresse e-mail publiée > formulaire de contact > message privé X / Instagram >
commentaire de blog. **Ne jamais deviner une adresse** : seulement une adresse lue sur une source.
Aucun contact trouvé : le dire, et donner le message seul.

## 2. Rédiger (anglais, court, poli)
Toujours en anglais (lu partout, même au Japon), même pour un auteur japonais ou français. 120 à 180 mots,
sans flatterie excessive ; utiliser ce que les sources disent du jeu (titre lu, cercle, annonce d'une règle
à venir). Modèle :

```
Subject: Rulebook PDF for <Jeu>

Hello <nom de l'auteur ou du cercle>,

I'm a board game player from France and I'm very interested in <Jeu>. I couldn't find the rulebook online
<(contexte : « your Game Market page mentions an English rulebook, but I couldn't find the PDF »)>.

Would you be willing to share the rulebook as a PDF, in English or French if available, otherwise in
<langue d'origine>? It would be for personal use only: to understand the game and, if you agree, to make a
French translation for my own play group. I would not distribute it without your permission.

If the rulebook will be published later, could you let me know where?

Thank you very much for your work, and congratulations on the game.

Best regards,
<signature laissée à l'utilisateur>
```

Pas de nom, d'adresse ni d'e-mail de l'utilisateur dans le message (il signe lui-même).

## 3. Enregistrer et dire
- Message dans `<Ludothèque>/_outils/<Jeu>/message_auteur.txt` (objet et texte) ; dans `NOTES.md`, rubrique
  « Sources », une ligne `- Contact de l'auteur : <moyen> — <lien ou adresse> (message préparé le <date>)`, avec
  les liens déjà trouvés (fiche, blog…). Pas de ligne dans `LISEZMOI.md` (aucun livret).
- Bilan : où envoyer (lien ou adresse), chemin du message, et « relancer `/regles-jeu:rechercher <Jeu>` avec le
  lien ou le fichier reçu ». Ne pas proposer de traduction.
