"""
This module checks the authentication of incoming requests. 
Where possible, like in the case of ``SessionAuthentication``, we make use of
Django's middlewares(which have already ran), to identify whether the request
is authenticated and who the authenticated user is.

In other cases, we implement the whole logic in the authentication class.
"""
from django.contrib.auth.models import AnonymousUser
from django.core.signing import TimestampSigner
from django.core.signing import BadSignature
from django.core.signing import SignatureExpired
from django.utils import timezone
from collections import OrderedDict
from datetime import datetime
import urllib
import time



class Authentication:
    pass

class NoAuthentication(Authentication):
    def is_authenticated(self, request, *args, **kwargs):
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

    So, all we have to do here is check whether the ``request.user`` is authenticated.
    """
    def is_authenticated(self, request, *args, **kwargs):
        if hasattr(request, 'user'):
            return request.user.is_authenticated()        
        return False

class SignatureAuthentication(Authentication):
    """
    Signature included in querystring of the incoming HttpRequest object. The
    signature is produced from a string, comprised of:
        * HTTP Method
        * URL with querystring parameters (including a parameter indicating the max_age
          of the signature)
    """
    def __init__(self, sig_param='s', max_age_param='m'):
        """
        @param sig_param:     Querystring parameter that carries the signature
        @param max_age_param: Querystring parameter that carries the max_age(in
        seconds of the signature)
        """
        self.signer = TimestampSigner()
        self.sig_param = sig_param
        self.max_age_param = max_age_param

    def is_authenticated(self, request, *args, **kwargs):
        """
        Strictly speaking, this is not an authentication check, since we don't
        really check whether the request is from who it claims to be. We check
        whether it's valid and can go through.
        
        Returns True if request signature is valid, else False
        """
        # url, without querystring
        url = request.build_absolute_uri().split('?')[0]
        method = request.method.upper()
        signature = request.GET.get(self.sig_param, '')
        # max_age parameter
        try:
            max_age = int(request.GET.get(self.max_age_param, 0))
        except ValueError:
            max_age = 0

        # Building the string that generated the signature, by constructing the
        # request url without the signature parameter
        query_params = {key: value for key, value in request.GET.items() if key != self.sig_param}
        qs = self._dict_to_ordered_qs(query_params)
        full_url = '%s?%s' % (url, qs)
        string = self._get_string(method, full_url)

        # Check if indeed this string generated the signature we got
        try:
            self.signer.unsign('%s:%s' % (string, signature), max_age=max_age)
        except BadSignature, SignatureExpires:
            return False
        return True        

    def get_signed_url(self, url, method, params, max_age):
        """
        This method should be used by API handlers.

        It signs the request, and returns the url with the signature and
        max_age parameters in the querystring.        
        """
        self._update_params(url, method, params, max_age)
        return '%s?%s' % (url, urllib.urlencode(params))

    def _update_params(self, url, method, params, max_age):
        """
        Updates the ``params`` dictionary, with signature and max_age
        parameters.

        This dictionary is now ready to be url encoded as a querystring and
        appended on the url.
        """
        params[self.max_age_param] = max_age
        params[self.sig_param] = self._get_signature(url, method, params, max_age)
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
        return '&'.join('%s=%s' % (key, value) for key, value in params.items())

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


class TokenAuthentication(Authentication):
    """
    Token included in ``Authentication``, indicates a token which belongs to a
    User. Parameter ``request.user`` is set accordingly.
    """
    pass


