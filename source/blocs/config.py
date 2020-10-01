# Ce module contient toutes les variables, classes et objets globaux du programme, qui ont besoin d'être accessibles via différents modules.
# Ce module doit être importé dans chaque fichier du programme.
# https://stackoverflow.com/a/423401

import os
import sys
import json
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk
import unidecode
import natsort

from . import tools


#---------------------------- GESTION ENCAPSULATION ----------------------------
# https://hackernoon.com/the-one-stop-guide-to-easy-cross-platform-python-freezing-part-1-c53e66556a0a

is_frozen = getattr(sys, "frozen", False)
frozen_temp_path = getattr(sys, "_MEIPASS", "")

if is_frozen:
    basedir = frozen_temp_path
else:
    basedir = "" # os.path.dirname(os.path.abspath(__file__))



#----------------------------- VARIABLES GLOBALES ------------------------------

if len(sys.argv) > 1 and sys.argv[1] == "--debug":
    DEBUG = True
    print("Chargement du programme - mode DEBUG")
else:
    DEBUG = False

with open(os.path.join(basedir, "resources", "data.json"), "r") as df:
    data = json.load(df)

TITLE = "Programme Club Q"

DATA_PARAMETERS = {         # Paramètres encryptés nécessaires dans data.json
    "DATABASE_URI": "URI d'accès aux données (protocol://user:pwd@server/base)",
    "FTP_HOST": "Adresse de l'hôte FTP",
    "FTP_USER": "Nom de l'utilisateur FTP",
    "FTP_PASSWORD": "Mot de passe d'accès FTP",
    "MAIL_SENDER": "Adresse mail du Club Q",
}
for param in DATA_PARAMETERS:
    globals()[param] = None     # Initialisation à None

MAIL_LOGIN = None           # Demandés lors de l'exécution du programme
MAIL_PASSWORD = None

lien_logo_q = os.path.join(basedir, "resources", "logo_q.png")
lien_logo_pc = os.path.join(basedir, "resources", "logo_pc.png")

root = None         # Fenêtre principale
fen_suivi = None    # Fenêtre d'attribution

saisons = []
saison = None

salles = []

# Paramètres par défaut, destinés à être écrasés dans menu.py [ou par lecture params.cfg - pas sûr ça]
promo_1A = 139

# Pour le mécontentement, bonus de promo :
bonus_1A = 1
bonus_2A = 0.8
bonus_3A = 0.6
bonus_4A = 0.4
bonus_autre = -10


def init_var_glob_saison():
    """À appeller à chaque chargement de saison"""
    global spectacles, clients, voeux, participations, attrib_ss_conflit_done, num_voeux, cas_en_cours, logs

    spectacles = []
    clients = []
    voeux = []
    participations = []

    attrib_ss_conflit_done = False
    init_mecontentement_done = False

    num_voeux = 1
    cas_en_cours = False

    logs = {}


def refresh_listes():
    try:
        liste_clients.refresh()
        liste_spectacles.refresh()
        liste_suvi_process.refresh()
    except Exception:
        pass


#----------------------------- CLASSES DE DONNÉES ------------------------------

def dataclass(initfunc):
    """Décorateur pour les fonctions __init__ des classes de données : définit self.bdd_cols, self.bdd_item et tous les attributs de données"""
    def new_initfunc(self, bdd_item):
        self.bdd_item = bdd_item
        self.bdd_cols = list(bdd_item.__dict__.keys())        # Noms des colonnes de la table
        for attr in self.bdd_cols:
            setattr(self, attr, getattr(bdd_item, attr))

        initfunc(self, bdd_item)        # Reste de l'initialisation

    return new_initfunc


class Saison():
    """Saison Qlturelle

    Classe de données liée à la table "saisons" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    @dataclass
    def __init__(self, bdd_saison):
        """Initialize self à partir d'une entrée de BDD existante"""
        # @dataclass => self.id, self.nom, self.promo_orga, self.debut, self.fin, self.debut_inscription, self.fin_inscription

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Saison #{self.id} ({self.nom})>"


class Salle():
    """Salle de spectacles

    Classe de données liée à la table "salles" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    @dataclass
    def __init__(self, bdd_salle):
        """Initialize self à partir d'une entrée de BDD existante"""
        # @dataclass => self.id, self.nom, self.description, self.image_path,
        #               self.url, self.adresse, self.latitude, self.longitude

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Salle #{self.id} ({self.nom})>"


