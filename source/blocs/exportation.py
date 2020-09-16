import os
import subprocess
import platform
import tkinter as tk
from tkinter import filedialog

import unidecode
import reportlab as rl
from reportlab.lib import units, pagesizes, styles
from reportlab.pdfgen import canvas
from reportlab.platypus import flowables

from . import config


cm = rl.lib.units.cm


def filenamify(str):
    return "".join(c for c in unidecode.unidecode(str) if c not in r'.\/:*?"<>|')       # str -> ACSII et enlève caractères interdits dans les noms de fichiers


def exporter_fiches_eleves():
    lien_dossier = tk.filedialog.askdirectory(title="Sélectionnez un dossier pour exporter les fiches PDF individuelles :")
    if lien_dossier:        # Dossier sélectionné (pas Annuler)
        N_pdf = len(config.clients)
        for i_pdf, client in enumerate(config.clients):
            pdf_client(client, lien_dossier, open_pdf=False, i_pdf=i_pdf, N_pdf=N_pdf)

        tk.messagebox.showinfo(title="Exportation", message=f"Fiches élèves exportées dans {lien_dossier} !")


def exporter_fiches_spectacles():
    lien_dossier = tk.filedialog.askdirectory(title="Sélectionnez un dossier où les fiches spectacles seront exportées :")
    if lien_dossier:        # Dossier sélectionné (pas Annuler)
        for spec in config.spectacles:
            pdf_spectacle(spec, lien_dossier, open_pdf=False)

        tk.messagebox.showinfo(title="Exportation", message=f"Fiches spectacles exportées dans {lien_dossier} !")



def pdf_client(client, lien_dossier=None, open_pdf=True, i_pdf=None, N_pdf=None):

    if not lien_dossier:
        lien_dossier = tk.filedialog.askdirectory(title=f"Sélectionnez un dossier pour exporter la fiche PDF de {client.prenom} {client.nom} :")

    filename = os.path.join(os.path.normpath(lien_dossier), f"{filenamify(client.nomprenom)}.pdf")

    etape = f" {i_pdf}/{N_pdf}" if N_pdf else "..."
    with config.ContextPopup(config.root, f"Génération du PDF{etape}"):
        canvas = rl.pdfgen.canvas.Canvas(filename, pagesize=rl.lib.pagesizes.A4)
        canvas.setAuthor("Club Q ESPCI Paris - PSL")
        canvas.setTitle(f"Compte-rendu {client.prenom}{client.nom}")
        canvas.setSubject(f"Saison {config.saison.nom}")

        styles = rl.lib.styles.getSampleStyleSheet()
        styleN = styles["Normal"]
        canvas.setFont("Times-Bold", 18)


        descr = [
            f"Nom : <b>{client.nom}</b>",
            f"Prénom : <b>{client.prenom}</b>",
            f"Promo : <b>{client.promo or client.autre}</b>",
            f"Adresse e-mail : <b>{client.email}</b>"
        ]


        specs = [f"{attrib.spectacle.nom} - {attrib.places_attribuees} place(s) -\t\t {attrib.spectacle.unit_price} €"
                 for attrib in client.attributions()]

        specs.append("-"*158)
        specs.append(f"Total à payer : {client.calcul_a_payer()} €.")


        # Conversion en objets reportlab
        blocs_descr = []
        for txt in descr:
            blocs_descr.append(rl.platypus.Paragraph(txt, styleN))
            blocs_descr.append(rl.platypus.Spacer(1, 0.2*cm))

        blocs_specs = []
        for txt in specs:
            blocs_specs.append(rl.platypus.Paragraph(txt, styleN))
            blocs_specs.append(rl.platypus.Spacer(1, 0.2*cm))


        # IMPRESSION
        canvas.setFont("Times-Bold", 18)
        canvas.drawString(1*cm, 28*cm, f"Compte-rendu Club Q")

        canvas.setFont("Times-Bold", 12)
        canvas.drawString(1*cm, 27.2*cm, f"Saison {config.saison.nom}")

        dX, dY = canvas.drawImage(config.lien_logo_pc, 14*cm, 27.22*cm, width=5.63*cm, height=1.2*cm, mask="auto")
        dX, dY = canvas.drawImage(config.lien_logo_q, 11.5*cm, 26.8*cm, width=2*cm, height=2*cm, mask="auto")

        frame_descr = rl.platypus.Frame(1*cm, 23.5*cm, 19*cm, 3*cm, showBoundary=True)
        frame_descr.addFromList(blocs_descr, canvas)

        frame_specs = rl.platypus.Frame(1*cm, 1*cm, 19*cm, 22*cm, showBoundary=True)
        frame_specs.addFromList(blocs_specs, canvas)

        canvas.showPage()


        # SAUVEGARDE
        canvas.save()

        if open_pdf:
            # Ouvre le PDF (https://stackoverflow.com/a/435669)
            if platform.system() == "Windows":      # Windows
                os.startfile(filename)
            elif platform.system() == "Darwin":     # macOS
                subprocess.call(("open", filepath))
            else:                                   # linux variants
                subprocess.run(["xdg-open", filename], check=True)




