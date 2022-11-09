from flask import Flask
from flask import render_template, redirect, url_for, request
from flask_login import LoginManager, login_required, login_user, logout_user

import sqlite3
import snaplogic
import os

from lib.migrate import migrate_pages

app = Flask( __name__ )
app.register_blueprint( migrate_pages )

sl = snaplogic.SnapLogic()
app.secret_key = bytes( sl.config['secret_key'], 'utf-8' )

login_manager = LoginManager()
login_manager.init_app( app )

@login_manager.user_loader
def load_user( user_id ):
    return snaplogic.SnapductorUser( user_id )

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect( '/login?next=' + request.path )

@app.route( "/logout" )
@login_required
def logout():
    logout_user()
    return render_template( 'logout.html' )

@app.route( '/login' )
def login():
    username = None
    if 'SNAPDUCTOR_DEBUG' in os.environ and os.environ['SNAPDUCTOR_DEBUG']:
        if 'SNAPDUCTOR_USER' in os.environ:
            username = os.environ['SNAPDUCTOR_USER']

    if username is None:
        username = flask.request.headers.get('your-header-name')

    if username is not None:
        login_user( snaplogic.SnapductorUser( username ) )
        return redirect( url_for( 'index' ) )
    
    return render_template( 'login.html' )

@app.route( "/" )
@login_required
def index():
    sl = snaplogic.SnapLogic()
    return render_template( 'index.html', sl=sl )

@app.route( "/cleanup",  methods = ['POST', 'GET'] )
@login_required
def cleanup():
    sl = snaplogic.SnapLogic()
    
    if flask.request.method == 'POST':
        for key in flask.request.form.keys():
            if key.startswith( "delete_" ):
                action = flask.request.form[key].split( ":" )
                sl.delete_asset( action[0], action[1] )
    
        sl.refresh_assets()

    return render_template( 'cleanup.html', sl=sl )

@app.route( "/history" )
@login_required
def history():
    sl = snaplogic.SnapLogic()
    conn = get_db_connection()
    
    requests = conn.execute( "SELECT * FROM migrate_requests WHERE status = 'complete' ORDER BY created_on DESC" ).fetchall()
    return render_template( 'history.html', sl=sl, requests=requests )

@app.route( "/refresh" )
@login_required
def refresh():
    sl = snaplogic.SnapLogic()
    sl.refresh_assets()
    return redirect(url_for('index'))

