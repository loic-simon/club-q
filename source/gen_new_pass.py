"""Utilitaire pour changer le mot de passe du programme et / ou l'URI de la BDD
et générer le fichier .env correpondant, avec les informations encryptées"""

import sys
import os
import json
import getpass

from blocs import tools


data_path = os.path.join("resources", "data.json")


# ------------------------ Mot de passe ------------------------

old_pwd = getpass.getpass("Mot de passe actuel (ne rien mettre pour nouvelle génération) : ")

if old_pwd:
    try:
        with open(data_path, "r") as df:
            data = json.load(df)
        PROGRAM_PASSWORD_HASH = data["PROGRAM_PASSWORD_HASH"]
    except Exception as e:
        sys.exit(f"Le fichier data.json est introuvable ou ne contient pas le hash de l'ancien mot de passe. Nouvelle génération obligatoire. [{type(e).__name__}: {e}]")

    if tools.hash(old_pwd) != PROGRAM_PASSWORD_HASH:     # Mauvais mot de passe
        sys.exit("Mot de passe incorrect")


# ------------------------ Confirmation ------------------------

new_pwd = getpass.getpass("Nouveau mot de passe : ")
if getpass.getpass("Nouveau mot de passe (confirmation) : ") != new_pwd:    # Confirmation non OK
    sys.exit("Mot de passe de confirmation différent")


# ---------------------- Récupération URI ----------------------

opt = ", ne rien mettre pour laisser inchangé" if old_pwd else ""
uri = input(f"URI d'accès BDD (protocol://user:pwd@server/base{opt}) :")
if not uri:
    if old_pwd:
        try:
            with open(data_path, "r") as df:
                data = json.load(df)
            DATABASE_URI_ENCRYPTED = data["DATABASE_URI_ENCRYPTED"]
        except Exception as e:
            sys.exit(f"Le fichier data.json ne contient pas l'ancienne URI encryptée'. Il est obligatoire de la spécifier. [{type(e).__name__}: {e}]")

        uri = tools.decrypt(old_pwd, DATABASE_URI_ENCRYPTED)     # On récupère l'ancienne
    else:
        sys.exit("URI nécessaire si ancien mot de passe non fourni")


# ------------------------ Chiffremment ------------------------

print("Chiffremment...")

PROGRAM_PASSWORD_HASH = tools.hash(new_pwd)
DATABASE_URI_ENCRYPTED = tools.encrypt(new_pwd, uri)


# ------------------------ Écriture .env -----------------------

print("Écriture de data.json...")

data = {
    "PROGRAM_PASSWORD_HASH": PROGRAM_PASSWORD_HASH,
    "DATABASE_URI_ENCRYPTED": DATABASE_URI_ENCRYPTED,
}
with open(data_path, "w") as df:
    json.dump(data, df)


print("Terminé.")
