from flask import Blueprint, request, jsonify
import requests
from datetime import datetime, timedelta
import json

booking_bp = Blueprint('booking', __name__)

TRAVELPAYOUTS_TOKEN = "c8ea19ecfemsh38802276d905c75p1c25e4jsn933067596bba"
AFFILIATE_MARKER = "pndi94uR"
TRAVELPAYOUTS_BASE_URL = "https://travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com"

RAPIDAPI_HEADERS = {
    "X-RapidAPI-Key": TRAVELPAYOUTS_TOKEN,
    "X-RapidAPI-Host": "travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com"
}

GRAMADO_AIRPORTS = {
    "POA": {"name": "Porto Alegre", "distance": "115 km de Gramado"},
    "CXJ": {"name": "Caxias do Sul", "distance": "65 km de Gramado"},
    "UBA": {"name": "Uruguaiana", "distance": "350 km de Gramado"}
}

@booking_bp.route('/search-flights', methods=['POST'])
def search_flights():
    try:
        data = request.get_json()
        origin = data.get('origin', 'GRU')
        departure_date = data.get('departure_date')
        return_date = data.get('return_date')
        passengers = data.get('passengers', 1)
        destination = "POA"
        url = f"{TRAVELPAYOUTS_BASE_URL}/v1/prices/cheap"
        params = {
            "origin": origin,
            "destination": destination,
            "depart_date": departure_date,
            "return_date": return_date if return_date else "",
            "currency": "BRL",
            "market": "BR",
            "locale": "pt"
        }
        response = requests.get(url, headers=RAPIDAPI_HEADERS, params=params)
        if response.status_code == 200:
            flight_data = response.json()
            processed_flights = process_flight_data(flight_data, origin, destination)
            return jsonify({
                'flights': processed_flights,
                'destination_info': GRAMADO_AIRPORTS[destination],
                'search_params': {
                    'origin': origin,
                    'destination': destination,
                    'departure_date': departure_date,
                    'return_date': return_date,
                    'passengers': passengers
                },
                'affiliate_info': {
                    'marker': AFFILIATE_MARKER,
                    'booking_url': f"https://compensair.tp.st/{AFFILIATE_MARKER}"
                }
            })
        else:
            return jsonify({
                'error': 'Erro ao buscar voos',
                'fallback_flights': get_fallback_flights(origin, destination)
            }), 500
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

def process_flight_data(flight_data, origin, destination):
    processed = []
    if 'data' in flight_data:
        for flight in flight_data['data'][:10]:
            processed.append({
                'price': flight.get('price', 0),
                'currency': 'BRL',
                'origin': origin,
                'destination': destination,
                'departure_date': flight.get('depart_date'),
                'return_date': flight.get('return_date'),
                'airline': flight.get('airline', 'N/A'),
                'duration': flight.get('duration', 'N/A'),
                'stops': flight.get('transfers', 0),
                'booking_url': f"https://compensair.tp.st/{AFFILIATE_MARKER}?origin={origin}&destination={destination}",
                'gramado_transfer': {
                    'distance': GRAMADO_AIRPORTS[destination]['distance'],
                    'options': [
                        'Ônibus executivo (2h30min)',
                        'Transfer privado (2h)',
                        'Carro alugado (2h)'
                    ]
                }
            })
    return processed

def get_fallback_flights(origin, destination):
    return [
        {
            'price': 450,
            'currency': 'BRL',
            'origin': origin,
            'destination': destination,
            'airline': 'GOL',
            'duration': '1h30min',
            'stops': 0,
            'booking_url': f"https://compensair.tp.st/{AFFILIATE_MARKER}",
            'note': 'Preço estimado'
        }
    ]
