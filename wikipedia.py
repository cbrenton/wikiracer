import functools


class Wikipedia(object):
    def __init__(self, session):
        self._session = session

    def getLinksFrom(self, title, continueToken=None):
        baseUrl = 'http://en.wikipedia.org/w/api.php?action=query&generator=links&format=json&titles={}&gpllimit=500{}'
        apiUrl = baseUrl.format(title, '&gplcontinue={}'.format(continueToken) if continueToken else '')
        future = self._session.get(apiUrl, background_callback=functools.partial(self.parseCb,
                                                                                 title=title))
        return future

    def getLinksTo(self, title, continueToken=None):
        baseUrl = 'http://en.wikipedia.org/w/api.php?action=query&generator=backlinks&format=json&gbltitle={}&gbllimit=500{}'
        apiUrl = baseUrl.format(title, '&gplcontinue={}'.format(continueToken) if continueToken else '')
        future = self._session.get(apiUrl, background_callback=functools.partial(self.parseCb,
                                                                                 title=title))
        return future

    def parseCb(self, _, resp, title):
        """
        Parse a response, adding a list of titles, a parent title, and a continue token to the response.
        This is a callback for requests_futures.session.get(), so it doesn't return anything, but
        rather modifies the response object for use later on.

        :param resp: the response
        :type resp: requests.models.Response
        :param title: the title of the page from the initial request, to be used as the parent
        :type title: str
        """
        data = resp.json()
        
        # Handle red links, which will return an empty query field, rather than a query field with an
        # empty pages field.
        try:
            # This is a hacky way to determine if a page is an actual article.
            # It would be nice if the api told us this info.
            pages = [x['title'] for x in data['query']['pages'].values() if ':' not in x['title']]
        except KeyError:
            pages = []

        continueToken = None
        # Check for a continue token
        if data.get('continue') and data.get('continue').get('gplcontinue'):
            continueToken = data.get('continue').get('gplcontinue')
        
        resp.pages = pages
        resp.title = title
        resp.continueToken = continueToken
