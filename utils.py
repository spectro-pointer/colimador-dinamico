from config import *
import sqlite3
from flask import g

DATABASE = './static/sp_config.db'

def connect_db():
    return sqlite3.connect('static/sp_config.db')

def delete_db(app):

    # Insert tuple with config data into database
    with app.app_context():
        conn = connect_db()
        c = conn.cursor()
        c.execute("DELETE FROM sp_config")
        conn.commit()
        conn.close()

def load_db(app):
    
    spectro_pointer_config = {}
    spectro_pointer_config['use_raspberry']             = int(USE_RASPBERRY)
    spectro_pointer_config['correct_vertical_camera']   = int(CORRECT_VERTICAL_CAMERA)
    spectro_pointer_config['correct_horizontal_camera'] = int(CORRECT_HORIZONTAL_CAMERA)
    spectro_pointer_config['center_radius']             = int(CENTER_RADIUS)
    spectro_pointer_config['show_center_circle']        = int(SHOW_CENTER_CIRCLE)
    spectro_pointer_config['enable_photo']              = int(ENABLE_PHOTO)
    spectro_pointer_config['enable_video']              = int(ENABLE_VIDEO)
    spectro_pointer_config['record_seconds']            = int(RECORD_SECONDS)
    
    # Create tuple with the config data
    config_data = ( spectro_pointer_config['use_raspberry'],
                    spectro_pointer_config['correct_vertical_camera'],
                    spectro_pointer_config['correct_horizontal_camera'],
                    spectro_pointer_config['center_radius'],
                    spectro_pointer_config['show_center_circle'],
                    spectro_pointer_config['enable_photo'],
                    spectro_pointer_config['enable_video'],
                    spectro_pointer_config['record_seconds'])
    # Insert tuple with config data into database
    with app.app_context():
        conn = connect_db()
        c = conn.cursor()
        c.execute("INSERT INTO sp_config VALUES (?,?,?,?,?,?,?,?)", config_data)
        conn.commit()
        conn.close()

def init_db(app):
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute('''create table sp_config (USE_RASPBERRY int, CORRECT_VERTICAL_CAMERA int,
                                             CORRECT_HORIZONTAL_CAMERA int, CENTER_RADIUS int,
                                             SHOW_CENTER_CIRCLE int, ENABLE_PHOTO int,
                                             ENABLE_VIDEO int,RECORD_SECONDS int)''')
        load_db(app)

    except sqlite3.OperationalError as e:
        print 'table sp_config already exists' in str(e)
    conn.commit()
    conn.close()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def set_sp_config(app,**spectro_pointer_config):
    with app.app_context():
        conn = connect_db()

        if spectro_pointer_config['use_raspberry']:
            conn.execute("UPDATE sp_config SET USE_RASPBERRY=?",(int(spectro_pointer_config['use_raspberry']),))

        if spectro_pointer_config['correct_vertical_camera']:
            conn.execute("UPDATE sp_config SET CORRECT_VERTICAL_CAMERA=?",(int(spectro_pointer_config['correct_vertical_camera']),))

        if spectro_pointer_config['correct_horizontal_camera']:
            conn.execute("UPDATE sp_config SET CORRECT_HORIZONTAL_CAMERA=?",(int(spectro_pointer_config['correct_horizontal_camera']),))

        if spectro_pointer_config['center_radius']:
            conn.execute("UPDATE sp_config SET CENTER_RADIUS=?",(int(spectro_pointer_config['center_radius']),))

        if spectro_pointer_config['show_center_circle']:
            conn.execute("UPDATE sp_config SET SHOW_CENTER_CIRCLE=?",(int(spectro_pointer_config['show_center_circle']),))

        if spectro_pointer_config['enable_photo']:
            conn.execute("UPDATE sp_config SET ENABLE_PHOTO=?",(int(spectro_pointer_config['enable_photo']),))

        if spectro_pointer_config['enable_video']:
            conn.execute("UPDATE sp_config SET ENABLE_VIDEO=?",(int(spectro_pointer_config['enable_video']),))

        if spectro_pointer_config['record_seconds']:
            conn.execute("UPDATE sp_config SET RECORD_SECONDS=?",(int(spectro_pointer_config['record_seconds']),))

        conn.commit()
        conn.close()

def get_sp_config(param,app):
    with app.app_context():
        g.db = connect_db()
        config_table = g.db.execute('select '+param+' from sp_config')
        result = 0
        try:
            result = config_table.fetchall()[0][0]
        except:
            result = 0

        g.db.close()
        return result
