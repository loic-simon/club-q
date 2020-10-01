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

    def __init__(self, *args, footer=False, **kwargs):
        """Initialize self."""
        super().__init__(*args, **kwargs)
        self.footer = footer

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
        if self.footer:                     # Si footer : on l'enlève
            footer_item = items.pop(-1)
        items.sort(key=natsort.natsort_keygen(lambda item: self.get(item, column)), reverse=sort_down)
        if self.footer:
            items.append(footer_item)       # Puis on le remet une fois trié
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
    def __init__(self, *args, filter_column=None, footer=None, **kwargs):
        """Initialize self."""
        super().__init__(*args, footer=footer, **kwargs)
        self.filter_column = filter_column
        self.validatecommand = self.register(self.validatecommand_callback)     # Fonction à passer à ttk.Entry
        # Syntaxe : ttk.Entry(parent, validate="key", validatecommand=(<FilterableTreeview instance>.validatecommand, "%P"))
        self.detached = []          # Items actuellement masqués
        self.footer = footer

    def filter(self, column, motif):
        """Filtre les entrées du Treeview pour ne laisser que celles telle que <motif> soit dans la colonne <clumn>"""
        def correspond(item, motif):
            return unidecode.unidecode(motif).lower() in unidecode.unidecode(self.get(item, column)).lower()

        items = list(self.get_children())
        if self.footer:                     # Si footer :
            footer_item = items.pop(-1)         # on le détache
            self.detach(footer_item)

        for item in items:
            if not correspond(item, motif):     # on filtre :
                self.detach(item)               # on détache les items qui ne correspondent plus
                self.detached.append(item)

        reattached = False
        for item in self.detached.copy():
            if correspond(item, motif):         # et on réattache ceux qui correspondent
                self.reattach(item, "", "end")
                self.detached.remove(item)
                reattached = True

        if self.footer:                     # on réattache le footer
            self.reattach(footer_item, "", "end")

        if reattached:          # On a réattaché des items
            self.sort()             # On re-trie sur les critères actuels, le cas échéant (gère le footer lui-même)

    def reset(self):
        """Supprime tous les items, l'indicateur de tri, et réinitialise les variables internes"""
        for item in self.detached:
            self.reattach(item, "", "end")
        self.detached = []
        super().reset()

    def validatecommand_callback(self, motif):
        """Fonction appellée à chaque modification de l'instance ttk.Entry

        Syntaxe : ttk.Entry(parent, validate="key", validatecommand=(<FilterableTreeview instance>.validatecommand, "%P"))
        """
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

    [footer_values] ligne "footer" à ajouter : toujours affichée en dernier, même si tri / filtrage / insertion... (défaut : None)
    [footer_id]     ID associé au footer (défaut : None)

    **kwargs        arguments directement passés à ttk.Treeview
    """
    def __init__(self, parent, columns, insert_func, sizes=None, stretches=None, id_func=lambda item: item.id, id_size=0, id_stretch=False, footer_values=None, footer_id=None, **kwargs):
        """Initialize self."""
        super().__init__(parent, columns=columns, footer=bool(footer_id), **kwargs)
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

        self.footer_values = footer_values
        self.footer_id = footer_id
        self.footer_packed = False

    def insert(self, *items, index="end"):
        """Insère <*items> à la position <index>, en utilisant les fonctions d'insertion définies à la création du Treeview"""
        self.items.extend(items)
        if self.footer_packed and index == "end":       # Ajout à la fin et footer affiché : l'enlève
            super().delete(self.footer_id)
            self.footer_packed = False

        for item in items:
            super().insert("", index, iid=self.id_func(item), values=self.insert_func(item))

        if self.footer_id and index == "end" and not self.footer_packed:       # Ajout à la fin et footer non affiché : l'affiche
            self.footer_packed = True
            super().insert("", "end", iid=self.footer_id, values=self.footer_values)

    def reset(self):
        """Supprime tous les items, l'indicateur de tri, et réinitialise les variables internes"""
        super().reset()
        self.items = []
        self.footer_packed = False

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
