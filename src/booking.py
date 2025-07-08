from flask import Blueprint
booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/')
def index():
    return {'message': 'Aurora online'}