from . import config, bdd

#----------------------------- CLASSES DE DONNÉES ------------------------------


class DataClass(type):
    """Métaclasse des classes de données

    Toutes les classes construites sur cette métaclasse viennent interfacer une table SQLAlchemy, dont le nom (clé de bdd.tables) doit être précisée à la construction :
        def MaClasse(metaclass=DataClass, tablename=ma_table):
            ...

    Si déclarée, leur méthode __init__ doit attendre un unique argument optionnel représentant un objet de cette table :
            def __init__(self, bdd_item=None):
                ...

    Cette métaclasse transforme (ou crée) leur méthode __init__ de telle sorte que MaClasse puisse être utilisée
        - soit pour représenter une entrée existante de la table de données :
            MaClasse(item) -> objet MaClasse reprenant les propriétés de item

        - soit pour créer une nouvelle entrée dans cette table :
            MaClasse(col1=val1, col2=val2...) -> objet MaClasse ajouté à la session en cours. Tous les arguments obligatoires (NOT NULL) de <table> doivent dans ce cas être spécifiés et cohérents. Si auto-incrémentale, la clé primaire n'a pas besoin d'être spécifiée.

    Si [bdd_item] est fourni, tous les arguments nommés sont ignorés.
    Dans tous les cas, les instances de MaClasse possèdent les attributs
        item.bdd_table          objet SQLAlchemy fourni à la déclaration de la classe ;
        item.bdd_item           objet SQLAlchemy fourni ou créé à l'instanciation ;
        item.bdd_cols           liste des noms des colonnes de <table> ;
        item.<col>              pour chacune des colonnes de <table> (valeurs de item.bdd_cols).
    """
    @staticmethod
    def transform_init(initfunc, tablename):     # Définie à l'import, appelée à chaque création de classe
        """Décorateur transformant / créant les méthodes __init__ des classes de données"""
        def __init__(item, bdd_item=None, **kwargs):       # Définie à la création de classe, appellée à chque création d'instance
            table = bdd.tables.get(tablename)
            assert table, f"Table \"{tablename}\" introuvable"
            item.bdd_table = table
            item.bdd_cols = [col.key for col in table.__table__.columns]           # Noms des colonnes de la table

            if bdd_item:        # Création à partir d'un objet existant
                if not isinstance(bdd_item, table):
                    raise TypeError(f"Tentative de création un objet {type(item)} à partir d'un objet {type(bdd_item)}")
                item.bdd_item = bdd_item

            else:
                item.bdd_item = table(**kwargs)     # Création d'un nouvel objet BDD : si les kwargs ne sont pas bons, lève une erreur
                bdd.session.add(item.bdd_item)
                bdd.session.flush()         # Envoi de l'objet à la BDD, remplissage ID / valeurs par défaut

            for col in item.bdd_cols:       # Passage des attributs
                setattr(item, col, getattr(bdd_item, col))

            if initfunc:        # __init__ déclaré dans la définition de la classe :
                initfunc(item, bdd_item)        # Reste de l'initialisation

        return __init__

    def __new__(metacls, name, bases, namespace, tablename):
        """Méthode créant la classe"""
        namespace["__init__"] = metacls.transform_init(namespace.get("__init__"), tablename=tablename)        # Modification / création de cls.__init__
        super().__new__(metacls, name, bases, namespace)

    def __init__(cls, name, bases, namespace, **kwargs):
        """Méthode initialisant la nouvelle classe"""
        super().__init__(name, bases, namespace)



class Saison(metaclass=DataClass, tablename="saisons"):
    """Saison Qlturelle

    Classe de données liée à la table "saisons" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    # @dataclass
    # def __init__(self, bdd_saison):
    #     """Initialize self à partir d'une entrée de BDD existante"""
        # @dataclass => self.id, self.nom, self.promo_orga, self.debut, self.fin

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Saison #{self.id} ({self.nom})>"


