import sqlite3

conn = sqlite3.connect('db/database.db')

migrate_requests_create = '''CREATE TABLE migrate_requests( 
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            status TEST NOT NULL DEFAULT 'new',
            created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            objects TEXT NOT NULL );'''

comments_create = '''CREATE TABLE comments(
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            request_id INTEGER NOT NULL,
            created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            comment TEXT NOT NULL);'''

conn.execute( migrate_requests_create )
conn.execute( comments_create )
conn.close()
