import platform
import tkinter as tk
from tkinter import ttk

from . import config, tools, assistant


def suivi_process():
    if config.fen_suivi and config.fen_suivi.winfo_exists():      # La fenêtre existe déja
        config.fen_suivi.lift()
        return

    config.fen_suivi = config.Toplevel()
    config.fen_suivi.title("Processus d'attribution")
    config.fen_suivi.resizable(False, False)


    gauche = tk.Frame(config.fen_suivi)
    init = ttk.LabelFrame(gauche, text="Initialisation")
    attrib = ttk.LabelFrame(gauche, text="Attribution")
    logs = ttk.LabelFrame(gauche, text="Logs")


    nb_specs = len(config.spectacles)

    def get_n_and_view_logs():
        n = lognum.get()
        if n in config.logs:
            view_logs(n)
        else:
            tk.messagebox.showinfo(message="Pas de logs pour ce voeu !", parent=config.fen_suivi)

    ttk.Label(logs, text="Logs attribution voeu n°").grid(row=0, column=0, padx=5, pady=5)
    lognum = tk.IntVar()
    ttk.OptionMenu(logs, lognum, 1, *range(1, nb_specs+1)).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(logs, text="Voir", command=get_n_and_view_logs).grid(row=0, column=2, padx=5, pady=5)


    def init_mec_et_grise():
        if init_mecontentements():
            ilm_button.configure(text="Supprimer mécontentements arbitraires")

    ilm_button = ttk.Button(init, text="Initialiser les mécontentements", command=init_mec_et_grise)
    ilm_button.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)
    if config.attrib_ss_conflit_done:
        ilm_button.configure(text="Supprimer mécontentements arbitraires")


    def reset_et_degrise():
        if reset_attribs():
            asc_button.configure(text="Attribuer les places sans conflit", state=tk.NORMAL)
            config.attrib_button.configure(text=f"Attribuer le voeu n°{config.num_voeux}", state=tk.NORMAL)

    clear_button = ttk.Button(init, text="Effacer toutes les attributions", command=reset_et_degrise)
    clear_button.pack(side=tk.RIGHT, padx=5, pady=5, ipadx=5)


    def attrib_et_grise():
        attribution_sans_conflit()
        asc_button.configure(text="Attribution sans conflit (fait)", state=tk.DISABLED)

    asc_button = ttk.Button(attrib, text="Attribuer les places sans conflit", command=attrib_et_grise)
    asc_button.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)
    if config.attrib_ss_conflit_done:
        asc_button.configure(text="Attribution sans conflit (fait)", state=tk.DISABLED)


    def attrib_vec():
        config.attributor = attribution_avec_conflit(config.num_voeux)        # Générateur
        next(config.attributor)                                 # Lance l'attribution automatique

    config.attrib_button = ttk.Button(attrib, text=f"Attribuer le voeu n°{config.num_voeux}/{nb_specs}", command=attrib_vec)
    config.attrib_button.pack(side=tk.RIGHT, padx=5, pady=5, ipadx=5)
    if config.cas_en_cours:
        config.attrib_button.configure(text=f"Attribution voeu {config.num_voeux} en cours", state=tk.DISABLED)


    init.grid(row=0, column=0, padx=20, pady=10, sticky=tk.EW + tk.N)
    attrib.grid(row=1, column=0, padx=20, pady=10, sticky=tk.EW)
    logs.grid(row=2, column=0, padx=20, pady=10, sticky=tk.EW + tk.S)


    def infos_voeu_n(prio):
        emis, decus, attr, partiel, placesdem, placesattr = 0, 0, 0, 0, 0, 0
        for voeu in config.voeux:
            if voeu.priorite == prio:
                emis += 1
                if voeu.places_attribuees == voeu.places_demandees:
                    attr += 1
                elif voeu.places_attribuees:
                    partiel += 1
                else:
                    decus += 1

                placesdem += voeu.places_demandees
                placesattr += voeu.places_attribuees or 0

        if prio < config.num_voeux:         # Attribution déjà faite pour ce voeu
            return [prio, emis, decus, attr, partiel, placesdem, placesattr]
        else:                               # Attribution pas encore faite : on ne marque pas les 0 pour plus de clarté
            return [prio, emis, "", attr or "", partiel or "", placesdem, placesattr or ""]


    droite = ttk.LabelFrame(config.fen_suivi, text="Voeux et attributions :")
    config.liste_suvi_process = config.ItemsTreeview(droite,
        columns=["Prio.", "Émis", "Déçus", "Comblés", "Partiel", "Places dem.", "Places attr."],
        insert_func=infos_voeu_n,
        sizes=[50, 50, 50, 60, 50, 75, 75],
        id_func=lambda prio: prio,
        height=nb_specs, selectmode=tk.NONE,
    )
    config.liste_suvi_process.insert(*range(1, nb_specs + 1))
    config.liste_suvi_process.pack(padx=10, pady=10)

    gauche.grid(row=0, column=0, sticky=tk.NS, padx=20, pady=10)
    droite.grid(row=0, column=1, sticky=tk.NS, padx=20, pady=20)

    if assistant.step == 6:
        assistant.step6b()



