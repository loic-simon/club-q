# Fenêtre d'attribution principale (frames vertes et jaunes)

import tkinter as tk
import tkinter.messagebox, tkinter.simpledialog
from tkinter import ttk

import hashlib

from . import config, classes, bdd, tools, fichier, attribution, exportation, publication, fiches, assistant


# Variables globales
frame_saisons = None
frame_spectacles = None
frame_clients = None
menubar = None


class SaisonMenu(ttk.OptionMenu):
    def __init__(self, parent, *saisons):
        self.saisons = saisons
        self.var = tk.StringVar()
        saisons_names = [saison.nom for saison in saisons]
        super().__init__(parent, self.var, saisons_names[0], *saisons_names)

    def set(self, saison):
        self.var.set(saison.nom)

    def get(self):
        return tools.get(self.saisons, nom=self.var.get())


def build_root():
    global frame_saisons, frame_spectacles, frame_clients, menubar

    # SAISONS
    frame_saisons = ttk.Frame(config.root)
    ttk.Label(frame_saisons, text="Saison :").grid(row=0, column=0, padx=5, pady=8)

    frame_saisons.pack(pady=5)


    # SPECTACLES
    ttk.Label(config.root, text="Liste des spectacles").pack(pady=10)

    frame_spectacles = tk.Frame(config.root, bg="green")
    config.liste_spectacles = config.ItemsTreeview(frame_spectacles,
        columns=["Nom", "Places", "Dem.", "Attr.","Rest."],
        insert_func=lambda s: [s.nom, s.nb_tickets, s.nb_places_demandees(), s.nb_places_attribuees(), s.nb_places_restantes()],
        sizes=[170, 68, 50, 50, 50],
        stretches=[True, False, False, False, False],
        height=7, selectmode="browse",
    )
    config.liste_spectacles.grid(row=0, column=0, sticky=tk.NSEW, padx=(10, 0), pady=10)
    config.liste_spectacles.bind("<Double-Button-1>", fiches.fiche_spec)
    config.liste_spectacles.bind("<Return>", fiches.fiche_spec)

    scroll_spectacles = ttk.Scrollbar(frame_spectacles, orient=tk.VERTICAL, command=config.liste_spectacles.yview)
    config.liste_spectacles.configure(yscrollcommand=scroll_spectacles.set)
    scroll_spectacles.grid(row=0, column=1, sticky=tk.NS, padx=(0, 10), pady=11)

    frame_spectacles.columnconfigure(0, weight=1)
    frame_spectacles.rowconfigure(0, weight=1)
    frame_spectacles.pack(fill=tk.BOTH, padx=20, pady=5, expand=True)


    # CLIENTS
    ttk.Label(config.root, text="Liste des élèves").pack(pady=10)

    frame_clients = tk.Frame(config.root, bg="yellow")
    config.liste_clients = config.ItemsTreeview(frame_clients,
        columns=["Nom", "Promo", "Dem.", "Attr.","Mécont."],
        insert_func=lambda c: [c.nomprenom, c.promo or c.autre, c.nb_places_demandees(), c.nb_places_attribuees(), round(c.mecontentement or 0, 3)],
        sizes=[160, 60, 50, 50, 68],
        stretches=[True, False, False, False, False],
        filter_column="Nom",
        height=7, selectmode="browse",
    )
    config.liste_clients.grid(row=1, column=0, sticky=tk.NSEW, padx=(10, 0), pady=(0, 10))
    config.liste_clients.bind("<Double-Button-1>", fiches.fiche_client)
    config.liste_clients.bind("<Return>", fiches.fiche_client)

    recherche_client = ttk.Entry(frame_clients, validate="key", validatecommand=(config.liste_clients.validatecommand, "%P"))
    recherche_client.grid(row=0, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=10)

    scroll_clients = ttk.Scrollbar(frame_clients, orient=tk.VERTICAL, command=config.liste_clients.yview)
    config.liste_clients.configure(yscrollcommand=scroll_clients.set)
    scroll_clients.grid(row=1, column=1, sticky=tk.NS, padx=(0, 10), pady=(0, 10))

    frame_clients.columnconfigure(0, weight=1)
    frame_clients.rowconfigure(1, weight=1)
    frame_clients.pack(fill=tk.BOTH, padx=20, pady=(5, 20), expand=True)


    #------------------------- MENU FENÊTRE PRINCIPALE -------------------------

    menubar = tk.Menu(config.root)

    menu_fichier = tk.Menu(menubar, tearoff=False)
    menu_fichier.add_command(label="Actualiser", command=config.refresh_listes)
    menu_fichier.add_command(label="Reconnexion", command=fichier.reconnect)
    menu_fichier.add_separator()
    menu_fichier.add_command(label="Sauvegarder les données", command=fichier.upload_all)
    menu_fichier.add_separator()
    menu_fichier.add_command(label="Paramètres", command=fichier.parametres)
    menu_fichier.add_command(label="Quitter", command=config.root.quit)
    menubar.add_cascade(label="Fichier", menu=menu_fichier)

    menubar.add_command(label="Suivi de l'attribution", command=attribution.suivi_process)

    menu_exporter = tk.Menu(menubar, tearoff=False)
    menu_exporter.add_command(label="Exporter les fiches spectacles", command=exportation.exporter_fiches_spectacles)
    menu_exporter.add_command(label="Exporter les fiches élèves", command=exportation.exporter_fiches_eleves)
    menubar.add_cascade(label="Exporter", menu=menu_exporter)

    menu_publier = tk.Menu(menubar, tearoff=False)
    menu_publier.add_command(label="Les fiches élèves sur le serveur", command=publication.publier_fiches_serveur)
    menu_publier.add_command(label="(puis) Envoyer les fiches par mail", command=publication.envoi_fiches_mail)
    menubar.add_cascade(label="Publier", menu=menu_publier)

    config.root.configure(menu=menubar)
    config.root.update()


