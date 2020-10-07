import tkinter as tk
from tkinter import ttk

from . import config, bdd, tools

#----------------------------- CLASSES DE DONNÉES ------------------------------


class DataClass():
    """Classe de base des classes de données

    Toutes les classes héritant de cette classe viennent interfacer une table SQLAlchemy, dont le nom (clé de bdd.tables) doit être précisée à la construction :
        def MaClasse(DataClass, tablename=ma_table):
            ...

    Si déclarée, leur méthode __init__ doit attendre un unique argument optionnel représentant un objet de cette table :
            def __init__(self, bdd_item=None):
                super().__init__(bdd_item)
                ...

    DataClass.__init__ permet à MaClasse d'être utilisée
        - soit pour représenter une entrée existante de la table de données :
            MaClasse(item) -> objet MaClasse reprenant les propriétés de item

        - soit pour créer une nouvelle entrée dans cette table :
            MaClasse(col1=val1, col2=val2...) -> objet MaClasse ajouté à la session en cours. Tous les arguments obligatoires (NOT NULL) de <table> doivent dans ce cas être spécifiés et cohérents. Si auto-incrémentale, la clé primaire n'a pas besoin d'être spécifiée.

    Si [bdd_item] est fourni, tous les arguments nommés sont ignorés.
    Dans tous les cas, les instances de MaClasse possèdent les attributs
        item.table              objet SQLAlchemy fourni à la déclaration de la classe ;
        item.bdd_item           objet SQLAlchemy fourni ou créé à l'instanciation ;
        item.bdd_cols           liste des noms des colonnes de <table> ;
        item.<col>              pour chacune des colonnes de <table> (valeurs de item.bdd_cols).
    """
    subclasses = []         # Classes héritant de DataClass
    pending_adds = []       # Objets nouvellement créés (flush mais pas commit), pour toutes les classes
    pending_modifs = []     # Tuples (objet, colonne, valeur) des modifications d'instances DataClass pas encore commit

    def __init__(self, bdd_item=None, **kwargs):
        if type(self) is DataClass:
            raise TypeError("DataClass n'est pas directement utilisable. Utiliser des classes dérivées.")
        if not self.session:
            raise RuntimeError(f"Table \"{self.tablename}\" pas encore armée")

        if bdd_item:        # Conversion d'une entrée existante
            if isinstance(bdd_item, self.table):
                self.bdd_item = bdd_item
            else:
                raise TypeError(f"Tentative de conversion d'un objet {type(bdd_item)} en objet {type(self)}")

        else:               # Création d'une nouvelle entrée
            self.bdd_item = self.table(**kwargs)     # Création d'un nouvel objet BDD : si les kwargs ne sont pas bons, lève une erreur
            self.session.add(self.bdd_item)
            self.session.flush()                    # Envoi de l'objet à la BDD, remplissage ID / valeurs par défaut
            self.pending_adds.append(self)
        #
        # for col in self.bdd_cols:       # Passage des attributs
        #     setattr(self, col, getattr(self.bdd_item, col))

    def __repr__(self):
        """Returns repr(self)"""
        return f"""<{type(self).__name__} #{getattr(self, self.primary_col, None)}>"""


    def __init_subclass__(cls, tablename, **kwargs):
        """Méthode de classe initialisant les classes héritant de celle-ci"""
        cls.subclasses.append(cls)      # Enregistrement de la classe

        cls.tablename = tablename
        cls.session = None      # On ne peut pas accéder à la table dès l'initialisation (pas encore connecté) : on le fera plus tard

        super().__init_subclass__(**kwargs)


    @classmethod
    def arm_dataclass(cls, session, tables):
        """Définit cls.session, cls.table... et toutes les propriétés d'accès / modification des colonnes à partir d'une session active SQLAlchemy et de la liste des tables associées"""
        cls.session = session
        cls.table = tables[cls.tablename]
        cls.raw_cols = cls.table.__table__.columns
        cls.primary_col = next(col.key for col in cls.raw_cols if col.primary_key)
        cls.bdd_cols = [col.key for col in cls.raw_cols]           # Noms des colonnes de la table

        def fget_for(col):
            def fget(self):             # Méthode appelée quand on ACCÈDE À self.<col>
                return getattr(self.bdd_item, col)          # on renvoie l'attribut de l'objet de BDD
            return fget

        def fset_for(col):
            def fset(self, new):        # Méthode appelée quand on MODIFIE self.<col>
                actual = getattr(self.bdd_item, col)
                if new != actual:                           # si modification effective :
                    if config.DEBUG: print(f" > MODIFIED {self}.{col} : {actual} -> {new}")
                    setattr(self.bdd_item, col, new)                    # on modifie l'objet de BDD
                    bdd.flag_modified(self.bdd_item, col)               # on signale la modif à SQLAlchemy
                    self.pending_modifs.append((self, col, new))        # et on enregistre la modif pour nous
            return fset

        def fdel_for(col):              # Méthode appelée quand on SUPPRIME (del) self.<col>
            def fdel(self):
                raise TypeError(f"del {self}.{col} : Impossible de supprimer un attribut de BDD !")
            return fdel

        for rcol in cls.raw_cols:    # Pour chaque colonne, on définit la propriété (au niveau de la table) : comportement pour accéder à / modifier / supprimer self.<col> (ex. client.nom, voeu.places_demandees)...
            setattr(cls, rcol.key, property(fget_for(rcol.key), fset_for(rcol.key), fdel_for(rcol.key), f"Attribut de BDD : colonne {rcol.key} (type {rcol.type})"))