def init_mecontentements():
    """Calcule le mécontentement actuel pour tous les clients"""
    if tk.messagebox.askokcancel(title="Initialiser les mécontentements ?", message="Tous les mécontentements arbitraires ajoutés seront effacés", parent=config.fen_suivi):
        for client in config.clients:
            client.init_mecontentement()

        config.liste_clients.refresh()
        config.init_mecontentements_done = True
        tk.messagebox.showinfo(title="Initialisation des mécontentements", message=f"Fait !\n\n(Avec les paramètres : Promo 1A = {config.promo_1A}, bonus = {config.bonus_1A} / {config.bonus_2A} / {config.bonus_3A} / {config.bonus_4A} / {config.bonus_autre})", parent=config.fen_suivi)

        if assistant.step == 7:
            assistant.step8()

        return True

    return False



def attribution_sans_conflit():
    """Attribue les voeux pour lesquels le nombre de places demandé est inférieur ou égal au nombre de places disponibles"""
    mess = ""

    for spec in config.spectacles:
        if spec.nb_tickets > spec.nb_places_demandees():
            mess += f"- {spec.nom}\n"

            for voeu in spec.voeux():
                voeu.attribuer(voeu.places_demandees)

    config.refresh_listes()

    config.attrib_ss_conflit_done = True
    tk.messagebox.showinfo(title="Attribution sans conflit", message=f"Spectacles traités :\n\n{mess or 'Aucun :('}", parent=config.fen_suivi)

    if assistant.step == 8:
        assistant.step9()



def reset_attribs():
    if tk.messagebox.askokcancel(title="Effacer toutes les attributions", message="Toutes les attributions seront supprimées. Les mécontentements arbitraires ne sont pas impactés.", parent=config.fen_suivi):

        config.attrib_ss_conflit_done = False

        config.num_voeux = 1
        config.cas_en_cours = False
        config.logs = {}

        for voeu in config.voeux:
            voeu.attribuer(0)

        config.refresh_listes()

        return True

    return False



