from flask import Flask,render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Numeric
from werkzeug.security import check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flaskadmin:Flask!1234@localhost:3306/invento'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'invento_clé_secrète'

# Initialize SQLAlchemy with the app
db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('signin.html')

# Route for login
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        print(f"Username: {username}")
        print(f"Password: {password}")

        # Fetch the user from the database
        user = User.query.filter_by(username=username).first()

        # Check if user exists
        if user is None:
            flash("Nom d'utilisateur ou mot de passe incorrect !", "danger")
           
        # Check if the password matches
        if user and check_password_hash(user.password, password):
           
            session['role'] = user.role  # Store the username in the session
            return redirect(url_for("admin"))  # Redirect to the admin page
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect !", "danger")  # Provide feedback to the user
    
    return render_template("signin.html")

@app.route('/logout')
def logout():
        session.clear()  # Efface la session pour déconnecter l'utilisateur
        return redirect(url_for('login'))

# Route pour la page d'administration
@app.route('/admin')
def admin():
    articles_data = Article.query.all()
    articles_count=0
    quantite_totale=0
    notification_count_quantite=0
    for article in articles_data:
        articles_count+=1
        quantite_totale += article.quantite  # Ajoute la quantité de chaque article
        if article.quantite <= article.quantite_min:
             notification_count_quantite +=1
    
    achats_data = Achat.query.all()
    achats_count=0
    achat_quantite_totale=0
    achat_prix_totale=0
    for achat in achats_data:
        achats_count+=1
        achat_quantite_totale += achat.quantite  # Ajoute la quantité de chaque article
        achat_prix_totale += achat.prix_achat

    ventes_data = Vente.query.all()
    ventes_count=0
    vente_quantite_totale=0
    vente_prix_totale=0
    for vente in ventes_data:
        ventes_count+=1
        vente_quantite_totale += vente.quantite  # Ajoute la quantité de chaque article
        vente_prix_totale += vente.prix_vente * vente.quantite 
    
    fournisseurs_data=Fournisseur.query.all()
    fournisseurs_count = Fournisseur.query.count()
    usines_data=Usine.query.all()
    usines_count=Usine.query.count()
    demandes_ventes_data=DemandeVente.query.all()
    demandes_achats_data=DemandeAchat.query.all()
    demandes_ventes_count=DemandeVente.query.count()
    demandes_achats_count=DemandeAchat.query.count()
    users_data=User.query.all()
    users_count=User.query.count()
    confirmation_sortie_data=DemandeVente.query.filter_by(etat=0,reception=1).all()
    confirmation_sortie_count=DemandeVente.query.filter_by(etat=0,reception=1).count()
    confirmation_arriver_data=DemandeVente.query.filter_by(etat=0,reception=1).all()
    confirmation_arriver_count=DemandeVente.query.filter_by(etat=0,reception=1).count()

    return render_template('index.html',users_count=users_count,
                           users_data=users_data,
                           articles_count=articles_count,
                           achats_count=achats_count,ventes_count=ventes_count,
                           usines_count=usines_count,
                           fournisseurs_count=fournisseurs_count,
                           demandes_achats_data=demandes_achats_data,
                           demandes_ventes_data=demandes_ventes_data,
                           demandes_achats_count=demandes_achats_count,
                           demandes_ventes_count=demandes_ventes_count,
                           notification_count_quantite=int(notification_count_quantite),
                           quantite_totale=quantite_totale,
                           articles=articles_data,
                           achats=achats_data,
                           achat_quantite_totale=achat_quantite_totale,
                           achat_prix_totale=achat_prix_totale,
                           ventes=ventes_data,
                           vente_prix_totale=vente_prix_totale,
                           quantite_vente_totale=vente_quantite_totale,
                           prix_vente_totale=vente_prix_totale,
                           confirmation_arriver_data=confirmation_arriver_data,
                           confirmation_arriver_count=confirmation_arriver_count,
                           confirmation_sortie_data=confirmation_sortie_data,
                           confirmation_sortie_count=confirmation_sortie_count,
                           fournisseurs_data=fournisseurs_data,
                           usines_data=usines_data)
       
