import tkinter as tk
from tkinter import ttk, font

import hashlib
import base64
from cryptography import fernet




def get(items, **kwargs):
    """Renvoie l'objet de la liste <items> tel que item.prop = <kwargs>[prop], pour tous les prop dans <kwargs>

    Ex. : tools.get(config.spectacles, id=2)
          tools.get(config.clients, nom="Allo")

    Lève une erreur si l'objet n'existe pas ou n'est pas unique
    """

    found = [item for item in items if all(getattr(item, prop) == val for prop, val in kwargs.items())]
    if not found:
        raise ValueError(f"Item « {kwargs} » inconnu")
    elif len(found) > 1:
        raise ValueError(f"Plusieurs items « {kwargs} »")
    else:
        return found[0]



def labels_grid(parent, LL, padx=0, pady=0):
    """Packs a grid of tkinter widgets / strings (<LL> grid-like list of lists) in <parent>

    Each element of <LL> should be one of
        - a tkinter / ttk widget (instance of tkinter.BaseWidget) in <parent>
        - a string instance, wich is converted to a tkinter.Label object
    Any other object is silently ignored (nothing done).

    [padx] and [pady] are passed to each .grid call (default 0 and 0).
    """
    RR = []
    for row, L in enumerate(LL):
        R = []
        for col, elem in enumerate(L):
            if isinstance(elem, tk.BaseWidget):
                r = elem
            else:
                r = ttk.Label(parent, text=str(elem))

            r.grid(row=row, column=col, padx=padx, pady=pady)
            R.append(r)
        RR.append(R)
    return RR


def underline_label(label):
    style = ttk.Style(label.winfo_toplevel())
    original_font = tk.font.nametofont(style.lookup("TLabel", "font"))
    f = font.Font(**original_font.configure())
    f.configure(underline=True)
    style.configure("Underline.TLabel", font=f)

    label.configure(style="Underline.TLabel", cursor="hand2")



def prepare_key(key_str):
    key_bytes = base64.urlsafe_b64encode(key_str.encode()).rstrip(b"=")
    while len(key_bytes) < 43:
        key_bytes *= 2
    return key_bytes[:43] + b"="       # Un peu de sorcellerie ça fait toujours plaiz


def encrypt(key_str, val_str):
    key_bytes = prepare_key(key_str)
    return fernet.Fernet(key_bytes).encrypt(val_str.encode()).hex()


def decrypt(key_str, hex_token):
    key_bytes = prepare_key(key_str)
    return fernet.Fernet(key_bytes).decrypt(bytes.fromhex(hex_token)).decode()


def hash(message):
    return hashlib.sha224(message.encode()).hexdigest()
