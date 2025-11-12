from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField
from wtforms.validators import DataRequired

class SelectPointsForm(FlaskForm):
    selected_diems = SelectMultipleField('Chọn điểm', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Tìm tuyến')
