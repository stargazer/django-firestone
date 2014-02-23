"""
This module checks the authentication of incoming requests. 
Where possible, like in the case of ``SessionAuthentication``, we make use of
Django's middlewares(which have already ran), to identify whether the request
is authenticated and who the authenticated user is.

In other cases, we implement the whole logic in the authentication class, make
sure that it can identify if the user is authenticated which user it is, and
set the corresponding HttpRequest object parameters, where possible
"""
from django.contrib.auth.models import AnonymousUser

class Authentication:
    pass

class NoAuthentication(Authentication):
    def is_authenticated(self, request, *args, **kwargs):
        request.user = AnonymousUser()
        return True

class SessionAuthentication(Authentication):    
    """
    Requires that the following Djanoo middlewares are enabled:
    * ``django.contrib.sessions.middleware.SessionMiddleWare``
    * ``django.contrib.auth.middleware.AuthenticationMiddleWare``

    The ``django.contrib.sessions.middleware.SessionMiddleWare``, takes care of
    translating the incoming requests's session key, and assigning the
    corresponding Session instance to ``request.session``.
    Then, the ``django.contrib.auth.middleware.AuthenticationMiddleware``,
    assings the User instance corresponding to ``request.session``, to
    ``request.user``.

    So here we check whether the ``request.user`` is authenticated.
    """
    def is_authenticated(self, request, *args, **kwargs):
        if hasattr(request, 'user'):
            return request.user.is_authenticated()        
        return False

class SignatureAuthentication(Authentication):
    """
    Signature included in querystring (or better some header) of the incoming HttpRequest object.
    The signature is computer using all querystring parameters. One standard
    querystring parameter, called ``u`` should point to the user id of the User
    on behalf of whom the request is performed.
    Parameters ``request.user`` is set accordingly.
    """
    pass

class TokenAuthentication(Authentication):
    """
    Token included in ``Authentication``, indicates a token which belongs to a
    User. Parameter ``request.user`` is set accordingly.
    """
    pass


