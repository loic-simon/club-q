import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import ftplib

from . import config, tools, sendmail, exportation


class MyFTP(ftplib.FTP):
    def __init__(self, *args, **kwargs):
        """Initialises self."""
        super().__init__(config.FTP_HOST, user=config.FTP_USER, passwd=config.FTP_PASSWORD, *args, **kwargs)

    def upload(self, filepath, name):
        """Envoie le fichier dans <filepath> sur le serveur, dans le répertoire courant, sous le nom <name>"""
        with open(filepath, "rb") as file:
            self.storbinary(f"STOR {name}", file)

    def download(self, name, filepath):
        """Télécharge le fichier <name> du répertoire courant du serveur et l'enregistre dans <filepath>"""
        with open(filepath, "wb") as file:
            self.retrbinary(f"RETR {name}", file.write)



def publier_fiches_serveur():
    if tk.messagebox.askokcancel(title="Publication sur le serveur", message="Générer les fiches élèves et les publier sur bde-espci.fr ?"):
        # Génération des fiches
        lien_dossier = os.path.join(config.tempdir, "fiches_clients")
        try:
            os.mkdir(lien_dossier)
        except FileExistsError:                             # Si le dossier temporaire fiches_clients existe déjà,
            for file in os.listdir(lien_dossier):               # On le vide
                os.remove(os.path.join(lien_dossier, file))

        contents = {}       # Dictionnaire id: nom du fichier
        with config.ContextPopup(config.root, "Génération des fiches...") as popup:
            N_pdf = len(config.clients)
            for i_pdf, client in enumerate(config.clients):     # On exporte toutes les fiches
                filepath = exportation.pdf_client(client, lien_dossier, open_pdf=False, i_pdf=i_pdf, N_pdf=N_pdf, popup=popup)
                contents[client.id] = os.path.basename(filepath)

        # Enregistre le lien client -> PDF (pour réutilisation ultérieure, genre envoi par mail)
        lien_contents = os.path.join(lien_dossier, "contents.json")
        with open(lien_contents, "w") as fich:
            json.dump(contents, fich)


        with config.ContextPopup(config.root, "Envoi sur le serveur...") as popup, MyFTP() as ftp:
            ftp.cwd("fiches_clients")               # Changement répertoire courant
            dirs = ftp.nlst()                       # Dossiers de saison
            saison_dir = str(config.saison.id)      # Nom du dossier de la saison concernée
            if not saison_dir in dirs:
                ftp.mkd(saison_dir)
            ftp.cwd(saison_dir)                     # On se positionne dans notre dossier de saison

            # Upload contents.json
            ftp.upload(lien_contents, "contents.json")

            # Upload fiches
            for i_file, (id, filename) in enumerate(contents.items()):
                popup.edit(f"Envoi fiche n°{i_file+1}/{N_pdf}...")
                ftp.upload(os.path.join(lien_dossier, filename), filename)
                participation = tools.get_or_none(config.participations, client_id=id, saison_id=config.saison.id)
                if participation:
                    participation.fiche_path = "/".join("fiches_clients", saison_dir, filaname)     # pas os.path.join parce que pour utilisation par PHP (et met des \\ si sous Windows)

        tk.messagebox.showinfo(title="Publication sur le serveur", message="Fiches publiées !")



def envoi_fiches_mail():
    # Récupération des fiches
    lien_dossier = os.path.join(config.tempdir, "fiches_clients")
    lien_contents = os.path.join(lien_dossier, "contents.json")

    contents = None
    if os.path.exists(lien_contents):
        with open(lien_contents, "r") as fich:
            contents = json.load(fich)

    else:       # Fiches non trouvées en local
        try:
            os.mkdir(lien_dossier)
        except FileExistsError:                             # Si le dossier temporaire fiches_clients existe déjà (mais sans config.json),
            for file in os.listdir(lien_dossier):               # On le vide
                os.remove(os.path.join(lien_dossier, file))

        with config.ContextPopup(config.root, "Récupération des fiches...") as popup, MyFTP() as ftp:
            ftp.cwd("fiches_clients")               # Changement répertoire courant
            dirs = ftp.nlst()                       # Dossiers de saison
            saison_dir = str(config.saison.id)      # Nom du dossier de la saison concernée
            if saison_dir in dirs:
                ftp.cwd(saison_dir)                 # On se positionne dans notre dossier de saison
                files = ftp.nlst()

                # Download contents.json
                filename = os.path.basename(lien_contents)
                if filename in files:
                    ftp.download("contents.json", lien_contents)

                    with open(lien_contents, "r") as fich:
                        contents = json.load(fich)

                    # Download fiches
                    N_pdf = len(contents)
                    for i_file, filename in enumerate(contents.values()):
                        popup.edit(f"Récupération fiche n°{i_file+1}/{N_pdf}...")
                        if filename in files:
                            ftp.download(filename, os.path.join(lien_dossier, filename))

    if contents is None:
        tk.messagebox.showerror(title="Fiches non trouvées", message="Fiches individuelles élèves non trouvées. Il faut d'abord publier les fiches sur le serveur avant de pouvoir les envoyer par mail.")
        return

    if len(contents) < len(config.clients):         # Il manque des fiches
        if not tk.messagebox.askokcancel(title="Fiches incomplètes", message=f"Seulement {len(contents)} fiches ont été trouvées sur le serveur, pour {len(config.clients)} élèves enregistrés. Continuer malgré tout ?"):
            return

    # Envoi par mail
    dict_clients_fichepaths = {}
    for strid, filename in contents.items():
        client = tools.get(config.clients, id=int(strid))
        dict_clients_fichepaths[client] = os.path.join(lien_dossier, filename)

    personaliser_puis_envoyer_mail(dict_clients_fichepaths)        # Récupère fromnane, objet, corps... et appelle la fonction d'envoi



