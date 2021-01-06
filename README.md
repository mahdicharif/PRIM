# PRIM
Ce dossier contient tous les fichiers propres au projet PRIM (Télécom Paris).

Les dumps Wikipedia sont extraits à partir de ce site : https://dumps.wikimedia.org/enwiki/20201001/ . Ils sont trop volumineux pour être ajoutés à ce dossier.

**Du 29/09/2020 au 13/10/2020**

- Choix du dataset : articles sur des films, tirés de Wikipédia
- Téléchargement de milliers de pages Wikipédia sur des films (format HTML)
- Preprocessing des données en récupérant les deux premières sections de chaque page (parsing HTML)
- Calcul des embeddings avec BERT (utilisation d'un modèle multilingue pré-entrainé).
- Stockage des encoding avec la librairie Annoy
--> ceci facilite l'import des articles encodé pour les comparer avec un nouvel article en entrée. Ceci permet de n'avoir à encoder qu'un seul article à chaque manipulation.


**Du 13/10/2020 au 03/11/2020**

- Décision de travailler sur la totalité du corpus d'articles de Wikipédia (plusieurs millions)
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


**Du 01/12/2020 au 08/12/2020**

- Changement du stockage des données : utilisation de sqlite3 et création d'un fichier .db
- Lancement en tâche de fond du processing du dump sur une machine distante de Télécom.
--> Plus de 24h d'exécution
--> Le Wikipédia anglais contient près de 6 million d'articles. Cependant, il existe également des articles de redirection et d'autres pages. Elles seront également extraites lors du parsing du document.
- Stockage des articles, contenant du texte ou redirigeant vers un autre article, des pages propres aux catégories etc... La pluralité des natures des pages Wikipédia justifie le dépassement des 6 millions d'articles traités.
- La structure du fichier est la suivante : (Nom de l'article, Texte de l'article, Liens internes, Nom de l'article de redirection).
Le "Nom de l'article de redirection" représente le nom récupérés dans le texte de l'article, si le mot "REDIRECT" est compris dans le texte. Dans le cas où cette condition n'est pas vérifiée, ce champ est égal à 0. Ceci me permet de ne pas avoir à stocker plusieurs fois un même texte.
--> Gain d'espace en mémoire et de chargement des données

**Nombre de pages extraites et traitées** : 20 776 899

Afin de pouvoir stocker les liens internes, j'ai converti la liste des liens de chaque article avec json. Ce format est supporté par sqlite3. 

- Encoding des articles sur la machine de Télécom (longue et lourde opération sur des millions de textes)
- Sachant qu'il y avait près de 50% des articles qui n'étaient que des redirections, j'ai décidé d'encoder les textes des articles ayant leur propre texte.
Ceci m'évite de stocker des encodings d'articles en doublon.

--> action lancée le 07/12/2020. J'estime que la génération du fichier contenant tous les embeddings prendra plusieurs jours.
Dans le doute, j'ai également commencé à chercher une autre solution de stockage, notamment via Sqlite3 (solution développée dès le 08/12/2020).


**Du 08/12/2020 au 18/12/2020**

- Encoding des textes et stockage dans une base de données Sqlite. 
--> nouvelle estimation portant l'encoding sur 10 jours, environ. Il s'agit d'une tâche de fond, déléguée à la LAME de Télécom via la commande *tmux*.
- Problèmes de permission sur le fichier généré. Le statut du fichier change en pleine exécution de mon script Python. 
- 11/12/2020 : problème réglé par l'utilisation d'un espace de stockage persisté. Lancement de l'encoding le 11/12/2020 à 01:08.
- Appropriation de la librairie Networkdisk pour le stockage d'un très grand graphe.

TO DO quand l'encoding sera terminé : utiliser DB Browser pour attribuer à la colonne des vecteurs un type "array" afin de pouvoir convertir le format json en un array, ayant oublié de le faire au préalable. 
Ceci m'éviterait de devoir convertir chaque ligne individuellement après l'import de la base de données.

J'ai dû tester plusieurs façons d'insérer les données : par tranches de 10 millions d'edges, en ingérant tous les liens dans la base de données... J'ai finalement retenu une insertion par tranche de 80 millions d'edges.

**Le 18/12/2020 : insertion des edges dans une base de données : 66 GB, plus de 200 millions d'edges.**


**Du 18/12/2020 au 03/01/2021**

- Fin de l'encoding des articles le 21/12/2020 à 9:43. Le fichier pèse 43GO. J'ai stocké les vecteurs après les avoir convertis bytes (format supporté par SQLite).

Concernant le graphe : définition des pistes d'exploitation avec M. Paperman à venir.

- Echange par mails avec M. Paperman : 

--> Création d'un petit tutoriel présentant mon script de création du graphe avec Networkdisk.
--> Faire une application de démonstration via Flask