class Saison(DataClass, tablename="saisons"):
    """Saison Qlturelle

    Classe de données liée à la table "saisons" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    pass    # DataClass => self.id, self.nom, self.promo_orga, self.debut, self.fin


class Salle(DataClass, tablename="salles"):
    """Salle de spectacles

    Classe de données liée à la table "salles" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    pass    # DataClass => self.id, self.nom, self.description, self.image_path,
            #              self.url, self.adresse, self.latitude, self.longitude


class Participation(DataClass, tablename="participations"):
    """Participation d'un client à une saison

    Classe de données liée à la table "participations" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    def __init__(self, bdd_participation=None, **kwargs):
        """Initialize self à partir d'une entrée de BDD existante"""
        super().__init__(bdd_participation, **kwargs)
        # DataClass => self.id, self.client_id, self.saison_id, self.mecontentement, self.fiche_path

        self.client = tools.get(config.clients, id=self.client_id)
        self.saison = tools.get(config.saisons, id=self.saison_id)


class Client(DataClass, tablename="clients"):
    """Client achetant des places

    Classe de données liée à la table "clients" : toutes les colonnes de cette tables (self.bdd_cols) scont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    def __init__(self, bdd_client=None, **kwargs):
        """Initialize self à partir d'une entrée de BDD existante"""
        super().__init__(bdd_client, **kwargs)
        # DataClass => self.id, self.id_wp, self.nom, self.prenom, self.promo, self.autre, self.email
        #              self.mecontentement, self.mecontentement_precedent, self.saison_actuelle_mec, self.a_payer
        self.mecontentement = self.mecontentement or 0

        self.nomprenom = f"{self.nom.upper()} {self.prenom}"

    def voeux(self):
        """Renvoie la liste des voeux émis par ce client"""
        return [voeu for voeu in config.voeux if voeu.client_id == self.id]

    def attributions(self):
        """Renvoie la liste des voeux exaucés (places attribués) pour ce client"""
        return [voeu for voeu in self.voeux() if voeu.places_attribuees]

    def nb_places_demandees(self):
        """Renvoie le nombre total de places demandées par ce client"""
        return sum(voeu.places_demandees or 0 for voeu in self.voeux())

    def nb_places_attribuees(self):
        """Renvoie le nombre total de places attribuées à ce client"""
        return sum(voeu.places_attribuees for voeu in self.attributions())

    def calcul_a_payer(self):
        """Renvoie la somme totale due par ce client à ce stade de l'attribution"""
        return sum(voeu.places_attribuees*voeu.spectacle.unit_price for voeu in self.attributions())

    def verif_priorites(self):
        """Affiche un avertissement si les priorités du client sont illégales (différentes de 1, 2, ..., N_voeux)"""
        priorites = sorted(voeu.priorite for voeu in self.voeux())
        if priorites != list(range(1, len(priorites) + 1)):
            tk.messagebox.showwarning(title="Priorités illégales", message=f"Priorité des voeux illégale pour {self.nomprenom} :\n{priorites}")

    def init_mecontentement(self):
        """Initialise le mécontentement du client à partir des différentes sources liées au client et à ses voeux (exaucés et comblés)"""
        # Si la saison actuelle n'est pas encore celle là, on change et on enregistre le mécontentement "actuel" comme mécontentement précédent
        if self.saison_actuelle_mec != config.saison.id:
            self.mecontentement_precedent = self.mecontentement
            self.saison_actuelle_mec = config.saison.id

        # Mécontentement de la saison précédente + celui ajouté arbitrairement dans la fiche élève :
        self.mecontentement = self.mecontentement_precedent or 0

        # Mécontentement lié au nombre de voeux : si l'élève a moins de voeux que le nombre moyen, son mécontentement augmente, il est favorisé :
        self.mecontentement += 0.9**(len(self.voeux()) - 1)

        # Idem pour le nombre total de places demandées :
        self.mecontentement += 2/self.nb_places_demandees()

        # Bonus/malus selon la promo :
        if self.promo == config.promo_1A:
            self.mecontentement += config.bonus_1A
        elif self.promo == config.promo_1A - 1:        # 2A
            self.mecontentement += config.bonus_2A
        elif self.promo == config.promo_1A - 2:        # 3A
            self.mecontentement += config.bonus_3A
        elif self.promo == config.promo_1A - 3:        # 4A
            self.mecontentement += config.bonus_4A
        else:
            self.mecontentement += config.bonus_autre

        # Malus selon les voeux déjà attribués pour cette saison : -0.5^priorité par voeu comblé
        for voeu in self.attributions():
            self.mecontentement += voeu.delta_mec()


