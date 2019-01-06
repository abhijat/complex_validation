from unittest import TestCase

from graph import Graph


class ValidationGraph(object):

    def __init__(self):
        self._required_together = Graph()
        self._mutually_exclusive = Graph()

    def add_required_together(self, elements):
        self._required_together.add_path(elements)

    def add_mutually_exclusive(self, elements):
        self._mutually_exclusive.add_path(elements)

    def validate_elements(self, elements):
        for element in elements:
            routes_to_element = self._required_together.find_all_routes(element)
            if routes_to_element:
                path_matched = False
                for (route, _) in routes_to_element:
                    missing_items = [item for item in route if item not in elements]
                    if not missing_items:
                        path_matched = True
                        break

                if not path_matched:
                    raise Exception('{} requires at least one of these paths to be present: {}'.format(
                        element,
                        [' & '.join([item for item in r.route]) for r in routes_to_element]
                    ))

        for element in elements:
            found = self._mutually_exclusive.find_route(element)
            if found:
                if set(found.route) < set(elements):
                    raise Exception(
                        'The presence of {} requires these items to NOT be present: {}'.format(
                            element,
                            found.route
                        )
                    )


class ValidationTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = ValidationGraph()
        cls.g.add_required_together(['can drive', 'can swim', 'hovercraft'])
        cls.g.add_required_together(['can drive', 'below 100 kg', 'mountain biking'])
        cls.g.add_required_together(['can swim', 'no thalassophobia', 'deep sea diving'])

    def test_required_together(self):
        data = ['mountain biking', 'can swim']
        self.g.validate_elements(data)

    def test_mutex(self):
        pass
