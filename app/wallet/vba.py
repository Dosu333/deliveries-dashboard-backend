import os, requests

class VirtualBankAccount:
    def __init__(self, first_name, last_name, phone, email):
        self.url = 'https://api.paystack.co/'
        self.headers = {'Authorization': 'Bearer sk_test_b7b83c1b97164a946a7c5bd50c3292acd56bc96d'}
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email

    def create_customer(self):
        url = self.url + 'customer'
        data = {
            'email': self.email,
            # 'first_name': self.first_name,
            # 'last_name': self.last_name,
            # 'phone': self.phone
        }

        res = requests.post(url, data=data, headers=self.headers)
        response = res.json()

        if response['status']:
            return response['data']['customer_code']
        return None

    def create_virtual_bank_account(self):
        url = self.url + 'dedicated_account'
        customer = self.create_customer()
        data = {
            'customer': customer,
            'preferred_bank': "test-bank"
        }

        res = requests.post(url, data=data, headers=self.headers)
        response = res.json()
        response = {
            'account_no': response['data']['account_number'],
            'bank': response['data']['bank']['slug'],
            'account_name': response['data']['account_name'],
            'customer': customer
        }
        return response

# vba = VirtualBankAccount('John', 'Doe', '+2347031589736', 'vladamir1865@gmail.com')

# print(vba.create_virtual_bank_account())