fromname = "Club Q"
replyto = "camille.georges@espci.psl.eu"
objet = "Attribution Club Q"
corps = """Bonjour {Prenom} {Nom},

Tu trouveras ci-joint la fiche récapitulant tes places pour cette saison du club Q.
Merci de payer la somme indiquée sur cette fiche avant le <XXX> :
<(informations de paiement)>

En cas de soucis, répond simplement à cet email.

Bonne saison !
L'équipe du Club Q"""


anchors = {
    "{Nom}": lambda c: c.nom,
    "{Prenom}": lambda c: c.prenom,
    "{NOM}": lambda c: c.nom.upper(),
    "{email}": lambda c: c.email,
    "{a_payer}": lambda c: f"{c.a_payer} €",
    "{promo}": lambda c: c.promo,
}

def customize(text, client):
    for anchor, func in anchors.items():
        text = text.replace(anchor, str(func(client)))
    return text



def personaliser_puis_envoyer_mail(dict_clients_fichepaths):
    global fromname, objet, replyto, corps

    fen_perso = config.Toplevel()
    fen_perso.title("Envoi de mail")

    frame_from = ttk.Frame(fen_perso)
    ttk.Label(frame_from, text="De : ").grid(row=0, column=0)
    fromname_entry = ttk.Entry(frame_from)
    fromname_entry.grid(row=0, column=1, sticky=tk.EW)
    fromname_entry.insert(0, fromname)
    ttk.Label(frame_from, text=f" <{config.MAIL_SENDER}>").grid(row=0, column=2)
    frame_from.columnconfigure(1, weight=1)
    frame_from.pack(padx=10, pady=10, fill=tk.X)

    frame_replyto = ttk.Frame(fen_perso)
    ttk.Label(frame_replyto, text="Adresse de réponse : ").pack(side=tk.LEFT)
    replyto_entry = ttk.Entry(frame_replyto)
    replyto_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    replyto_entry.insert(0, replyto)
    frame_replyto.pack(padx=10, fill=tk.X, expand=True)

    frame_objet = ttk.Frame(fen_perso)
    ttk.Label(frame_objet, text="Objet : ").pack(side=tk.LEFT)
    objet_entry = ttk.Entry(frame_objet)
    objet_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    objet_entry.insert(0, objet)
    frame_objet.pack(padx=10, pady=10, fill=tk.X)

    ttk.Label(fen_perso, text="Corps du message :").pack(padx=10, pady=5, fill=tk.X)
    corps_entry = tk.Text(fen_perso)
    corps_entry.pack(padx=10, pady=5, ipadx=5, ipady=5, fill=tk.BOTH)
    corps_entry.insert(tk.INSERT, corps)
    ttk.Label(fen_perso, text=f"(utiliser {', '.join(anchors)} pour insérer une valeur spécifique à l'élève)").pack(padx=10, pady=5, fill=tk.X)

    def envoyer():
        global fromname, objet, replyto, corps
        fromname = fromname_entry.get()
        objet = objet_entry.get()
        replyto = replyto_entry.get()
        corps = corps_entry.get("1.0", "end-1c")

        login_et_envoi_mails(dict_clients_fichepaths, fen_perso)

    def previsualiser():
        some_client, some_filepath = next(iter(dict_clients_fichepaths.items()))
        this_objet = customize(objet_entry.get(), some_client)
        this_corps = customize(corps_entry.get("1.0", "end-1c"), some_client)
        this_pj = os.path.basename(some_filepath)
        this_pjsize = os.path.getsize(some_filepath)
        this_to = f"{some_client.nomprenom} <{some_client.email}>"
        tk.messagebox.showinfo(title="Prévisualisation", message=f"De : {fromname_entry.get()} <{config.MAIL_SENDER}>\nÀ : {this_to}\nRépondre à : {replyto_entry.get()}\nObjet : {this_objet}\nPièce jointe : {this_pj} ({this_pjsize/1000:.2f} Ko)\n\n{this_corps}", parent=fen_perso)

    frame_boutons = ttk.Frame(fen_perso)
    ttk.Button(frame_boutons, text="Prévisualiser", command=previsualiser).grid(row=0, column=0, padx=10, pady=5)
    ttk.Button(frame_boutons, text="Envoyer", command=envoyer).grid(row=0, column=1, padx=10, pady=5)
    ttk.Button(frame_boutons, text="Annuler", command=fen_perso.destroy).grid(row=0, column=2, padx=10, pady=5)
    frame_boutons.pack(padx=10, pady=10)



