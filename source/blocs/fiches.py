import math
import platform
import tkinter as tk
from tkinter import ttk

import webbrowser

from . import config, dataclasses, bdd, tools, exportation, publication


def fiche_client(event, client=None):
    if not client:      # Appel depuis un Treeview
        selected = event.widget.selection()
        if not selected:
            return
        client = tools.get(config.clients, id=int(selected[0]))

    fen_ele = config.Toplevel(event.widget.winfo_toplevel())
    fen_ele.title(f"Fiche élève : {client.prenom} {client.nom}")

    haut = tk.Frame(fen_ele)
    infos = ttk.LabelFrame(haut, text="Infos")

    labs = tools.labels_grid(infos, [
            [f"Nom : {client.nom}",                                                         f"Prénom : {client.prenom}"],
            [f"Promo : {client.promo}" if client.promo else f"Origine : {client.autre}",    f"Email : {client.email or 'non renseigné'}"],
        ], padx=5, pady=2)

    if client.email:
        tools.underline_label(labs[1][1])
        labs[1][1].bind("<Button-1>", lambda event: webbrowser.open(f"mailto:{client.email}"))

    infos.pack(padx=10, pady=10, side=tk.TOP, fill=tk.X)


    def update_mec(event=None):
        delta_mec = float(nouveau.get() or 0)
        client.mecontentement += delta_mec
        l32.configure(text=f"Mécontentement ajouté : {round((client.mecontentement or 0) - (client.mecontentement_precedent or 0), 3)}")
        nouveau.set(0)
        config.liste_clients.refresh()


    mec = ttk.LabelFrame(haut, text="Mécontentement")
    ttk.Label(mec, text=f"Ancien mécontentement : {round(client.mecontentement_precedent or 0, 3)}", justify=tk.LEFT).pack(side=tk.TOP)

    l32 = ttk.Label(mec, text=f"Mécontentement ajouté : {round((client.mecontentement or 0) - (client.mecontentement_precedent or 0), 3)}")
    l32.pack(side=tk.TOP)

    ttk.Label(mec, text="Ajouter/soustraire arbitrairement :").pack(side=tk.LEFT, padx=5)

    ttk.Button(mec, text="Go", command=update_mec).pack(side=tk.RIGHT, padx=3, pady=3)

    nouveau = ttk.Spinbox(mec, width=6, increment=0.1, from_=-math.inf, to=math.inf)
    nouveau.set(0)
    nouveau.bind("<Return>", update_mec)
    nouveau.pack(side=tk.RIGHT, padx=3, pady=3)

    mec.pack(padx=10, pady=10, side=tk.BOTTOM, fill=tk.X)

    haut.pack(padx=10, side=tk.TOP)

    bas = tk.Frame(fen_ele)
    ttk.Label(bas, text="Voeux et attributions :").pack()
    liste_voeux = config.ItemsTreeview(bas,
        columns=["Prio.", "Spectacle", "Dem.", "Min.", "Attr."],
        insert_func=lambda v: [v.priorite, v.spectacle.nom, v.places_demandees, v.places_minimum, v.places_attribuees or 0],
        sizes=[50, 160, 50, 50, 50],
        stretches=[False, True, False, False, False],
        height=7, selectmode="browse",
        footer_id=-client.id, footer_values=["", "[Ajouter un voeu]", "", "", ""],
    )
    liste_voeux.insert(*client.voeux(), )
    liste_voeux.sort("Prio.")
    liste_voeux.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

    liste_voeux.bind("<Double-1>", modif_voeu)
    liste_voeux.bind("<Return>", modif_voeu)

    bas.pack(padx=10, fill=tk.X)

    def envoi():
        filepath = exportation.pdf_client(client, config.tempdir, open_doc=False)
        publication.personaliser_puis_envoyer_mail({client: filepath})        # Récupère fromnane, objet, corps... et appelle la fonction d'envoi

    frame_boutons = ttk.Frame(fen_ele)
    ttk.Button(frame_boutons, text="Exporter la fiche", command=lambda: exportation.pdf_client(client)).pack(padx=5, pady=10, side=tk.LEFT)
    ttk.Button(frame_boutons, text="Envoyer par email", command=envoi).pack(padx=5, pady=10, side=tk.RIGHT)
    frame_boutons.pack()



