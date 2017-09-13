#!/usr/bin/env python

import asyncio
import click
import functools
import sys
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
import requests

from bfsbranch import BFSBranch
from wikipedia import Wikipedia


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
        sourceBranch = BFSBranch()
        sourceBranch.addPages([src])
        destBranch = BFSBranch()
        destBranch.addPages([dest])
        # We will alternate between requesting pages from the source and destination branches.
        branches = [sourceBranch, destBranch]
        branchIndex = 0

        session = FuturesSession(executor=executor)
        wikipedia = Wikipedia(session)
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
                return fullPath
            # Get a page from current branch for each available worker, alternating between
            # source and dest
            pages = branches[branchIndex].dequeueN(numWorkers)
            # Create partial functions for each session.get
            partials = [functools.partial(wikipedia.getLinksFrom,
                                          title,
                                          continueToken) if branchIndex == 0
                        else functools.partial(wikipedia.getLinksTo,
                                               title,
                                               continueToken)
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

def create_loop(src, dest, workers):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(createLoop(src, dest, workers))

@click.command()
@click.argument('src')
@click.argument('dest')
@click.option('--workers', type=int, default=5, help='Number of concurrent requests. ' + 
              'Counterintuitively, lower numbers tend to work better.')
def main(src, dest, workers):
    create_loop(src, dest, workers)

if __name__ == '__main__':
    main()