def login_et_envoi_mails(dict_clients_fichepaths, fen_perso):
    if config.MAIL_LOGIN:               # Login déjà enregistré
        with config.ContextPopup(fen_perso, "Connexion au serveur...") as popup:
            with sendmail.ConnectPC(config.MAIL_LOGIN, config.MAIL_PASSWORD, verbose=config.DEBUG) as server:
                envoi_mails(dict_clients_fichepaths, server, popup)
            # fen_perso.destroy()

    else:
        fen_login = config.Toplevel()
        fen_login.title("Connexion ESPCI")
        fen_login.resizable(False, False)

        tk.Message(fen_login, text=f"L'envoi de mails depuis l'adresse {config.MAIL_SENDER} nécessite la connexion à un compte ESPCI valide (n'importe lequel).\n\nInformations de connexion (les mêmes que pour accéder à l'Intranet) :").pack(padx=10, pady=10)

        frame_entries = ttk.Frame(fen_login)
        ttk.Label(frame_entries, text="Identifiant :").grid(row=0, column=0, padx=5, pady=2)
        login_entry = ttk.Entry(frame_entries)
        login_entry.grid(row=0, column=1, padx=5, pady=10)
        ttk.Label(frame_entries, text="Mot de passe :").grid(row=1, column=0, padx=5, pady=2)
        pwd_entry = ttk.Entry(frame_entries, show="*")
        pwd_entry.grid(row=1, column=1, padx=5, pady=10)
        frame_entries.pack(padx=5, pady=10)

        def valider():
            login = login_entry.get()
            pwd = pwd_entry.get()
            with config.ContextPopup(fen_perso, "Connexion au serveur...") as popup:
                with sendmail.ConnectPC(login, pwd, verbose=config.DEBUG) as server:
                    # Si pas d'exception levée, connexion OK
                    config.MAIL_LOGIN = login
                    config.MAIL_PASSWORD = pwd
                    fen_login.destroy()
                    envoi_mails(dict_clients_fichepaths, server, popup)
                # fen_perso.destroy()

        ttk.Button(fen_login, text="Valider", command=valider).pack(padx=10, pady=10)


def envoi_mails(dict_clients_fichepaths, server, popup):         # (enfin !)
    sender = f"{fromname} <{config.MAIL_SENDER}>"
    N_mails = len(dict_clients_fichepaths)

    for i_mail, (client, filepath) in enumerate(dict_clients_fichepaths.items()):
        popup.edit(f"Envoi mail {i_mail+1}/{N_mails}...")
        if client.email and "@" in client.email:        # Flemme de vérifier rigoureusement que l'adresse est syntaxiquement correcte
            this_dests = [client.email]
            this_objet = customize(objet, client)
            this_corps = customize(corps, client)

            msg = sendmail.Message(sender, this_dests, this_objet, this_corps, replyto)
            msg.join(filepath)
            try:
                msg.send(server, verbose=config.DEBUG)
            except Exception as exc:
                tk.messagebox.showerror(title="Erreur lors de l'envoi", message=f"Exception lors de l'envoi à {client.nomprenom} :\n{exc}\n\nEmail non envoyé, passage au suivant")

        else:
            tk.messagebox.showwarning(title="Adresse incorrecte", message=f"Adresse email de {client.nomprenom} non renseignée ou incorrecte :\n{client.email}\n\nEmail non envoyé, passage au suivant")

    tk.messagebox.showinfo(title="Envoi des fiches par mail", message="Messages envoyés !")