@app.route('/ajouter_article',methods=["GET", "POST"])
def ajouter_article():
       
            if request.method == 'POST':
                # Retrieve form data
                article_data = {
                'code_article': request.form.get('code_article'),
                'libelle_article': request.form.get('libelle_article'),
                'prix_achat': request.form.get('prix_achat'),
                'assignation': request.form.get('assignation'),
                'quantite': request.form.get('quantite'),
                'fournisseur': request.form.get('fournisseur'),
                'quantite_min': request.form.get('quantite_min'),
                'image': request.form.get('image')
            }

                # Call the function to add user
                if fun_ajouter_article(article_data):
                    message = "Article ajouté avec succès."
                    # Return a JavaScript alert with the message and then redirect
                    return f"""<script>alert("{message}");window.location.href = "{url_for('index')}";</script>"""
                else:
                    message = "Erreur lors de l'ajout de l'article 1."
                    # Return a JavaScript alert with the message and then redirect
                    return f"""<script>alert("{message}");window.location.href = "{url_for('ajouter_article')}";</script>"""
            return render_template('ajouter_article.html')
     
    
    


    # routes.py

@app.route('/rechercher_article', methods=['GET', 'POST'])
def rechercher_article():
    
        if request.method == 'POST':
            code_article = request.form.get("code_article")
            article = fun_info_article(code_article)
            if article:
                return render_template('editer_article.html', article=article)
            else:
                message = "Article not found."

                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('editer_article')}";</script>"""
                
@app.route('/editer_article', methods=['POST','GET'])
def editer_article():
    
        code_article = request.form.get('code_article')
        action = request.form.get('action')  # Récupérer l'action (edit ou delete)
        article = fun_info_article(code_article)
       
        if action == 'edit':
            if article:
                # Mettre à jour les informations de l'article
                article.code_article = request.form.get('code_article')
                article.libelle_article = request.form.get('libelle_article')
                article.prix_achat = request.form.get('prix')
                article.assignation = request.form.get('assignation')
                article.quantite = request.form.get('quantite')
                article.fournisseur = request.form.get('fournisseur')
                article.quantite_min = request.form.get('quantite_min')
                article.image = request.form.get('image')
                print(article.image)
                print(len(article.image))
               

                

                # Valider les données et committer les mises à jour
                try:
                    
                    db.session.commit()
                    message = "Article modifié avec succès."
                    # Return a JavaScript alert with the message and then redirect
                    return f"""<script>alert("{message}");window.location.href = "{url_for('editer_article')}";</script>"""
                    
                except :
                    db.session.rollback()
                    message = "Erreur lors de la mise à jour de l'article. 1 "
                    # Return a JavaScript alert with the message and then redirect
                    return f"""<script>alert("{message}");window.location.href = "{url_for('editer_article')}";</script>"""
            else:
                message = "Article not found."
                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('editer_article')}";</script>"""

        elif action == 'delete':
            if article:
                # Supprimer l'article de la base de données
                db.session.delete(article)
                db.session.commit()
                message = "Article supprimé avec succès."
                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('editer_article')}";</script>"""

                
               
            else:
                message = "Article not found."
                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('editer_article')}";</script>"""

        return render_template('editer_article.html')  # Rediriger si aucune action trouvée
    
@app.route('/supprimer_article')
def supprimer_article():
    code_article = request.form.get('code_article')  # Get the article code from the form

    # Find the article in the database
    article = Article.query.filter_by(code=code_article).first()

    if article:
        db.session.delete(article)  # Delete the article if found
        db.session.commit()  # Commit the transaction
        message = "Article deleted successfully!."
        # Return a JavaScript alert with the message and then redirect
        return f"""<script>alert("{message}");window.location.href = "{url_for('editer_article')}";</script>"""
    else:
                message = "Article not found."
                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('editer_article')}";</script>"""




    # routes.py
        




