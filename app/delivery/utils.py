from .models import DeliveryRate
from datetime import datetime
import requests
import os


def distance_matrix(merchant_address, consumer_address):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={consumer_address}&destinations={merchant_address}&key={os.environ.get('GOOGLE_KEY')}"

    r = requests.get(url)
    res = r.json()
    dist = res['rows'][0]['elements'][0]['distance']['text'].split()[0]

    return float(dist)


def calculate_shipping_fee(weight_range, merchant_state, receiver_state):
    available_rates = {
        'small': ['0.5kg - 4kg', '4kg - 10kg'],
        'big': [
            '10kg - 15kg',
            '15kg - 20kg',
            '20kg - 25kg',
            "25kg - 30kg",
        ]
    }
    try:
        if merchant_state.lower() == receiver_state.lower():
            if DeliveryRate.objects.filter(states__contains=[merchant_state]).exists():
                rate = DeliveryRate.objects.filter(
                    states__contains=[merchant_state]).first()

                if weight_range in available_rates['small']:
                    return {'shipping_fee': float(rate.min_intrastate_fee)}
                return {'shipping_fee': float(rate.max_intrastate_fee)}
            return {'shipping_fee': float(rate.max_intrastate_fee)}

        if DeliveryRate.objects.filter(states__contains=[merchant_state, receiver_state]).exists():
            rate = DeliveryRate.objects.filter(
                states__contains=[merchant_state]).first()

            if weight_range in available_rates['small']:
                return {'shipping_fee': float(rate.min_interstate_fee)}
            return {'shipping_fee': float(rate.max_interstate_fee)}
        return {'shipping_fee': float(3000.00)}
    except Exception as e:
        return {'shipping_fee': float(3000.00)}


def split_datetime_object(datetime_object):
    if datetime_object and type(datetime_object) is not dict:
        datetime_object = datetime_object.split('+')
        date = datetime.strptime(datetime_object[0].split('T')[0], '%Y-%m-%d')
        time_obj = datetime.strptime(datetime_object[0].split('T')[1], '%H:%M:%S.%f')
        return {'date': date.strftime('%d/%m/%Y'), 'time':time_obj.strftime("%I:%M %p")}
    return datetime_object