class Participation():
    """Participation d'un client à une saison

    Classe de données liée à la table "participations" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    @dataclass
    def __init__(self, bdd_saison):
        """Initialize self à partir d'une entrée de BDD existante"""
        # @dataclass => self.id, self.client_id, self.saison_id, self.mecontentement, self.fiche_path

        self.client = tools.get(config.clients, id=self.client_id)
        self.saison = tools.get(config.saisons, id=self.saison_id)

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Inscription #{self.id} ({self.client}/{self.saison})>"


class Client():
    """Client achetant des places

    Classe de données liée à la table "clients" : toutes les colonnes de cette tables (self.bdd_cols) scont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    @dataclass
    def __init__(self, bdd_client):
        """Initialize self à partir d'une entrée de BDD existante"""
        # @dataclass => self.id, self.id_wp, self.nom, self.prenom, self.promo, self.autre, self.email
        #               self.mecontentement, self.mecontentement_precedent, self.saison_actuelle_mec, self.a_payer

        self.nomprenom = f"{self.nom.upper()} {self.prenom.title()}"

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Client #{self.id} ({self.nomprenom})>"

    def voeux(self):
        """Renvoie la liste des voeux émis par ce client"""
        return [voeu for voeu in voeux if voeu.client_id == self.id]

    def attributions(self):
        """Renvoie la liste des voeux exaucés (places attribués) pour ce client"""
        return [voeu for voeu in self.voeux() if voeu.places_attribuees]

    def nb_places_demandees(self):
        """Renvoie le nombre total de places demandées par ce client"""
        return sum(voeu.places_demandees or 0 for voeu in self.voeux())

    def nb_places_attribuees(self):
        """Renvoie le nombre total de places attribuées à ce client"""
        return sum(voeu.places_attribuees for voeu in self.attributions())

    def calcul_a_payer(self):
        """Renvoie la somme totale due par ce client à ce stade de l'attribution"""
        return sum(voeu.places_attribuees*voeu.spectacle.unit_price for voeu in self.attributions())

    def verif_priorites(self):
        """Affiche un avertissement si les priorités du client sont illégales (différentes de 1, 2, ..., N_voeux)"""
        priorites = sorted(voeu.priorite for voeu in self.voeux())
        if priorites != list(range(1, len(priorites) + 1)):
            tk.messagebox.showwarning(title="Priorités illégales", message=f"Priorité des voeux illégale pour {self.nomprenom} :\n{priorites}")

    def init_mecontentement(self):
        """Initialise le mécontentement du client à partir des différentes sources liées au client et à ses voeux (exaucés et comblés)"""
        # Si la saison actuelle n'est pas encore celle là, on change et on enregistre le mécontentement "actuel" comme mécontentement précédent
        if self.saison_actuelle_mec != saison.id:
            self.mecontentement_precedent = self.mecontentement
            self.saison_actuelle_mec = saison.id

        # Mécontentement de la saison précédente + celui ajouté arbitrairement dans la fiche élève :
        self.mecontentement = self.mecontentement_precedent or 0

        # Mécontentement lié au nombre de voeux : si l'élève a moins de voeux que le nombre moyen, son mécontentement augmente, il est favorisé :
        self.mecontentement += 0.9**(len(self.voeux()) - 1)

        # Idem pour le nombre total de places demandées :
        self.mecontentement += 2/self.nb_places_demandees()

        # Bonus/malus selon la promo :
        if self.promo == promo_1A:
            self.mecontentement += bonus_1A
        elif self.promo == promo_1A - 1:        # 2A
            self.mecontentement += bonus_2A
        elif self.promo == promo_1A - 2:        # 3A
            self.mecontentement += bonus_3A
        elif self.promo == promo_1A - 3:        # 4A
            self.mecontentement += bonus_4A
        else:
            self.mecontentement += bonus_autre

        # Malus selon les voeux déjà attribués pour cette saison : -0.5^priorité par voeu comblé
        for voeu in self.attributions():
            self.mecontentement += voeu.delta_mec()