def fiche_spec(event, spec=None):
    if not spec:    # Appel depuis un Treeview
        selected = event.widget.selection()
        if not selected:
            return
        spec = tools.get(config.spectacles, id=int(selected[0]))

    fen_spec = config.Toplevel(event.widget.winfo_toplevel())
    fen_spec.title(f"Fiche spectacle : {spec.nom}")


    frame_infos = ttk.LabelFrame(fen_spec, text="Infos")
    tools.labels_grid(frame_infos, [
            [f"Titre : {spec.nom}",         f"Catégorie : {spec.categorie}" ],
            [f"Date : {spec.date}",         f"Heure : {spec.heure}"],
            [f"Lieu : {spec.lieu()}",       f"Prix de la place : {spec.unit_price:.2f} €"],
        ], padx=5, pady=2)

    frame_infos.pack(pady=10, padx=10)


    frame_places = ttk.LabelFrame(fen_spec, text="Places")
    tools.labels_grid(frame_places, [
            [f"Nombre de places en tout : {spec.nb_tickets}",           f"Places demandées : {spec.nb_places_demandees()}"],
            [f"Places attribuées : {spec.nb_places_attribuees()}",      f"Places restantes : {spec.nb_places_restantes()}"],
        ], padx=5, pady=2)

    frame_places.pack(pady=10, padx=10)


    ttk.Label(fen_spec, text="Liste des élèves désirant des places : ").pack()
    liste_voeux = config.ItemsTreeview(fen_spec,
        columns=["Prio.", "Nom", "Dem.", "Min.", "Attr."],
        insert_func=lambda v: [v.priorite, v.client.nomprenom, v.places_demandees, v.places_minimum, v.places_attribuees or 0],
        sizes=[50, 178, 50, 50, 50],
        stretches=[False, True, False, False, False],
        height=7, selectmode="browse",
    )
    liste_voeux.insert(*spec.voeux())
    liste_voeux.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)
    liste_voeux.bind("<Double-1>", modif_voeu)

    bas = ttk.Frame(fen_spec)
    ttk.Button(bas, text="Exporter le PDF", command=lambda: exportation.pdf_spectacle(spec)).grid(row=0, column=0, padx=2)
    ttk.Button(bas, text="Exporter l'Excel", command=lambda: exportation.excel_spectacle(spec)).grid(row=0, column=1, padx=2)
    bas.pack(padx=2, pady=5)




def modif_voeu(event):
    treeview = event.widget
    selected = treeview.selection()
    if not selected:
        return

    selected_id = int(selected[0])
    if selected_id < 0:   # Nouveau voeu
        nouveau_voeu(-selected_id, treeview=treeview)
        return

    voeu = tools.get(config.voeux, id=selected_id)
    spec = voeu.spectacle
    client = voeu.client

    modif = config.Toplevel(treeview.winfo_toplevel())
    modif.title("Modification de l'attribution")
    modif.resizable(False, False)

    haut1 = ttk.Frame(modif)
    labels_info = tools.labels_grid(haut1, [
            [f"Élève : {client.prenom} {client.nom}",       f"Places demandées en tout : {client.nb_places_demandees()}"],
            [f"Spectacle : {spec.nom}",                     f"Places restantes :  {spec.nb_places_restantes()}"],
        ], padx=5, pady=2)


    tools.underline_label(labels_info[0][0])
    labels_info[0][0].bind("<Button-1>", lambda event: fiche_client(event, client))
    tools.underline_label(labels_info[1][0])
    labels_info[1][0].bind("<Button-1>", lambda event: fiche_spec(event, spec))
    haut1.pack(padx=5, pady=5)

    haut2 = ttk.Frame(modif)
    tools.labels_grid(haut2, [
            [f"Nombre de places demandées : {voeu.places_demandees}",     f"Priorité du voeu : {voeu.priorite}"],
            [f"Nombre de places minimum : {voeu.places_minimum}",         f"Places attribuées : {voeu.places_attribuees}"],
        ], padx=5, pady=2)
    haut2.pack(padx=5, pady=5)

    def valider(event=None):
        places = int(nouv.get() or 0)
        voeu.attribuer(places)
        config.refresh_listes()
        treeview.refresh()
        modif.destroy()

    def valider_zero():
        nouv.set(0)
        valider()

    mil = tk.Frame(modif)
    ttk.Label(mil, text="Nouveau nombre de places attribuées :").grid(row=0, column=0, padx=2)
    nouv = ttk.Spinbox(mil, width=10, values=[0] + list(range(voeu.places_minimum, voeu.places_demandees+1)))
    nouv.set(voeu.places_attribuees or 0)
    nouv.grid(row=0, column=1, padx=2, pady=5)
    nouv.bind("<Return>", valider)
    mil.pack(padx=5, pady=5)

    bas = ttk.Frame(modif)
    ttk.Button(bas, text="Annuler", command=modif.destroy).grid(row=0, column=0, padx=2)
    ttk.Button(bas, text="Modifier", command=valider).grid(row=0, column=1, padx=2)
    ttk.Button(bas, text="Mettre 0 places", command=valider_zero).grid(row=0, column=2, padx=2)
    bas.pack(padx=2, pady=5)



