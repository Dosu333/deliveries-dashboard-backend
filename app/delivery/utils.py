import requests
import os

def distance_matrix(merchant_address, consumer_address):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={consumer_address}&destinations={merchant_address}&key={os.environ.get('GOOGLE_KEY')}"

    r = requests.get(url)
    res = r.json()
    dist = res['rows'][0]['elements'][0]['distance']['text'].split()[0]
    
    return float(dist)


def calculate_shipping_fee(merchant_address, consumer_address, weight_range, merchant_state, consumer_state):
    pass