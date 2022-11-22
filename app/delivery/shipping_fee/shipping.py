import pandas as pd
import os, requests

cwd = os.getcwd()
filepath = f'{cwd}/delivery/shipping_fee/Tariff_Zoning_location .xlsx'
zoning_df = pd.read_excel(filepath, sheet_name=2)
pricing_df = pd.read_excel(filepath, sheet_name=1)
add_price_df = pd.read_excel(filepath, sheet_name=5)
intrastate_states = ['ibadan', 'ife', 'oshogbo', 'lagos(mainland)', 'lagos(island)']
speedaf_states = ['lagos', 'abuja', 'kaduna', 'kano', 'bauchi', 'calabar', 'katsina']

def speedaf(merchant_state, receiver_state, total_weight):
    stations = zoning_df['STATION NAME'].values
    if merchant_state.upper() not in stations or receiver_state.upper() not in stations:
        return None
    zone = zoning_df.loc[zoning_df['STATION NAME']==merchant_state.split('(')[0].upper(), receiver_state.split('(')[0].upper()].tolist()
    try:
        price = pricing_df.loc[pricing_df['Weight']==total_weight, 'ZONE ' + str(zone[0])].tolist()
    except:
        price = pricing_df.loc[pricing_df['Weight']==10, 'ZONE ' + str(zone[0])].tolist()
        extra_weight_rate = add_price_df[f'ZONE {zone[0]}']
        extra_weight = float(10.0) - float(total_weight)
        extra_price = extra_weight * extra_weight_rate
        price += extra_price

    return price

def topship(merchant_state, receiver_state, total_weight):
    topship_directory = f'{cwd}/delivery/shipping_fee/Topship.xlsx'
    receiver_state = receiver_state + ' state'
    if merchant_state.lower() == 'lagos':
        topship_df = pd.read_excel(topship_directory, sheet_name=0)
        merchant_state = 'Lagos state'
    elif merchant_state.lower() == 'abuja':
        topship_df = pd.read_excel(topship_directory, sheet_name=1)
        merchant_state = 'Abuja'
    else:
        return None

    if float(total_weight) <= float(2.0):
        total_weight = '0-2kg'
    elif float(total_weight) == float(3.0):
        total_weight = '3kg '
    else:
        total_weight = str(total_weight) + 'kg'
    price = topship_df.loc[topship_df['States']==receiver_state].loc[topship_df['WEIGHT']==total_weight]['TOPSHIP STANDARD PRICE']
    delivery_eta = topship_df.loc[topship_df['States']==receiver_state].loc[topship_df['WEIGHT']==total_weight]['DELIVERY TIMELINE']
    return (price.tolist()[0], delivery_eta.tolist()[0])


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
    if merchant_state.lower() != receiver_state.lower():
        if shipping_type == 'NORMAL': 
            if (merchant_state.lower() in ['lagos(mainland)', 'lagos(island)']) and (receiver_state.lower() in ['lagos(mainland)', 'lagos(island)']):
                return {'success': True, 'fee': 2500}
            zone = zoning_df.loc[zoning_df['STATION NAME']==merchant_state.split('(')[0].upper(), receiver_state.split('(')[0].upper()].tolist()
            try:
                price = pricing_df.loc[pricing_df['Weight']==total_weight, 'ZONE ' + str(zone[0])].tolist()
            except:
                price = pricing_df.loc[pricing_df['Weight']==10, 'ZONE ' + str(zone[0])].tolist()
                extra_weight_rate = add_price_df[f'ZONE {zone[0]}']
                extra_weight = float(10.0) - float(total_weight)
                extra_price = extra_weight * extra_weight_rate
                price += extra_price
            return {'success': True, 'fee': round(price[0] + (0.03*price[0]), -1)}

    elif merchant_state.lower() == receiver_state.lower():
        if merchant_state.lower() in ['ife', 'ibadan']:
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
                    return {'success': True, 'fee': 1500, 'actual': fee}
                elif fee > 2000 and merchant_state.lower() == 'ibadan':
                    return {'success': True, 'fee': 1500, 'actual': fee}
                return {'success': True, 'fee': round(fee, -1), 'actual': fee}  
            return {'success': True, 'fee':850}
        elif merchant_state.lower() == 'lagos(mainland)':
            return {'success': True, 'fee':1700}
        elif merchant_state.lower() == 'oshogbo':
            return {'success': True, 'fee':800}
        return {'success':True, 'fee':1500}


def calculate_shipping_rates(merchant_state, receiver_state, total_weight, merchant_address, receiver_address, merchant_city, receiver_city, logistics_company, shipping_type='NORMAL'):
    match logistics_company:
        case "speedaf":
            if merchant_state.lower() in speedaf_states:
                merchant_city = merchant_state.lower()
            elif 'ife' in merchant_city.lower():
                merchant_city = 'ife'

            if receiver_state.lower() in speedaf_states:
                receiver_city = receiver_state.lower()
            elif 'ife' in receiver_city.lower():
                receiver_city = 'ife'

            price = speedaf(merchant_city, receiver_city, total_weight)

            if price:
                fee = round(price[0] + (0.03*price[0]), -1)
            else:
                fee = price
                
            if merchant_city.lower() != receiver_city.lower():
                delivery_eta = "2 to 5 working days"
            else:
                delivery_eta = "1 to 2 working days"
            return {'success': True, 'fee': fee, 'delivery_eta': delivery_eta}
        case "dhl":
            return {'success': True, 'fee':4000, 'delivery_eta': "1 to 2 working days"}
        case "topship":
            price = topship(merchant_state, receiver_state, total_weight)

            if price:
                fee = round(float(price[0]) + (0.03*float(price[0])), -1)
                delivery_eta = price[1]
            else:
                fee = price
                delivery_eta = None
            return {'success': True, 'fee': fee, 'delivery_eta': delivery_eta}