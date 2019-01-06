import json
from collections import namedtuple
from typing import Optional
from unittest import TestCase

SearchResult = namedtuple('SearchResult', ['route', 'node'])


class Graph(object):

    def __init__(self, root=None):
        if root is None:
            self.root = {}
        else:
            self.root = root

    def add_path(self, elements):

        node = self.find_prefix_node(elements)
        if not node:
            node = self.root

        for element in elements:
            node[element] = {}
            node = node[element]

    def add_key(self, key, node=None):
        if node is None:
            node = self.root
        node[key] = {}
        return node[key]

    def find_route(self, key):
        route = self._bfs(key, self.root, [])
        return None if not route else route

    def find_all_routes(self, key):
        routes = []
        self._traverse(key, self.root, [], routes)
        return routes

    def find_prefix_node(self, route):
        return self._prefix_node(route, node=self.root)

    def _prefix_node(self, route, node):
        if not route:
            return node

        head = route[0]
        route = route[1:]

        node = node.get(head, None)
        if not node:
            return None
        else:
            return self._prefix_node(route, node)

    def _traverse(self, key, node, route, routes):
        if key in node:
            routes.append(SearchResult(route[:], node))

        for k, v in node.items():
            route.append(k)
            self._traverse(key, v, route, routes)
            route.pop()

    def _bfs(self, key, node, route) -> Optional[SearchResult]:
        if key in node:
            return SearchResult(route=route, node=node[key])
        else:
            for _key, _node in node.items():
                if _node:
                    route.append(_key)
                    found = self._bfs(key, _node, route)
                    if found:
                        return found
                    route.pop()

    def __repr__(self) -> str:
        return json.dumps(self.root, indent=' ')


class GraphTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = Graph({
            1: {
                2: {3: {4: {}}},
                5: {22: {}},
                919: {2: {}}
            }
        })

    def test_path_is_returned_for_given_key(self):
        self.assertListEqual(self.g.find_route(22).route, [1, 5])
        self.assertListEqual(self.g.find_route(2).route, [1])
        self.assertListEqual(self.g.find_route(4).route, [1, 2, 3])

    def test_none_is_returned_for_missing_key(self):
        self.assertIsNone(self.g.find_route(99))

    def test_add_paths_with_branching(self):
        g = Graph()
        g.add_path([1, 2, 3, 4, 5])
        g.add_path([3, 8, 998])
        self.assertListEqual(g.find_route(998).route, [3, 8])

    def test_find_all_routes(self):
        routes = self.g.find_all_routes(2)
        self.assertEqual(len(routes), 2)
        self.assertListEqual([1], routes[0].route)
        self.assertListEqual([1, 919], routes[1].route)

    def test_find_prefix(self):
        n = self.g.find_prefix_node([1, 2, 3])
        self.assertDictEqual({4: {}}, n)

    def test_add_prefixed_path_results_in_single_path(self):
        self.g.add_path([1024, 4096])
        self.g.add_path([1024, 4096, 779])
        self.assertEqual(len(self.g.find_all_routes(4096)), 1)
        self.assertEqual(len(self.g.find_all_routes(779)), 1)
