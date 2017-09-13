from unittest import TestCase
from unittest.mock import MagicMock, patch
import requests

import wikiracer


class FunctionalTest(TestCase):
    def find_links_from(self, title):
        """
        :param title: the source page title
        :returns: a list of titles the page links to
        """
        baseUrl = 'http://en.wikipedia.org/w/api.php?action=query&generator=links&format=json&titles={}&gpllimit=500{}'
        apiUrl = baseUrl.format(title, '')

        resp = requests.get(apiUrl)
        pages, continueToken = self.parse_pages_from_resp(resp)
        # While continue token exists, add to pages
        while continueToken:
            apiUrl = baseUrl.format(title, '&gplcontinue={}'.format(continueToken) if continueToken else '')
            resp = requests.get(apiUrl)
            newPages, continueToken = self.parse_pages_from_resp(resp)
            pages += newPages
        return pages

    def assert_path_is_valid(self, path):
        """
        :param path: a list of page titles
        """
        # Cur src is first el in path
        src = path.pop(0)
        # While path has additional elements:
        for el in path:
            # Verify path from src to path head
            assert el in self.find_links_from(src)
            src = el

    def parse_pages_from_resp(self, resp):
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
        
        return pages, continueToken

    def test_foo(self):
        path = wikiracer.create_loop('Brazil', 'Asia', 5)
        self.assert_path_is_valid(path)
