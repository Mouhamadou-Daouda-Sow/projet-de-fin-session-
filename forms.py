from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateTimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

class InscriptionForm(FlaskForm):
    nom_utilisateur = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    mot_de_passe = PasswordField('Mot de passe', validators=[DataRequired()])
    confirmer_mot_de_passe = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('mot_de_passe')])
    submit = SubmitField('S\'inscrire')

class ConnexionForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    mot_de_passe = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

class EvenementForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateTimeField('Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    lieu = StringField('Lieu', validators=[DataRequired()])
    billets_disponibles = IntegerField('Billets disponibles', validators=[DataRequired()])
    submit = SubmitField('Créer/Mettre à jour l\'événement')

class ReservationForm(FlaskForm):
    billets_reserves = IntegerField('Nombre de billets a réserver', validators=[DataRequired()])
    submit = SubmitField('Réserver')