class Voeu(DataClass, tablename="voeux"):
    """Voeu / attribution d'un client pour un spectacle

    Classe de données liée à la table "voeux" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    def __init__(self, bdd_voeu=None, **kwargs):
        """Initialize self à partir d'une entrée de BDD existante"""
        super().__init__(bdd_voeu, **kwargs)
        # DataClass => self.id, self.client_id, self.spectacle_id, self.places_demandees,
        #              self.priorite, self.places_minimum, self.statut, self.places_attribuees

        self.client = tools.get(config.clients, id=self.client_id)
        self.spectacle = tools.get(config.spectacles, id=self.spectacle_id)

    def delta_mec(self):
        """Mécontentement ajouté lors de l'attribution du voeu"""
        return -0.5**self.priorite

    def attribuer(self, places):
        """Définit le nombre de places attribuées du voeu à <places> et modifie le mécontentement et la somme à payer du client en conséquence"""
        if (not self.places_attribuees) and places:         # Voeu -> attribution
            self.client.mecontentement += self.delta_mec()
        elif self.places_attribuees and (not places):       # Attribution -> voeu
            self.client.mecontentement -= self.delta_mec()

        self.places_attribuees = places
        self.client.a_payer = self.client.calcul_a_payer()


class Spectacle(DataClass, tablename="spectacles"):
    """Spectacle pour lequel des places sont proposées

    Classe de données liée à la table "spectacles" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    def __init__(self, bdd_spectacle=None, **kwargs):
        """Initialize self à partir d'une entrée de BDD existante"""
        super().__init__(bdd_spectacle, **kwargs)
        # DataClass => self.id, self.saison_id, self.nom, self.categorie, self.description, self.affiche_path,
        #              self.salle_id, self.dateheure, self.nb_tickets, self.unit_price, self.score

        self.date = self.dateheure.strftime("%d/%m/%Y") if self.dateheure else "???"
        self.heure = self.dateheure.strftime("%H:%M") if self.dateheure else "???"

        self.saison = tools.get(config.saisons, id=self.saison_id)
        self.salle = tools.get(config.salles, id=self.salle_id)

    def lieu(self):
        """Renvoie le nom de la salle de ce spectacle"""
        return self.salle.nom if self.salle else "???"

    def voeux(self):
        """Renvoie la liste des voeux émis pour ce spectacle"""
        return [voeu for voeu in config.voeux if voeu.spectacle_id == self.id]

    def attributions(self):
        """Renvoie la liste des voeux attribués pour ce spectacle"""
        return [voeu for voeu in self.voeux() if voeu.places_attribuees]

    def nb_places_demandees(self):
        """Renvoie le nombre total de places demandées pour ce spectacle"""
        return sum(voeu.places_demandees or 0 for voeu in self.voeux())

    def nb_places_attribuees(self):
        """Renvoie le nombre total de places attribuées pour ce spectacle"""
        return sum(voeu.places_attribuees or 0 for voeu in self.voeux())

    def nb_places_restantes(self):
        """Renvoie le nombre total de places encore disponibles pour ce spectacle"""
        return (self.nb_tickets - self.nb_places_attribuees())

    def liste_eleve_desirant_spec(self):
        """Prend un objet spectacle en argument et renvoie une liste de type ['Vidon Guillaume 3 places voeu1", "Mosso ...']"""
        L = []
        for voeu in self.voeux():
            client = voeu.client
            L.append(f"{client.prenom} {client.nom} \t {voeu.places_demandees} places demandées - vœu n° {voeu.priorite}")
        return L

    def liste_eleve_ayant_spec(self):
        """Prend un objet spectacle en argument et renvoie une liste de type ['Vidon Guillaume 3 places voeu1", "Mosso ...']"""
        L = []
        for voeu in self.voeux():
            if voeu.places_attribuees:
                client = voeu.client
                L.append(f"{client.prenom} {client.nom} \t {voeu.places_attribuees} places attribuées / {voeu.places_demandees} demandées - vœu n° {voeu.priorite}")
        return L

    def nbplacesamodifier(self):
        """Méthode d'un spectacle qui renvoie le nombre de places supplémentaires à demander ou le nombre à retirer"""
        if (nbplacesspectacle(self) > self.places_demandees):
            return ("Il faudrait demander " + str(nbplacesspectacle(self)-self.places_demandees) + " places en plus")
        else:
            return ("Il faudrait retirer " + str(self.places_demandees-nbplacesspectacle(self)) + " places")
