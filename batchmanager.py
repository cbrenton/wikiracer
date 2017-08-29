import requests

class BatchManager(object):
    def __init__(self):
        self._queue = []
        self._continue = ''
        self._limit = 500
        self._visited = {}

    def hasTarget(self, target):
        return target in self._queue

    def hasNext(self):
        return self._queue or self._continue

    def next(self):
        if self.hasNext():
            if not self._continue:
                numTitles = 1
                # @TODO: fix circular link problem
                self._curTitle = self._queue.pop(0)
                '''
                while self._curTitle in visited:
                    print('skipping {}'.format(self._curTitle))
                    self._curTitle = self._queue.pop(0)
                '''
                #self._curTitles, self._queue = '|'.join(self._queue[:numTitles]), self._queue[numTitles:]
                #self._curTitles = self._queue[0]
                #self._queue = self._queue[1:]
            return self.getPage()
            # get next page for cur titles

    def getPage(self):
        # get page with
        url = 'http://en.wikipedia.org/w/api.php?action=query&generator=links&format=json&titles={}&gpllimit={}{}'.format(self._curTitle,
                                                                                                                          self._limit,
                                                                                                                          '&gplcontinue={}'.format(self._continue) if self._continue else '')
        resp = requests.get(url)

        data = resp.json()
        if data.get('continue') and data.get('continue').get('gplcontinue'):
            self._continue = data.get('continue').get('gplcontinue')
            print('continuing from {}'.format(self._continue))
        else:
            self._continue = ''
            print('new batch')
        # @TODO: add handling for when this might fail
        # Handle red links
        try:
            pages = {x['title']:self._curTitle for x in data['query']['pages'].values() if self.isValid(x['title'])}
        except KeyError:
            pages = {}
        return pages

    def isValid(self, title):
        '''
        prefixes = [
            'Wikipedia:',
            'Help:',
            'Template:',
            'Category:'
        ]
        for prefix in prefixes:
            if title.startswith(prefix):
                return False
        return True
        '''
        return ':' not in title

    def addPages(self, pages):
        self._queue += pages
