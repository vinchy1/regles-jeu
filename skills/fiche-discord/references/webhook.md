# Publier par webhook

Un webhook est une adresse secrète créée par un admin du serveur, liée à un salon. Ce qui y est envoyé apparaît
sous le nom du webhook (par exemple « Fiches Golden Meeple »), pas sous celui de l'utilisateur. Sur un salon
forum, chaque envoi peut créer un post (titre + message + pièces jointes) ou répondre dans un post existant.

## Mise en place (une fois, par un admin du serveur)
1. Discord → salon *discussion-par-titre* → roue dentée (Modifier le salon) → **Intégrations** → **Webhooks**
   → **Nouveau webhook** ; lui donner un nom et une image, vérifier que le salon est bien *discussion-par-titre*.
2. **Copier l'URL du webhook** et la transmettre en privé à l'utilisateur.
3. L'utilisateur la colle seul dans `~/.claude/regles-jeu/discord-webhook.txt` (une ligne ; hors de la
   ludothèque, qui est synchronisée sur GitHub). Ne jamais la lui demander dans la conversation, ne jamais
   l'afficher, la recopier ni la mettre dans un autre fichier : qui a cette adresse peut poster dans le salon.
   Fuite → l'admin supprime le webhook et en crée un autre.

## Publier
1. **Accord explicite** : lister les jeux à publier et demander un oui (AskUserQuestion). Valable pour cette
   liste-là seulement, jamais pour la suivante.
2. **Doublons** : demander à l'utilisateur d'avoir cherché ces titres dans le salon (Claude n'ouvre pas Discord).
3. **Essai** pour chaque jeu : `python -I -X utf8 <skill>/scripts/webhook.py "<Ludothèque>/<Jeu>"`. Contrôle
   l'adresse (lecture seule : nom du webhook, salon), le titre, la longueur du message (2000 caractères), les
   pièces jointes (10 au plus, 10 Mo en tout sans boost du serveur). Montrer le résultat. Problème → corriger,
   ne pas envoyer.
4. **Envoi** : même commande avec `--envoyer` : un seul message (titre, message, couverture, livrets anglais et
   français). Le lien du post est noté dans `_outils/<Jeu>/fiche/envoye.txt` ; un second envoi du même jeu est refusé par le script.
5. Donner les liens des posts. Rappeler ce que le webhook ne sait pas faire : **épingler** le message des
   règles (Guide des posts) et ajouter les **étiquettes** du forum ; un modérateur le fait à la main.

## Erreurs Discord
- 401 / 404 : webhook supprimé ou adresse fausse → demander une nouvelle adresse à l'admin.
- 400 avec `thread_name` : le salon n'est pas un forum, ou titre refusé.
- 413 : pièces jointes trop lourdes → version allégée du livret, ou lien des règles dans le message.
- 429 : trop d'envois rapprochés → attendre quelques secondes entre deux jeux.
