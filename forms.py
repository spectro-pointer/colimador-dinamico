from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from config import *

class ConfigForm(FlaskForm):
    use_raspberry             = StringField('use_raspberry', validators=[Length(max=64)])#,render_kw={"placeholder": USE_RASPBERRY})
    correct_vertical_camera   = StringField('correct_vertical_camera', validators=[Length(max=64)])#,render_kw={"placeholder": CORRECT_VERTICAL_CAMERA})
    correct_horizontal_camera = StringField('correct_horizontal_camera', validators=[Length(max=64)])#,render_kw={"placeholder": CORRECT_HORIZONTAL_CAMERA})
    center_radius             = StringField('center_radius', validators=[Length(max=64)])#,render_kw={"placeholder": CENTER_RADIUS})
    show_center_circle        = StringField('show_center_circle', validators=[Length(max=64)])#,render_kw={"placeholder": SHOW_CENTER_CIRCLE})
    enable_photo              = StringField('enable_photo', validators=[Length(max=64)])#,render_kw={"placeholder": ENABLE_PHOTO})
    enable_video              = StringField('enable_video', validators=[Length(max=64)])#,render_kw={"placeholder": ENABLE_VIDEO})
    record_seconds            = StringField('record_seconds', validators=[Length(max=64)])#,render_kw={"placeholder": RECORD_SECONDS})
    submit                    = SubmitField('Registrar')