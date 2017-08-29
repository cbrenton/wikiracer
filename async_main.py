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

    def parseCb(session, resp, title):
        """
        Parse a response, adding a list of titles, a parent title, and a continue token
        to the response.
        """
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
        
        resp.pages = pages
        resp.title = title
        resp.continueToken = continueToken

    with ThreadPoolExecutor(max_workers=numWorkers) as executor:

        sourceBranch = BFSBranch('Segment')
        destBranch = BFSBranch('The game')
        branches = [sourceBranch, destBranch]
        branchIndex = 0

        session = FuturesSession(executor=executor)
        loop = asyncio.get_event_loop()

        while True:
            intersect = sourceBranch.findIntersect(destBranch)
            if intersect:
                print(intersect)
                # Calculate path
                sourcePath = sourceBranch.calculatePath(intersect)
                sourcePath.reverse()
                destPath = destBranch.calculatePath(intersect)
                fullPath = sourcePath + [intersect] + destPath
                print(fullPath)
                return
            # Get a page from current branch for each available worker, alternating between
            # source and dest
            pages = branches[branchIndex].dequeueN(numWorkers)
            print('getting {} pages from branch {}'.format(len(pages), branchIndex))
            partials = [functools.partial(session.get,
                                          makeUrl(title, continueToken),
                                          background_callback=functools.partial(parseCb,
                                                                                title=title))
                        for title, continueToken in pages]
            futures = [
                loop.run_in_executor(executor, partial)
                for partial in partials
            ]

            for response in await asyncio.gather(*futures):
                result = response.result()
                branches[branchIndex].addPages(result.pages, result.title, result.continueToken)

            branchIndex = (branchIndex + 1) % len(branches)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
