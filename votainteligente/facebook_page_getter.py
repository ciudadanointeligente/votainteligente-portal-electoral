# encoding = utf-8
import facebook
from django.conf import settings
try:
    import urlparse
    from urllib import urlencode
except: # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode


def facebook_getter(url):

    graph = facebook.GraphAPI(access_token=settings.FACEBOOK_ACCESS_TOKEN, version='2.5')
    params = {
        'fields': 'about,picture,events'
    }
    url_parts = list(urlparse.urlparse(url))
    query = dict()
    query.update(params)
    url_parts[4] = urlencode(query)
    url = urlparse.urlunparse(url_parts)
    _object = graph.get_object(url)
    _id = _object.get('id')
    return {
        'about': unicode(_object['about']),
        'id': _id,
        'picture_url': _object['picture']['data']['url'],
        'events': _object['events']
    }

