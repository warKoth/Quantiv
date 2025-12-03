import sqlite3


class Database:
    """Classe base de gestion de la base de données SQLite."""

    def __init__(self, db_name:str = "quantivdata.db"):
        """Initialise la connexion à la base de données SQLite.

        Args:
            db_name (str): Le nom du fichier de la base de données SQLite.
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Crée les tables nécessaires dans la base de données (si elles n'existent pas déjà)."""

        