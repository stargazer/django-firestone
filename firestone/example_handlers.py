from firestone.handlers import BaseHandler
from firestone import exceptions
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils import timezone
from itsdangerous import TimedJSONWebSignatureSerializer


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
        s = TimedJSONWebSignatureSerializer(
            settings.SECRET_KEY, 
            expires_in=3600*24
        )
        token = s.dumps({'iss': self.request.data.id} # ``iss`` symbolizes the issuer(user)
        
        return {'token': token}

