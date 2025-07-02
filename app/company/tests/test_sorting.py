from dataclasses import dataclass

from django.test import SimpleTestCase

from ..utils.sorting import create_sort_key, merge_sort


@dataclass
class Dummy:
    name: str
    age: int
    score: float


@dataclass
class DummyPartial:
    name: str
    age: int = None
    score: float = None


class TestSorting(SimpleTestCase):
    def setUp(self):
        self.dummy_list = [
            Dummy(name='Charlie', age=30, score=90.5),
            Dummy(name='Alice', age=25, score=95.2),
            Dummy(name='Bob', age=28, score=80.0),
            Dummy(name='Alice', age=29, score=95.2),
        ]

    def test_merge_sort_by_single_field(self):
        key_fn = create_sort_key(['age'])
        sorted_objs = merge_sort(self.dummy_list, key=key_fn)
        self.assertEqual([o.age for o in sorted_objs], [25, 28, 29, 30])

    def test_merge_sort_by_single_field_descending(self):
        key_fn = create_sort_key(['-score'])
        sorted_objs = merge_sort(self.dummy_list, key=key_fn)
        self.assertEqual([o.score for o in sorted_objs], [95.2, 95.2, 90.5, 80.0])

    def test_merge_sort_by_multiple_fields(self):
        key_fn = create_sort_key(['name', '-age'])
        sorted_objs = merge_sort(self.dummy_list, key=key_fn)
        result = [(o.name, o.age) for o in sorted_objs]
        self.assertEqual(result, [('Alice', 29), ('Alice', 25), ('Bob', 28), ('Charlie', 30)])

    def test_merge_sort_with_strings(self):
        key_fn = create_sort_key(['name'])
        sorted_objs = merge_sort(self.dummy_list, key=key_fn)
        self.assertEqual([o.name for o in sorted_objs], ['Alice', 'Alice', 'Bob', 'Charlie'])
