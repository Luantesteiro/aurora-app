from flask import Flask
from booking import booking_bp

app = Flask(__name__)
app.register_blueprint(booking_bp)
