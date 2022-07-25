import pandas as pd
import os, requests

cwd = os.getcwd()
filepath = f'{cwd}/delivery/shipping_fee/Tariff_Zoning_location .xlsx'
zoning_df = pd.read_excel(filepath, sheet_name=2)
pricing_df = pd.read_excel(filepath, sheet_name=1)
add_price_df = pd.read_excel(filepath, sheet_name=5)
intrastate_states = ['ibadan', 'ife', 'oshogbo']

def distance_matrix(merchant_address, consumer_address):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={consumer_address}&destinations={merchant_address}&key={os.environ.get('GOOGLE_KEY')}"

    try:
        r = requests.get(url)
        res = r.json()
        dist = res['rows'][0]['elements'][0]['distance']['text'].split()[0]
        
        return float(dist)
    except:
        return None


def calculate_shipping_fee(merchant_state, receiver_state, total_weight, merchant_address, receiver_address, shipping_type='NORMAL'):
    zone = zoning_df.loc[zoning_df['STATION NAME']==merchant_state.upper(), receiver_state.upper()].tolist()
    
    try:
        price = pricing_df.loc[pricing_df['Weight']==total_weight, 'ZONE ' + str(zone[0])].tolist()
    except:
        price = pricing_df.loc[pricing_df['Weight']==10, 'ZONE ' + str(zone[0])].tolist()
        extra_weight_rate = add_price_df[f'ZONE {zone[0]}']
        extra_weight = float(10.0) - float(total_weight)
        extra_price = extra_weight * extra_weight_rate
        price += extra_price

    if (merchant_state.lower() != receiver_state.lower()) or (merchant_state.lower() == 'lagos'):
        if shipping_type == 'NORMAL': 
            return {'success': True, 'fee': price[0] + (0.1*price[0])}
        elif shipping_type == 'EXPRESS' and merchant_state.lower() == 'lagos' and receiver_state.lower() == 'lagos':
            return {'success': True, 'fee': price[0] + (0.3*price[0])}
        return {'success': False, 'fee':0, 'message': "We do not yet fufill express deliveries within this location. We're working hard to be in your city soon" }

    elif (merchant_state.lower() == receiver_state.lower()) and (merchant_state in intrastate_states):
        if merchant_state.lower() == 'oshogbo':
            return {'success': True, 'fee':800}
        elif merchant_state.lower() in ['ife', 'ibadan']:
            distance = distance_matrix(merchant_address=merchant_address, consumer_address=receiver_address)
            if distance:
                fee = distance * 70
                if float(total_weight) > 3:
                    extra_weight = (float(total_weight) / 3) - 1
                    extra_fee = extra_weight * 100
                    fee += extra_fee

                if shipping_type == 'EXPRESS':
                    fee += (0.1*fee)

                if fee < 500:
                    return {'success': True, 'fee': 500, 'actual': fee}

                elif fee > 1000 and merchant_state.lower() == 'ife':
                    return {'success': True, 'fee': 1000, 'actual': fee}
                elif fee > 2000 and merchant_state.lower() == 'ibadan':
                    return {'success': True, 'fee': 2000, 'actual': fee}
                return {'success': True, 'fee': round(fee, -1), 'actual': fee}
                
            return {'success': True, 'fee':850}
    else:
        return {'success': True, 'fee': price[0] + (0.1*price[0])}