def pdf_spectacle(spec, lien_dossier=None, open_pdf=True, i_pdf=None, N_pdf=None):

    if not lien_dossier:
        lien_dossier = tk.filedialog.askdirectory(title=f"Sélectionnez un dossier pour exporter la fiche PDF de {spec.nom} :")

    filename = os.path.join(os.path.normpath(lien_dossier), f"{filenamify(spec.nom)}.pdf")

    etape = f" {i_pdf}/{N_pdf}" if N_pdf else "..."
    with config.ContextPopup(config.root, f"Génération du PDF{etape}"):
        canvas = rl.pdfgen.canvas.Canvas(filename, pagesize=rl.lib.pagesizes.A4)
        styles = rl.lib.styles.getSampleStyleSheet()
        styleN = styles["Normal"]
        canvas.setFont("Times-Bold", 18)


        descr = [
            f"Titre : <b>{spec.nom}</b> ({spec.categorie or 'catégorie inconnue'})",
            f"Salle : <b>{spec.lieu()}</b>, {spec.salle.adresse or 'adresse inconnue'}",
            f"Date : <b>{spec.date or 'inconnue'}  {spec.heure or '(heure inconnue)'}</b>",
            # f"Heure : <b>{spec.heure}</b>",
            f"Nombre de places : <b>{spec.nb_tickets}</b> – Demandées : <b>{spec.nb_places_demandees()}</b> – Attribuées : <b>{spec.nb_places_attribuees()}</b>",
        ]

        eleves = [f"{attrib.client.nomprenom}, {attrib.client.promo or attrib.client.autre}, {attrib.client.email} - {attrib.places_attribuees} place(s)"
                  for attrib in spec.attributions()]


        # Conversion en objets reportlab

        blocs_descr = []
        for txt in descr:
            blocs_descr.append(rl.platypus.Paragraph(txt, styleN))
            blocs_descr.append(rl.platypus.Spacer(1, .2*cm))

        blocs_eleves = []
        for txt in eleves:
            blocs_eleves.append(rl.platypus.Paragraph(txt, styleN))
            blocs_eleves.append(rl.platypus.Spacer(1, .2*cm))


        # IMPRESSION PAGE 1
        canvas.setFont("Times-Bold", 18)
        canvas.drawString(1*cm, 28*cm, f"Compte-rendu {spec.nom}")

        canvas.setFont("Times-Bold", 12)
        canvas.drawString(1*cm, 27.2*cm, f"Saison {config.saison.nom}")

        dX, dY = canvas.drawImage(config.lien_logo_pc, 14*cm, 27.22*cm, width=5.63*cm, height=1.2*cm, mask="auto")
        dX, dY = canvas.drawImage(config.lien_logo_q, 11.5*cm, 26.8*cm, width=2*cm, height=2*cm, mask="auto")

        frame_descr = rl.platypus.Frame(1*cm, 23.5*cm, 19*cm, 3*cm, showBoundary =1)
        frame_descr.addFromList(blocs_descr, canvas)

        frame_eleves = rl.platypus.Frame(1*cm, 1*cm, 19*cm, 22*cm, showBoundary =1)
        frame_eleves.addFromList(blocs_eleves, canvas)

        canvas.showPage()


        # PAGE 2 (liste d'attente)

        voeux = [voeu for voeu in spec.voeux() if not voeu.places_attribuees]

        if voeux:
            voeux.sort(key=lambda a: a.client.mecontentement or 0, reverse=True)

            voeux_txt = ["Liste d'attente :"]
            for voeu in voeux:
                voeux_txt.append(f"M: {round(voeu.client.mecontentement or 0, 2)} - {voeu.client.nomprenom} - {voeu.places_demandees} place(s) ({voeu.places_minimum} min) - Voeu n°{voeu.priorite}")

        else:
            voeux_txt = ["Pas de liste d'attente."]


        blocs_descr = []        # Détruits à la précédente impression...
        for txt in descr:
            blocs_descr.append(rl.platypus.Paragraph(txt, styleN))
            blocs_descr.append(rl.platypus.Spacer(1, .2*cm))

        blocs_voeux = []
        for txt in voeux_txt:
            blocs_voeux.append(rl.platypus.Paragraph(txt, styleN))
            blocs_voeux.append(rl.platypus.Spacer(1, .2*cm))


        # IMPRESSION PAGE 2
        canvas.setFont("Times-Bold", 18)
        canvas.drawString(1*cm, 28*cm, f"Liste d'attente {spec.nom}")

        canvas.setFont("Times-Bold", 12)
        canvas.drawString(1*cm, 27.2*cm, f"Saison {config.saison.nom}")

        dX, dY = canvas.drawImage(config.lien_logo_pc, 14*cm, 27.22*cm, width=5.63*cm, height=1.2*cm, mask="auto")
        dX, dY = canvas.drawImage(config.lien_logo_q, 11.5*cm, 26.8*cm, width=2*cm, height=2*cm, mask="auto")

        frame_descr = rl.platypus.Frame(1*cm, 23.5*cm, 19*cm, 3*cm, showBoundary =1)
        frame_descr.addFromList(blocs_descr, canvas)

        frame_eleves = rl.platypus.Frame(1*cm, 1*cm, 19*cm, 22*cm, showBoundary =1)
        frame_eleves.addFromList(blocs_voeux, canvas)

        canvas.showPage()


        # SAUVEGARDE
        canvas.save()

        if open_pdf:
            # Ouvre le PDF (https://stackoverflow.com/a/435669)
            if platform.system() == "Windows":      # Windows
                os.startfile(filename)
            elif platform.system() == "Darwin":     # macOS
                subprocess.call(("open", filepath))
            else:                                   # linux variants
                subprocess.run(["xdg-open", filename], check=True)
