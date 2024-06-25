import mysql.connector
from flask import Flask, render_template, redirect, url_for, flash, session,request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from forms import InscriptionForm, ConnexionForm, EvenementForm, ReservationForm


app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'connexion'

db = mysql.connector.connect(
    host=Config.MYSQL_HOST,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DB
)


class Utilisateur(UserMixin):
    def __init__(self, id, nom_utilisateur, email, mot_de_passe):
        self.id = id
        self.nom_utilisateur = nom_utilisateur
        self.email = email
        self.mot_de_passe = mot_de_passe


@login_manager.user_loader
def load_user(user_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM utilisateurs WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return Utilisateur(user['id'], user['nom_utilisateur'], user['email'], user['mot_de_passe'])
    return None


@app.route('/')
def accueil():
    return render_template('accueil.html')


@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    form = InscriptionForm()
    if form.validate_on_submit():
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM utilisateurs WHERE email = %s", (form.email.data,))
        user = cursor.fetchone()
        if user:
            flash('Cet email est déjà utilisé.', 'danger')
        else:
            hashed_password = generate_password_hash(form.mot_de_passe.data, method='pbkdf2:sha256')
            cursor.execute("INSERT INTO utilisateurs (nom_utilisateur, email, mot_de_passe) VALUES (%s, %s, %s)",
                           (form.nom_utilisateur.data, form.email.data, hashed_password))
            db.commit()
            flash('Inscription réussie. Vous pouvez vous connecter.', 'success')
            return redirect(url_for('connexion'))
        cursor.close()
    return render_template('inscription.html', form=form)


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    form = ConnexionForm()
    if form.validate_on_submit():
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM utilisateurs WHERE email = %s", (form.email.data,))
        user = cursor.fetchone()
        cursor.close()
        if user and check_password_hash(user['mot_de_passe'], form.mot_de_passe.data):
            user_obj = Utilisateur(user['id'], user['nom_utilisateur'], user['email'], user['mot_de_passe'])
            login_user(user_obj)
            session['loggedin'] = True
            flash('Connexion réussie.', 'success')
            return redirect(url_for('accueil'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    return render_template('connexion.html', form=form)


@app.route('/deconnexion')
@login_required
def deconnexion():
    logout_user()
    session.pop('loggedin', None)
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('accueil'))


@app.route('/evenements', methods=['GET', 'POST'])
def evenements():
    search = request.args.get('search')
    date = request.args.get('date')
    lieu = request.args.get('lieu')
    billets_min = request.args.get('billets_min')
    billets_max = request.args.get('billets_max')

    query = "SELECT * FROM evenements WHERE 1=1"
    params = []

    if search:
        query += " AND (nom LIKE %s OR description LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    if date:
        query += " AND date = %s"
        params.append(date)

    if lieu:
        query += " AND lieu LIKE %s"
        params.append(f"%{lieu}%")

    if billets_min:
        query += " AND billets_disponibles >= %s"
        params.append(billets_min)

    if billets_max:
        query += " AND billets_disponibles <= %s"
        params.append(billets_max)

    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params)
    evenements = cursor.fetchall()
    cursor.close()

    return render_template('evenements.html', evenements=evenements)



@app.route('/reservation/<int:evenement_id>', methods=['GET', 'POST'])
@login_required
def reservation(evenement_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM evenements WHERE id = %s", (evenement_id,))
    evenement = cursor.fetchone()
    cursor.close()

    if not evenement:
        flash('Événement non trouvé.', 'danger')
        return redirect(url_for('evenements'))

    form = ReservationForm()
    if form.validate_on_submit():
        cursor = db.cursor()
        cursor.execute("INSERT INTO reservations (utilisateur_id, evenement_id, billets_reserves) VALUES (%s, %s, %s)",
                       (current_user.id, evenement_id, form.billets_reserves.data))
        db.commit()
        cursor.close()
        flash('Réservation réussie!', 'success')
        return redirect(url_for('evenements'))
    return render_template('reservation.html', form=form, evenement=evenement)


@app.route('/admin')
@login_required
def admin():
    if not current_user.is_authenticated or current_user.email != Config.ADMIN_EMAIL:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM evenements")
    evenements = cursor.fetchall()
    cursor.close()
    return render_template('admin.html', evenements=evenements)


@app.route('/ajouter_evenement', methods=['GET', 'POST'])
@login_required
def ajouter_evenement():
    if not current_user.is_authenticated or current_user.email != Config.ADMIN_EMAIL:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    form = EvenementForm()
    if form.validate_on_submit():
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO evenements (nom, description, date, lieu, billets_disponibles) VALUES (%s, %s, %s, %s, %s)",
            (form.nom.data, form.description.data, form.date.data, form.lieu.data, form.billets_disponibles.data))
        db.commit()
        cursor.close()
        flash('Événement ajouté avec succès.', 'success')
        return redirect(url_for('admin'))
    return render_template('ajouter_evenement.html', form=form)


@app.route('/modifier_evenement/<int:evenement_id>', methods=['GET', 'POST'])
@login_required
def modifier_evenement(evenement_id):
    if not current_user.is_authenticated or current_user.email != Config.ADMIN_EMAIL:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM evenements WHERE id = %s", (evenement_id,))
    evenement = cursor.fetchone()
    cursor.close()

    if not evenement:
        flash('Événement non trouvé.', 'danger')
        return redirect(url_for('admin'))

    form = EvenementForm(obj=evenement)
    if form.validate_on_submit():
        cursor = db.cursor()
        cursor.execute(
            "UPDATE evenements SET nom = %s, description = %s, date = %s, lieu = %s, billets_disponibles = %s WHERE ""id = %s",
            (form.nom.data, form.description.data, form.date.data, form.lieu.data, form.billets_disponibles.data,
             evenement_id))
        db.commit()
        cursor.close()
        flash('Événement modifié avec succès.', 'success')
        return redirect(url_for('admin'))
    return render_template('modifier_evenement.html', form=form)


@app.route('/supprimer_evenement/<int:evenement_id>', methods=['POST'])
@login_required
def supprimer_evenement(evenement_id):
    if not current_user.is_authenticated or current_user.email != Config.ADMIN_EMAIL:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    cursor = db.cursor()
    cursor.execute("DELETE FROM evenements WHERE id = %s", (evenement_id,))
    db.commit()
    cursor.close()
    flash('Événement supprimé avec succès.', 'success')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=8080)
