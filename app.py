import os
import requests
from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim

################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""

    city = request.args.get('city')
    units = request.args.get('units')

    params = {
        'appid': API_KEY,
        'q': city,
        'units': units
    }

    result_json = requests.get(API_URL, params=params).json()

    #pp.pprint(result_json)

    sunrise = datetime.fromtimestamp(result_json['sys']['sunrise'])
    sunset = datetime.fromtimestamp(result_json['sys']['sunset'])
    context = {
        'date': (datetime.now()).strftime('%A, %B %d, %Y'),
        'city': city,
        'units': units,
        'description': result_json['weather'][0]['description'],
        'temp':  result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': sunrise.strftime('%H:%M'),
        'sunset': sunset.strftime('%H:%M'),
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')

    params = {
        'one': {
            'appid': API_KEY,
            'q': city1,
            'units': units
            },
        'two': {
            'appid': API_KEY,
            'q': city2,
            'units': units
        }
    }

    result_json_one = requests.get(API_URL, params=params['one']).json()
    result_json_two = requests.get(API_URL, params=params['two']).json()

    context = { 
        'date': (datetime.now()).strftime('%A, %B %d, %Y'),
        'units': units,
        'units_letter': get_letter_for_units(units),
        'city1_info': {
            'city': city1,
            'temp':  result_json_one['main']['temp'],
            'humidity': result_json_one['main']['humidity'],
            'wind_speed': result_json_one['wind']['speed'],
            'sunrise': result_json_one['sys']['sunrise'],
            'sunset': int((datetime.fromtimestamp(result_json_one['sys']['sunset'])).strftime('%H'))
        },
        'city2_info': {
            'city': city2,
            'temp':  result_json_two['main']['temp'],
            'humidity': result_json_two['main']['humidity'],
            'wind_speed': result_json_two['wind']['speed'],
            'sunrise': result_json_two['sys']['sunrise'],
            'sunset': int((datetime.fromtimestamp(result_json_two['sys']['sunset'])).strftime('%H'))
        }
    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)