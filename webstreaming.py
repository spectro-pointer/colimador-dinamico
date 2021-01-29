from utils import *
from tracker_lib import *
import threading
import argparse
from flask import Flask, url_for
from flask import render_template
from flask_bootstrap import Bootstrap
from flask import request, redirect
#from flask_appconfig import AppConfig
from config import *
from forms import ConfigForm
from time import sleep

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
update_parameters_en = False
# lock = threading.Lock()
# initialize a flask object
#app = Flask(__name__, template_folder="./")
# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()


def create_app(configfile=None):

    app = Flask(
                __name__,
                template_folder="templates",
                static_folder="static"
                )
    # AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
    #                             # highly recommend =)
    #                             # https://github.com/mbr/flask-appconfig
    Bootstrap(app)

    # in a real app, these should be configured through Flask-Appconfig
    app.config['SECRET_KEY'] = 'devkey'
    app.config['RECAPTCHA_PUBLIC_KEY'] = \
        '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'

    @app.route("/")
    def index():
        # return the rendered template
        return redirect(url_for('set_config'))

    @app.route("/video_feed")
    def video_feed():
        # return the response generated along with the specific media
        # type (mime type)
        return Response(generate(),mimetype = "multipart/x-mixed-replace; boundary=frame")

    @app.route("/config", methods=["GET","POST"])
    def set_config():
        # return the response generated along with the specific media
        # type (mime type)
        form = ConfigForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                spectro_pointer_config = {}
                spectro_pointer_config['use_raspberry']             = form.use_raspberry.data
                spectro_pointer_config['correct_vertical_camera']   = form.correct_vertical_camera.data
                spectro_pointer_config['correct_horizontal_camera'] = form.correct_horizontal_camera.data
                spectro_pointer_config['center_radius']             = form.center_radius.data
                spectro_pointer_config['show_center_circle']        = form.show_center_circle.data
                spectro_pointer_config['enable_photo']              = form.enable_photo.data
                spectro_pointer_config['enable_video']              = form.enable_video.data
                spectro_pointer_config['record_seconds']            = form.record_seconds.data
                with lock:
                    set_sp_config(app,**spectro_pointer_config)
            return redirect(url_for('set_config'))
        else:
            form.use_raspberry.render_kw                 = {'placeholder':get_sp_config('USE_RASPBERRY',app)}
            form.correct_vertical_camera.render_kw       = {'placeholder':get_sp_config('CORRECT_VERTICAL_CAMERA',app)}
            form.correct_horizontal_camera.render_kw     = {'placeholder':get_sp_config('CORRECT_HORIZONTAL_CAMERA',app)}
            form.center_radius.render_kw                 = {'placeholder':get_sp_config('CENTER_RADIUS',app)}
            form.show_center_circle.render_kw            = {'placeholder':get_sp_config('SHOW_CENTER_CIRCLE',app)}
            form.enable_photo.render_kw                  = {'placeholder':get_sp_config('ENABLE_PHOTO',app)}
            form.enable_video.render_kw                  = {'placeholder':get_sp_config('ENABLE_VIDEO',app)}
            form.record_seconds.render_kw                = {'placeholder':get_sp_config('RECORD_SECONDS',app)}
            form.use_raspberry.label                     = 'USE RASPBERRY:'
            form.correct_vertical_camera.label           = 'CORRECT VERTICAL CAMERA:'
            form.correct_horizontal_camera.label         = 'CORRECT HORIZONTAL CAMERA:'
            form.center_radius.label                     = 'CENTER RADIUS:'
            form.show_center_circle.label                = 'SHOW CENTER CIRCLE:'
            form.enable_photo.label                      = 'ENABLE PHOTO:'
            form.enable_video.label                      = 'ENABLE VIDEO:'
            form.record_seconds.label                    = 'RECORD SECONDS:'
        return render_template("config.html",form=form)

    @app.route("/default",methods=['GET','POST'])
    def set_default_config():
        if request.method == 'POST':
            with lock:
                delete_db(app)
                load_db(app)
            return redirect(url_for('set_config'))
        else:
            return redirect(url_for('set_config'))
    return app


def start_webstreaming():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
        help="ephemeral port number of the server (1024 to 65535)")
    args = vars(ap.parse_args())

    # start the flask app
    app = create_app()
    init_db(app)

    t1 = threading.Thread(target=camera_loop,args=(app,))
    t1.daemon = True
    t1.start()

    app.run(host=args["ip"], port=args["port"], debug=True,
        threaded=True, use_reloader=False)
