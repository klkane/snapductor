from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
import snaplogic

migrate_pages = Blueprint( 'migrate_pages', __name__, template_folder='../templates' )

@migrate_pages.route( "/migrate",  methods = [ 'POST', 'GET' ] )
@login_required
def migrate():
    sl = snaplogic.SnapLogic()
    conn = sl.get_db_connection()
    if request.method == 'POST':
        objects = []
        for key in request.form.keys():
            if key.startswith( "migrate_" ):
                objects.append( request.form[key] )
    
        inp = [ current_user.username, ';'.join( objects ) ]
        conn.execute( "INSERT INTO migrate_requests ( username, objects ) VALUES( ?, ? );", inp )
        conn.commit()
    requests = conn.execute('SELECT * FROM migrate_requests WHERE status != "complete"').fetchall()
    conn.close()
    return render_template( 'migrate.html', sl=sl, requests=requests )

@migrate_pages.route( "/migrate/complete/<request_id>" )
@login_required
def migrate_complete( request_id ):
    sl = snaplogic.SnapLogic()
    conn = sl.get_db_connection()
    
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
    
    conn.execute( "UPDATE migrate_requests SET status = 'complete', completed_on = CURRENT_TIMESTAMP, completed_by = ? WHERE request_id = ?", [ current_user.username, request_id ] )
    conn.commit()

    conn.close()
    return render_template( 'migrate_complete.html', sl=sl, requests=requests, comments=comments )
    
@migrate_pages.route( "/migrate/delete/<request_id>" )
@login_required
def migrate_delete( request_id ):
    sl = snaplogic.SnapLogic()
    conn = sl.get_db_connection()
    conn.execute( "DELETE FROM migrate_requests WHERE request_id = ?", [ request_id ] )
    conn.execute( "DELETE FROM comments WHERE request_id = ?", [ request_id ] )
    conn.commit()
    conn.close()
    return redirect( url_for( 'migrate' ) )
    
@migrate_pages.route( "/migrate/<request_id>",  methods = [ 'POST', 'GET' ] )
@login_required
def migrate_detail( request_id ):
    sl = snaplogic.SnapLogic()
    conn = sl.get_db_connection()

    if request.method == 'POST':
        conn.execute( "INSERT INTO comments( username, request_id, comment ) VALUES( ?, ?, ? )", 
            [ 'kkane', request_id, request.form['addComment' ] ] )
        conn.commit()
    
    requests = conn.execute( "SELECT * FROM migrate_requests WHERE request_id = ?", [ request_id ] ).fetchall()
    comments = conn.execute( "SELECT * FROM comments WHERE request_id = ?", [ request_id ] ).fetchall()
    
    return render_template( 'migrate_detail.html', sl=sl, requests=requests, comments=comments )
