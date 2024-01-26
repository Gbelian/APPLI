@app.route('/', methods=['GET', 'POST'])
def entreprise_graph():
    query = Entreprises.query
    data = query.all()
    entreprises = Entreprises.query.all()
    query_contacts = Contacts.query
    secteur_activite = request.form.get('secteur_activite')
    ville = request.form.get('ville')
    type_contact = request.form.get('type')
    departement = request.form.get('departement')
    commune = request.form.get('commune')
    
    localite = request.form.get('localite')
    chiffre_affaire_from = request.form.get('chiffre_affaire_from')
    chiffre_affaire_to = request.form.get('chiffre_affaire_to')

    # Construire la requête en fonction des filtres sélectionnés
    query = Entreprises.query
     
    sort_by = request.args.get('sort_by', 'alphabet')  

    search_term = request.form.get('search', '')
    if search_term:
        query = Entreprises.query.filter(Entreprises.nom.ilike(f"%{search_term}%"))

    if secteur_activite:
        query = query.filter_by(secteur_activite=secteur_activite)
    if ville:
        query = query.filter_by(ville=ville)
    if type_contact:
        # Assurez-vous d'ajuster le nom de la colonne et la logique de filtrage en fonction de votre modèle
        query = query.filter(Entreprises.Contacts.any(type=type_contact))
        query_contacts = query_contacts.filter_by(type=type_contact)
    if departement:
        query = query.filter_by(departement=departement)
    if commune:
        print(commune)
        query = query.filter_by(commune=commune)
    if localite:
        query = query.filter_by(localite=localite)
    if chiffre_affaire_from:
        query = query.filter(Entreprises.chiffre_affaires >= float(chiffre_affaire_from))
    if chiffre_affaire_to:
        query = query.filter(Entreprises.chiffre_affaires <= float(chiffre_affaire_to))

    total_entreprises = query.count()
    total_contacts = query_contacts.count()
    type_counts = db.session.query(Contacts.type, func.count()).group_by(Contacts.type).all()
    # Préparez les données pour le graphique
    types = [count[0] for count in type_counts]
    counts = [count[1] for count in type_counts]

    entreprises_par_ville = db.session.query(Entreprises.ville, func.count()).group_by(Entreprises.ville).all()
    # Préparez les données pour le graphique
    villes = [entreprise[0] for entreprise in entreprises_par_ville]
    entreprises_par_ville_counts = [entreprise[1] for entreprise in entreprises_par_ville]
    # Préparez les données pour le graphique
    villes = [entreprise[0] for entreprise in entreprises_par_ville]
    entreprises_par_ville_counts = [entreprise[1] for entreprise in entreprises_par_ville]
    entreprises_par_secteur = db.session.query(Entreprises.secteur_activite, func.count()).group_by(Entreprises.secteur_activite).all()
    # Préparez les données pour le graphique
    secteurs_activite = [entreprise[0] for entreprise in entreprises_par_secteur]
    entreprises_par_secteur_counts = [entreprise[1] for entreprise in entreprises_par_secteur]

    today = datetime.now().date()
    # Obtenez les données par jour pour le nombre total d'entreprises
    entreprises_par_jour = db.session.query(func.date(Entreprises.date_mise_a_jour), func.count()).group_by(func.date(Entreprises.date_mise_a_jour)).all()
    # Générez une liste de dates à partir de la première date jusqu'à aujourd'hui
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    # Obtenez les données par jour pour le nombre total de contacts
    contacts_par_jour = db.session.query(func.date(Contacts.date_mise_a_jour), func.count()).group_by(func.date(Contacts.date_mise_a_jour)).all()
    # Obtenez les données par jour pour le nombre de sites
    sites_par_jour = db.session.query(func.date(Entreprises.date_mise_a_jour), func.count()).filter(Entreprises.site_web != '').group_by(func.date(Entreprises.date_mise_a_jour)).all()
    # Obtenez les données par jour pour le nombre de contacts par type
    contacts_mail_par_jour = db.session.query(func.date(Contacts.date_mise_a_jour), func.count()).filter(Contacts.type == 'Mail').group_by(func.date(Contacts.date_mise_a_jour)).all()
    contacts_fixe_par_jour = db.session.query(func.date(Contacts.date_mise_a_jour), func.count()).filter(Contacts.type == 'Fixe').group_by(func.date(Contacts.date_mise_a_jour)).all()
    contacts_mobile_par_jour = db.session.query(func.date(Contacts.date_mise_a_jour), func.count()).filter(Contacts.type == 'Mobile').group_by(func.date(Contacts.date_mise_a_jour)).all()
    # Générez une liste de dates à partir de la première date jusqu'à aujourd'hui
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    # Générez les séries de données pour chaque type de graphique
    contacts_data = [next((count for date, count in contacts_par_jour if date == d), 0) for d in dates]
    entreprises_data = [next((count for date, count in entreprises_par_jour if date == d), 0) for d in dates]
    sites_data = [next((count for date, count in sites_par_jour if date == d), 0) for d in dates]
    contacts_mail_data = [next((count for date, count in contacts_mail_par_jour if date == d), 0) for d in dates]
    contacts_fixe_data = [next((count for date, count in contacts_fixe_par_jour if date == d), 0) for d in dates]
    contacts_mobile_data = [next((count for date, count in contacts_mobile_par_jour if date == d), 0) for d in dates]



    # Utilisez maintenant la fonction get_unique_values
    secteurs_activite_uniques = get_unique_values(Entreprises, 'secteur_activite')
    villes_uniques = get_unique_values(Entreprises, 'ville')
    types_contacts_uniques = get_unique_values(Contacts, 'type')
    departements_uniques = get_unique_values(Entreprises, 'departement')
    communes_uniques = get_unique_values(Entreprises, 'commune')
    localites_uniques = get_unique_values(Entreprises, 'localite')

    # Après avoir obtenu les valeurs uniques, extrayez la première colonne des tuples
    secteurs_activite_uniques = [secteur[0] for secteur in secteurs_activite_uniques]
    villes_uniques = [ville[0] for ville in villes_uniques]
    types_contacts_uniques = [type_contact[0] for type_contact in types_contacts_uniques]
    departements_uniques = [departement[0] for departement in departements_uniques]
    communes_uniques = [commune[0] for commune in communes_uniques]
    localites_uniques = [localite[0] for localite in localites_uniques]

    return render_template('dashboard/entreprise_graph.html', 
                       dates=dates,
                       entreprises_data=entreprises_data,
                       contacts_data=contacts_data,
                       sites_data=sites_data,
                       contacts_mail_data=contacts_mail_data,
                       contacts_fixe_data=contacts_fixe_data,
                       contacts_mobile_data=contacts_mobile_data,
                       types=types,  # Assurez-vous de définir correctement cette variable dans votre code
                       counts=counts,   # Assurez-vous de définir correctement cette variable dans votre code
                       total_contacts=total_contacts,
                       total_entreprises=total_entreprises,
                       villes=villes, entreprises_par_ville_counts=entreprises_par_ville_counts,
                       secteurs_activite_uniques=secteurs_activite_uniques,
                       secteurs_activite=secteurs_activite, entreprises_par_secteur_counts=entreprises_par_secteur_counts,
                       villes_uniques=villes_uniques,
                       types_contacts_uniques=types_contacts_uniques,
                       departements_uniques=departements_uniques,
                       communes_uniques=communes_uniques,
                       localites_uniques=localites_uniques)
















