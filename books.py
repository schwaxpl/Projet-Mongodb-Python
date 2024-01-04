from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField,SelectField, validators

class CreateTask(FlaskForm):
    type = StringField('Type')
    titre = StringField('Titre')
    auteurs = StringField('Auteur(s)')
    year = IntegerField('Annee')
    create = SubmitField('Create')

class DeleteTask(FlaskForm):
    key = StringField('ID du livre')
    auteur = StringField('Auteur')
    annee = IntegerField("Année",validators=[validators.Optional()])
    delete = SubmitField('Delete')

class UpdateTask(FlaskForm):
    key = StringField('Id')
    titre = StringField('Nouveau titre')
    annee = IntegerField("Nouvelle année",validators=[validators.Optional()])
    update = SubmitField('Update')

class ResetTask(FlaskForm):
    reset = SubmitField('Reset')

class SearchTask(FlaskForm):
    auteur = StringField('Auteur')
    titre = StringField('Titre')
    annee = IntegerField("Annee",validators=[validators.Optional()])
    type = StringField('Type')
    tri = SelectField('Tri',choices=["annee","titre"])
    sens_tri = SelectField('Sens',choices=["Croissant","Décroissant"])
    nb_resultats = SelectField('Nb Résultats',choices=[10,25,50,100])
    page_debut = IntegerField("Page",default=1)
    search = SubmitField('Search')