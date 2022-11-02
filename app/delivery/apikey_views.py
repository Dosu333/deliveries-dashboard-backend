from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_api_key.models import APIKey


class GenerateAPIKey(views.APIView):
    """Generate API Key for a user"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            api_key, key = APIKey.objects.create_key(name=str(self.request.user.id))
            return Response({'success':True, 'key': key}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        