@app.route('/', methods=['GET', 'POST'])
def entreprise_graph():
    try:
        query = build_base_query()
        data = query.all()
        entreprises = Entreprises.query.all()
        query_contacts = Contacts.query

        # Récupérer les filtres depuis le formulaire
        filters = get_filters_from_request()

        # Construire la requête en fonction des filtres sélectionnés
        query = apply_filters(query, filters, query_contacts)

        # Récupérer les données pour le graphique
        chart_data = get_chart_data(query, query_contacts)

        # Utiliser maintenant la fonction get_unique_values
        unique_values = get_unique_values()

        return render_template('dashboard/entreprise_graph.html', **chart_data, **unique_values)
    except Exception as e:
        return render_template('erreur.html', error=str(e))
    
    

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

def apply_filters(query, filters, query_contacts):
    query = query.filter_by(secteur_activite=filters['secteur_activite'])
    query = query.filter_by(ville=filters['ville'])
    
    if filters['type_contact']:
        query = query.filter(Entreprises.contacts.any(type=filters['type_contact']))
        query_contacts = query_contacts.filter_by(type=filters['type_contact'])

    if filters['departement']:
        query = query.filter_by(departement=filters['departement'])
    
    if filters['commune']:
        query = query.filter_by(commune=filters['commune'])

    # Ajoutez d'autres conditions pour les filtres restants

    if filters['search_term']:
        query = Entreprises.query.filter(Entreprises.nom.ilike(f"%{filters['search_term']}%"))

    return query


def get_chart_data(query, query_contacts):
    today = datetime.now().date()

    # Obtenez les données par jour pour le nombre total d'entreprises
    entreprises_par_jour = query.with_entities(
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
    sites_par_jour = query.with_entities(
        func.date(Entreprises.date_mise_a_jour),
        func.count()
    ).filter(Entreprises.site_web != '').group_by(func.date(Entreprises.date_mise_a_jour)).all()

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
    total_entreprises = query.count()
    total_contacts = query_contacts.count()

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
        'total_contacts': total_contacts
    }

def get_unique_values():
    # Utiliser la fonction get_unique_values
    secteurs_activite_uniques = get_unique_values(Entreprises, 'secteur_activite')
    villes_uniques = get_unique_values(Entreprises, 'ville')
    types_contacts_uniques = get_unique_values(Contacts, 'type')
    departements_uniques = get_unique_values(Entreprises, 'departement')
    communes_uniques = get_unique_values(Entreprises, 'commune')
    localites_uniques = get_unique_values(Entreprises, 'localite')

    # Après avoir obtenu les valeurs uniques, extrayez la première colonne des tuples
    secteurs_activite_uniques = [secteur[0] for secteur in secteurs_activite_uniques]
    villes_uniques = [ville[0] for ville in villes_uniques]
    types_contacts_uniques = [type_contact[0] for type_contact in types_contacts_uniques]
    departements_uniques = [departement[0] for departement in departements_uniques]
    communes_uniques = [commune[0] for commune in communes_uniques]
    localites_uniques = [localite[0] for localite in localites_uniques]

    return {
        'secteurs_activite_uniques': secteurs_activite_uniques,
        'villes_uniques': villes_uniques,
        'types_contacts_uniques': types_contacts_uniques,
        'departements_uniques': departements_uniques,
        'communes_uniques': communes_uniques,
        'localites_uniques': localites_uniques
    }