@app.route('/ajouter_user', methods=['GET', 'POST'])
def ajouter_user():
        
            if request.method == 'POST':
                # Retrieve form data
                user_data = {
                    'username': request.form['username'],
                    'password': request.form['password'],
                    'emplacement': request.form['emplacement'],
                    'role': request.form['role'],
                    'numero_telephone': request.form['numero_telephone']
                }

                # Call the function to add user
                if fun_ajouter_user(user_data):
                    flash("Utilisateur ajouté avec succès", "success")
                else:
                    flash("Erreur lors de l'ajout de l'utilisateur", "danger")
            return render_template('ajouter_user.html')
        

@app.route('/rechercher_user', methods=['GET', 'POST'])
def rechercher_user():
    
        if request.method == 'POST':
            username = request.form.get("username")
            user = fun_info_user(username)
            if user:
                return render_template('editer_user.html', user=user)
            else:
                message = "user not found."

                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('editer_user')}";</script>"""
        return render_template('editer_user.html')
        

        
@app.route('/editer_user', methods=['POST', 'GET'])
def editer_user():
    if request.method == 'POST':
        print(request.form)  # Debugging: Print all submitted form data
        id_user = request.form.get('id')
        action = request.form.get('action')
        print(f"Received id_user: {id_user}, action: {action}")

        user = User.query.get(id_user)
        if not user:
            print("user not found.")
            message = "user not found."
            return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_user')}";</script>"""

        if action == 'edit':
            user.username = request.form.get('username')  # Correct field name
            new_password = request.form.get('password')
            if new_password == user.password :
                user.password=new_password
            else :
                hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
                user.password=hashed_password
            user.emplacement = request.form.get('emplacement')
            user.numero_telephone = request.form.get('numero_telephone')
            user.role = request.form.get('role')  # Make sure this is in the form
            print("Updating user details")
            print(user)
            try:
                db.session.commit()
                message = "user modifié avec succès."
                return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_user')}";</script>"""
            except Exception as e:
                db.session.rollback()
                message = f"Erreur lors de la mise à jour du user: {e}"
                print(message)
                return f"""<script>alert("{message}");</script>"""

        elif action == 'delete':
            print("Attempting to delete user")
            try:
                db.session.delete(user)
                db.session.commit()
                message = "user supprimé avec succès."
                return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_user')}";</script>"""
            except Exception as e:
                db.session.rollback()
                message = f"Erreur lors de la suppression user: {e}"
                print(message)
                return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_user')}";</script>"""

    return render_template('editer_user.html')

    
@app.route('/supprimer_user')
def supprimer_user():

    username = request.form.get('username') 
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)  
        db.session.commit() 
        message = "User deleted successfully!."
        return f"""<script>alert("{message}");window.location.href = "{url_for('editer_article')}";</script>"""
    else:
        message = "User not found."
        return f"""<script>alert("{message}");window.location.href = "{url_for('editer_article')}";</script>"""
    
        
        

@app.route('/ajouter_usine',methods=['GET', 'POST'])
def ajouter_usine():
       
            if request.method == 'POST':
                # Retrieve form data
                usine_data = {
                    'nom_usine': request.form['nom_usine'],
                    'region': request.form['region'],
                    'adresse': request.form['adresse'],
                    'latitude': request.form['latitude'],
                    'longitude': request.form['longitude'],
                    'telephone': request.form['telephone'],
                    'etat': request.form['etat']
                }

                # Call the function to add user
                if fun_ajouter_usine(usine_data):
                    flash("Usine ajouté avec succès", "success")
                else:
                    flash("Erreur lors de l'ajout de l'usine", "danger")
            return render_template('ajouter_usine.html')
        


   
        
@app.route('/rechercher_usine', methods=['GET', 'POST'])
def rechercher_usine():
    
        if request.method == 'POST':
            nom_usine = request.form.get("nom_usine")
            usine = fun_info_usine(nom_usine)
            if usine:
                return render_template('editer_usine.html', usine=usine)
            else:
                message = "Usine not found."

                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('editer_usine')}";</script>"""
        return render_template('editer_usine.html')
        
    
        
