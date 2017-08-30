from unittest import TestCase
from unittest.mock import MagicMock, patch

from bfsbranch import BFSBranch


class TestBFSBranch(TestCase):
    def setUp(self):
        self.branch = BFSBranch()

    def assertInQueue(self, item):
        assert item in self.branch._queue
        
    def assertNotInQueue(self, item):
        assert item not in self.branch._queue

    def assertInCache(self, title, isVisited=None, parent=''):
        assert title in self.branch._cache
        if isVisited is not None:
            assert self.branch._cache[title]['visited'] == isVisited
        if parent != '':
            assert self.branch._cache[title]['parent'] == parent

    def assertNotInCache(self, title, parent=''):
        if parent != '':
            if title in self.branch._cache:
                assert self.branch._cache[title]['parent'] != parent
        else:
            assert title not in self.branch._cache

    def test_addToCache_adds_new_page_with_valid_parent(self):
        self.branch.addPages(['foo'])
        self.branch.addToCache('bar', 'foo')
        self.assertInCache('bar', parent='foo')

    def test_addToCache_does_not_add_page_with_same_parent(self):
        self.branch.addToCache('foo', 'foo')
        self.assertNotInCache('foo')

    def test_addToCache_does_not_modify_page_already_in_cache(self):
        self.branch.addPages(['foo'])
        self.branch.addPages(['bar'], 'foo')
        self.assertInCache('bar', parent='foo')
        self.branch.addPages(['bar'], 'baz')
        self.assertInCache('bar', parent='foo')
        self.assertNotInCache('bar', parent='baz')

    def test_isVisited_returns_false_if_page_is_not_in_cache(self):
        assert not self.branch.isVisited('foo')

    def test_isVisited_returns_false_if_page_is_in_cache_but_unvisited(self):
        self.branch.addPages(['foo'])
        assert not self.branch.isVisited('foo')

    def test_isVisited_returns_true_if_page_is_in_cache_and_visited(self):
        self.branch.addPages(['foo'])
        self.branch.addPages(['bar'], 'foo')
        assert self.branch.isVisited('foo')

    def test_dequeueN_removes_and_returns_n_items_from_queue_of_greater_than_n_length(self):
        self.branch.addPages(['foo', 'bar', 'baz'], 'poo')
        assert len(self.branch._queue) == 3
        self.assertInQueue(('foo', None))
        self.assertInQueue(('bar', None))
        self.assertInQueue(('baz', None))
        items = self.branch.dequeueN(2)
        assert items == [('foo', None), ('bar', None)]
        assert len(self.branch._queue) == 1
        self.assertNotInQueue(('foo', None))
        self.assertNotInQueue(('bar', None))
        self.assertInQueue(('baz', None))

    def test_dequeueN_skips_visited_items(self):
        self.branch.addPages(['foo'])
        self.branch.addPages(['bar', 'baz'], 'foo')
        assert self.branch.dequeueN(2) == [('bar', None)]

    def test_dequeueN_does_not_break_when_n_is_larger_than_queue_length(self):
        self.branch.addPages(['foo'])
        # Should raise no exception
        assert self.branch.dequeueN(20) == [('foo', None)]

    def test_addPages_adds_initial_source_to_queue(self):
        self.branch.addPages(['foo'])
        self.assertInQueue(('foo', None))

    def test_addPages_adds_initial_source_to_cache_as_unvisited(self):
        self.branch.addPages(['foo'])
        self.assertInCache('foo', False, None)

    def test_addPages_adds_subsequent_source_to_cache_and_marks_parent_visited(self):
        self.branch.addPages(['foo'])
        self.branch.addPages(['bar', 'baz'], 'foo')
        self.assertInCache('bar', False, 'foo')
        self.assertInCache('baz', False, 'foo')
        self.assertInCache('foo', True, None)

    def test_addPages_adds_subsequent_sources_to_queue(self):
        self.branch.addPages(['foo'])
        self.assertInQueue(('foo', None))
        self.branch.addPages(['bar', 'baz'], 'foo')
        self.assertInQueue(('bar', None))
        self.assertInQueue(('baz', None))

    def test_addPages_with_continue_adds_parent_back_into_queue(self):
        self.branch.addPages(['foo'])
        self.branch.addPages(['bar', 'baz'], 'foo', 'continueTestToken')
        self.assertInQueue(('foo', 'continueTestToken'))

    def test_findIntersect_returns_none_with_no_intersect(self):
        branch1 = BFSBranch()
        branch2 = BFSBranch()
        branch1.addPages(['foo'])
        branch1.addPages(['bar', 'baz'], 'foo')
        branch2.addPages(['poo'])
        branch2.addPages(['par', 'paz'], 'poo')
        assert branch1.findIntersect(branch2) is None

    def test_findIntersect_returns_single_intersecting_element(self):
        branch1 = BFSBranch()
        branch2 = BFSBranch()
        branch1.addPages(['foo'])
        branch1.addPages(['bar', 'baz'], 'foo')
        branch2.addPages(['poo'])
        branch2.addPages(['par', 'baz'], 'poo')
        assert branch1.findIntersect(branch2) == 'baz'

    def test_findIntersect_returns_one_of_several_intersecting_elements(self):
        branch1 = BFSBranch()
        branch2 = BFSBranch()
        branch1.addPages(['foo'])
        branch1.addPages(['bar', 'baz'], 'foo')
        branch2.addPages(['poo'])
        branch2.addPages(['bar', 'baz'], 'poo')
        intersect = branch1.findIntersect(branch2)
        assert intersect in ['bar', 'baz']

    def test_calculatePath_returns_path_from_parent_of_intersect_to_source(self):
        self.branch.addPages(['foo'])
        self.branch.addPages(['bar', 'baz'], 'foo')
        self.branch.addPages(['boo', 'ban'], 'bar')
        self.branch.addPages(['new', 'nar'], 'boo')
        assert self.branch.calculatePath('new') == ['boo', 'bar', 'foo']

    def test_calculatePath_returns_empty_path_when_intersect_is_source(self):
        self.branch.addPages(['foo'])
        assert self.branch.calculatePath('foo') == []
