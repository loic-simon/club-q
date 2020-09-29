"""Utilitaire pour changer le mot de passe du programme et / ou les paramètres
confidentiels chiffrés et générer le fichier data.json correpondant"""

import sys
import os
import json
import getpass

from blocs import tools, config


data_path = os.path.join("resources", "data.json")

def name_to_encrname(name):
    return f"{name}_ENCRYPTED"


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


# --------------------- Récupération données ---------------------

raw_data = {}

opt = "(ne rien mettre pour laisser inchangé) " if old_pwd else ""
for name, descr in config.DATA_PARAMETERS.items():      # Paramètres attendus dans data.json et leur description
    raw = input(f"{descr} ({name}) {opt}: ")
    if not raw:
        if old_pwd:
            try:
                with open(data_path, "r") as df:
                    old_data = json.load(df)
                old_val = old_data[name_to_encrname(name)]
            except Exception as e:
                sys.exit(f"Le fichier data.json ne contient pas le paramètre '{name_to_encrname(name)}'. Il est donc obligatoire de le spécifier. [{type(e).__name__}: {e}]")

            raw = tools.decrypt(old_pwd, old_val)           # On récupère l'ancienne
        else:
            sys.exit(f"{name} nécessaire si ancien mot de passe non fourni")

    raw_data[name] = raw


# ------------------------ Chiffremment ------------------------

print("Chiffremment...")

encryption_table = {}
new_data = {
    "PROGRAM_PASSWORD_HASH": tools.hash(new_pwd),       # Hashage mot de passe
}
for name, raw in raw_data.items():
    encrname = name_to_encrname(name)
    new_data[encrname] = tools.encrypt(new_pwd, raw)    # Chiffremment nouveaux paramètres
    encryption_table[encrname] = name


# ------------------------ Écriture .env -----------------------

print("Écriture de data.json...")

new_data["_encryption_table"] = encryption_table        # Stockage liste données à décrypter

with open(data_path, "w") as df:
    json.dump(new_data, df, indent=4)


print("Terminé.")
