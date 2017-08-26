#!/usr/bin/env python
from pprint import pprint
from batchmanager import BatchManager

def bfsPage(page, target):
    # @TODO: make this pretty
    s_visited = set()
    t_visited = set()
    s_bm = BatchManager()
    s_bm.addPages([page])
    t_bm = BatchManager()
    t_bm.addPages([target])
    while s_bm.hasNext() or t_bm.hasNext():
        # check for intersect
        if intersectExists(s_visited, t_visited):
            print('target found')
            return target
        '''
        if bm.hasTarget(target):
            print('target found')
            return target
        '''
        s_results = s_bm.next()
        s_bm.addPages([n for n in s_results if n not in s_visited])
        s_visited.update(s_results)
        t_results = t_bm.next()
        t_bm.addPages([n for n in t_results if n not in t_visited])
        t_visited.update(t_results)
        print(len(s_visited))
        print(len(t_visited))
    print('not found')
    return None

def intersectExists(set1, set2):
    intersect = set1.intersection(set2)
    if len(intersect) > 0:
        print('ayyyy')
        print(intersect)
    return len(set1.intersection(set2)) > 0

bfsPage('Segment', 'The game')
