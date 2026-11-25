from flask import Flask
from flask_session import Session

from auth import auth_bp
from doctor import doctor_bp
from patient import patient_bp

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.register_blueprint(auth_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(patient_bp)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
