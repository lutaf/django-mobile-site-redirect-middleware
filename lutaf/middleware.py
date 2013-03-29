#encoding:utf-8
import operator
import logging
import re
from django.conf import settings
from django.utils.cache import patch_vary_headers
import urlparse
from django.http import HttpResponseRedirect


logger = logging.getLogger(__name__)
lower = operator.methodcaller('lower')

UNSET = object()

def get_domain():
    if getattr(settings, 'SITE_INFO', False):
        return settings.SITE_INFO['domain']
    else:
        return ''



class SubdomainMiddleware(object):
    """
    A middleware class that adds a ``subdomain`` attribute to the current request.
    """
    def get_domain_for_request(self, request):
        """
        Returns the domain that will be used to identify the subdomain part
        for this request.
        """
        return get_domain()

    def process_request(self, request):
        """
        Adds a ``subdomain`` attribute to the ``request`` parameter.
        """
        domain, host = map(lower,
            (self.get_domain_for_request(request), request.get_host()))

        pattern = r'^(?:(?P<subdomain>.*?)\.)?%s(?::.*)?$' % re.escape(domain)
        matches = re.match(pattern, host)

        if matches:
            request.subdomain = matches.group('subdomain')
        else:
            request.subdomain = None
            logger.warning('The host %s does not belong to the domain %s, '
                'unable to identify the subdomain for this request',
                request.get_host(), domain)


class SubdomainURLRoutingMiddleware(SubdomainMiddleware):
    """
    A middleware class that allows for subdomain-based URL routing.
    """
    def process_request(self, request):
        """
        Sets the current request's ``urlconf`` attribute to the urlconf
        associated with the subdomain, if it is listed in
        ``settings.SUBDOMAIN_URLCONFS``.
        """
        super(SubdomainURLRoutingMiddleware, self).process_request(request)

        subdomain = getattr(request, 'subdomain', UNSET)

        if subdomain is not UNSET:
            urlconf = settings.SUBDOMAIN_URLCONFS.get(subdomain)
            if urlconf is not None:
                logger.debug("Using urlconf %s for subdomain: %s",
                    repr(urlconf), repr(subdomain))
                request.urlconf = urlconf

    def process_response(self, request, response):
        """
        Forces the HTTP ``Vary`` header onto requests to avoid having responses
        cached across subdomains.
        """
        if getattr(settings, 'FORCE_VARY_ON_HOST', True):
            patch_vary_headers(response, ('Host',))

        return response




class BrowscapParser(object):
    DEFAULT_UA_STRINGS = (
        'Android',
        'BlackBerry',
        'IEMobile',
        'Maemo',
        'Opera Mini',
        'SymbianOS',
        'WebOS',
        'Windows Phone',
        'iPhone',
        'iPod',
    )
    def __init__(self):
        self._cache = {}

    def detect_mobile(self, user_agent):
        try:
            return self._cache[user_agent]
        except KeyError:
            for lookup in BrowscapParser.DEFAULT_UA_STRINGS:
                if lookup in user_agent:
                    self._cache[user_agent] = True
                    break
            else:
                self._cache[user_agent] = False
        return self._cache[user_agent]

browser = BrowscapParser()

class MobileRedirectMiddleware(object):
    def process_request(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        is_mobile = browser.detect_mobile(user_agent)
        
        #跳转规则：
        # 如果是mobile，而host是主站，那么跳转到m站
        
        request.is_mobile = is_mobile
        request_host = request.META.get('HTTP_HOST','')
        if is_mobile and request_host != settings.SITE_INFO['mobile_host']:
            jump_url = "http://%s" % settings.SITE_INFO['mobile_host']
            return HttpResponseRedirect(jump_url)
