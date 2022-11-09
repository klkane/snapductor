from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
import snaplogic

migrate_pages = Blueprint( 'simple_page', __name__, template_folder='../templates' )

@migrate_pages.route( "/migrate",  methods = [ 'POST', 'GET' ] )
@login_required
def migrate():
    sl = snaplogic.SnapLogic()
    conn = sl.get_db_connection()
    if request.method == 'POST':
        objects = []
        for key in request.form.keys():
            if key.startswith( "migrate_" ):
                objects.append( flask.request.form[key] )
    
        inp = [ 'kkane', ';'.join( objects ) ]
        conn.execute( "INSERT INTO migrate_requests ( username, objects ) VALUES( ?, ? );", inp )
        conn.commit()
    requests = conn.execute('SELECT * FROM migrate_requests WHERE status != "complete"').fetchall()
    conn.close()
    return render_template( 'migrate.html', sl=sl, requests=requests )

