from collections import defaultdict


class BFSBranch(object):
    def __init__(self):
        """
        There are two main data structures used to track a branch of a bidirectional BFS.

        Queue: this contains pages to be checked in the next iteration. Follows the following
        format:
            [(title, continueToken), ...]
        If the page to be checked still has links that have not yet been returned by the API,
        there will be a continue token in the response. We use that to get the next set of
        links.

        Cache: this tells us which pages have already been visited, as well as the parent/child
        relationships we need to calculate the path from the start point to the point of
        intersection. Follows the following format:
            {
                'Page 1': {
                    'parent': None,
                    'visited': True
                },
                'Page 2': {
                    'parent': 'Page 1',
                    'visited': False
                },
                ...
            }
        """
        self._queue = []
        self._cache = defaultdict(dict)

    def addToCache(self, title, parent=None):
        """
        Add a page to the cache. Since this is called when a link is first encountered (NOT when
        the page is visited), it will be entered as unvisited. When the page is actually visited,
        the visited field will be set to True.

        :param title: the title of the page
        :type title: str
        :param parent: the page's parent
        :type parent: str|None
        """
        # Sometimes pages link to themselves. I don't know why but we shouldn't allow that.
        if title == parent:
            return
        # Add title to cache if it isn't already present
        if title not in self._cache: 
            self._cache[title] = {'parent': parent, 'visited': False}

    def isVisited(self, title):
        """
        Check if the given page has been visited yet.

        :param title: the page to check
        :type title: str
        :returns: True if the page exists in the cache and has been visited, otherwise False
        :rtype: bool
        """
        if title in self._cache:
            if self._cache[title]['visited']:
                return True
        return False

    def dequeueN(self, n):
        """
        Remove and return the next n items from the queue, filtering out already visited pages.

        :param n: the number of items to return
        :type n: int
        :returns: a list of n queue items
        :rtype: [(str, str|None)]
        """
        items = [x for x in self._queue[:n] if not self.isVisited(x[0])]
        self._queue = self._queue[n:]
        return items

    def addPages(self, pages, parent=None, parentContinue=None):
        """
        Add new page data to the cache and queue.

        :param pages: the pages and continue tokens to be added
        :type pages: [title1, title2, ...]
        :param parent: the parent page
        :type parent: str
        :param parentContinue: the continue token for the parent, if it exists
        :type parentContinue: str
        """
        # Add all pages to cache
        for title in pages:
            self.addToCache(title, parent)
        # Format the list of page titles to fit the queue format (add a null continue token)
        queuePages = [(x, None) for x in pages]
        # Mark the parent as visited
        if parent:
            self._cache[parent]['visited'] = True
            # Add the parent back to the queue if there is a continue token
            if parentContinue:
                queuePages.append((parent, parentContinue))
        # Append all pages (plus the parent if there is a continue token) to the queue
        self._queue += queuePages

    def findIntersect(self, other):
        """
        Determine if two BFSBranches have an intersection.

        :param other: the other BFSBranch to be checked
        :type other: BFSBranch
        :returns: a single intersecting page if any exist, otherwise None
        :rtype: str|None
        """
        # @TODO: make these a property
        sourceSet = set(self._cache.keys())
        targetSet = set(other._cache.keys())
        intersect = sourceSet & targetSet
        if len(intersect) > 0:
            return intersect.pop()
        else:
            return None

    def calculatePath(self, intersect):
        """
        Calculate a path from a page to this branch's source. Technically this returns the path
        from the given page's parent to the source, because we will combine this with the path from
        the opposing BFSBranch, so we don't want to duplicate the intersecting page.

        :param intersect: the starting point of the path
        :type intersect: str
        :returns: the path from the given page to the source, excluding the page
        :rtype: [str]
        """
        path = []

        parent = self._cache[intersect]['parent']
        while parent:
            path.append(parent)
            parent = self._cache[parent]['parent']

        return path
