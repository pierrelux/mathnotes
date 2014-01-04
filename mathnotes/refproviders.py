from mathnotes.views.auth import zotero
from flask.ext.login import current_user
from flask.ext.cache import Cache
from flask import current_app
import feedparser, json, urllib

class ZoteroApi:
    """ Implements some of the read API for Zotero

    Atoms feeds are cached to the caching implementation: dict, redis, memcache
    """

    def userid_getter(self, f):
        self._userid_getter = f
        return f

    def get_userid(self):
        assert self._userid_getter is not None, 'missing userid_getter'
        return self._userid_getter()

    def key_getter(self, f):
        self._key_getter = f
        return f

    def get_key(self):
        assert self._key_getter is not None, 'missing key_getter'
        return self._key_getter()

    def get_base_url(self):
        return "users/{0}/items?format=atom&content=json&key={1}".format(self.get_userid(), self.get_key())

    def hash_request(self, data):
        """ Return a hash for the data part of a url

        Used for caching. The following implementation does not
        support recursive dict. Good enough for now.
        """
        return hash(tuple(sorted(data.items())))

    def query(self, req, data, timeout=1800):
        cache_key = self.hash_request(data)
        hit = cache.get(cache_key)
        if hit is None:
            current_app.logger.debug('Cache miss')
            resp = zotero.request(req, data)
            if resp.status == 200:
                hit = resp.data
                cache.set(cache_key, hit, timeout)
        return hit

    def parse_response(self, content):
        d = feedparser.parse(content)

        response = []
        for entry in d.entries:
          content = json.loads(entry['content'][0]['value'])
          response.append({ 'title':content['title'],
            'date': content['date'],
            'authors': [u' '.join((author['firstName'], author['lastName'])) for author in content['creators']],
            'provider':'zotero',
            'source':entry['zapi_key'] })

        # Flask doesn't allow for array response
        return {'items':response}

    def search(self, search_expression):
        return self.parse_response(self.query(self.get_base_url(), {'q':search_expression, 'qmode':'titleCreatorYear'}))

    def last_modified(self, n=50):
        return self.parse_response(self.query(self.get_base_url(), {'order':'dateModified', 'limit':n}))

    def last_added(self, n=50):
        return self.parse_response(self.query(self.get_base_url(), {'order':'dateAdded', 'limit':n}))

    def last_accessed(self, n=50):
        return self.parse_response(self.query(self.get_base_url(), {'order':'accessDate', 'limit':n}))

    def hints(self, n=50):
        return self.last_modified(n)

# Hack from pyzotero
def ib64_patched(self, attrsD, contentparams):
    """ Patch isBase64 to prevent Base64 encoding of JSON content
    """
    if attrsD.get('mode', '') == 'base64':
        return 0
    if self.contentparams['type'].startswith('text/'):
        return 0
    if self.contentparams['type'].endswith('+xml'):
        return 0
    if self.contentparams['type'].endswith('/xml'):
        return 0
    if self.contentparams['type'].endswith('/json'):
        return 0
    return 0

feedparser._FeedParserMixin._isBase64 = ib64_patched
cache = Cache()
zoteroapi = ZoteroApi()

@zoteroapi.userid_getter
def get_userid():
    return current_user.authorizations.first().userID

@zoteroapi.key_getter
def get_key():
    return current_user.authorizations.first().oauth_secret

