from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from config import *

class ConfigForm(FlaskForm):
    use_raspberry             = StringField('use_raspberry', validators=[Length(max=64)])
    correct_vertical_camera   = StringField('correct_vertical_camera', validators=[Length(max=64)])
    correct_horizontal_camera = StringField('correct_horizontal_camera', validators=[Length(max=64)])
    center_radius             = StringField('center_radius', validators=[Length(max=64)])
    show_center_circle        = StringField('show_center_circle', validators=[Length(max=64)])
    enable_photo              = StringField('enable_photo', validators=[Length(max=64)])
    enable_video              = StringField('enable_video', validators=[Length(max=64)])
    record_seconds            = StringField('record_seconds', validators=[Length(max=64)])
    threshold                 = StringField('threshold', validators=[Length(max=64)])
    submit                    = SubmitField('Actualizar')