@app.route('/editer_usine', methods=['POST', 'GET'])
def editer_usine():
    if request.method == 'POST':
        print(request.form)  # Debugging: Print all submitted form data
        id_usine = request.form.get('id_usine')
        action = request.form.get('action')
        print(f"Received id_usine: {id_usine}, action: {action}")

        usine = Usine.query.get(id_usine)
        if not usine:
            print("Usine not found.")
            message = "Usine not found."
            return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_usine')}";</script>"""

        if action == 'edit':
            usine.nom_usine = request.form.get('nom_usine')  # Correct field name
            usine.region = request.form.get('region')
            usine.adresse = request.form.get('adresse')
            usine.latitude = request.form.get('latitude')
            usine.longitude = request.form.get('longitude')
            usine.telephone = request.form.get('telephone')
            usine.etat = request.form.get('etat')  # Make sure this is in the form
            print("Updating usine details")
            print(usine)
            try:
                db.session.commit()
                message = "Usine modifié avec succès."
                return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_usine')}";</script>"""
            except Exception as e:
                db.session.rollback()
                message = f"Erreur lors de la mise à jour du usine: {e}"
                print(message)
                return f"""<script>alert("{message}");</script>"""

        elif action == 'delete':
            print("Attempting to delete usine")
            try:
                db.session.delete(usine)
                db.session.commit()
                message = "Usine supprimé avec succès."
                return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_usine')}";</script>"""
            except Exception as e:
                db.session.rollback()
                message = f"Erreur lors de la suppression usine: {e}"
                print(message)
                return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_usine')}";</script>"""

    return render_template('editer_usine.html')

    
@app.route('/supprimer_usine')
def supprimer_usine():
        
            return render_template('editer_usine.html')
        
        
@app.route('/ajouter_fournisseur',methods=['GET', 'POST'])
def ajouter_fournisseur():
        
            if request.method == 'POST':
                # Retrieve form data
                fournisseur_data = {
                    'nom_fournisseur': request.form['nom_fournisseur'],
                    'matricule_fiscale': request.form['matricule_fiscale'],
                    'adresse': request.form['adresse'],
                    'telephone': request.form['telephone'],
                }

                # Call the function to add user
                if fun_ajouter_fournisseur(fournisseur_data):
                    flash("Fournisseur ajouté avec succès", "success")
                else:
                    flash("Erreur lors de l'ajout de fournisseur", "danger")
            return render_template('ajouter_fournisseur.html')
        
        
        
@app.route('/rechercher_fournisseur', methods=['GET', 'POST'])
def rechercher_fournisseur():
    
        if request.method == 'POST':
            nom_fournisseur = request.form.get("nom_fournisseur")
            fournisseur = fun_info_fournisseur(nom_fournisseur)
            if fournisseur:
                return render_template('editer_fournisseur.html', fournisseur=fournisseur)
            else:
                message = "Fournisseur not found."

                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('editer_fournisseur')}";</script>"""
        return render_template('editer_fournisseur.html')
        
    
        
