from collections import defaultdict


class BFSBranch(object):
    def __init__(self, source):
        self._queue = []
        self._cache = defaultdict(dict)
        self.addPages([source])

    def addToQueue(self, pages):
        self._queue += pages

    # @TODO: this is trash
    def addToCache(self, title, parent=None):
        if title == parent:
            #print('skipping link to self in {}'.format(title))
            return
        # Detect loops
        if not self.existsInPath(title, parent):
            self._cache[title] = {'parent': parent, 'visited': False}

    def existsInPath(self, title, parent):
        if parent:
            cur = self._cache[parent]['parent']
            while cur:
                if cur == title:
                    #print('found a loop between {} and {}'.format(title, parent))
                    return True
                cur = self._cache[cur]['parent']
        return False

    def isVisited(self, title):
        """
        This exists because we're using a defaultdict.
        @TODO: flesh out this docstring.
        """
        if title in self._cache:
            if self._cache[title]['visited']:
                return True
        return False

    def dequeueN(self, n):
        items = [x for x in self._queue[:n] if not self.isVisited(x)]
        self._queue = self._queue[n:]
        return items

    def dequeueAll(self):
        items = [x for x in self._queue if not self.isVisited(x)]
        self._queue = []
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
        for title in pages:
            self.addToCache(title, parent)
        # Format the pages to fit the queue
        queuePages = [(x, None) for x in pages]
        # Mark the parent as visited
        if parent:
            self._cache[parent]['visited'] = True
            # Add the parent back to the queue if there is a continue token
            if parentContinue:
                queuePages.append((parent, parentContinue))
        self.addToQueue(queuePages)

    def findIntersect(self, other):
        # @TODO: make these a property
        sourceSet = set(self._cache.keys())
        targetSet = set(other._cache.keys())
        intersect = sourceSet & targetSet
        if len(intersect) > 0:
            print('ayyyy')
            print(intersect)
            return intersect.pop()
        else:
            return None

    def calculatePath(self, intersect):
        path = []

        parent = self._cache[intersect]['parent']
        while parent:
            path.append(parent)
            parent = self._cache[parent]['parent']

        return path
