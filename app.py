from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template, request

app = Flask(__name__)

# Paramètres de connexion à la base de données
dbname = "yuyu"
user = "waouhmonde"
password = "waouhmonde"
host = "localhost"
port = "5432"

# Configuration de la base de données PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
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

@app.route('/menu_list')
def menu_list():
    return render_template('menu_list.html')


# Exemple de route pour accéder à la base de données
@app.route('/', methods=['GET', 'POST'])
def accueil():
    # Déterminez les critères de tri par défaut
    tri_entreprises = request.args.get('tri_entreprises', 'nom')
    tri_contacts = request.args.get('tri_contacts', 'type')

    # Gestion de la barre de recherche
    terme_recherche = request.args.get('recherche', '')

    # Tri des entreprises
    resultats_entreprises = Entreprises.query.order_by(tri_entreprises).all()

    # Tri et recherche des contacts
    if terme_recherche:
        resultats_contacts = Contacts.query.filter(Contacts.valeur.ilike(f"%{terme_recherche}%")).order_by(tri_contacts).all()
    else:
        resultats_contacts = Contacts.query.order_by(tri_contacts).all()

    return render_template('index.html', resultats_entreprises=resultats_entreprises, resultats_contacts=resultats_contacts,
                           tri_entreprises=tri_entreprises, tri_contacts=tri_contacts, terme_recherche=terme_recherche)

if __name__ == '__main__':
    app.run(debug=True)
