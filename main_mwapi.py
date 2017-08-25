#!/usr/bin/env python
from pprint import pprint
from batchmanager import BatchManager

def bfsPage(page, target):
    visited = set()
    bm = BatchManager()
    bm.addPages([page])
    while bm.hasNext():
        if bm.hasTarget(target):
            print('target found')
            return target
        #results = bm.next(visited)
        results = bm.next()
        #print(results)
        # @TODO (somewhere) - store path from source to node for each visited node
        #print([n for n in results if n in visited])
        bm.addPages([n for n in results if n not in visited])
        visited.update(results)
        print(len(visited))
    return None

bfsPage('Segment', 'Jesus')