#-------------------------------- DÉVEROUILLAGE --------------------------------

def unlock():
    PROGRAM_PASSWORD_HASH = config.data.get("PROGRAM_PASSWORD_HASH")
    assert PROGRAM_PASSWORD_HASH, f"PROGRAM_PASSWORD_HASH introuvable"

    encryption_table = config.data.get("_encryption_table")         # Dictionnaire paramètre à décrypter: nom une fois décrypté
    assert encryption_table, f"encryption_table introuvable"

    ok = False
    while not ok:
        pwd = tk.simpledialog.askstring(title=config.TITLE, prompt="Mot de passe :", show='*')
        if pwd is None:     # Appui sur Annuler
            return False
        elif tools.hash(pwd) == PROGRAM_PASSWORD_HASH:
            ok = True
            for encrname, name in encryption_table.items():
                encrypted = config.data.get(encrname)                       # Paramètre chiffré
                assert encrypted, f"{encrname} introuvable"
                setattr(config, name, tools.decrypt(pwd, encrypted))        # On déchiffre tous les paramètres confidentiels avec le mot de passe en clair
            del pwd         # On supprime explicitement le mot de passe en clair, dans le doute
        else:
            retry = tk.messagebox.askretrycancel(title=config.TITLE, message="Mot de passe incorrect :(")
            if not retry:       # Appui sur Annuler
                return False

    return ok


#-------------------------- CONNEXION AU SERVEUR ---------------------------

def connect():
    """Connexion au serveur"""
    with config.ContextPopup(config.root, "Connexion au serveur..."):
        try:
            bdd.connect()
        except Exception as exc:
            raise RuntimeError(f"Erreur de connexion BDD : {exc}") from exc

        assert bdd.session, "Erreur de connexion BDD : impossible de démarrer une session"
        assert bdd.tables, "Erreur de connexion BDD : aucune table trouvée"


#--------------------------- CHARGEMENT DONNÉES ----------------------------

