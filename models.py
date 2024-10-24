from dbconn import db

# Définition du modèle de la base de données pour les produits, par exemple
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Product {self.name}>"

# Fonction pour créer les tables dans la base de données
def init_db():
    db.create_all()
