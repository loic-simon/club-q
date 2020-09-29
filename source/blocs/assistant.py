# Assistant d'attribution

import traceback
import platform
import tkinter as tk
from tkinter import ttk

from . import config, main


step = None             # Étape actuelle de l'assistant d'attribution

assistant = None
consigne = None
footer = None
suivant_button = None
skip_button = None

size = "400x250"
suivant_text = "Suivant >"


def create():
    global assistant, consigne, footer, suivant_button, skip_button, step

    assistant = config.Toplevel()
    assistant.title("Assistant d'attribution")
    assistant.geometry(size)
    assistant.resizable(False, False)

    def confirm_close():
        global assistant, step

        if tk.messagebox.askokcancel(title="Fermeture", message="Quitter l'assistant d'attribution ? Il est impossible de le réouvrir sans relancer le programme.", parent=assistant):
            assistant.destroy()
            assistant = None
            if step < 1:            # Si on quitte en cours de route, assure que le programme soit utilisable
                if not main.unlock():
                    config.root.quit()
            if step < 2:
                main.connect()
                main.load_saisons_and_current()
                main.build_saisons_menu()
            if step < 3:
                step = None
                main.load(config.saison)
                main.toogle_menubar(activate=True)

    assistant.protocol("WM_DELETE_WINDOW", confirm_close)        # Demande confirmation à la fermeture de la fenêtre


    ttk.Style().configure('My.TFrame', background="#64b9e9")
    footer = ttk.Frame(assistant, style='My.TFrame')

    suivant_button = ttk.Button(footer, text=suivant_text)
    suivant_button.pack(side=tk.RIGHT, padx=10, pady=7)

    skip_button = ttk.Button(footer, text="Passer")

    footer.pack(side=tk.BOTTOM, fill=tk.X)
    footer.configure()


    consigne = tk.Message(assistant, text="""Initialisation...""", width=370)
    consigne.pack(pady=10, fill=tk.X)



def step0():
    global step, assistant, consigne
    step = 0

    consigne.configure(text="""Bienvenue dans l'Assistant d'attribution ! Il a pour but de guider les membres du Club Q, même néophytes, à travers tout le processus d'attribution des places. Laissez-vous guider !

La fenêtre de départ affiche maintenant divers éléments, dont les listes des spectacles et des élèves, qui vont se remplir dans les prochaines étapes.

Le programme va commencer par demander le mot de passe pour déverouiller l'accès aux données (que vous connaissez, normalement. Sinon, c'est pas de chance)""")

    def unlock_and_continue():
        ok = main.unlock()                  # Demande le mot de passe
        if ok:
            step1()

    suivant_button.configure(command=unlock_and_continue)
    assistant.lift()



def step1():
    global step, assistant, consigne, suivant_button
    step = 1

    consigne.configure(text="""Parfait !

Le programme va maintenant se connecter au serveur et récupérer la liste des différentes saisons crées.""")

    def next():
        try:
            main.connect()
            main.load_saisons_and_current()         # Charge config.saisons, config.saison (= saison la plus récente)
            main.build_saisons_menu()               # Menu de changement de saison
        except RuntimeError as exc:
            step2_error(type(exc), exc, exc.__traceback__)
        else:
            step2()

    suivant_button.configure(command=next)
    assistant.lift()        # Remet l'assistant au premier plan




def step2():
    global step, assistant, consigne, suivant_button
    step = 2

    consigne.configure(text="""C'est tout bon !

La saison sélectionnée est maintenant affichée en haut de la fenêtre principale. Par défaut, la saison démarrant en dernier est sélectionnée, mais on peut changer à tout moment en cliquant sur la liste défilante.

Une fois la bonne saison sélectionnée, appuyer sur « Charger ».
(Le message d'avertissement est générique, ne pas en tenir compte dans le cadre de cet assistant)""")

    suivant_button.configure(text="(Cliquer sur « Charger »)", state=tk.DISABLED)
    # suivant_button.configure(command=lambda e: main.load(config.saison))
    assistant.lift()        # Remet l'assistant au premier plan




