from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def index():
    user = None
    return render_template( 'index.html', user=user )

@app.route("/history")
def history():
    user = None
    return render_template( 'history.html', user=user )

@app.route("/profile")
def profile():
    user = None
    return render_template( 'profile.html', user=user )
