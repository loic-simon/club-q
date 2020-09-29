# Envoi de mails à partir d'une adresse ESPCI

import os
import ssl
import pathlib
import getpass
import smtplib
import email
from email.mime import base, multipart, application, text


class Message(email.mime.multipart.MIMEMultipart):
    """Classe fille de MIMEMultipart simplifiant la création d'un message simple et l'attachement de pièces jointes

    Syntaxe :
        msg = Message(sender: str, dests: list, subject: str, message: str, replyto: str = None)

    <dest> liste de destinatires de la forme "x.y@domain.com" ou "X Y <x.y@domain.com>"
    """
    def __init__(self, sender: str, dests: list, subject: str, corps: str, replyto: str = None):
        """Initialises self."""
        super().__init__()
        self["FROM"] = sender
        self["TO"] = ", ".join(dests)
        self["SUBJECT"] = subject
        if replyto:
            self.add_header('Reply-To', replyto)
        self.attach(email.mime.text.MIMEText(corps, "plain"))

    def join_bytes(self, content: bytes, name: str):
        """Joins les données binaires (bytes) dans <content> au message, en tant que fichier de nom <name>"""
        part = email.mime.base.MIMEBase("application", "octet-stream")
        part.set_payload(content)
        email.encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=\"{name}\"")
        self.attach(part)

    def join(self, brutpath: str):
        """Joins le fichier dans <brutpath> (chemin str non traité par os.path) au message"""
        path = pathlib.Path(brutpath)       # Transformation chemin brut en chemin ouvrable
        with open(path, "rb") as file:
            content = file.read()
        self.join_bytes(content, os.path.basename(path))

    def send(self, server: smtplib.SMTP_SSL, verbose=False):
        """Envoi le message via <server>"""
        server.send_message(self)
        if verbose:
            print("Envoyé")


class ConnectPC(smtplib.SMTP_SSL):
    """Classe fille de smtplib.SMTP_SSL (context manager) pour se connecter simplement au serveur mail de l'ESPCI Paris - PSL

    Syntaxe :
        with ConnectPC(PC_id: str, password: str = None, verbose=False) as server:
            ...

    <PC_id> identifiant pour se connecter à l'Intranet ESPCI : lsimon, tlacoma...
    Si [password] n'est pas spécifié, getpass.getpass est utilisé pour le demander.
    """
    def __init__(self, ID_pc: str, password: str = None, verbose=False):
        """Initialises self."""
        ctx = ssl.create_default_context()                  # Création connexion sécuriséee
        super().__init__("mailer.espci.fr", port=465, context=ctx)      # Connexion au serveur
        if password is None:
            password = getpass.getpass(f"Mot de passe Intranet ESPCI pour {ID_pc} : ")
        self.login(f"{ID_pc}@espci.fr", password)           # Authentification
        if verbose:
            print("Login OK")
