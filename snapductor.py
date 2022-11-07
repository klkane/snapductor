from flask import Flask
from flask import render_template, redirect, url_for
import flask

import sqlite3
import snaplogic
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('db/database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    user = None
    sl = snaplogic.SnapLogic()
    return render_template( 'index.html', user=user, sl=sl )

@app.route("/history")
def history():
    user = None
    sl = snaplogic.SnapLogic()
    return render_template( 'history.html', user=user, sl=sl )

@app.route("/profile")
def profile():
    user = None
    sl = snaplogic.SnapLogic()
    return render_template( 'profile.html', user=user, sl=sl )

@app.route("/refresh")
def refresh():
    user = None
    sl = snaplogic.SnapLogic()
    sl.refresh_assets()
    return render_template( 'index.html', user=user, sl=sl )

@app.route("/migrate/delete/<request_id>" )
def migrate_delete( request_id ):
    user = None
    conn = get_db_connection()
    conn.execute( "DELETE FROM migrate_requests WHERE request_id = ?", [ request_id ] )
    conn.execute( "DELETE FROM comments WHERE request_id = ?", [ request_id ] )
    conn.commit()
    conn.close()
    return redirect(url_for('migrate'))
    
@app.route("/migrate/<request_id>",  methods = ['POST', 'GET'])
def migrate_detail( request_id ):
    user = None
    conn = get_db_connection()

    if flask.request.method == 'POST':
        conn.execute( "INSERT INTO comments( username, request_id, comment ) VALUES( ?, ?, ? )", 
            [ 'kkane', request_id, flask.request.form['addComment' ] ] )
        conn.commit()

    requests = conn.execute( "SELECT * FROM migrate_requests WHERE request_id = ?", [ request_id ] ).fetchall()
    comments = conn.execute( "SELECT * FROM comments WHERE request_id = ?", [ request_id ] ).fetchall()
    conn.close()
    sl = snaplogic.SnapLogic()
    return render_template( 'migrate_detail.html', user=user, sl=sl, requests=requests, comments=comments )
 
@app.route("/migrate",  methods = ['POST', 'GET'])
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
    user = None
    conn.close()
    sl = snaplogic.SnapLogic()
    return render_template( 'migrate.html', user=user, sl=sl, requests=requests )

