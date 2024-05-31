from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import TextArea


class HSKAnalysisForm(FlaskForm):
    text = StringField('Text', validators=[DataRequired(), Length(min=1, max=10000)])
    submit = SubmitField('Submit')