#!/usr/bin/env python
import mwclient
from pprint import pprint

site = mwclient.Site('en.wikipedia.org')
startPage = site.Pages['Segment']
print(startPage)

visited = {}

def parsePage(page, stack):
    # Store visited links
    if page.name in visited:
        pass
    # Get all links
    allLinks = list(page.links())
    # Basic bfs

def bfsPage(page, target):
    visited = set()
    queue = [page]
    strResults = ''
    while queue:
        cur = queue.pop(0)
        print('checking {}'.format(cur.name))
        strResults += cur.name.replace(' ','%20') + '|'
        print(strResults)
        if cur.name == target.name:
            return cur
        for n in list(cur.links()):
            if n not in visited:
                visited.add(n)
                queue.append(n)
    return None

bfsPage(startPage, site.Pages['Jesus'])
