import math

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from . import config, dataclasses, tools, bdd, assistant


def parametres():
    fen_param = config.Toplevel()
    fen_param.resizable(False, False)

    haut = tk.Frame(fen_param)
    promo_frame = tk.LabelFrame(haut, text="Promotion actuelle")
    malus_frame = tk.LabelFrame(haut, text="Malus de mécontentement")

    promo_spinbox = ttk.Spinbox(promo_frame, width=5, format="%.0f", from_=1, to=math.inf)

    labels = ["Malus 1A",       "Malus 2A",         "Malus 3A",         "Malus 4A",         "Malus autres"    ]
    values = [config.bonus_1A,  config.bonus_2A,    config.bonus_3A,    config.bonus_4A,    config.bonus_autre]
    spinboxes = [ttk.Spinbox(malus_frame, width=6, increment=0.1, from_=-math.inf, to=math.inf) for i in range(5)]

    def reset():
        promo_spinbox.set(config.promo_1A)
        for sb, val in zip(spinboxes, values):
            sb.set(val)

    def valider(event=None):
        config.promo_1A = int(promo_spinbox.get() or config.promo_1A)
        config.bonus_1A, config.bonus_2A, config.bonus_3A, config.bonus_4A, config.bonus_autre = [float(sb.get() or defval) for sb, defval in zip(spinboxes, values)]
        fen_param.destroy()
        if assistant.step == 5:
            assistant.step6()

    tools.labels_grid(promo_frame, [["Actuellement en 1A :", promo_spinbox]], padx=5, pady=2)
    tools.labels_grid(malus_frame, zip(labels, spinboxes), padx=5, pady=2)

    reset()
    tools.labels_grid(haut, [[promo_frame, malus_frame]], padx=10, pady=10)
    haut.pack()

    bas = ttk.Frame(fen_param)
    ttk.Button(bas, text="Annuler", command=fen_param.destroy).grid(row=0, column=0, padx=2)
    ttk.Button(bas, text="Valeurs actuelles", command=reset).grid(row=0, column=1, padx=2)
    ttk.Button(bas, text="Valider", command=valider).grid(row=0, column=2, padx=2)
    bas.pack(padx=2, pady=5)

    if assistant.step == 4:
        assistant.step5()


# def reconnect():
#     bdd.session.rollback()
#     tk.messagebox.showinfo(title="Réparation de la connexion", message="La session a été réinitialisée")


# J'ai pensé à une structure... pyramidale
def upload_all():
    if tk.messagebox.askokcancel(title="Sauvegarder les données ?", message="Les données vont être exportées sur le serveur.\nToute attribution précédement envoyée sera écrasée."):
        with config.ContextPopup(config.root, "Sauvegarde en cours..."):
            bdd.session.commit()        # Toutes les modifications sont maintenant flag à la volée

        tk.messagebox.showinfo(title="Sauvegarde", message="Données sauvegardées :\n"
            f"  - {len(dataclasses.DataClass.pending_adds)} entrée(s) ajoutée(s)\n"
            f"  - {len(dataclasses.DataClass.pending_modifs)} attribut(s) modifié(s)\n\n"
            "(vérifier quand même en rechargeant la saison)"
        )

        dataclasses.DataClass.pending_adds = []
        dataclasses.DataClass.pending_modifs = []

        if assistant.step == 11:
            assistant.step12()


def quitter():
    if dataclasses.DataClass.pending_adds or dataclasses.DataClass.pending_modifs:      # Modifications non enregistrées
        really = tk.messagebox.askokcancel(title="Modifications non sauvegardées", message="Les actions suivantes n'ont pas été sauvegardées en base :\n"
            f"  - {len(dataclasses.DataClass.pending_adds)} nouvelle(s) entrée(s) : {', '.join(str(pend) for pend in dataclasses.DataClass.pending_adds)}\n"
            f"  - {len(dataclasses.DataClass.pending_modifs)} modification(s) d'attribut(s) : {', '.join('{}.{} = {}'.format(*pend) for pend in dataclasses.DataClass.pending_modifs)}\n\n"
            "Quitter malgré tout ?"
        )
        if really:
            config.root.quit()
    else:
        config.root.quit()
