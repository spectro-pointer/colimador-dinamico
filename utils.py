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
    # Create empty list for appending every value
    config_data = list()

    spectro_pointer_config['use_raspberry']             = int(USE_RASPBERRY)
    config_data.append(spectro_pointer_config['use_raspberry'])

    spectro_pointer_config['correct_vertical_camera']   = int(CORRECT_VERTICAL_CAMERA)
    config_data.append(spectro_pointer_config['correct_vertical_camera'])
    
    spectro_pointer_config['correct_horizontal_camera'] = int(CORRECT_HORIZONTAL_CAMERA)
    config_data.append(spectro_pointer_config['correct_horizontal_camera'])
    
    spectro_pointer_config['center_radius']             = int(CENTER_RADIUS)
    config_data.append(spectro_pointer_config['center_radius'])
    
    spectro_pointer_config['show_center_circle']        = int(SHOW_CENTER_CIRCLE)
    config_data.append(spectro_pointer_config['show_center_circle'])
    
    spectro_pointer_config['enable_photo']              = int(ENABLE_PHOTO)
    config_data.append(spectro_pointer_config['enable_photo'])
    
    spectro_pointer_config['enable_video']              = int(ENABLE_VIDEO)
    config_data.append(spectro_pointer_config['enable_video'])
    
    spectro_pointer_config['record_seconds']            = int(RECORD_SECONDS)
    config_data.append(spectro_pointer_config['record_seconds'])
    
    #  Transform config_data list into a tuple
    config_data = tuple(config_data)

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
        # Aux variable for value control
        contVal = 0
        # Create string were SQL statements will be added
        s = "UPDATE sp_config SET "
        # Create empty list were values to update will be appended
        l = []
        
        # Check every possible value, if true, append value and extend SQL statement
        if spectro_pointer_config['use_raspberry']:            
            s = s + "USE_RASPBERRY=?"
            l.append(int(spectro_pointer_config['use_raspberry']))
            contVal+=1

        if spectro_pointer_config['correct_vertical_camera']:
            s2 = "CORRECT_VERTICAL_CAMERA=?"
            if contVal == 0:
                s = s + s2
            else:
                s = s + "," + s2         
            l.append(int(spectro_pointer_config['correct_vertical_camera']))
            contVal+=1

        if spectro_pointer_config['correct_horizontal_camera']:
            s3 = "CORRECT_HORIZONTAL_CAMERA=?"
            if contVal == 0:
                s = s + s3
            else:
                s = s + "," + s3
            l.append(int(spectro_pointer_config['correct_horizontal_camera']))
            contVal+=1

        if spectro_pointer_config['center_radius']:
            s4 = "CENTER_RADIUS=?"
            if contVal == 0:
                s = s + s4
            else:
                s = s + "," + s4
            l.append(int(spectro_pointer_config['center_radius']))
            contVal+=1

        if spectro_pointer_config['show_center_circle']:
            s5 = "SHOW_CENTER_CIRCLE=?"
            if contVal == 0:
                s = s + s5
            else:
                s = s + "," + s5
            l.append(int(spectro_pointer_config['show_center_circle']))
            contVal+=1

        if spectro_pointer_config['enable_photo']:
            s6 = "ENABLE_PHOTO=?"
            if contVal == 0:
                s = s + s6
            else:
                s = s + "," + s6
            l.append(int(spectro_pointer_config['enable_photo']))
            contVal+=1

        if spectro_pointer_config['enable_video']:
            s7 = "ENABLE_VIDEO=?"
            if contVal == 0:
                s = s + s7
            else:
                s = s + "," + s7
            l.append(int(spectro_pointer_config['enable_video']))
            contVal+=1
            
        if spectro_pointer_config['record_seconds']:
            s8 = "RECORD_SECONDS=?"
            if contVal == 0:
                s = s + s8
            else:
                s = s + "," + s8
            l.append(int(spectro_pointer_config['record_seconds']))
            contVal+=1
        # Convert list into tuple
        l = tuple(l)
        
        # Execute UPDATE statement
        conn.execute('"'+s+'"',l)

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
