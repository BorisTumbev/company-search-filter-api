from company.models import Company
from django.test import TestCase

from ..utils.common.parsing import parse_query
from ..utils.searching import apply_search


class TestSearchLogic(TestCase):
    fixtures = ['test_companies.json']

    def setUp(self):
        self.companies = list(
            Company.objects.select_related('details').prefetch_related('financials'),
        )

    def test_search_by_text_field(self):
        # Text partial (case-insensitive)
        conds = parse_query('industry:tech')
        filtered = apply_search(self.companies, conds)
        self.assertTrue(all('tech' in c.industry.lower() for c in filtered))
        self.assertTrue(len(filtered) > 0)

    def test_search_by_exact_field(self):
        conds = parse_query('country=USA')
        filtered = apply_search(self.companies, conds)
        self.assertTrue(all(c.country == 'USA' for c in filtered))
        self.assertTrue(len(filtered) > 0)

    def test_search_by_quoted_name(self):
        conds = parse_query('name="Alpha Corp"')
        filtered = apply_search(self.companies, conds)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].name, 'Alpha Corp')

    def test_search_by_numeric(self):
        # Should match companies where any financials record has revenue > 1,000,000
        conds = parse_query('revenue>1000000')
        filtered = apply_search(self.companies, conds)
        self.assertTrue(
            any(any(f.revenue > 1_000_000 for f in c.financials.all()) for c in filtered),
        )

    def test_search_by_nested_field(self):
        conds = parse_query('details__size=Large')
        filtered = apply_search(self.companies, conds)
        self.assertTrue(all(hasattr(c, 'details') and c.details.size == 'Large' for c in filtered))
