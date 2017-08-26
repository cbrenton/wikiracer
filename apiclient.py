import mwclient
import mwapi
import requests

class APIClient(object):
    site = mwclient.Site('en.wikipedia.org')
    startPage = Page('Segment', site)

class Page(object):
    def __init__(self, title, site):
        self._title = title
        self._site = site
        self._data = site.Pages[self._title]

    @property
    def name(self):
        return self._title

class Site(object):
    def __init__(self, baseurl=''):
        self._baseurl = baseurl

    def getLinks(self, title):
        endpoint = 'w/api.php?action=query&generator=links&format=json&titles=Fruit%20anatomy&gpllimit=500&redirects'
        endpoint = 'w/api.php?action=query&prop=links&format=json&titles=G}&pllimit=5000'
