import requests

class BatchManager(object):
    def __init__(self):
        self._queue = []
        self._curTitles = ''
        self._continue = ''
        self._limit = 500

    def hasTarget(self, target):
        return target in self._queue

    def hasNext(self):
        return self._queue or self._continue

    def next(self):
        if self.hasNext():
            if not self._continue:
                # @TODO: later on, this pulls out 50 titles that may still be in the visited cache. deal with this
                numTitles = min(50, len(self._queue))
                # generate curTitles
                print('new curTitles')
                self._curTitles, self._queue = '|'.join(self._queue[:numTitles]), self._queue[numTitles:]
            return self.getPage()
            # get next page for cur titles

    def getPage(self):
        # get page with
        url = 'http://en.wikipedia.org/w/api.php?action=query&generator=links&format=json&titles={}&gpllimit={}{}'.format(self._curTitles,
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
        pages = [x['title'] for x in data['query']['pages'].values()]
        return pages

    def addPages(self, pages):
        self._queue += pages
