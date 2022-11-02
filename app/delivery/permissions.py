from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import BaseHasAPIKey, KeyParser

class BearerKeyParser(KeyParser):
    keyword = "Bearer"

class HasAPIKey(BaseHasAPIKey):
    model = APIKey
    key_parser = BearerKeyParser()
