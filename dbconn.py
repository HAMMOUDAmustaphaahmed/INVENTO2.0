from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

db = SQLAlchemy()

def test_db_connection(app):
    db.init_app(app)
    try:
        # Créer un moteur pour tester la connexion
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        # Établir une connexion
        with engine.connect() as connection:
            return True  # La connexion a réussi
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return False  # La connexion a échoué
