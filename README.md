# PRIM
Ce dossier contient tous les fichiers propres au projet PRIM (Télécom Paris).

Les dumps Wikipedia sont extraits à partir de ce site : https://dumps.wikimedia.org/enwiki/20201001/ . Ils sont trop volumineux pour être ajoutés à ce dossier.

**Du 29/09/2020 au 13/10/2020**

- Choix du dataset : films de Wikipedia
- Téléchargement de milliers de pages Wikipedia sur des films (format HTML)
- Preprocessing des données en récupérant les deux premières sections de chaque page (parsing HTML)
- Calcul des embeddings avec BERT (utilisation d'un modèle multilingue pré-entrainé).
- Stockage des encoding avec la librairie Annoy
--> ceci facilite l'import des articles encodé pour les comparer avec un nouvel article en entrée. Ceci permet de n'avoir à encoder qu'un seul article à chaque manipulation.


**Du 13/10/2020 au 03/11/2020**

- Utilisation de parsers HTML et XML sur un dump Wikipedia.
- Preprocessing du texte pour éliminer les tags non traités par les parsers.
- Récupération des titres des articles et des liens internes (wikilinks)
- Création de graphes (networkx) pour lier un article donné et ses liens.
- Calcul de la similarité entre les différents textes.

--> utilisation de BERT (impliquant des transformers).


**Du 03/11/2020 au 17/11/2020**

Compte tenu du fait que beaucoup de textes devaient être traités de nouveau afin d'éliminer les tags XML superflus et que beaucoup d'articles n'étaient en réalité que des redirections vers d'autres articles, j'ai laissé les graphes en suspens.
Je travaille toujours sur une portion (1/30) du dump total. Ceci me permet de parfaire le pre processing des données avant d'appliquer ces techniques à un très grand jeu de données (plus de 17Go compressés). L'utilisation de la totalité du Dump résoudra le problème des redirections ne pointant vers aucune page.

- Configuration d'un tunnel SSH pour le transfert des fichiers vers les machines LAMES de Télécom Paris.
- Envoi des fichiers volumineux sur la machine distante. 
- De nombreux problèmes subsistent après nettoyage du texte (des tags sont transformés en texte, par exemple).
--> modification du parser pour y ajouter un parser HTML et un parser XML supplémentaire (mwparserfromhell).
- Prise en compte d'un problème redondant de Wikipédia : les articles de redirection.

Objectif pour les prochaines semaines :

- Application des méthodes de parsing et pre-processing sur le dump entier.
- Création de graphes sur la totalité du dataset et calcul du shortest path.
--> essai des fonctions de networkx et essai de pyspdag 


**Du 17/11/2020 au 01/12/2020**

- Application des techniques de parsing à la totalité du dump
--> Temps d'exécution considérable : plus de 14h pour 7.3 millions d'articles. 
- Partitionnement des fichiers .pkl contenant les articles, leurs textes et leurs liens internes. J'avais décidé d'inclure dans chacun des fichiers 100 000 articles, afin de pouvoir vider le cache après le stockage. Ceci permettait d'éviter un crash du notebook mais aussi de pouvoir reprendre à un certain indice si ce crash arrivait, sans avoir à regénérer la totalité du fichier.
--> ces manipulations sont très coûteuses en mémoire. J'ai tenté plusieurs approches, impliquant l'utilisation de différentes librairies.
- Décision d'empiler tous les noms des articles dans un seul et même fichier et d'en faire de même pour les textes des articles et des wikilinks.
Ce choix a été compte tenu du fait des erreurs de mémoire qui apparaissaient et des limites de taille de fichiers pour le stockage sous format pickle.

NB : Un problème de connexion SSH m'a empêché d'utiliser les ressources des machines de Télécom Paris.

- Gestion des redirections
--> Le processing du dump de la totalité de Wikipédia permet de trouver les pages de redirection, chose qui n'était pas possible sur une petite portion du dump (comme lors des semaines précédentes).

L'édition des graphes n'a pas pu être effectuée car la taille du dataset des liens internes affiliés aux articles étaient trop importante. Une erreur de mémoire était renvoyée, même en utilisant un autre format plus adapté aux données volumineuses (ex: shelve).
J'ai voulu effectuer ces opérations coûteuses sur une machine de Télécom, bien plus puissante, mais un problème de connexion SSH est apparu. Ce problème est en cours de résolution.