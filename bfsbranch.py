from collections import defaultdict

class BFSBranch(object):
    def __init__(self, source, dest=None):
        self._queue = []
        self._cache = [defaultdict(dict), defaultdict(dict)]
        self.addPages([source], fromSource=True)
        if dest:
            self.addPages([dest])
        # No lock is needed since asyncio is single-threaded and only context switches on yield points

    def addToQueue(self, pages):
        self._queue += pages

    # @TODO: this is trash
    def addToCache(self, title, parent=None, fromSource=False):
        if title == parent:
            print('skipping link to self in {}'.format(title))
            return
        if fromSource:
            if not self.existsInPath(title, parent, 0):
                self._cache[0][title] = {'parent': parent, 'visited': False}
        else:
            '''
            if parent and self._cache[1][parent]['parent'] == title:
                print('mutual parents: {} / {}'.format(parent, title))
                return
            '''
            if not self.existsInPath(title, parent, 1):
                self._cache[1][title] = {'parent': parent, 'visited': False}

    def existsInPath(self, title, parent, cacheIndex):
        if parent:
            cur = self._cache[cacheIndex][parent]['parent']
            while cur:
                if cur == title:
                    print('found a loop between {} and {}'.format(title, parent))
                    return True
                cur = self._cache[cacheIndex][cur]['parent']
        return False

    def isVisited(self, title):
        if title in self._cache[0]:
            if self._cache[0][title]['visited']:
                return True
        if title in self._cache[1]:
            if self._cache[1][title]['visited']:
                return True
        return False

    def dequeueAll(self):
        #items = [x for x in self._queue if not self._cache[x[0]].get('visited')]
        #items = [x for x in self._queue if not self._cache[0][x[0]].get('visited') and not self._cache[1][x[0]].get('visited')]
        items = [x for x in self._queue if not self.isVisited(x)]
        self._queue = []
        return items

    def addPages(self, pages, fromSource=False, parent=None, parentContinue=None):
        """
        Add new page data to the cache and queue.

        :param pages: the pages and continue tokens to be added
        :type pages: [title1, title2, ...]
        :param fromSource: whether this is from the source or not (backwards from dest)
        :type fromSource: bool
        :param parent: the parent page
        :type parent: str
        :param parentContinue: the continue token for the parent, if it exists
        :type parentContinue: str
        """
        for title in pages:
            self.addToCache(title, parent, fromSource)
        # Format the pages to fit the queue
        queuePages = [(x, None, fromSource) for x in pages]
        # Mark the parent as visited
        if parent:
            index = 0 if fromSource else 1
            self._cache[index][parent]['visited'] = True
            # Add the parent back to the queue if there is a continue token
            if parentContinue:
                queuePages.append((parent, parentContinue, fromSource))
        self.addToQueue(queuePages)

    def findIntersect(self):
        # @TODO: make these a property
        sourceSet = set(self._cache[0].keys())
        targetSet = set(self._cache[1].keys())
        intersect = sourceSet & targetSet
        if len(intersect) > 0:
            print('ayyyy')
            print(intersect)
            return intersect.pop()
        else:
            return None

    def calculatePath(self, intersect):
        left = []
        right = []

        # @TODO: why is the right a lot longer than the left?
        print('left: {}, right: {}'.format(len(self._cache[0]), len(self._cache[1])))
        leftParent = self._cache[0][intersect]['parent']
        while leftParent:
            left.append(leftParent)
            leftParent = self._cache[0][leftParent]['parent']
        # reverse order for left side since we're tracing backwards
        left.reverse()

        rightParent = self._cache[1][intersect]['parent']
        while rightParent:
            right.append(rightParent)
            rightParent = self._cache[1][rightParent]['parent']

        return left + [intersect] + right


    def tmpIsFound(self, target):
        return target in self._cache

'''
b = BFSBranch('United States of America')
b.addToCache('The game')
b.addToCache('Jesus', 'Edom', True)
print(b.peek('The game'))
print(b.peek('Jesus'))
print(b.peek('Segment'))
'''
