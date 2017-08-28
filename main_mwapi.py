#!/usr/bin/env python
from pprint import pprint
from batchmanager import BatchManager

def bfsPage(page, target):
    # @TODO: make this pretty
    s_visited = {page: None}
    t_visited = {target: None}
    s_bm = BatchManager()
    s_bm.addPages([page])
    t_bm = BatchManager()
    t_bm.addPages([target])
    while s_bm.hasNext() or t_bm.hasNext():
        # check for intersect
        intersect = findIntersect(s_visited, t_visited)
        if intersect:
            return findPath(s_visited, t_visited, intersect)
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

def findPath(sourceVisited, targetVisited, intersect):
    left = []
    right = []

    leftParent = sourceVisited[intersect]
    while leftParent:
        left.append(leftParent)
        leftParent = sourceVisited[leftParent]
    # @TODO: reverse order for left side since we're tracing backwards
    left.reverse()

    rightParent = targetVisited[intersect]
    while rightParent:
        right.append(rightParent)
        rightParent = targetVisited[rightParent]

    return left + [intersect] + right

def findIntersect(sourceVisited, targetVisited):
    sourceSet = set(sourceVisited.keys())
    targetSet = set(targetVisited.keys())
    intersect = sourceSet & targetSet
    if len(intersect) > 0:
        print('ayyyy')
        print(intersect)
        return intersect.pop()
    else:
        return None

print(bfsPage('Segment', 'The game'))
