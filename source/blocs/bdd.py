import sqlalchemy
import sqlalchemy.ext.automap
import sqlalchemy.orm
import sqlalchemy.exc

from . import config


SQLAlchemyError = sqlalchemy.exc.SQLAlchemyError
flag_modified = sqlalchemy.orm.attributes.flag_modified


engine = None
base = None
tables = {}
session = None


def connect():
    """Se connecte à la BDD, affecte `engine` et `base` et renvoie un objet Session"""

    global engine, base, tables, session

    assert config.DATABASE_URI, "Tentative de connexion BDD avant déchiffrement de l'URI"
    engine = sqlalchemy.create_engine(config.DATABASE_URI, echo=config.DEBUG, pool_pre_ping=True)           # Moteur SQL : connexion avec le serveur

    base = sqlalchemy.ext.automap.automap_base()                                # Récupération des tables depuis le shéma de la base
    base.prepare(engine, reflect=True)

    tables = dict(base.classes.items())

    for tablename, table in base.classes.items():                               # Ajout des tables aux globals, sous nom CapWords
        classname = tablename.title().replace("_", "")
        globals()[classname] = table

    Session = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)         # Classe Session : ses instances servent à communiquer avec la base SQL

    session = Session()