class Voeu():
    """Voeu / attribution d'un client pour un spectacle

    Classe de données liée à la table "voeux" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    @dataclass
    def __init__(self, bdd_voeu):
        """Initialize self à partir d'une entrée de BDD existante"""
        # @dataclass => self.id, elf.client_id, self.spectacle_id, self.places_demandees,
        #               self.priorite, self.places_minimum, self.places_attribuees

        self.client = tools.get(clients, id=self.client_id)
        self.spectacle = tools.get(spectacles, id=self.spectacle_id)

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Voeu #{self.id} ({self.client}/{self.spectacle})>"

    def delta_mec(self):
        """Mécontentement ajouté lors de l'attribution du voeu"""
        return -0.5**self.priorite

    def attribuer(self, places):
        """Définit le nombre de places attribuées du voeu à <places> et modifie le mécontentement du client en conséquence"""
        if (not self.places_attribuees) and places:         # Voeu -> attribution
            self.client.mecontentement += self.delta_mec()
        elif self.places_attribuees and (not places):       # Attribution -> voeu
            self.client.mecontentement -= self.delta_mec()

        self.client.a_payer = self.client.calcul_a_payer()
        self.places_attribuees = places


class Spectacle():
    """Spectacle pour lequel des places sont proposées

    Classe de données liée à la table "spectacles" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    @dataclass
    def __init__(self, bdd_spectacle):
        """Initialize self à partir d'une entrée de BDD existante"""
        # @dataclass => self.id, self.saison_id, self.nom, self.categorie, self.description, self.affiche_path,
        #               self.salle_id, self.dateheure, self.nb_tickets, self.unit_price, self.score

        self.date = self.dateheure.strftime("%d/%m/%Y") if self.dateheure else "???"
        self.heure = self.dateheure.strftime("%H:%M") if self.dateheure else "???"

        self.saison = tools.get(saisons, id=self.saison_id)
        self.salle = tools.get(salles, id=self.salle_id)

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Spectacle #{self.id} ({self.nom})>"

    def lieu(self):
        """Renvoie le nom de la salle de ce spectacle"""
        return self.salle.nom if self.salle else "???"

    def voeux(self):
        """Renvoie la liste des voeux émis pour ce spectacles"""
        return [voeu for voeu in voeux if voeu.spectacle_id == self.id]

    def attributions(self):
        """Renvoie la liste des voeux attribués pour ce spectacles"""
        return [voeu for voeu in self.voeux() if voeu.places_attribuees]

    def nb_places_demandees(self):
        """Renvoie le nombre total de places demandées pour ce spectacle"""
        return sum(voeu.places_demandees or 0 for voeu in self.voeux())

    def nb_places_attribuees(self):
        """Renvoie le nombre total de places attribuées pour ce spectacle"""
        return sum(voeu.places_attribuees or 0 for voeu in self.voeux())

    def nb_places_restantes(self):
        """Renvoie le nombre total de places encore disponibles pour ce spectacle"""
        return (self.nb_tickets - self.nb_places_attribuees())

    def liste_eleve_desirant_spec(self):
        """Prend un objet spectacle en argument et renvoie une liste de type ['Vidon Guillaume 3 places voeu1", "Mosso ...']"""
        L = []
        for voeu in self.voeux():
            client = voeu.client
            L.append(f"{client.prenom} {client.nom} \t {voeu.places_demandees} places demandées - vœu n° {voeu.priorite}")
        return L

    def liste_eleve_ayant_spec(self):
        """Prend un objet spectacle en argument et renvoie une liste de type ['Vidon Guillaume 3 places voeu1", "Mosso ...']"""
        L = []
        for voeu in self.voeux():
            if voeu.places_attribuees:
                client = voeu.client
                L.append(f"{client.prenom} {client.nom} \t {voeu.places_attribuees} places attribuées / {voeu.places_demandees} demandées - vœu n° {voeu.priorite}")
        return L

    def nbplacesamodifier(self):
        """Méthode d'un spectacle qui renvoie le nombre de places supplémentaires à demander ou le nombre à retirer"""
        if (nbplacesspectacle(self) > self.places_demandees):
            return ("Il faudrait demander " + str(nbplacesspectacle(self)-self.places_demandees) + " places en plus")
        else:
            return ("Il faudrait retirer " + str(self.places_demandees-nbplacesspectacle(self)) + " places")



#---------------------------- SOUS-CLASSES TKINTER -----------------------------

class Toplevel(tk.Toplevel):
    """Classe fille de tkinter.Toplevel permettant de mettre le nom du programme systématiquement"""

    def __init__(self, parent=root, *args, **kwargs):
        """Initialize self."""
        super().__init__(parent, *args, **kwargs)
        self.title()

    def title(self, txt=None):
        """Définit le titre en y ajoutant le nom du programme"""
        super().title(f"{txt} – {TITLE}" if txt else TITLE)


