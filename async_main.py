import asyncio
import functools
import requests
import sys
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from requests_futures.sessions import FuturesSession

from bfsbranch import BFSBranch


def makeUrl(title, continueToken=None):
    baseUrl = 'http://en.wikipedia.org/w/api.php?action=query&generator=links&format=json&titles={}&gpllimit=500{}'
    return baseUrl.format(title, '&gplcontinue={}'.format(continueToken) if continueToken else '')

async def main():

    numWorkers = int(sys.argv[1])
    print('{} workers'.format(numWorkers))

    def parseCb(session, resp, title, fromSource=False):
        """
        Parse a response, adding a list of titles, a parent title, and a continue token
        to the response.
        """
        print('parsing {}'.format(title))
        data = resp.json()
        
        # Handle red links
        try:
            # @TODO: this is a hacky way to determine if a page is an actual article.
            # Would be nice if the api told us this info.
            # Can we filter out red links by checking pageid > -1?
            pages = [x['title'] for x in data['query']['pages'].values() if ':' not in x['title']]
        except KeyError:
            pages = []

        continueToken = None
        if data.get('continue') and data.get('continue').get('gplcontinue'):
            continueToken = data.get('continue').get('gplcontinue')
            #print('continuing {} from {}'.format(title, continueToken))
        
        resp.pages = pages
        resp.title = title
        resp.continueToken = continueToken
        resp.fromSource = fromSource
    

    with ThreadPoolExecutor(max_workers=numWorkers) as executor:

        branch = BFSBranch('Segment', 'The game')

        session = FuturesSession(executor=executor)
        loop = asyncio.get_event_loop()

        while True:
            # @TODO: somewhere this is breaking
            intersect = branch.findIntersect()
            if intersect:
                print(intersect)
                print(branch.calculatePath(intersect))
                return
            pages = branch.dequeueAll()
            partials = [functools.partial(session.get,
                                          makeUrl(title, continueToken),
                                          background_callback=functools.partial(parseCb,
                                                                                title=title,
                                                                                fromSource=fromSource))
                        for title, continueToken, fromSource in pages]
            futures = [
                loop.run_in_executor(executor, partial)
                for partial in partials
            ]

            for response in await asyncio.gather(*futures):
                result = response.result()
                branch.addPages(result.pages, result.fromSource, result.title, result.continueToken)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