class Salle(metaclass=DataClass, tablename="salles"):
    """Salle de spectacles

    Classe de données liée à la table "salles" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    # @dataclass
    # def __init__(self, bdd_salle):
    #     """Initialize self à partir d'une entrée de BDD existante"""
    #     # @dataclass => self.id, self.nom, self.description, self.image_path,
    #     #               self.url, self.adresse, self.latitude, self.longitude

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Salle #{self.id} ({self.nom})>"


class Participation(metaclass=DataClass, tablename="participations"):
    """Participation d'un client à une saison

    Classe de données liée à la table "participations" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    # @dataclass
    def __init__(self, bdd_participation):
        """Initialize self à partir d'une entrée de BDD existante"""
        # @dataclass => self.id, self.client_id, self.saison_id, self.mecontentement, self.fiche_path

        self.client = tools.get(config.clients, id=self.client_id)
        self.saison = tools.get(config.saisons, id=self.saison_id)

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Inscription #{self.id} ({self.client}/{self.saison})>"


class Client(metaclass=DataClass, tablename="clients"):
    """Client achetant des places

    Classe de données liée à la table "clients" : toutes les colonnes de cette tables (self.bdd_cols) scont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    # @dataclass
    def __init__(self, bdd_client):
        """Initialize self à partir d'une entrée de BDD existante"""
        # @dataclass => self.id, self.id_wp, self.nom, self.prenom, self.promo, self.autre, self.email
        #               self.mecontentement, self.mecontentement_precedent, self.saison_actuelle_mec, self.a_payer

        self.nomprenom = f"{self.nom.upper()} {self.prenom}"

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Client #{self.id} ({self.nomprenom})>"

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


class Voeu(metaclass=DataClass, tablename="voeux"):
    """Voeu / attribution d'un client pour un spectacle

    Classe de données liée à la table "voeux" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    # @dataclass
    def __init__(self, bdd_voeu):
        """Initialize self à partir d'une entrée de BDD existante"""
        # @dataclass => self.id, elf.client_id, self.spectacle_id, self.places_demandees,
        #               self.priorite, self.places_minimum, self.statut, self.places_attribuees

        self.client = tools.get(config.clients, id=self.client_id)
        self.spectacle = tools.get(config.spectacles, id=self.spectacle_id)

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Voeu #{self.id} ({self.client}/{self.spectacle})>"

    def delta_mec(self):
        """Mécontentement ajouté lors de l'attribution du voeu"""
        return -0.5**self.priorite

    def attribuer(self, places):
        """Définit le nombre de places attribuées du voeu à <places> et modifie le mécontentement du client en conséquence"""
        if (not self.places_attribuees) and places:         # Voeu -> attribution
            self.client.mecontentement += self.delta_mec()
        elif self.places_attribuees and (not places):       # Attribution -> voeu
            self.client.mecontentement -= self.delta_mec()

        self.client.a_payer = self.client.calcul_a_payer()
        self.places_attribuees = places


class Spectacle(metaclass=DataClass, tablename="spectacles"):
    """Spectacle pour lequel des places sont proposées

    Classe de données liée à la table "spectacles" : toutes les colonnes de cette tables (self.bdd_cols) sont des attributs des instances de cette classe, qui contient l'objet SQLAlchemy associé dans self.bdd_item
    """
    # @dataclass
    def __init__(self, bdd_spectacle):
        """Initialize self à partir d'une entrée de BDD existante"""
        # @dataclass => self.id, self.saison_id, self.nom, self.categorie, self.description, self.affiche_path,
        #               self.salle_id, self.dateheure, self.nb_tickets, self.unit_price, self.score

        self.date = self.dateheure.strftime("%d/%m/%Y") if self.dateheure else "???"
        self.heure = self.dateheure.strftime("%H:%M") if self.dateheure else "???"

        self.saison = tools.get(config.saisons, id=self.saison_id)
        self.salle = tools.get(config.salles, id=self.salle_id)

    def __repr__(self):
        """Returns repr(self)"""
        return f"<Spectacle #{self.id} ({self.nom})>"

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
