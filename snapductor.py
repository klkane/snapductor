from flask import Flask
from flask import render_template, redirect, url_for, request
from flask_login import LoginManager, login_required, login_user, logout_user

import sqlite3
import snaplogic
import os

login_manager = LoginManager()

app = Flask( __name__ )
sl = snaplogic.SnapLogic()
app.secret_key = bytes( sl.config['secret_key'], 'utf-8' )

login_manager.init_app( app )

def get_db_connection():
    conn = sqlite3.connect( 'db/database.db' )
    conn.row_factory = sqlite3.Row
    return conn

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

@app.route( "/migrate/complete/<request_id>" )
@login_required
def migrate_complete( request_id ):
    sl = snaplogic.SnapLogic()
    conn = get_db_connection()
    
    requests = conn.execute( "SELECT * FROM migrate_requests WHERE request_id = ?", [ request_id ] ).fetchall()
    comments = conn.execute( "SELECT * FROM comments WHERE request_id = ?", [ request_id ] ).fetchall()
    
    objects = None
    for row in requests:
        objects = row['objects'].split( ';' )

    to_objects = []
    from_objects = []
    asset_types = []
    for obj in objects:
        inner = obj.split( ':' )
        asset_types.append( inner[0] )
        to_objects.append( inner[1].replace( sl.config['test_target'], sl.config['prod_target'] ) )
        from_objects.append( inner[1] )
    
    for i in range( len( objects ) ):
        sl.migrate_asset( asset_types[i], from_objects[i], to_objects[i] )
    
    conn.execute( "UPDATE migrate_requests SET status = 'complete' WHERE request_id = ?", [ request_id ] )
    conn.commit()

    conn.close()
    return render_template( 'migrate_complete.html', sl=sl, requests=requests, comments=comments )
    
@app.route( "/migrate/delete/<request_id>" )
@login_required
def migrate_delete( request_id ):
    conn = get_db_connection()
    conn.execute( "DELETE FROM migrate_requests WHERE request_id = ?", [ request_id ] )
    conn.execute( "DELETE FROM comments WHERE request_id = ?", [ request_id ] )
    conn.commit()
    conn.close()
    return redirect( url_for( 'migrate' ) )
    
@app.route( "/migrate/<request_id>",  methods = [ 'POST', 'GET' ] )
@login_required
def migrate_detail( request_id ):
    conn = get_db_connection()

    if flask.request.method == 'POST':
        conn.execute( "INSERT INTO comments( username, request_id, comment ) VALUES( ?, ?, ? )", 
            [ 'kkane', request_id, flask.request.form['addComment' ] ] )
        conn.commit()

    requests = conn.execute( "SELECT * FROM migrate_requests WHERE request_id = ?", [ request_id ] ).fetchall()
    comments = conn.execute( "SELECT * FROM comments WHERE request_id = ?", [ request_id ] ).fetchall()
    conn.close()
    sl = snaplogic.SnapLogic()
    return render_template( 'migrate_detail.html', sl=sl, requests=requests, comments=comments )
 
@app.route( "/migrate",  methods = [ 'POST', 'GET' ] )
@login_required
def migrate():
    conn = get_db_connection()
    if flask.request.method == 'POST':
        objects = []
        for key in flask.request.form.keys():
            if key.startswith( "migrate_" ):
                objects.append( flask.request.form[key] )
    
        inp = [ 'kkane', ';'.join( objects ) ]
        conn.execute( "INSERT INTO migrate_requests ( username, objects ) VALUES( ?, ? );", inp )
        conn.commit()
    requests = conn.execute('SELECT * FROM migrate_requests WHERE status != "complete"').fetchall()
    conn.close()
    sl = snaplogic.SnapLogic()
    return render_template( 'migrate.html', sl=sl, requests=requests )