def step3():
    global step, assistant, consigne, suivant_button
    step = 3

    main.toogle_menubar(activate=True)

    consigne.configure(text="""Bien, les spectacles de la saison devraient maintenant apparaître dans la zone du haut, et les élèves ayant émis des voeux cette saison dans la zone du bas. Un champ de recherche est disponible pour les élèves.

Les listes sont triables en cliquant sur les noms de colonnes, et un double clic sur chaque élément ouvre une fiche plus détaillée, permettant de voir les voeux et attributions et de faire des actions manuelles.

Le bouton « Accès direct » au lancement du programme amène directement à cette étape.""")

    suivant_button.configure(text=suivant_text, state=tk.NORMAL)
    suivant_button.configure(command=step4)
    assistant.lift()        # Remet l'assistant au premier plan




def step4():
    global step, assistant, consigne, footer, suivant_button, skip_button
    step = 4

    consigne.configure(text="""Pour nous, il est temps de commencer l'attribution proprement dite !

La première chose à faire est de vérifier les paramètres généraux du programme : pour cela, ouvrir le menu « Fichier » puis « Paramètres ».""")

    suivant_button.configure(text="(Cliquer sur « Fichier » puis « Paramètres »)", state=tk.DISABLED)

    skip_button.pack(side=tk.RIGHT, padx=10, pady=7)
    skip_button.configure(command=step6)
    assistant.lift()        # Remet l'assistant au premier plan



def step5():
    global step, assistant, consigne, suivant_button, skip_button
    step = 5

    if skip_button.winfo_ismapped():
        skip_button.pack_forget()

    consigne.configure(text="""Modifier les paramètres si nécessaires.

Les malus permettent de prioritiser certaines promotions dans l'attribution des places, en ajoutant le malus indiqué à leur mécontentement initial.

Une fois les paramètres renseignés, appuyer sur « Valider ».""")

    suivant_button.configure(text="(Appuyer sur « Valider »)", state=tk.DISABLED)
    assistant.lift()        # Remet l'assistant au premier plan



def step6():
    global step, assistant, consigne, suivant_button, skip_button
    step = 6

    if skip_button.winfo_ismapped():
        skip_button.pack_forget()

    consigne.configure(text="""Toute la suite se fait via la fenêtre de suivi de l'attribution, qui rassemble toutes les optons utiles (avant disponibles directement dans le menu).""")

    suivant_button.configure(text="(Appuyer sur « Suivi de l'attribution »)", state=tk.DISABLED)
    assistant.lift()        # Remet l'assistant au premier plan



def step6b():
    global step, assistant, consigne, suivant_button
    step = 6.5

    consigne.configure(text="""La première chose à faire est d'initialiser le mécontentement de tous les élèves. Plusieurs composantes sont sommées :
    - Le mécontentement hérité de la saison précédente ;
    - Le mécontentement lié au nombre de voeux (plus l'élève formule de voeux, plus il sera pénalisé) : + 0.9^(Nvoeux - 1) ;
    - Le nombre total de places demandées (à l'inverse, plus un élève demande de places, moins il sera pénalisé) : + 2/Nplaces ;
    - Le bonus/malus selon la promo, vu dans les paramètres ;
    - Le mécontentement lié aux voeux déjà attribués (nul ici normalement, mais permet d'utiliser ce bouton n'importe quand) : - 0.5^priorité par voeu.""")

    suivant_button.configure(text=suivant_text, state=tk.NORMAL)
    suivant_button.configure(command=step7)
    assistant.lift()        # Remet l'assistant au premier plan



def step7():
    global step, assistant, consigne, suivant_button
    step = 7

    consigne.configure(text="""Les mécontentements individuels peuvent ensuite être modifiés arbitrairement dans les fiches des élèves, notemment parce que, pour reprendre le mode d'emploi 134 : « j’ajoutais 1.5 à tous les gens du club Q pour qu’ils partent avec un avantage et soient traités en premier (oui, il faut un peu des privilèges à un moment donné !) » et « (tu peux aussi mettre des valeurs négatives pour les gens que tu n’aimes pas mouahaha) »

Bref, pour le moment l'initialisation se fait en cliquant sur « Initialiser les mécontentements ».""")

    suivant_button.configure(text="(Cliquer sur « Initialiser les mécontentements »)", state=tk.DISABLED)
    assistant.lift()        # Remet l'assistant au premier plan



