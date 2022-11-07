from flask import Flask
from flask import render_template

import snaplogic

app = Flask(__name__)

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

@app.route("/migrate",  methods = ['POST', 'GET'])
def migrate():
    user = None
    sl = snaplogic.SnapLogic()
    return render_template( 'migrate.html', user=user, sl=sl )