def view_logs(n):
    fen = config.Toplevel()
    fen.title(f"Logs voeu n°{n}")

    frame_logs = ttk.Frame(fen)
    canvas = tk.Canvas(frame_logs)
    scrollbar = ttk.Scrollbar(frame_logs, orient=tk.VERTICAL, command=canvas.yview)
    subframe = ttk.Frame(canvas)
    subframe.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox(tk.ALL)))
    canvas.create_window((0, 0), window=subframe, anchor=tk.NW)
    canvas.configure(yscrollcommand=scrollbar.set)
    # Envie de mourir, tk de ses énormes morts
    if platform.system() == "Windows":      # Windows
        fen.bind("<MouseWheel>", lambda event: canvas.yview_scroll(-event.delta//120, tk.UNITS))
    elif platform.system() == "Darwin":     # macOS
        fen.bind("<MouseWheel>", lambda event: canvas.yview_scroll(-event.delta, tk.UNITS))
    else:                                   # linux variants
        fen.bind("<Button-4>", lambda event: canvas.yview_scroll(-event.delta//120, tk.UNITS))
        fen.bind("<Button-5>", lambda event: canvas.yview_scroll(event.delta//120, tk.UNITS))

    tk.Message(subframe, text=config.logs[n], width=600, font=("Courier", 9)).pack(padx=10, pady=5)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    frame_logs.pack(padx=0, pady=10, expand=True, fill=tk.BOTH)



def attribution_avec_conflit(prio):     # GÉNÉRATEUR : cette fonction retourne un générateur !
    """Attribue les voeux pour lesquels le nombre de places demandé est supérieur au nombre de places disponibles

    Retourne un générateur qui yield dès qu'une action humaine est nécessaire, après avoir afficher une fenêtre
    """
    voeux_tries = [voeu for voeu in config.voeux if voeu.priorite == prio and not voeu.places_attribuees]      # Voeux n° prio non attribués
    voeux_tries.sort(key=lambda v: v.client.mecontentement, reverse=True)        # Voeux des clients les plus mécontents en premier

    plages_voeux = []   # liste de listes des voeux prio de même mécontentement, du plus ou moins mécontent, dont le voeu prio n'a pas encore été pourvu
    mec = None

    for voeu in voeux_tries:
        if mec and abs(voeu.client.mecontentement - mec) < 0.001:
            plages_voeux[-1].append(voeu)       # Ajout à la plage en cours
        else:
            res.append([voeu])                  # Nouvelle plage
            plages_voeux = voeu.client.mecontentement


    n_plages = len(plages_voeux)

    config.logs[config.num_voeux] = f"Attribution automatique voeu n°{config.num_voeux}\n"
    def log(txt):
        config.logs[config.num_voeux] += txt


    for i, plage in enumerate(plages_voeux):
        log(f"\n - {i + 1}/{n_plages} [méc. {round(plage[0].client.mecontentement, 3)}] :\n")

        if len(plage) > 1:              # Plusieurs voeux de clients de même mécontentement
            group_par_spec = {}
            for voeu in plage:
                if voeu.spectacle in group_par_spec:
                    group_par_spec[voeu.spectacle].append(voeu)
                else:
                    group_par_spec[voeu.spectacle] = [voeu]

            for spec, voeux in list(group_par_spec.items()):    # list permet de figer l'itérateur (et on peut modifier group_par_spec)
                if len(voeux) > 1:          # Possible conflit : plusieurs voeux de même mécontentement pour un même spectacle
                    places_dem = sum(voeu.places_demandees for voeu in voeux)
                    if places_dem > spec.nb_places_restantes():      # Pas assez de places ==> oskour !

                        # BESOIN D'AIDE MANUELLE
                        attribution_manuelle(voeux)
                        del group_par_spec[spec]        # On enlève les voeux, déjà traités
                        config.attrib_button.configure(text=f"Attribution voeu {config.num_voeux} en cours ({i}/{n_plages})", state=tk.DISABLED)
                        config.cas_en_cours = True
                        config.refresh_listes()
                        yield                   # Attente du prochain next() du générateur pour continuer (= résolution du cas)

            plage = [voeu for sublist in group_par_spec.values() for voeu in sublist]


        # Attribution automatique : pas de conflits, ou déjà gérés (et voeux correspondants supprimés de plage)
        for voeu in plage:
            spec = voeu.spectacle
            log(f"     {voeu.client.nomprenom} -> ")

            if voeu.places_demandees <= spec.nb_places_restantes():  # on lui attribue les places spec'il y en a assez
                # client.spectaclesattribues.append(f"Voeu n°{prio} attribué: {spec} avec {voeu.nbplaces} places")
                voeu.attribuer(voeu.places_demandees)
                log(f"{voeu.places_demandees} places pour {spec.nom} (comblé)\n")

            elif voeu.places_minimum <= spec.nb_places_restantes():
                # client.spectaclesattribues.append(f"Voeu n°{prio} partiellement attribué: {spec} avec {spec.nb_places_restantes} places")
                voeu.attribuer(spec.nb_places_restantes())
                log(f"{spec.nb_places_restantes()} places pour {spec.nom} (sur {voeu.places_demandees})\n")

            else:
                log(f"plus de places pour {spec.nb_places_restantes()}\n")


    # Fin de l'attribution
    config.num_voeux += 1
    config.refresh_listes()

    tk.messagebox.showinfo(title="Attribution automatique", message=f"Voeu n°{config.num_voeux - 1} attribué !", parent=config.fen_suivi)
    config.cas_en_cours = False

    if config.num_voeux <= len(config.spectacles):
        config.attrib_button.configure(text=f"Attribuer le voeu n°{config.num_voeux}", state=tk.NORMAL)
    else:
        config.attrib_button.configure(text=f"Tous voeux attribués", state=tk.DISABLED)

    if assistant.step == 10:
        assistant.step11()

    yield       # Évite le StopIteration, qu'on a la flemme de catch



def attribution_manuelle(voeux):
    fen = config.Toplevel()
    fen.title("Cas d'égalité")
    fen.resizable(False, False)
    fen.protocol("WM_DELETE_WINDOW", lambda: None)          # Empêche de fermer la fenêtre
    fen.bell()

    def log(txt):
        config.logs[config.num_voeux] += txt

    spec = voeux[0].spectacle
    log(f"     ATTRIBUTION MANUELLE demandée pour {spec.nom} :\n")

    ttk.Label(fen, text=f"Cas d'égalité lors de l'attribution du voeu n°{config.num_voeux} :\n\n"
        f"- Spectacle : {spec.nom}\n"
        f"- Places restantes : {spec.nb_places_restantes()}"
    ).pack(padx=10, pady=10)

    decision = ttk.LabelFrame(fen, text="Attribution manuelle")

    nouv_boxes = {voeu: ttk.Spinbox(decision, width=5, values=[0] + list(range(voeu.places_minimum, voeu.places_demandees+1))) for voeu in voeux}
    for box in nouv_boxes.values():
        box.set(0)

    tools.labels_grid(decision,
          [["Élève",                "Places demandées",     "Places minimum",       "Places attribuées" ]]
        + [[voeu.client.nomprenom,  voeu.places_demandees,  voeu.places_minimum,    nouv_boxes[voeu]    ] for voeu in voeux],
    padx=2, pady=2)

    decision.pack(padx=10, pady=10, ipadx=5, ipady=5)


    def valider():
        places = {voeu: int(nouv_boxes[voeu].get() or 0) for voeu in voeux}
        if sum(places.values()) > spec.nb_places_restantes():
            tk.messagebox.showerror(title="Impossible wtf", message="Plus de places à attribuer que de places restantes pour ce spectacle !", parent=fen)
        else:
            for voeu, nb_places in places.items():
                voeu.attribuer(nb_places)
                log(f"        * {voeu.client.nomprenom} -> {nb_places} place(s) [dem. {voeu.places_demandees} / min. {voeu.places_minimum}]\n")
            fen.destroy()
            next(config.attributor)                # Continue l'attribution

    ttk.Button(fen, text="Valider", command=valider).pack(padx=10, pady=10)
