from app import zotero, cache
import feedparser

class ZoteroApi:
    """ Implements some of the read API for Zotero

    Atoms feeds are cached to the caching implementation: dict, redis, memcache
    """

    def __init__(self, app):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.zotero_api = self

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

    def query(self, req, timeout=None):
        hit = cache.get(req)
        if hit is None:
            resp = zotero.get(req)
            if resp.status == 200:
                hit = feedparser.parse(resp.data)
                cache.set(req, hit, timeout)
        return hit

    def search(self, search_expression):
        return self.query("{0}&q={1}&qmode=titleCreatorYear".format(self.get_base_url(), search_expression), timeout=60)

    def last_modified(self, n=50):
        return self.query("{0}&order=dateModified&limit={1}".format(self.get_base_url(), n), timeout=60)

    def last_added(self, n=50):
        return self.query("{0}&order=dateAdded&limit={1}".format(self.get_base_url(), n), timeout=60)

    def last_accessed(self, n=50):
        return self.query("{0}&order=accessDate&limit={1}".format(self.get_base_url(), n), timeout=60)

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
