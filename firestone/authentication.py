

class Authentication:
    pass

class NoAuthentication(Authentication):
    def is_authenticated(self, request, *args, **kwargs):
        return True

class DjangoAuthentication(Authentication):    
    def is_authenticated(self, request, *args, **kwargs):
        return request.user.is_authenticated()        
