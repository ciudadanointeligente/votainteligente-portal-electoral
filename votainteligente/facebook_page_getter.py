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
        'fields': 'about,picture,events,name'
    }
    url_parts = list(urlparse.urlparse(url))
    query = dict()
    query.update(params)
    url_parts[4] = urlencode(query)
    url = urlparse.urlunparse(url_parts)
    _object = graph.get_object(url)
    _id = _object.get('id')
    _about = unicode(_object.get('about', ''))
    _events = _object.get('events', [])
    _picture_url = _object.get('picture', []).get('data', []).get('url','' )
    _name = _object.get('name', 'Facebook Page')
    return {
        'about': _about,
        'id': _id,
        'picture_url': _object['picture']['data']['url'],
        'events': _events,
        'name': _name,
    }