def load(saison, reloading=False):
    """Charge la saison <saison>"""
    if reloading:
        if tk.messagebox.askokcancel(title=f"Charger {saison.nom} ?", message="Toutes les modifications d'attributions non envoyées seront perdues."):
            # On efface les listes
            config.liste_spectacles.reset()
            config.liste_clients.reset()
            # On ferme la fenêtre de suivi de l'attribution si elle est ouverte
            if config.fen_suivi and config.fen_suivi.winfo_exists():
                config.fen_suivi.destroy()
        else:
            return

    with config.ContextPopup(config.root, "Récupération des données..."):
        config.saison = saison
        config.init_var_glob_saison()

        try:
            bdd.session.query(bdd.tables["salles"]).all()     # On ping un truc random pour "réveiller" la session (c'est un peu de la sorcellerie mais ça marche... ah on me fait signe que non)
        except bdd.SQLAlchemyError:
            bdd.session.rollback()          # Si erreur BDD, toujours rollback dans le doute

        # Récupération des salles
        salles_bdd = bdd.session.query(bdd.tables["salles"]).all()

        # Récupération des spectacles de la saison
        spectacles_bdd = bdd.session.query(bdd.tables["spectacles"]).filter_by(saison_id=saison.id).all()
        # Récupération des voeux & attributions pour ces spectacles
        voeux_bdd = bdd.session.query(bdd.tables["voeux"]).filter(bdd.tables["voeux"].spectacle_id.in_([spectacle.id for spectacle in spectacles_bdd])).all()
        # Récupération des clients liés à ces voeux
        clients_bdd = bdd.session.query(bdd.tables["clients"]).filter(bdd.tables["clients"].id.in_([voeu.client_id for voeu in voeux_bdd])).all()
        # Récupération des participations de ces clients à cette saison
        participations_bdd = bdd.session.query(bdd.tables["participations"]).filter(bdd.tables["participations"].client_id.in_([client.id for client in clients_bdd])).filter_by(saison_id=config.saison.id).all()

        # Passage aux objets enrichis (dans cet ordre, car classes.Voeu() a besoin de config.clients et config.spectacles)
        config.salles = [classes.Salle(salle) for salle in salles_bdd]
        config.spectacles = [classes.Spectacle(spectacle) for spectacle in spectacles_bdd]
        config.clients = [classes.Client(client) for client in clients_bdd]
        config.voeux = [classes.Voeu(voeu) for voeu in voeux_bdd]
        config.participations = [classes.Participation(partic) for partic in participations_bdd]

        # Remplissage des treeviews
        config.liste_spectacles.insert(*config.spectacles)
        config.liste_clients.insert(*config.clients)
        config.liste_clients.sort("Nom")

        # Vérification des priorités
        for client in config.clients:
            client.verif_priorites()

        # Détection si tous les mécontentements ont déjà été initialisés précédemment
        if all(client.saison_actuelle_mec == saison.id for client in config.clients):
            config.init_mecontentement_done = True

    if assistant.step == 2:
        assistant.step3()


def load_saisons_and_current():
    # Récupération des saisons, détection saison en cours
    bdd_saisons = bdd.session.query(bdd.tables["saisons"]).all()
    config.saisons = [classes.Saison(saison) for saison in bdd_saisons]
    config.saison = max(config.saisons, key=lambda s:s.debut)


def build_saisons_menu():
    global frame_saisons

    # Création menu changement saison
    saisons_dropdown = SaisonMenu(frame_saisons, *config.saisons)
    saisons_dropdown.set(config.saison)
    saisons_dropdown.grid(row=0, column=1, pady=5)
    ttk.Button(frame_saisons, text="Charger", command=lambda: load(saisons_dropdown.get(), True)).grid(row=0, column=2, padx=5, pady=5)


def toogle_menubar(activate=True):
    global menubar

    # nb_menus = len(menubar.winfo_children())      # Ça marche pas du tout, nik
    for i_menu in range(1, 5):      # Vraiment le jour ou je trouve qui a codé Tk ça va très mal se passer, on est pas dans Matlab ici merde
        menubar.entryconfig(i_menu, state=tk.ACTIVE if activate else tk.DISABLED)