def nouveau_voeu(client_id, treeview=None):
    client = tools.get(config.clients, id=client_id)

    nouv = config.Toplevel(treeview.winfo_toplevel())
    nouv.title("Nouveau voeu")
    nouv.resizable(False, False)

    haut1 = ttk.Frame(nouv)
    labels_info = tools.labels_grid(haut1, [
            [f"Élève : {client.prenom} {client.nom}",       f"Voeux déjà formulés : {len(client.voeux())}"],
            # [f"Spectacle : {spec.nom}",                     f"Places restantes :  {spec.nb_places_restantes()}"],
        ], padx=5, pady=2)


    tools.underline_label(labels_info[0][0])
    labels_info[0][0].bind("<Button-1>", lambda event: fiche_client(event, client))
    haut1.pack(padx=5, pady=5)


    haut2 = ttk.Frame(nouv)

    spec_name = tk.StringVar()
    spectacles_dropdown = ttk.OptionMenu(haut2, spec_name, "", *(spec.nom for spec in config.spectacles))

    placesdem_spinbox = ttk.Spinbox(haut2, width=10, from_=1, to=50)
    placesmin_spinbox = ttk.Spinbox(haut2, width=10, from_=1, to=50)
    prio_spinbox = ttk.Spinbox(haut2, width=10, from_=1, to=50)
    prio_spinbox.set(len(client.voeux()) + 1)

    tools.labels_grid(haut2, [
            ["Spectacle :",                 spectacles_dropdown],
            [f"Places demandées : ",        placesdem_spinbox],
            [f"Places minimum : ",          placesmin_spinbox],
            [f"Priorité : ",                prio_spinbox],
        ], padx=5, pady=2)
    haut2.pack(padx=5, pady=5)

    def ajouter():
        spec = tools.get(config.spectacles, nom=spec_name.get())
        placesdem = int(placesdem_spinbox.get() or 1)
        placesmin = int(placesmin_spinbox.get() or 1)
        prio = int(prio_spinbox.get() or 1)

        voeu = dataclasses.Voeu(client_id=client.id, spectacle_id=spec.id, places_demandees=placesdem, places_minimum=placesmin, priorite=prio, places_attribuees=0)
        config.voeux.append(voeu)

        config.refresh_listes()
        if treeview:
            treeview.insert(voeu)

        nouv.destroy()


    bas = ttk.Frame(nouv)
    ttk.Button(bas, text="Annuler", command=nouv.destroy).grid(row=0, column=0, padx=2)
    ttk.Button(bas, text="Ajouter", command=ajouter).grid(row=0, column=1, padx=2)
    bas.pack(padx=2, pady=5)
