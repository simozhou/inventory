from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length
from app.models import Location
from app import db
from flask import request


def select_location_choices():
    return db.session.query(Location).all


class AddObjectForm(FlaskForm):
    object_name = StringField("Che cos'è?", validators=[DataRequired()])
    object_location = QuerySelectField('Dove si trova?', query_factory=select_location_choices(),
                                       validators=[DataRequired()])
    object_notes = TextAreaField('Descrivilo in dettaglio...', validators=[Length(min=0, max=300)])
    submit = SubmitField("Aggiungi all'inventario")


class AddLocationForm(FlaskForm):
    location_name = StringField('Come si chiama?')
    submit = SubmitField("Aggiungi all'inventario")


class EditObjectForm(FlaskForm):
    object_name = StringField("Che cos'è?", validators=[DataRequired()])
    object_location = QuerySelectField('Dove si trova?', query_factory=select_location_choices(),
                                       validators=[DataRequired()])
    object_notes = TextAreaField('Descrivilo in dettaglio...', validators=[Length(min=0, max=300)])
    submit = SubmitField("Modifica")


class EditLocationForm(FlaskForm):
    location_name = StringField('Come si chiama?')
    submit = SubmitField("Modifica")


class SearchForm(FlaskForm):
    q = StringField('Cerca oggetto', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