@app.route('/editer_fournisseur', methods=['POST', 'GET'])
def editer_fournisseur():
    if request.method == 'POST':
        id_fournisseur = request.form.get('id_fournisseur')  # Retrieve id_fournisseur
        action = request.form.get('action')  # Retrieve the action (edit or delete)
        print(f"Received id_fournisseur: {id_fournisseur}, action: {action}")  # Debug statement

        # Use ID to find the fournisseur
        fournisseur = Fournisseur.query.get(id_fournisseur)
        if not fournisseur:
            print("Fournisseur not found.")  # Debug statement
            message = "Fournisseur not found."
            return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_fournisseur')}";</script>"""

        if action == 'edit':
            # Update fournisseur details
            fournisseur.nom_fournisseur = request.form.get('nom_fournisseur')
            fournisseur.matricule_fiscale = request.form.get('matricule_fiscale')
            fournisseur.adresse = request.form.get('adresse')
            fournisseur.telephone = request.form.get('telephone')
            print("Updating fournisseur details")  # Debug statement
            print(fournisseur)
            try:
                db.session.commit()
                message = "Fournisseur modifié avec succès."
                return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_fournisseur')}";</script>"""
            except Exception as e:
                db.session.rollback()
                message = f"Erreur lors de la mise à jour du fournisseur: {e}"
                print(message)  # Debug statement
                return f"""<script>alert("{message}");</script>"""

        elif action == 'delete':
            # Delete the fournisseur
            print("Attempting to delete fournisseur")  # Debug statement
            try:
                db.session.delete(fournisseur)
                db.session.commit()
                message = "Fournisseur supprimé avec succès."
                return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_fournisseur')}";</script>"""
            except Exception as e:
                db.session.rollback()
                message = f"Erreur lors de la suppression du fournisseur: {e}"
                print(message)  # Debug statement
                return f"""<script>alert("{message}");window.location.href = "{url_for('rechercher_fournisseur')}";</script>"""

    # Render the edit form if the request method is GET
    return render_template('editer_fournisseur.html')  # Show the form if no action found

       
        
@app.route('/supprimer_fournisseur')
def supprimer_fournisseur():
        
            return render_template('editer_fournisseur.html')
        


@app.route('/ajouter_demande_achat',methods=["GET", "POST"])
def ajouter_demande_achat():
       
            if request.method == 'POST':
                # Retrieve form data
                demande_achat_data = {
                'code_article': request.form.get('code_article'),
                'libelle_article': request.form.get('libelle_article'),
                'assignation': request.form.get('assignation'),
                'quantite': request.form.get('quantite'),
            }

                # Call the function to add user
                if fun_ajouter_demande_achat(demande_achat_data):
                    message = "Demande d'achat ajouté avec succès."
                    # Return a JavaScript alert with the message and then redirect
                    return f"""<script>alert("{message}");window.location.href = "{url_for('admin')}";</script>"""
                else:
                    message = "La quantité de la demande dépasse la quantité dans le stock"
                    # Return a JavaScript alert with the message and then redirect
                    return f"""<script>alert("{message}");window.location.href = "{url_for('ajouter_demande_achat')}";</script>"""
            return render_template('ajouter_demande_achat.html')
     


    


    # routes.py

@app.route('/rechercher_demande_achat', methods=['GET', 'POST'])
def rechercher_demande_achat():
        demandes_achats=DemandeAchat.query.all()
        if request.method == 'POST':
            code_demande = request.form.get("code_demande")
            demande_achat = fun_info_demande_achat(code_demande)
            if demande_achat:
                return render_template('confirmer_demande_achat.html', demande_achat=demande_achat,demandes_achats=demandes_achats)
            else:
                message = "Demande achat not found."

                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('confirmer_demande_achat')}";</script>"""
                