def step8():
    global step, assistant, consigne, suivant_button, skip_button
    step = 8

    consigne.configure(text="""Voilà qui est fait. Pour y voir plus clair, la liste des élèves peut être triée par mécontentement en cliquant sur le nom de la colonne.

Bon, il est temps de passer aux choses sérieuses. D'abord, attribuons les places « sans conflit » (si il y en a !), c'est-à-dire les spectacles pour lesquels on a plus de places qu'il n'y a de demande : elles sont attribuées automatiquement à tous ceux le souhaitant.

Cela se passe en cliquant sûr « Attribuer les places sans conflit ».""")

    skip_button.pack(side=tk.RIGHT, padx=10, pady=7)
    skip_button.configure(command=step9)
    suivant_button.configure(text="(Cliquer sur « Attribuer les places sans conflit »)", state=tk.DISABLED)
    assistant.lift()        # Remet l'assistant au premier plan




def step9():
    global step, assistant, consigne, suivant_button, skip_button
    step = 9

    if skip_button.winfo_ismapped():
        skip_button.pack_forget()

    consigne.configure(text="""Le troisième bouton, « Effacer toutes les attributions », permet de remttre tous les voeux à 0 places attribuées. Les mécontentements arbitraires ne sont pas impactés : utiliser le bouton « Supprimer mécontentements arbitraires » pour cela.

Le procédé d'attribution consiste maintenant à considérer les voeux émis par ordre de priorité : les premiers voeux d'abord, puis les deuxièmes, etc... jusqu'à que tous les voeux aient été évalués.""")

    suivant_button.configure(text=suivant_text, state=tk.NORMAL)
    suivant_button.configure(command=step10)
    assistant.lift()        # Remet l'assistant au premier plan




def step10():
    global step, assistant, consigne, suivant_button
    step = 10

    consigne.configure(text="""Le tableau sur la droite permet de suivre l'état de l'attribution.

Pour chaque voeu, l'attribution est automatique : les élèves les plus mécontents sont traités en premier, et le maximum de places demandées leur est donné tant que c'est possible.
Si deux élèves ou plus ont le même mécontentement et qu'il n'y a pas assez de places pour tous les satisfaire, une fenêtre apparaîtra pour demander d'attribuer manuellement les places.

Appuyer sur « Attribuer le voeu n° 1 », et ainsi de suite jusqu'à la fin de l'attribution.""")

    suivant_button.configure(text="(Attribuer tous les voeux)", state=tk.DISABLED)
    assistant.lift()        # Remet l'assistant au premier plan







def step11():
    global step, assistant, consigne, suivant_button, skip_button
    step = 11

    consigne.configure(text="""Bon bah voilà, c'est quasiment bon ! Les attributions peuvent être ajustées manuellement à l'envi.

Dernière chose, évidemment : sauvegarder tout ça ! Et oui, pour l'instant rien n'est modifié sur le serveur, et tout est oublié si le programme est fermé / une autre saison est chargée...

Il suffit de cliquer sur « Fichier » / « Sauvegarder les données ». À noter qu'à ce stade, il est quasiment certain qu'une erreur BDD survienne mais pas de panique, il suffit de réessayer et (normalement) ça marche, comme dit dans le message d'erreur ! C'est un peu moche, on essaiera de corriger ça dans les versions futures.""")

    skip_button.pack(side=tk.RIGHT, padx=10, pady=7)
    skip_button.configure(command=step12)
    suivant_button.configure(text="(« Fichier » / « Sauvegarder les données »)", state=tk.DISABLED)
    assistant.lift()        # Remet l'assistant au premier plan



def step12():
    global step, assistant, consigne, suivant_button, skip_button
    step = 12

    if skip_button.winfo_ismapped():
        skip_button.pack_forget()

    consigne.configure(text="""Dernière chose, les fiches PDF élèves / spectacles peuvent être exportées via le menu ad hoc, en sélectionnant simplement le dossier où les stocker.
Les fiches peuvent aussi être exportées individuellement grâce au bouton en bas de la fenêtre élève / spectacle.

L'envoi des PDF sur le serveur et aux élèves par mail (dans cet ordre !) se fait via le menu « Publier ».""")

    suivant_button.configure(text=suivant_text, state=tk.NORMAL)
    suivant_button.configure(command=step13)
    assistant.lift()        # Remet l'assistant au premier plan



