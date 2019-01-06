from typing import Set
from unittest import TestCase

from graph import Graph


class ValidationError(Exception):

    def __init__(self, message: str, clashing_items: Set = None, missing_items: Set = None) -> None:
        super().__init__(message)
        self.clashing_items = clashing_items
        self.missing_items = missing_items


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
                all_missing = set()
                for (route, _) in routes_to_element:
                    missing_items = [item for item in route if item not in elements]
                    if not missing_items:
                        path_matched = True
                        break
                    else:
                        all_missing.update(set(missing_items))

                if not path_matched:
                    raise ValidationError(
                        '{} requires at least one of these paths to be present: {}'.format(
                            element,
                            [' & '.join([item for item in r.route]) for r in routes_to_element]
                        ),
                        missing_items=all_missing
                    )

        for element in elements:
            found = self._mutually_exclusive.find_route(element)
            if found:
                if set(found.route) < set(elements):
                    raise ValidationError(
                        'The presence of {} requires these items to NOT be present: {}'.format(
                            element,
                            found.route
                        ),
                        clashing_items=set(found.route)
                    )


class ValidationTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = ValidationGraph()
        cls.g.add_required_together(['can drive', 'can swim', 'hovercraft'])
        cls.g.add_required_together(['can drive', 'below 100 kg', 'bike license', 'mountain biking'])
        cls.g.add_required_together(['can drive', 'below 100 kg', 'car license', 'dune buggy'])
        cls.g.add_required_together(['can swim', 'deep sea diving'])

        cls.g.add_mutually_exclusive(['thalassophobia', 'deep sea diving'])
        cls.g.add_mutually_exclusive(['motion sickness', 'hovercraft'])

    def test_required_together(self):
        data = ['mountain biking', 'bike license', 'can drive', 'can swim']
        with self.assertRaises(ValidationError) as w:
            self.g.validate_elements(data)
        self.assertEqual({'below 100 kg'}, w.exception.missing_items)

    def test_mutex(self):
        data = ['can swim', 'deep sea diving', 'thalassophobia']
        with self.assertRaises(ValidationError) as w:
            self.g.validate_elements(data)
        self.assertEqual({'thalassophobia'}, w.exception.clashing_items)