class SortableTreeview(ttk.Treeview):
    """Classe fille de ttk.Treeview ajoutant des boutons de tri

    *args et **kwargs sont directement passés à ttk.Treeview.
    Le tri est fait par le module natsort (pypi.org/project/natsort) qui propose un tri « naturel » ("1" < "2" < "12" au lieu de "1" < "12" < "2", par exemple)
    """

    def __init__(self, *args, **kwargs):
        """Initialize self."""
        super().__init__(*args, **kwargs)
        self.sort_column = None
        self.sort_down = False

        self.up_image = ImageTk.PhotoImage(Image.open(os.path.join(basedir, "resources", "sort_up.png")))
        self.down_image = ImageTk.PhotoImage(Image.open(os.path.join(basedir, "resources", "sort_down.png")))

        self.bind("<Button-1>", self.on_clic)

    def get(self, item, column):
        """Récupère la valeur de <column> pour <item>, codé de manière utilisable"""
        if column == "#0":
            return self.item(item, "text")
        else:
            return self.set(item, column)       # Qui code un module ou set récupère une valeur ??????

    def sort(self, column=None, sort_down=None):
        """Trie le Treeview selon la colonne [column], en ordre décroissant si [sort_down] == True

        Si [column] n'est pas spécifiée,
            - trie selon la colonne de tri actuelle si elle existe
            - ne fait rien si elle n'existe pas

        Si [sort_down] n'est pas spécifié,
            - trie selon le sens inverse de celui actuel si [column] est la colonne de tri actuelle
            - trie en ordre croissant                    si [column] est une autre colonne
            - trie selon le sens de tri actuel           si [column] n'est pas spécifiée
        """
        if not column:
            if self.sort_column:
                column = self.sort_column       # On retrie selon la même colonne
            else:
                return
            if sort_down is None:
                sort_down = self.sort_down
        elif self.sort_column == column:
            if sort_down is None:
                sort_down = not self.sort_down
        else:
            if sort_down is None:
                sort_down = False
            if self.sort_column:                            # Si c'était trié selon une autre colonne
                self.heading(self.sort_column, image="")        # on enlève l'indicateur

        self.heading(column, image=self.down_image if sort_down else self.up_image)
        self.sort_column = column
        self.sort_down = sort_down

        items = list(self.get_children())
        items.sort(key=natsort.natsort_keygen(lambda item: self.get(item, column)), reverse=sort_down)
        self.set_children("", *items)

    def reset(self):
        """Supprime tous les items, l'indicateur de tri, et réinitialise les variables internes"""
        self.delete(*self.get_children())
        if self.sort_column:
            self.heading(self.sort_column, image="")
        self.sort_column = None
        self.sort_down = False

    def on_clic(self, event):
        """Méthode appeléé en cas de simple clic : gère le tri le cas échéant"""
        if self.identify_region(event.x, event.y) == "heading":     # Clic sur un nom de colonne
            self.sort(self.identify_column(event.x))


class FilterableTreeview(SortableTreeview):
    """Classe fille de SortableTreeview ajoutant une méthode de filtrage

    *args et **kwargs sont directement passés à SortableTreeview.
    """
    def __init__(self, *args, filter_column=None, **kwargs):
        """Initialize self."""
        super().__init__(*args, **kwargs)
        self.filter_column = filter_column
        self.validatecommand = self.register(self.validatecommand_callback)     # Fonction à passer à ttk.Entry
        # Syntaxe : ttk.Entry(parent, validate="key", validatecommand=(<FilterableTreeview instance>.validatecommand, "%P"))
        self.detached = []          # Items actuellement masqués

    def filter(self, column, motif):
        """Filtre les entrées du Treeview pour ne laisser que celles telle que <motif> soit dans la colonne <clumn>"""
        def correspond(item, motif):
            return unidecode.unidecode(motif).lower() in unidecode.unidecode(self.get(item, column)).lower()

        for item in self.get_children():
            if not correspond(item, motif):
                self.detach(item)
                self.detached.append(item)

        reattached = False
        for item in self.detached.copy():
            if correspond(item, motif):
                self.reattach(item, "", "end")
                self.detached.remove(item)
                reattached = True

        if reattached:          # On a réattaché des items
            self.sort()             # On re-trie sur les critères actuels, le cas échéant

    def reset(self):
        """Supprime tous les items, l'indicateur de tri, et réinitialise les variables internes"""
        for item in self.detached:
            self.reattach(item, "", "end")
        self.detached = []
        super().reset()

    def validatecommand_callback(self, motif):
        """Fonction appellée à chaque modification de l'instance ttk.Entry

        Syntaxe : ttk.Entry(parent, validate="key", validatecommand=(<FilterableTreeview instance>.validatecommand, "%P"))"""
        if self.filter_column:
            self.filter(self.filter_column, motif)
            return True
        else:
            raise RuntimeError(f"Le Treeview {self} n'a pas été configuré pour accepter la filtration")


