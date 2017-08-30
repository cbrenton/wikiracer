#!/usr/bin/env python

import asyncio
import click
import functools
import sys
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession

from bfsbranch import BFSBranch


def makeUrl(title, continueToken=None, isSource=True):
    """
    Generate a url for the API request for a given page. If this is originating from the source
    branch, it will check links. If it's originating from the destination, it will check backlinks.

    :param title: the page title
    :type title: str
    :param continueToken: the continue token for the page, if any
    :type continueToken: str|None
    :returns: a url for the API request
    :rtype: str
    """
    if isSource:
        baseUrl = 'http://en.wikipedia.org/w/api.php?action=query&generator=links&format=json&titles={}&gpllimit=500{}'
    else:
        baseUrl = 'http://en.wikipedia.org/w/api.php?action=query&generator=backlinks&format=json&gbltitle={}&gbllimit=500{}'
    return baseUrl.format(title, '&gplcontinue={}'.format(continueToken) if continueToken else '')


def parseCb(_, resp, title):
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


async def createLoop(src, dest, numWorkers):
    """
    Create a thread pool and a BFSBranch for each end of the search, then search for linked pages
    from both ends until an intersection is found. Requests are sent using requests_futures, so
    they are non-blocking.

    :param src: the source page
    :type src: str
    :param dest: the destination page
    :type dest: str
    :param numWorkers: the number of worker threads to use when making requests
    :type numWorkers: int
    """
    print('Searching from \"{}\" to \"{}\" using {} workers'.format(src, dest, numWorkers))

    # Create the thread pool for the event loop.
    with ThreadPoolExecutor(max_workers=numWorkers) as executor:
        # Create branches for both sides of the search.
        sourceBranch = BFSBranch(src)
        destBranch = BFSBranch(dest)
        # We will alternate between requesting pages from the source and destination branches.
        branches = [sourceBranch, destBranch]
        branchIndex = 0

        session = FuturesSession(executor=executor)
        loop = asyncio.get_event_loop()

        # Iterate until the loop is broken, since checking for empty queues isn't a reliable way of
        # seeing if we're done - the queues may be temporarily empty while waiting for a batch of
        # requests to complete.
        while True:
            # Check for intersection between the two branches
            intersect = sourceBranch.findIntersect(destBranch)
            if intersect:
                # Calculate path from source to intersection to dest
                sourcePath = sourceBranch.calculatePath(intersect)
                # Reverse the source path since we're traveling from source to intersection
                sourcePath.reverse()
                destPath = destBranch.calculatePath(intersect)
                fullPath = sourcePath + [intersect] + destPath
                print(fullPath)
                return
            # Get a page from current branch for each available worker, alternating between
            # source and dest
            pages = branches[branchIndex].dequeueN(numWorkers)
            # Create partial functions for each session.get
            partials = [functools.partial(session.get,
                                          makeUrl(title, continueToken, branchIndex == 1),
                                          background_callback=functools.partial(parseCb,
                                                                                title=title))
                        for title, continueToken in pages]
            # Create futures and add to event loop
            futures = [
                loop.run_in_executor(executor, partial)
                for partial in partials
            ]

            # Gather future results and add new and continued pages to the correct branch's queue
            for response in await asyncio.gather(*futures):
                result = response.result()
                branches[branchIndex].addPages(result.pages, result.title, result.continueToken)

            # Increment the branch index
            branchIndex = (branchIndex + 1) % len(branches)

@click.command()
@click.argument('src')
@click.argument('dest')
@click.option('--workers', type=int, default=5, help='Number of concurrent requests. ' + 
              'Counterintuitively, lower numbers tend to work better.')
def main(src, dest, workers):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(createLoop(src, dest, workers))

if __name__ == '__main__':
    main()
