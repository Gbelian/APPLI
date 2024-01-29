from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template, request
from flask import redirect, url_for
import plotly.express as px
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sqlalchemy import func
from datetime import datetime, timedelta
from flask import jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import flash
from decouple import config
import os
from sqlalchemy import distinct

# Charger les variables d'environnement à partir du fichier .env
DATABASE_URL = config('DATABASE_URL', default='sqlite:///:memory:')

app = Flask(__name__)


# Set a secret key for session management
app.secret_key = 'judesimon'

# Configuration de la base de données PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de l'extension SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Modèle pour la table Entreprises
class Entreprises(db.Model):
    entreprise_id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    secteur_activite = db.Column(db.String(200))
    site_web = db.Column(db.String(200))
    chiffre_affaires = db.Column(db.DECIMAL(15, 2))
    numero_identification = db.Column(db.String(100))
    adresse = db.Column(db.String(300))
    localite = db.Column(db.String(200))
    ville = db.Column(db.String(200))
    arrondissement = db.Column(db.String(200))
    commune = db.Column(db.String(100))
    departement = db.Column(db.String(200))
    pays = db.Column(db.String(100))
    code_postal = db.Column(db.String(200))
    opt_in = db.Column(db.Boolean)
    status_sms = db.Column(db.Boolean)
    status_appel = db.Column(db.Boolean)
    status_mail = db.Column(db.Boolean)
    date_mise_a_jour = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# Modèle pour la table Contacts_Entreprises
class Contacts(db.Model):
    contact_id = db.Column(db.Integer, primary_key=True)
    entreprise_id = db.Column(db.Integer, db.ForeignKey('entreprises'))
    type = db.Column(db.String(50))
    valeur = db.Column(db.TEXT)
    sources = db.Column(db.String(100))
    status = db.Column(db.Boolean)
    date_mise_a_jour = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Définissez la relation entre Entreprises et Contacts_Entreprises
    entreprise = db.relationship('Entreprises', backref=db.backref('Contacts', lazy=True))

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_utilisateur = db.Column(db.String(100), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(300), unique=True, nullable=False) 
    
#########################################################################################
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash




