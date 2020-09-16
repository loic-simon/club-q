import sys
import os
import traceback
import datetime
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from blocs import config, bdd, main, assistant


version = "2.0.1"

welcome_text = """Bienvenue dans le programme d'attribution des places du Club Q !

Un assistant est disponible pour aider à prendre en main le programme et conseillé pour commencer une attribution.
Pour reprendre la dernière attribution sauvegardée, l'interface d'attribution principale peut être affichée directement.

Ce programme se récupère les données de bde-espci.fr, et dépend donc d'un accès à Internet et de la disponibilité du site.
Un mot de passe sera demandé avant tout accès aux données.

Bonne attribution !
Loïc 137 pour les GRI"""


#---------------------------------- ASSISTANT ----------------------------------

def go_assistant():
    """Lance l'assistant d'attribution"""
    loader_frame.pack_forget()              # Efface la fenêtre de lancement
    main.build_root()                       # Construit l'interface (frames & menu)
    main.toogle_menubar(activate=False)     # Désactive le menu

    assistant.create()
    assistant.step0()


#-------------------------------- ACCÈS DIRECT ---------------------------------

def go_direct():
    """Charge l'interface principale"""
    ok = main.unlock()                      # Demande le mot de passe
    if not ok:
        return
        
    loader_frame.pack_forget()              # Efface la fenêtre de lancement
    main.build_root()                       # Construit l'interface (frames & menu)
    main.toogle_menubar(activate=False)     # Désactive le menu

    main.connect()                          # Connexion aux bdd bde-espci.fr
    main.load_saisons_and_current()         # Charge config.saisons, config.saison (= saison la plus récente)
    main.load(config.saison)                # Charge config.spectacles, config.voeux, config.clients et remplissage Treeviews
    main.build_saisons_menu()               # Menu de changement de saison

    main.toogle_menubar(activate=True)      # Réactive le menu


#--------------------------- GESTION DES EXCEPTIONS ----------------------------

def report_exc(exc, val, tb):
    """Affiche un pop-up (et rollback BDD si nécessaire) en cas d'erreur"""
    sys.stderr.write(f"--- {datetime.datetime.now()} Exception :\n{traceback.format_exc()}")    # log système
    if issubclass(exc, bdd.SQLAlchemyError):
        bdd.session.rollback()          # Si erreur BDD, toujours rollback dans le doute
        tk.messagebox.showerror(title=f"{config.TITLE} - {exc.__name__}", message=f"Exception lors de l'accès aux données. Cela arrive souvent lorsque du temps passe entre deux appels, une requêtre de reconnexion a été envoyée.\n\nRefaire l'action voulue, ça devrait marcher !")
    elif config.DEBUG:
        tk.messagebox.showerror(title=f"{config.TITLE} - {exc.__name__}", message=f"Exception Python :\n{val}\n\n{traceback.format_exc()}")
    else:
        tk.messagebox.showerror(title=f"{config.TITLE} - {exc.__name__}", message=f"Exception Python :\n{val}")


try:
    #---------------------------- FENÊTRE D'ACCUEIL ----------------------------

    config.root = tk.Tk()       # Fenêtre maître du programme

    config.root.title(config.TITLE)
    config.root.geometry("467x570")
    config.root.minsize(467, 570)
    config.root.iconphoto(True, tk.PhotoImage(file=os.path.join(config.basedir, "resources", "icon_q.png")))
    config.root.report_callback_exception = report_exc

    # Frame de lancement
    loader_frame = ttk.Frame(config.root)

    # Logos et titre
    logo_pc = ImageTk.PhotoImage(Image.open(config.lien_logo_pc).resize((249, 53), Image.ANTIALIAS))
    ttk.Label(loader_frame, image=logo_pc).pack(pady=5)

    ttk.Label(loader_frame, text=f"Programme Club Q – v{version}").pack(pady=0)

    logo_q = ImageTk.PhotoImage(Image.open(config.lien_logo_q).resize((150, 150), Image.ANTIALIAS))
    ttk.Label(loader_frame, image=logo_q).pack(pady=15)

    # Message d'accueil
    tk.Message(loader_frame, text=welcome_text, width=380).pack(pady=15)

    # Boutons
    boutons_frame = ttk.Frame(loader_frame)
    ttk.Button(boutons_frame, text="Assistant d'attribution", command=go_assistant).grid(row=0, column=0, padx=5)
    ttk.Button(boutons_frame, text="Accès direct", command=go_direct).grid(row=0, column=1, padx=5)
    ttk.Button(boutons_frame, text="Quitter", command=config.root.quit).grid(row=0, column=2, padx=5)
    boutons_frame.pack(pady=10)

    loader_frame.pack(padx=0)


    #---------------------------- BOUCLE PRINCIPALE ----------------------------

    if config.DEBUG:
        print("Entrée dans la mainloop")
    config.root.mainloop()


except Exception as exc:        # Exception pendant l'initialisation (avant le mainloop)
    report_exc(type(exc), exc, exc.__traceback__)
