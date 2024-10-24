from flask import Flask
from routes import blueprint as routes_blueprint
from dbconn import test_db_connection

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flaskadmin:Flask!1234@localhost:3306/invento'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Tester la connexion à la base de données
    if test_db_connection(app):
        print("Connexion à la base de données réussie.")
    else:
        print("Échec de la connexion à la base de données.")
    
    # Enregistrer les routes
    app.register_blueprint(routes_blueprint)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