class ItemsTreeview(FilterableTreeview):
    """Classe fille de FilterableTreeview pour afficher une liste d'items et les insérer à l'aide de fonctions personnalisées

    <parent>        objet Tk contenant le Treeview
    <columns>       liste des noms de colonnes
    <insert_func>   fonction item -> liste des valeurs à afficher dans les colonnes (doit avoir la même longeur que <columns>)
    [sizes]         liste des tailles des colonnes, en pixels (doit avoir la même longeur que <columns> si présent)
    [stretches]     liste des déformabilités des colonnes, booléens (défaut : toutes à False, doit avoir la même longeur que <columns> si présent)

    [id_func]       fonction telle que id_function(item) = ID unique (défaut : lambda item: item.id)
    [id_size]       taille de la colonne ID (défaut : 0, i.e. ne pas afficher l'ID)
    [id_stretch]    déformabilité de la colonne ID (défaut : False)

    **kwargs        arguments directement passés à ttk.Treeview
    """
    def __init__(self, parent, columns, insert_func, sizes=None, stretches=None, id_func=lambda item: item.id, id_size=0, id_stretch=False, **kwargs):
        """Initialize self."""
        super().__init__(parent, columns=columns, **kwargs)
        self.column("#0", width=id_size, minwidth=id_size, stretch=id_stretch, anchor=tk.W)
        if not sizes:
            sizes = [None]*len(columns)
        if not stretches:
            stretches = [False]*len(columns)
        for column, size, stretch in zip(columns, sizes, stretches):
            self.column(column, width=size, minwidth=size, stretch=stretch, anchor=tk.W)
            self.heading(column, text=column, anchor=tk.W)

        self.items = []
        self.insert_func = insert_func
        self.id_func = id_func

    def insert(self, *items, index="end"):
        """Insère <*items> à la position <index>, en utilisant les fonctions d'insertion définies à la création du Treeview"""
        self.items.extend(items)
        for item in items:
            super().insert("", index, iid=self.id_func(item), values=self.insert_func(item))

    def reset(self):
        """Supprime tous les items, l'indicateur de tri, et réinitialise les variables internes"""
        super().reset()
        self.items = []

    def refresh(self):
        """Recalcule les attributs de chaque item"""
        for item in self.items:
            self.item(self.id_func(item), values=self.insert_func(item))


class ContextPopup():
    """Context manager affichant une fenêtre Toplevel tout le long d'un processus long"""

    def __init__(self, master, text, title=None, existing=None):
        """Initialize self."""
        if existing and isinstance(existing, ContextPopup):     # Mise à jour d'une popup déjà existante (et pas création d'une nouvelle)
            self.existing = existing
            self.existing.edit(text)
        else:
            self.existing = None
            self.master = master
            self.fenetre = Toplevel(master)
            self.fenetre.title(title)
            self.fenetre.protocol("WM_DELETE_WINDOW", lambda: None)          # Empêche de fermer la popup
            self.message = tk.Message(self.fenetre, text=text, padx=20, pady=20)
            self.message.pack()

    def __enter__(self):
        """Entrée dans le bloc with : affiche la fenêtre et le curseur"""
        if self.existing:
            return self.existing
        else:
            self.fenetre.configure(cursor="wait")
            self.master.configure(cursor="wait")
            self.fenetre.update()
            return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Sortie du bloc with : supprime la fenêtre et rétablit le curseur"""
        if not self.existing:
            self.fenetre.destroy()
            self.master.configure(cursor="")

    def edit(self, text):
        """Modifie le texte de la popup"""
        if self.existing:
            self.existing.message.configure(text=text)
            self.existing.fenetre.update()
            self.existing.fenetre.lift()
        else:
            self.message.configure(text=text)
            self.fenetre.lift()
