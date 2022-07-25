from celery import shared_task
from core.celery import APP
from twilio.rest import Client
from user.utils import get_user_data
import datetime


@APP.task()
def send_alert_updates(delivery_object):
    user = get_user_data(delivery_object['business_id'])
    pickup_time = datetime.datetime.strptime(delivery_object['pickup_time'], '%Y-%m-%d')

    if delivery_object['pickup_state'].lower() == delivery_object['destination_state'].lower():
        eta = pickup_time + datetime.timedelta(days=1)
    else:
        eta = pickup_time + datetime.timedelta(days=5)

    pickup_eta = pickup_time + datetime.timedelta(days=1)
    delivery_date = eta.strftime('%A, %d/%m/%Y')
    delivery_day = eta.strftime('%A')
    date_delivery = eta.strftime('%d/%m/%Y')
    pickup_day = pickup_eta.strftime('%A')
    pickup_date = pickup_eta.strftime('%d/%m/%Y')

    from_number = '+12312625574'
    admin_to_numbers = ['+2347056918098', '+2348136800327', '+2349077499434']
    customer_to_number = '+234' + delivery_object['customer_phone'].lstrip('0')
    merchant_to_number = '+234' + str(user['phone']).lstrip('0')

    admin_body = f"{user['businessname']} requested a delivery that cost {delivery_object['amount_paid']}. The owner's name and phone number are {user['firstname']+' '+user['lastname']} and {user['phone']} respectively. {delivery_object['number_of_items']} items are to be picked up from {delivery_object['pickup_address']} in {delivery_object['pickup_state']} on {pickup_time.strftime('%A, %d/%m/%Y')} and delivered to {delivery_object['destination_address']} in {delivery_object['destination_state']}. The customer receiving the goods is {delivery_object['customer_name']} and their phone number is {delivery_object['customer_phone']}."
    customer_body = f"Hi, this is Rotimi from Boxin. Boxin is a logistics company that works with {str(user['businessname']).capitalize()}. We will be picking up your order from {str(user['businessname']).capitalize()} and it will be delivered to you on {delivery_date} at the latest."
    merchant_body = f"Hi, this is Rotimi from Boxin. We have received your delivery request. It will be picked up on or before {pickup_day}, {pickup_date} and will also be delivered to your customer on {delivery_day}, {date_delivery} at the latest."

    client = Client()
    client.messages.create(to=f'whatsapp:{merchant_to_number}', from_=f'whatsapp:{from_number}', body=merchant_body)
    client.messages.create(to=f'whatsapp:{customer_to_number}', from_=f'whatsapp:{from_number}', body=customer_body)

    for number in admin_to_numbers:
        client.messages.create(to=f"whatsapp:{number}", from_=f'whatsapp:{from_number}', body=admin_body)