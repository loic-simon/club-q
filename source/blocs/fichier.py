import math

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from . import config, tools, bdd, assistant


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


def reconnect():
    bdd.session.rollback()
    tk.messagebox.showinfo(title="Réparation de la connexion", message="La session a été réinitialisée")


# J'ai pensé à une structure... pyramidale
def upload_all():
    if tk.messagebox.askokcancel(title="Sauvegarder les données ?", message="Les données vont être exportées sur le serveur.\nToute attribution précédement envoyée sera écrasée."):
        with config.ContextPopup(config.root, "Sauvegarde en cours..."):
            for item in config.clients + config.spectacles + config.voeux:
                for col in item.bdd_cols:                                   # Pour chaque colonne de la table,
                    if not col.startswith("_"):                                 # (chaque vraie colonne),
                        if getattr(item, col) != getattr(item.bdd_item, col):       # Si on a modifié la valeur,
                            if config.DEBUG:
                                print(f"> MODIFIED < : {item}.{col} = {getattr(item, col)} (avant {getattr(item.bdd_item, col)})")

                            # (désolé)
                            setattr(item.bdd_item, col, getattr(item, col))             # on actualise l'argument du vrai item-bdd (qui peut être uploadé)
                            bdd.flag_modified(item.bdd_item, col)                       # et on flag pour modification

        bdd.session.commit()

        tk.messagebox.showinfo(title="Sauvegarde", message="Données sauvegardées ! (normalement, vérifier quand même en rechargeant la saison)")

        if assistant.step == 11:
            assistant.step12()
