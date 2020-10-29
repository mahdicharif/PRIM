# PRIM
Ce dossier contient tous les fichiers propres au projet PRIM (Télécom Paris).

Les dumps Wikipedia sont extraits https://dumps.wikimedia.org/enwiki/20201001/ . Ils sont trop volumineux pour être ajoutés à ce dossier.

**Du 29/09/2020 au 13/10/2020**

- Téléchargement de milliers de pages Wikipedia sur des films (format HTML)
- Preprocessing des données en récupérant les deux premières sections de chaque page (parsing HTML)
- Calcul des embeddings avec BERT (utilisation d'un modèle multilingue pré-entrainé).
- Stockage des encoding avec la librairie Annoy
--> ceci facilite l'import des articles encodé pour les comparer avec un nouvel article en entrée. Ceci permet de n'avoir à encoder qu'un seul article à chaque manipulation.

**Du 13/10/2020 au 03/10/2020**

- Utilisation de parsers HTML et XML sur un dump Wikipedia.
- Preprocessing du texte pour éliminer les tags non traités par les parsers.
- Récupération des titres des articles et des liens internes (wikilinks)
- Création de graphs (networkx) pour lier un article donné et ses liens.
- Calcul de la similarité entre les différents textes.

--> utilisation de BERT (impliquant des transformers).
