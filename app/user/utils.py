from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from django.core.files import File
from urllib.request import urlretrieve
import os, requests

def send_email(subject, email_from, html_alternative, text_alternative):
    msg = EmailMultiAlternatives(
        subject, text_alternative, settings.EMAIL_FROM, [email_from])
    msg.attach_alternative(html_alternative, "text/html")
    msg.send(fail_silently=False)


async def create_file_from_image(url):
    return File(open(url, 'rb'))


def get_user_data(user_id):
    url = f"{os.environ.get('AUTH_URL')}/{user_id}/"
    res = requests.get(url, verify=False)
    user = res.json()
    return user

def get_user_store_orders(user_id):
    url = f"https://api.boxin.ng/api/v1/store/store-orders/?user={user_id}/"
    res = requests.get(url, verify=False)
    orders = res.json()

    if orders['success']:
        return orders['orders']
    return None