# Registration route
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Use the recommended hash method 'pbkdf2:sha256'
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = users(nom_utilisateur=username, mot_de_passe=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('user/signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.query.filter_by(email = email).first()
        if user and check_password_hash(user.mot_de_passe, password):
            session['user_id'] = user.id
            return redirect(url_for('entreprise_graph'))
    return render_template('user/signup.html')

    # Route de profil
@app.route('/profile')
def profile():
    if 'user_id' in session:
        user = users.query.get(session['user_id'])
        if user:
            return render_template('user/profil.html', user=user)
    return redirect(url_for('login'))
# Logout route
    
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

#########################################################################################


## ####################  Entreprises   ############################
    
            ###############   Graph ###########################
    
def get_unique_values_from_db(model, column):
    values = db.session.query(getattr(model, column)).distinct().all()
    return [value[0] for value in values if value[0] is not None]

def get_unique_values():
    secteurs_activite_uniques = get_unique_values_from_db(Entreprises, 'secteur_activite')
    villes_uniques = get_unique_values_from_db(Entreprises, 'ville')
    types_contacts_uniques = get_unique_values_from_db(Contacts, 'type')
    departements_uniques = get_unique_values_from_db(Entreprises, 'departement')
    communes_uniques = get_unique_values_from_db(Entreprises, 'commune')
    localites_uniques = get_unique_values_from_db(Entreprises, 'localite')

    return {
        'secteurs_activite_uniques': secteurs_activite_uniques,
        'villes_uniques': villes_uniques,
        'types_contacts_uniques': types_contacts_uniques,
        'departements_uniques': departements_uniques,
        'communes_uniques': communes_uniques,
        'localites_uniques': localites_uniques
    }

@app.route('/dentreprise_graph', methods=['GET', 'POST'])
def entreprise_graph():
    if 'user_id' in session:
        user = users.query.get(session['user_id'])
        if user:
            try:
                # Construire la requête de base pour les entreprises
                query_entreprises = build_base_query()
                # Récupérer les filtres depuis le formulaire
                filters = get_filters_from_request()
                # Appliquer les filtres à la requête d'entreprises et obtenir la requête de contacts
                query_entreprises, query_contacts = apply_filters(query_entreprises, Contacts.query, filters)
                # Récupérer les données pour le graphique
                chart_data = get_chart_data(query_entreprises, query_contacts)
                # Utiliser maintenant la fonction get_unique_values
                unique_values = get_unique_values()
                return render_template('dashboard/entreprise_graph.html', user=user, **chart_data, **unique_values)
            except Exception as e:
                return render_template('erreur.html', error=str(e))
    
    return redirect(url_for('login'))


def build_base_query():
    return Entreprises.query

def get_filters_from_request():
    return {
        'secteur_activite': request.form.get('secteur_activite'),
        'ville': request.form.get('ville'),
        'type_contact': request.form.get('type'),
        'departement': request.form.get('departement'),
        'commune': request.form.get('commune'),
        'localite': request.form.get('localite'),
        'chiffre_affaire_from': request.form.get('chiffre_affaire_from'),
        'chiffre_affaire_to': request.form.get('chiffre_affaire_to'),
        'sort_by': request.args.get('sort_by', 'alphabet'),
        'search_term': request.form.get('search', '')
    }


def apply_filters(query_entreprises, query_contacts, filters):
    if filters['secteur_activite']:
        query_entreprises = query_entreprises.filter_by(secteur_activite=filters['secteur_activite'])
    if filters['ville']:
        query_entreprises = query_entreprises.filter_by(ville=filters['ville'])
    
    if filters['type_contact']:
        query_entreprises = query_entreprises.filter(Entreprises.Contacts.any(type=filters['type_contact']))
        query_contacts = query_contacts.filter_by(type=filters['type_contact'])

    if filters['departement']:
        query_entreprises = query_entreprises.filter_by(departement=filters['departement'])
    
    if filters['commune']:
        query_entreprises = query_entreprises.filter_by(commune=filters['commune'])

    if filters['search_term']:
        query_entreprises = query_entreprises.filter(Entreprises.nom.ilike(f"%{filters['search_term']}%"))

    return query_entreprises, query_contacts



def get_chart_data(query_entreprises, query_contacts):
    today = datetime.now().date()

    entreprises_par_jour = query_entreprises.with_entities(
        func.date(Entreprises.date_mise_a_jour),
        func.count()
    ).group_by(func.date(Entreprises.date_mise_a_jour)).all()
   

    # Générez une liste de dates à partir de la première date jusqu'à aujourd'hui
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]

    # Obtenez les données par jour pour le nombre total de contacts
    contacts_par_jour = query_contacts.with_entities(
        func.date(Contacts.date_mise_a_jour),
        func.count()
    ).group_by(func.date(Contacts.date_mise_a_jour)).all()

    # Obtenez les données par jour pour le nombre de sites
    sites_par_jour = query_entreprises.with_entities(
        func.date(Entreprises.date_mise_a_jour),
        func.count()
    ).filter(Entreprises.site_web.isnot(None), Entreprises.site_web != '').group_by(func.date(Entreprises.date_mise_a_jour)).all()
   
    # Obtenez les données par jour pour le nombre de contacts par type
    contacts_mail_par_jour = query_contacts.with_entities(
        func.date(Contacts.date_mise_a_jour),
        func.count()
    ).filter(Contacts.type == 'Mail').group_by(func.date(Contacts.date_mise_a_jour)).all()

    contacts_fixe_par_jour = query_contacts.with_entities(
        func.date(Contacts.date_mise_a_jour),
        func.count()
    ).filter(Contacts.type == 'Fixe').group_by(func.date(Contacts.date_mise_a_jour)).all()

    contacts_mobile_par_jour = query_contacts.with_entities(
        func.date(Contacts.date_mise_a_jour),
        func.count()
    ).filter(Contacts.type == 'Mobile').group_by(func.date(Contacts.date_mise_a_jour)).all()

    # Générez les séries de données pour chaque type de graphique
    contacts_data = [next((count for date, count in contacts_par_jour if date == d), 0) for d in dates]
    entreprises_data = [next((count for date, count in entreprises_par_jour if date == d), 0) for d in dates]
    sites_data = [next((count for date, count in sites_par_jour if date == d), 0) for d in dates]
    contacts_mail_data = [next((count for date, count in contacts_mail_par_jour if date == d), 0) for d in dates]
    contacts_fixe_data = [next((count for date, count in contacts_fixe_par_jour if date == d), 0) for d in dates]
    contacts_mobile_data = [next((count for date, count in contacts_mobile_par_jour if date == d), 0) for d in dates]

    # Ajoutez les données pour le graphique des types, villes et secteurs_activite
    type_counts = db.session.query(Contacts.type, func.count()).group_by(Contacts.type).all()
    types = [count[0] for count in type_counts]
    counts = [count[1] for count in type_counts]

    entreprises_par_ville = db.session.query(Entreprises.ville, func.count()).group_by(Entreprises.ville).all()
    villes = [entreprise[0] for entreprise in entreprises_par_ville]
    entreprises_par_ville_counts = [entreprise[1] for entreprise in entreprises_par_ville]

    entreprises_par_secteur = db.session.query(Entreprises.secteur_activite, func.count()).group_by(Entreprises.secteur_activite).all()
    secteurs_activite = [entreprise[0] for entreprise in entreprises_par_secteur]
    entreprises_par_secteur_counts = [entreprise[1] for entreprise in entreprises_par_secteur]

    # Ajoutez les données pour le nombre total d'entreprises et de contacts
    total_entreprises = query_entreprises.count()
    total_contacts = query_contacts.count()
    # Nombre de contacts de type 'Mail'
    total_contacts_mail = query_contacts.filter(Contacts.type == 'Mail').count()
    # Nombre de sites web non vides
    total_sites_web = query_entreprises.filter(Entreprises.site_web != '').count()
    # Nombre de villes différentes
    total_villes = db.session.query(func.count(distinct(Entreprises.ville))).scalar()
    # Dernière date de mise à jour
    derniere_date_mise_a_jour = query_entreprises.with_entities(func.max(Entreprises.date_mise_a_jour)).scalar()


    return {
        'dates': dates,
        'entreprises_data': entreprises_data,
        'contacts_data': contacts_data,
        'sites_data': sites_data,
        'contacts_mail_data': contacts_mail_data,
        'contacts_fixe_data': contacts_fixe_data,
        'contacts_mobile_data': contacts_mobile_data,
        'types': types,
        'counts': counts,
        'villes': villes,
        'entreprises_par_ville_counts': entreprises_par_ville_counts,
        'secteurs_activite': secteurs_activite,
        'entreprises_par_secteur_counts': entreprises_par_secteur_counts,
        'total_entreprises': total_entreprises,
        'total_contacts': total_contacts,
        'total_contacts_mail': total_contacts_mail,
        'total_sites_web': total_sites_web,
        'total_villes': total_villes,
        'derniere_date_mise_a_jour': derniere_date_mise_a_jour
    }


    
        ###############   Extraction ###########################

def get_table_data(query_entreprises, query_contacts):
    entreprises = query_entreprises.all()

    data_for_template = {
        'entreprises': [],
        'headers': ['Nom', 'Secteur', 'Site Web', 'Mail', 'Ville']
    }

    for entreprise in entreprises:
        row_data = {
            'id' : entreprise.entreprise_id,
            'Nom': entreprise.nom,
            'Secteur': entreprise.secteur_activite,
            'Site Web': entreprise.site_web,
            'Mail': '',
            'Ville': entreprise.ville if hasattr(entreprise, 'ville') else ''
            # Add more fields as needed
        }
        # Fetch contacts related to the current entreprise
        contacts = [contact for contact in entreprise.Contacts if contact.type == 'Mail']
        if contacts:
            # Use the first email contact as the 'Mail' value
            row_data['Mail'] = contacts[0].valeur

        data_for_template['entreprises'].append(row_data)

    return data_for_template


def paginate(data_for_template, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = {
        'entreprises': data_for_template['entreprises'][start:end],
        'headers': data_for_template['headers']
    }
    return paginated_data


@app.route('/extraction_entreprise', methods=['GET', 'POST'])
def extraction_entreprise():
    if 'user_id' in session:
        user = users.query.get(session['user_id'])
        if user:
            try:
                sort_by = request.args.get('sort_by', 'alphabet')
                page = request.args.get('page', 1, type=int)
                per_page = 10
                
                query_entreprises = build_base_query()
                filters = get_filters_from_request()
                query_entreprises, query_contacts = apply_filters(query_entreprises, Contacts.query, filters)
                table_data = get_table_data(query_entreprises, query_contacts)
                
                paginated_data = paginate(table_data, page, per_page)
                total_pages = len(table_data['entreprises']) // per_page + (1 if len(table_data['entreprises']) % per_page != 0 else 0)

                unique_values = get_unique_values()
                return render_template('dashboard/extraction_entreprise.html', user=user,**paginated_data, total_pages=total_pages, **unique_values, page=page)
            except Exception as e:
                return render_template('erreur.html', user=user, error=str(e))
    return redirect(url_for('login'))

    

import pandas as pd
from flask import send_file

@app.route('/export_excel', methods=['GET'])
def export_excel():
    try:
        sort_by = request.args.get('sort_by', 'alphabet')
        query_entreprises = build_base_query()
        filters = get_filters_from_request()
        query_entreprises, query_contacts = apply_filters(query_entreprises, Contacts.query, filters)
        table_data = get_table_data(query_entreprises, query_contacts)
        # Créer un DataFrame
        df = pd.DataFrame(table_data['entreprises'])
        # Remplacer les valeurs nulles (None) par une chaîne vide ('')
        df.fillna('', inplace=True)
        # Nom du fichier Excel de sortie
        excel_filename = 'export_entreprises.xlsx'
        # Exporter le DataFrame vers un fichier Excel
        df.to_excel(excel_filename, index=False)
        return send_file(excel_filename, as_attachment=True)
    except Exception as e:
        return render_template('erreur.html', error=str(e))


## ####################  Delete Ajout Edith  ############################
    
    ### Delete

    # Add this route to handle delete


@app.route('/delete_entreprise/<int:entreprise_id>', methods=['POST'])
def delete_entreprise(entreprise_id):
    try:
        # Fetch the entreprise based on the provided ID
        entreprise = Entreprises.query.get_or_404(entreprise_id)
        # Delete the entreprise
        db.session.delete(entreprise)
        db.session.commit()

        flash('Entreprise deleted successfully!', 'success')
        return redirect(url_for('extraction_entreprise'))
    except Exception as e:
        return render_template('erreur.html', error=str(e))


####  Edit



from sqlalchemy.exc import SQLAlchemyError

@app.route('/edit_entreprise/<int:entreprise_id>', methods=['GET', 'POST'])
def edit_entreprise(entreprise_id):
    if 'user_id' in session:
        user = users.query.get(session['user_id'])
        if user:
            try:
                # Assurez-vous que l'entreprise appartient à l'utilisateur actuel
                entreprise = Entreprises.query.filter_by(entreprise_id=entreprise_id).first_or_404()

                if request.method == 'POST':
                    # Mise à jour de toutes les informations de l'entreprise basée sur les données du formulaire
                    entreprise.nom = request.form['nom']
                    entreprise.secteur_activite = request.form['secteur_activite']
                    entreprise.site_web = request.form['site_web']
                    entreprise.chiffre_affaires = request.form['chiffre_affaires']
                    # Mettez à jour d'autres champs si nécessaire
                    db.session.commit()

                    flash('Entreprise mise à jour avec succès!', 'success')
                    return redirect(url_for('extraction_entreprise'))

                # Rendre le formulaire de modification
                return render_template('dashboard/edit_entreprise.html', user=user, entreprise=entreprise)
            except SQLAlchemyError as e:
                return render_template('erreur.html', error=str(e))
    return redirect(url_for('login'))



@app.route('/particular_graph')
def particular_graph():
    if 'user_id' in session:
        user = users.query.get(session['user_id'])
        if user:
            return render_template('dashboard/particular_graph.html',user=user)
    return redirect(url_for('login'))

@app.route('/extraction_particular')
def extraction_particular():
    if 'user_id' in session:
        user = users.query.get(session['user_id'])
        if user:
            return render_template('dashboard/extraction_particular.html',user=user)
    return redirect(url_for('login'))

@app.route('/parametre')
def parametre():
    if 'user_id' in session:
        user = users.query.get(session['user_id'])
        if user:
            return render_template('dashboard/parametre.html', user=user)
    return redirect(url_for('login'))


@app.route('/erreur')
def erreur():
    if 'user_id' in session:
        user = users.query.get(session['user_id'])
        print(user)
        if user:
            return render_template('erreur.html',user=user)
    return redirect(url_for('login'))



if __name__ == '__main__':
    
    app.run(debug=True)