@app.route('/confirmer_demande_achat', methods=['POST','GET'])
def confirmer_demande_achat():
        demandes_achats=DemandeAchat.query.all()
        code_demande = request.form.get('code_demande')
        action = request.form.get('action')  # Récupérer l'action (edit ou delete)
        demande_achat = fun_info_demande_achat(code_demande)
       
        if action == 'confirmer':
            if demande_achat:
                # Mettre à jour les informations de l'article
                demande_achat.code_article = request.form.get('code_article')
                demande_achat.libelle_article = request.form.get('libelle_article')
                demande_achat.prix_achat = request.form.get('prix')
                demande_achat.assignation = request.form.get('assignation')
                demande_achat.quantite = request.form.get('quantite')
                demande_achat.fournisseur=request.form.get('fournisseur')
                demande_achat.prix_achat=request.form.get('prix_achat')
                demande_achat.etat=0
                # Valider les données et committer les mises à jour
                try:
                    
                    db.session.commit()
                    message = "Demande d'achat modifié avec succès."
                    # Return a JavaScript alert with the message and then redirect
                    return f"""<script>alert("{message}");window.location.href = "{url_for('confirmer_demande_achat')}";</script>"""
                    
                except :
                    db.session.rollback()
                    message = "Erreur lors de la mise à jour de la demande d'achat. 1 "
                    # Return a JavaScript alert with the message and then redirect
                    return f"""<script>alert("{message}");window.location.href = "{url_for('confirmer_demande_achat')}";</script>"""
            else:
                message = "Demande d'achat not found."
                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('confirmer_demande_achat')}";</script>"""

        elif action == 'delete':
            if demande_achat:
                # Supprimer l'article de la base de données
                demande_achat.etat=2
                demande_achat.reception=2
                db.session.commit()
                message = "Demande d'achat supprimé avec succès."
                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('confirmer_demande_achat')}";</script>"""

                
               
            else:
                message = "Demande not found."
                # Return a JavaScript alert with the message and then redirect
                return f"""<script>alert("{message}");window.location.href = "{url_for('confirmer_demande_achat')}";</script>"""

        return render_template('confirmer_demande_achat.html',demandes_achats=demandes_achats)  # Rediriger si aucune action trouvée
    



