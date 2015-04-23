"""
This module implements the functionality for request authentication. 
API handler classes can inherit the functionality of any of these mixins.

Where possible, like in the case of ``SessionAuthentication``, we make use of
Django's middlewares(which have already ran), to identify whether the request
is authenticated and who the authenticated user is.
In other cases, we implement the whole logic in the authentication mixin.
"""
class AuthenticationMixin(object):
    """
    Any API handler that inherits from this Mixin or any of its children
    classes, inherits the ``is_authenticated`` method, which returns True if
    the request is authenticated, or False otherwise. Some ``request`` object
    attributes might be set as well.
    """
    def is_authenticated(self):
        raise NotImplemented


class NoAuthentication(AuthenticationMixin):
    def is_authenticated(self):
        return True


class SessionAuthentication(AuthenticationMixin):
    """
    Requires that the following Django middlewares are enabled:
    * ``django.contrib.sessions.middleware.SessionMiddleWare``
    * ``django.contrib.auth.middleware.AuthenticationMiddleWare``

    The ``django.contrib.sessions.middleware.SessionMiddleWare``, takes care of
    translating the incoming requests's session key, and assigning the
    corresponding Session instance to ``request.session``.
    Then, the ``django.contrib.auth.middleware.AuthenticationMiddleware``,
    assigns the User instance corresponding to ``request.session``, to
    ``request.user``.

    If the user indeed has a valid and authenticated session, then
    ``request.user`` will point to a valid User instance. Otherwise it points
    to an AnonymousUser instance. Applying the User class's
    ``is_authenticated`` method, returns True or False accordingly.
    """
    def is_authenticated(self):
        if hasattr(self.request, 'user'):
            return self.request.user.is_authenticated()
        return False


