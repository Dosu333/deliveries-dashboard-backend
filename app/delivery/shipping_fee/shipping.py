import pandas as pd
import os

cwd = os.getcwd()
filepath = f'{cwd}/delivery/shipping_fee/Tariff_Zoning_location .xlsx'
zoning_df = pd.read_excel(filepath, sheet_name=2)
pricing_df = pd.read_excel(filepath, sheet_name=1)
add_price_df = pd.read_excel(filepath, sheet_name=5)
intrastate_states = ['ibadan', 'ife', 'oshogbo']

def calculate_shipping_fee(merchant_state, receiver_state, total_weight, shipping_type='NORMAL'):
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
        return {'success': True, 'fee':700}
    else:
        return {'success': True, 'fee': price[0] + (0.1*price[0])}