"""
This module implements the functionality for request authentication. The
classes here are actually mixins, and therefore are not meant to stand on their
own. They add the authentication functionality to API handler classes.
Where possible, like in the case of ``SessionAuthentication``, we make use of
Django's middlewares(which have already ran), to identify whether the request
is authenticated and who the authenticated user is.

In other cases, we implement the whole logic in the authentication mixin.
"""
from django.contrib.auth.models import AnonymousUser
from django.core import signing
from django.contrib.auth import get_user_model
User = get_user_model()
from collections import OrderedDict
import itsdangerous
import urllib


class Authentication(object):
    """
    All the mixins of this module, other than ``Authentication`` can be used in
    the ``authentication`` parameter of any API handler, therefore defining the
    handler's authentication method.

    The handler's metaclass makes sure that the ``authentication`` class is
    used as a mixin(superclass) by the handler, therefore inheriting its
    functionality.
    """
    pass


class NoAuthentication(Authentication):
    def is_authenticated(self):
        return True


class SessionAuthentication(Authentication):
    """
    Requires that the following Django middlewares are enabled:
    * ``django.contrib.sessions.middleware.SessionMiddleWare``
    * ``django.contrib.auth.middleware.AuthenticationMiddleWare``

    The ``django.contrib.sessions.middleware.SessionMiddleWare``, takes care of
    translating the incoming requests's session key, and assigning the
    corresponding Session instance to ``request.session``.
    Then, the ``django.contrib.auth.middleware.AuthenticationMiddleware``,
    assings the User instance corresponding to ``request.session``, to
    ``request.user``.

    So, all we have to do here is check whether the ``request.user``
    is authenticated.
    """
    def is_authenticated(self):
        if hasattr(self.request, 'user'):
            return self.request.user.is_authenticated()
        return False


class SignatureAuthentication(Authentication):
    """
    Signature included in querystring of the incoming HttpRequest object. The
    signature is produced from a string, comprised of:
        * HTTP Method
        * URL with querystring parameters (including a parameter indicating
          the max_age of the signature)

    Makes use of the handler class parameters ``signer``, ``sig_param``, and
    ``max_age_param``
    """
    def is_authenticated(self):
        """
        Strictly speaking, this is not an authentication check, since we don't
        really check whether the request is from who it claims to be. We check
        whether it's valid and can go through.

        Returns True if request signature is valid, else False
        """
        # url, without querystring
        url = self.request.build_absolute_uri().split('?')[0]
        method = self.request.method.upper()
        signature = self.request.GET.get(self.sig_param, '')
        # max_age parameter
        try:
            max_age = int(self.request.GET.get(self.max_age_param, 0))
        except ValueError:
            max_age = 0

        # Building the string that generated the signature, by constructing the
        # request url without the signature parameter
        query_params = {key: value for key, value in self.request.GET.items()
                        if key != self.sig_param}
        qs = self._dict_to_ordered_qs(query_params)
        full_url = '%s?%s' % (url, qs)
        string = self._get_string(method, full_url)

        # Check if indeed this string generated the signature we got
        try:
            self.signer.unsign('%s:%s' % (string, signature), max_age=max_age)
        except signing.BadSignature, signing.SignatureExpires:
            return False

        self.request.user = self.verify_request_user()
        return True

    def get_signed_url(self, url, method, params, max_age):
        """
        This method should be used by API handlers.

        It signs the request, and returns the url with the signature and
        max_age parameters in the querystring.
        """
        self._update_params(url, method, params, max_age)
        return '%s?%s' % (url, urllib.urlencode(params))

    def verify_request_user(self):
        """
        Returns:
            User instance, if correctly identified by the signature and
            querystring.
            None otherwise.

        Override in the handler class to specify the logic.
        """
        return AnonymousUser()

    def _update_params(self, url, method, params, max_age):
        """
        Updates the ``params`` dictionary, with signature and max_age
        parameters.

        This dictionary is now ready to be url encoded as a querystring and
        appended on the url.
        """
        params[self.max_age_param] = max_age
        params[self.sig_param] = self._get_signature(
            url,
            method,
            params,
            max_age
        )
        return params

    def _get_signature(self, url, method, params, max_age):
        """
        Returns signature
        """
        qs = self._dict_to_ordered_qs(params)
        # generate full_url
        full_url = '%s?%s' % (url, qs)
        # generate string to sign
        string = self._get_string(method, full_url)

        return self._sign_string(string)

    def _dict_to_ordered_qs(self, params):
        """
        Turns the ``params`` dict to a sorted querystring and returns it
        """
        # make params a sorted dictionary
        params = OrderedDict(sorted(params.items(), key=lambda t: t[0]))
        # turn params into a querystring
        return '&'.join(
            '%s=%s' % (key, value) for key, value in params.items()
        )

    def _get_string(self, method, url):
        """
        Builds the string that we want to sign
        """
        return '%s-%s' % (method.upper(), url)

    def _sign_string(self, string):
        """
        @param string: String to sign. It has the form:
            ``<HTTP method>-<url with querystring parameters>``
        """
        # Signature is of form <string>:<sig1>:<sig2>.
        sig = self.signer.sign(string)

        # I want to return the part ``<sig1>:<sig2>``
        parts = sig.rsplit(':', 2)
        return '%s:%s' % (parts[1], parts[2])


class JWTAuthentication(Authentication):
    def is_authenticated(self):
        """
        Retrieves the token from the ``Authorization`` header, verifies it,
        makes sure it refers to a valid User instance, sets ``request.user``
        accordingly.
        """
        # Retrieve token from request header
        token = self._get_token()
        if not token:
            return False

        s = self.jwt_signer
        try:
            payload = s.loads(token)
        except itsdangerous.BadSignature:
            return False

        # Get the user that the JWT authenticates
        self.request.user = self.verify_request_user(payload)
        if not self.request.user.id:
            return False

        return True

    def verify_request_user(self, payload):
        """
        @param payload: Decrypted payload

        Returns:
            User instance, if correctly identified by the JWT token
            AnonymousUser() otherwise.

        This method assumes that the ``iss`` payload parameter contains the
        User id, and sets the ``self.request.user`` to that corresponding User
        instance.
        Override in the handler class if the ``payload`` contains different
        data.
        """
        user = AnonymousUser()

        user_id = payload.get('iss', None)
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

        return user

    def _get_token(self):
        """
        Returns the token from the ``Authorization: JWT <token>`` header
        """
        authorization = self.request.META.get('HTTP_AUTHORIZATION', '')
        if not authorization:
            return None

        try:
            type, token = authorization.split()
        except ValueError:
            return None

        if type != 'JWT':
            return None

        return token


# TODO
# class ApiKeyAuthentication?
# Or something similar that actually signs requests. Study the Amazon AWS
# authentication scheme.
