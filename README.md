# club-q

*(Français)*
Programme Python implémentant une interface graphique pour l'attribution de places de spectacles à des étudiants de l'ESPCI Paris - PSL, dans le cadre de l'activité du club chargé de cette tâche, dit « Club Q ».

Conçu pour un usage dans ce cadre uniquement. Ce programme est basé sur des données privées et organisées de manière spécifique ; l'accès aux données est protégé par mot de passe.

*(English)*
Python program implementing a graphical interface for allocating show tickets to ESPCI Paris - PSL students, as part of the "Club Q" activity. Designed for use in this setting only. This program relies on private data, organized in a specific way and password-protected.


## Fonctionnalités

* Affichage détaillé des étudiants, spectacles et vœux
* Attribution automatique par minimisation des mécontentements individuels
* Ajustement manuel des attributions
* Synchronisation avec le site d'inscription
* Génération des fiches récapitulatives PDF des élèves et spectacles
* [v2.1] Publication des fiches élèves individuelles sur le serveur d'inscription
* [v2.1] Envoi des fiches élèves individuelles par mail
* [v2.2] Génération d'un fichier Excel récapitulant les sommes à payer
* [v2.3] Création de nouveaux vœux (pour les élèves déjà existants)
* [v2.4] Génération de fichiers Excel récapitulatifs pour les spectacles

## Installation

### Exécutable

Pour les utilisateurs sous Windows, l'application est disponible sous forme d'un exécutable : [`club-q.exe`](club-q.exe).

Ce fichier est autonome et n'a pas de dépendances : il suffit de le télécharger et de l'exécuter.  \
Testé sous Windows 10 / 64 bits uniquement ; devrait fonctionner sous toutes les versions récentes.


### Code source

À défaut, le dossier [`source`](source/club-q.py) contient l'ensemble des fichiers nécessaires au fonctionnement de l'application.  \
Le point d'entrée du programme est alors [`source/club-q.py`](source/club-q.py), qu'il suffit d'exécuter comme tout script Python.


#### Dépendances

* Python 3.6+
* Packages : SQLAlchemy, PyMySQL, ReportLab, cryptography, Unidecode, Pillow, natsort, openpyxl (voir [`requirements.txt`](requirements.txt))

Pour installer tous les packages nécessaires, avec [pip](https://pip.pypa.io/en/stable/) (gestionnaire de packages usuel) :

```bash
pip install -r source/requirements.txt
```

### Geler le code

Le fichier exécutable fourni a été gelé à l'aide de [PyInstaller](https://pypi.org/project/pyinstaller/). La commande suivante permet d'en faire un équivalent pour l'environnement d'exécution courant (à la racine du dossier [`source`](source/club-q.py)) :

```bash
pyinstaller ./club-q.spec
```

L'exécutable ainsi généré est placé par défaut dans le dossier [`source/dist`](source/dist).

## Usage

Utiliser l'assistant intégré au programme pour appréhender son utilisation.

### Mot de passe

Le hash du mot de passe du programme et les paramètres sensibles chiffrées peuvent être redéfinis à l'aide du script [`source/gen_new_pass.py`](source/gen_new_pass.py).

### Utilisation en ligne de commande
Les options suivantes, principalement utiles pour le développement, sont disponibles :

* `--debug` : affiche certaines informations détaillées au cours de l'exécution du programme
* `--direct` : lance directement la fenêtre principale, sans passer par l'écran d'accueil
* `--assistant` : lance directement l'assistant d'attribution, sans passer par l'écran d'accueil


## Contributions

Ce projet n'est pas ouvert aux contributions extérieures. N'hésitez pas à me contacter pour toute remarque.


## Licence

Ce programme est partagé sous [licence MIT](https://choosealicense.com/licenses/mit/).

© 2020 Loïc Simon – Association GRI – ESPCI Paris - PSL  \
Basé sur un programme initialement développé par Jessie Mosso 134, Miguel Cano 134 et Guillaume Vidon – logo du club Q par Anaëlle Chrétien 134

Pour toute question, n'hésitez pas à me contacter par mail : [loic.simon@espci.org](mailto:loic.simon@espci.org)
