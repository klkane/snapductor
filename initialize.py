import sqlite3


conn = sqlite3.connect( 'var/snapductor_database.db' )

migrate_requests_create = '''CREATE TABLE migrate_requests( 
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            status TEST NOT NULL DEFAULT 'new',
            created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_on TIMESTAMP,
            completed_by TEXT,
            objects TEXT NOT NULL );'''

comments_create = '''CREATE TABLE comments(
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            request_id INTEGER NOT NULL,
            created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            comment TEXT NOT NULL);'''

users_create = '''CREATE TABLE users(
            username TEXT PRIMARY KEY,
            user_role TEXT NOT NULL,
            created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT NOT NULL);'''

conn.execute( migrate_requests_create )
conn.execute( comments_create )
conn.execute( users_create )

name = input("Enter username of initial Admin user: ") 
conn.execute( "INSERT INTO users (username, user_role, created_by) values(?, ?, ?)", [name, "Admin", name] )
conn.commit()

conn.close()