def fun_ajouter_user(data):
    try:
        # Hash the password
        password=data['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create a new user
        new_user = User(
            username=data['username'],
            password=hashed_password,
            emplacement=data['emplacement'],
            role=data['role'],
            numero_telephone=data['numero_telephone']
        )
        # Add and commit to the database
        db.session.add(new_user)
        db.session.commit()
        fun_history_ajouter_user(data)
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'utilisateur : {e}")
        db.session.rollback()  # Roll back changes on error
        return False

def fun_ajouter_demande_achat(data):
    try:        
        # Create a new Article
        new_demande_achat = DemandeAchat(
            code_article=data['code_article'],
            libelle_article=data['libelle_article'],
            assignation=data['assignation'],
            quantite=data['quantite'],
            etat=1,
            date=datetime.now(timezone.utc),
            reception=1,
            
        )
        article=Article.query.filter_by(code_article=new_demande_achat.code_article).first()
        if article.quantite >= new_demande_achat.quantite:
            # Add and commit to the database
            db.session.add(new_demande_achat)
            db.session.commit()
            fun_history_ajouter_demande_achat(data)
            return True
        else: 
             print(f"La quantité de la demande dépasse la quantité dans le stock")
             return False
    except Exception as e:
        print(f"Erreur lors de l'ajout de la demande d'achat: {e}")
        db.session.rollback()  # Roll back changes on error
        return False
    

def fun_ajouter_article(data):

    try:
       
        
        # Create a new Article
        new_article = Article(
            code_article=data['code_article'],
            libelle_article=data['libelle_article'],
            prix_achat=data['prix_achat'],
            assignation=data['assignation'],
            quantite=data['quantite'],
            fournisseur=data['fournisseur'],
            date=datetime.now(timezone.utc),
            quantite_min=data['quantite_min'],
            image=data['image']
        )

        # Add and commit to the database
        db.session.add(new_article)
        db.session.commit()
        fun_history_ajouter_article(data)
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'article: {e}")
        db.session.rollback()  # Roll back changes on error
        return False

def fun_ajouter_usine(data):

    try:
       
        
        # Create a new Usine
        new_usine = Usine(
            nom_usine=data['nom_usine'],
            region=data['region'],
            adresse=data['adresse'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            telephone=data['telephone'],
            etat=data['etat']
        )

        # Add and commit to the database
        db.session.add(new_usine)
        db.session.commit()
        fun_history_ajouter_usine(data)
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'usine: {e}")
        db.session.rollback()  # Roll back changes on error
        return False


def fun_ajouter_fournisseur(data):
    try:
        # Create a new Fournisseur
        new_fournisseur = Fournisseur(
            nom_fournisseur=data['nom_fournisseur'],
            matricule_fiscale=data['matricule_fiscale'],
            adresse=data['adresse'],
            telephone=data['telephone'],
        )
        # Add and commit to the database
        db.session.add(new_fournisseur)
        db.session.commit()
        fun_history_ajouter_fournisseur(data)
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout de fournisseur: {e}")
        db.session.rollback()  # Roll back changes on error
        return False

def fun_history_ajouter_fournisseur(data):
    
    new_history=History(
        fournisseur=data['nom_fournisseur'],
        action="ajout d'un nouveau fournisseur",
        details=str(' matricule fiscale : '+data['matricule_fiscale']+' addresse : '+data['adresse']+' telephone : '+data['telephone'])
        )
    db.session.add(new_history)
    db.session.commit()
    return True
    
def fun_history_ajouter_user(data):
    
    new_history=History(
        user=data['username'],
        action="ajout d'un nouveau user",
        details=str(' emplacement : '+data['emplacement']+' role : '+data['role']+' telephone : '+data['telephone'])
        )
    db.session.add(new_history)
    db.session.commit()
    return True
    
def fun_history_ajouter_article(data):
    
    new_history=History(
        code_article=data['code_article'],
        libelle_article=data['libelle_article'],
        emplacement=data['assignation'],
        prix=data['prix_achat'],
        action="ajout d'un nouveau article",
        fournisseur=data['fournisseur'],
        details=str('date : ' + str(datetime.now(timezone.utc)) + 'quantite_min : ' + data['quantite_min'])
        )
    db.session.add(new_history)
    db.session.commit()
    return True

def fun_history_ajouter_demande_achat(data):
    new_history=History(
        code_article=data['code_article'],
        libelle_article=data['libelle_article'],
        emplacement=data['assignation'],
        
        action="ajout d'un nouveau demande d'achat",
       
        details=str('date : ' + str(datetime.now(timezone.utc)))
        )
    db.session.add(new_history)
    db.session.commit()
    return True     


def fun_history_ajouter_usine(data):
    
    new_history=History(
        nom_usine=data['nom_usine'],
        emplacement=data['region'],
        action="ajout d'un nouveau usine",
        details=str('addresse : ' + data['telephone'] + 'etat : ' + data['etat']))
    db.session.add(new_history)
    db.session.commit()
    return True

def fun_history_editer_article(data):
    
    new_history=History(
        code_article=data['code_article'],
        libelle_article=data['libelle_article'],
        prix=data['prix_achat'],
        fournisseur=data['fournisseur'],
        action="editre un article")
    db.session.add(new_history)
    db.session.commit()
    return True
    
def fun_info_demande_achat(code_demande):
    demande_achat_data = DemandeAchat.query.filter_by(code_demande=code_demande).first()
    return demande_achat_data

def fun_info_article(code_article):
    article_data = Article.query.filter_by(code_article=code_article).first()
    return article_data

def fun_info_fournisseur(nom_fournisseur):
    fournisseur_data = Fournisseur.query.filter_by(nom_fournisseur=nom_fournisseur).first()
    return fournisseur_data
                
def fun_info_usine(nom_usine):
    usine_data = Usine.query.filter_by(nom_usine=nom_usine).first()
    return usine_data

def fun_info_user(username):
     user_data=User.query.filter_by(username=username).first()
     return user_data


# User Model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    emplacement = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    numero_telephone = db.Column(db.Integer, nullable=True)

# Article Model
class Article(db.Model):
    __tablename__ = 'articles'
    id_article = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code_article = db.Column(db.String(20), nullable=False)
    libelle_article = db.Column(db.String(255), nullable=False)
    prix_achat = db.Column(db.Float, nullable=False)
    assignation = db.Column(db.String(255), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    fournisseur = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    quantite_min = db.Column(db.Integer, nullable=False)
    image=db.Column(db.String(255),nullable=True)

# Supplier Model (Fournisseur)
class Fournisseur(db.Model):
    __tablename__ = 'fournisseur'
    id_fournisseur = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_fournisseur = db.Column(db.String(255), nullable=False)
    matricule_fiscale = db.Column(db.String(50), nullable=True)
    adresse = db.Column(db.String(255), nullable=True)
    telephone = db.Column(db.String(50), nullable=True)

# Purchase Model (Achats)
class Achat(db.Model):
    __tablename__ = 'achats'
    code_demande = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code_article = db.Column(db.Integer, nullable=False)
    libelle_article = db.Column(db.String(255), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_achat = db.Column(db.Float, nullable=False)
    assignation = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    fournisseur = db.Column(db.String(255), nullable=False)
    lot_achat = db.Column(db.String(255), nullable=False)

# Sales Model (Ventes)
class Vente(db.Model):
    __tablename__ = 'ventes'
    id_vente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code_demande = db.Column(db.Integer, nullable=True)
    code_article = db.Column(db.Integer, nullable=True)
    libelle_article = db.Column(db.String(20), nullable=True)
    quantite = db.Column(db.Integer, nullable=True)
    prix_vente = db.Column(Numeric(6, 3), nullable=True)
    assignation = db.Column(db.String(20), nullable=True)
    vers = db.Column(db.String(20), nullable=True)
    demandeur = db.Column(db.String(20), nullable=True)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

# Sales Request Model (DemandeVente)
class DemandeVente(db.Model):
    __tablename__ = 'demande_vente'
    code_demande = db.Column(db.Integer, primary_key=True)
    code_article = db.Column(db.String(50), nullable=False)
    libelle_article = db.Column(db.String(20), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_vente = db.Column(Numeric(6, 3), nullable=True)
    assignation = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    demandeur = db.Column(db.String(20), nullable=True)
    vers = db.Column(db.String(20), nullable=True)
    commande = db.Column(db.String(20), nullable=True)
    etat = db.Column(db.Integer, nullable=False)
    reception = db.Column(db.Integer, nullable=False)
    commentaire = db.Column(db.String(255), nullable=True)

# Purchase Request Model (DemandeAchat)
class DemandeAchat(db.Model):
    __tablename__ = 'demande_achat'
    code_demande = db.Column(db.Integer, primary_key=True)
    code_article = db.Column(db.String(50), nullable=False)
    libelle_article = db.Column(db.String(20), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_achat = db.Column(Numeric(6, 3), nullable=True)
    assignation = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    demandeur = db.Column(db.String(20), nullable=True)
    vers = db.Column(db.String(20), nullable=True)
    commande = db.Column(db.String(20), nullable=True)
    etat = db.Column(db.Integer, nullable=False)
    reception = db.Column(db.Integer, nullable=False)
    commentaire = db.Column(db.String(255), nullable=True)

# History Model
class History(db.Model):
    __tablename__ = 'history'
    id_history = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code_demande = db.Column(db.Integer, nullable=True)
    code_article = db.Column(db.String(50), nullable=True)
    libelle_article = db.Column(db.String(255), nullable=True)
    quantite = db.Column(db.Integer, nullable=True)
    prix = db.Column(db.Float, nullable=True)
    fournisseur = db.Column(db.String(20), nullable=True)
    emplacement = db.Column(db.String(20), nullable=True)
    action = db.Column(db.String(50), nullable=True)
    user = db.Column(db.String(20), nullable=True)
    details = db.Column(db.String(255), nullable=True)
    usine = db.Column(db.String(20), nullable=True)
    date_action = db.Column(db.TIMESTAMP, nullable=True)
    date_approuver_demande = db.Column(db.TIMESTAMP, nullable=True)
    date_reception = db.Column(db.TIMESTAMP, nullable=True)

# Factory Model (Usine)
class Usine(db.Model):
    __tablename__ = 'usine'
    id_usine = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_usine = db.Column(db.String(20), nullable=False)
    region = db.Column(db.String(20), nullable=False)
    adresse = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.String(20), nullable=True)
    longitude = db.Column(db.String(20), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    etat = db.Column(db.String(20), nullable=False)  
    


if __name__ == '__main__':
    app.run(debug=True)
