from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TimeField, SubmitField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Length
from app import db

class PlayerForm(FlaskForm):
    name = StringField('Player Name', validators=[DataRequired()])
    school = SelectField('School', choices=[('Smørås', 'Smørås'), ('Apeltun', 'Apeltun')], validators=[DataRequired()])
    submit = SubmitField('Add Player')

class MatchForm(FlaskForm):
    date = DateField('Match Date', validators=[DataRequired()])
    time = TimeField('Match Time', validators=[DataRequired()])
    opponent = StringField('Opponent', validators=[DataRequired()])
    team = SelectField('Team', choices=[('Smørås Ferrari', 'Smørås Ferrari'), ('Smørås Maserati', 'Smørås Maserati'),('Smørås Lamborghini', 'Smørås Lamborghini')], validators=[DataRequired()])
    players = SelectMultipleField('Select Players', coerce=int)
    submit = SubmitField('Add Match')

class MatchResultForm(FlaskForm):
    result = SelectField('Match Result', choices=[('Win', 'Win'), ('Loss', 'Loss'), ('Draw', 'Draw')], validators=[DataRequired()])
    submit = SubmitField('Update Result')