def step13():
    global step, assistant, consigne, suivant_button
    step = 13

    consigne.configure(text="""Voilà, c'est tout bon ! Merci d'avoir suivi cet assistant. En cas de questions ou pour quoi que ce soit, ne pas hésiter à contacter les GRI (Loïc 137 ou toute personne ayant repris le programme depuis).

Pour les prochaines attributions, vous pouvez utiliser le bouton « Accès direct », mais cet assistant permet de s'assurer qu'on oublie rien !""")

    suivant_button.configure(text="Terminer", state=tk.NORMAL)
    suivant_button.configure(command=assistant.destroy)
    assistant.lift()        # Remet l'assistant au premier plan





def step2_error(exc, val, traceback_):
    global assistant, footer, consigne, suivant_button

    assistant.bell()
    consigne.configure(text=f"""Le programme n'a pas pu se connecter à bde-espci.fr : « {val} ».

Si l'erreur est compréhensible et résolvable, le faire et réessayer. Dans le cas contraire, vérifier la connexion Internet de l'ordinateur, réessayer dans quelques minutes, puis contacter Loïc 137 (ou toute personnne chargée de la maintenance de ce programme !)""")

    frame_details = ttk.Frame(assistant)
    canvas = tk.Canvas(frame_details)
    scrollbar = ttk.Scrollbar(frame_details, orient=tk.VERTICAL, command=canvas.yview)
    ttk.Style().configure('Details.TFrame', background="#000000")
    subframe = ttk.Frame(canvas, style='Details.TFrame')
    subframe.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox(tk.ALL)))
    canvas.create_window((0, 0), window=subframe, anchor=tk.NW)
    canvas.configure(yscrollcommand=scrollbar.set)
    # Envie de mourir, tk de ses énormes morts
    if platform.system() == "Windows":      # Windows
        assistant.bind("<MouseWheel>", lambda event: canvas.yview_scroll(-event.delta//120, tk.UNITS))
    elif platform.system() == "Darwin":     # macOS
        assistant.bind("<MouseWheel>", lambda event: canvas.yview_scroll(-event.delta, tk.UNITS))
    else:                                   # linux variants
        assistant.bind("<Button-4>", lambda event: canvas.yview_scroll(-event.delta//120, tk.UNITS))
        assistant.bind("<Button-5>", lambda event: canvas.yview_scroll(event.delta//120, tk.UNITS))

    tk.Message(subframe, text=traceback.format_exc(), width=355, font=("Courier", 9), bg="#000000", fg="white").pack(padx=10, pady=5)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


    def hide_details():
        frame_details.pack_forget()
        assistant.geometry(size)
        details_button.configure(text="Afficher les détails", command=show_details)

    def show_details():
        frame_details.pack(padx=0, pady=10)

        assist_h = assistant.winfo_height()
        assist_w = assistant.winfo_width()
        assistant.geometry(f"{assist_w}x{assist_h + 250}")
        details_button.configure(text="Masquer les détails", command=hide_details)


    def retry():
        suivant_button.configure(text="Suivant")
        consigne.configure(text=f"Nouvelle tentative...")
        frame_details.pack_forget()
        details_button.pack_forget()
        assistant.geometry(size)
        try:
            main.connect()
            main.load_saisons_and_current()         # Charge config.saisons, config.saison (= saison la plus récente)
            main.build_saisons_menu()               # Menu de changement de saison
        except RuntimeError as exc:
            step2_error(type(exc), exc, exc.__traceback__)
        else:
            step2()

    suivant_button.configure(text="Réessayer", command=retry)
    details_button = ttk.Button(footer, text="Afficher les détails", command=show_details)
    details_button.pack(side=tk.RIGHT, padx=10, pady=7)
    assistant.lift()        # Remet l'assistant au premier plan
