from firestone.handlers import BaseHandler
from firestone import exceptions
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import jwt


class ObtainJWTHandler(BaseHandler):
    """
    Logs in a Django user with POST {username, password}.
    Returns a JWT that's valid for a day.
    """
    http_methods = ('POST',)
    post_body_fields = ('username', 'password',)
    
    template = {
        'fields': ('token',) 
    }

    def validate(self):
        user = authenticate(
            username=self.request.data.get('username', ''),
            password=self.request.data.get('password', ''),
        )
        if not user or not user.is_active:
            raise exceptions.BadRequest('Incorrect credentials')

        self.request.data = user

    def post(self):
        headers = {
            'typ': 'JWT', 
            'alg': 'HS512', 
        }
        payload = {
            'iss': self.request.data.id,                  # issuer: The user making the request       
            'iat': timezone.now(),                        # issued at
            'exp': timezone.now() +  timedelta(days=1),   # expires at
        }            

        return {
            'token': jwt.encode(
                        headers=headers,
                        payload=payload, 
                        key=settings.SECRET_KEY,
                        algorithm=headers['alg'],
                     )
        }

