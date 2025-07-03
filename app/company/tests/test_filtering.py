from company.models import Company
from django.test import TestCase

from ..queryset import SearchQuerySet
from ..utils.filtering import apply_filter


class TestFilteringLogic(TestCase):
    fixtures = ['test_companies.json']

    def setUp(self):
        self.companies = list(
            Company.objects.select_related('details').prefetch_related('financials'),
        )

    def test_filter_by_simple_field(self):
        filtered = apply_filter(self.companies, 'industry=Tech')
        self.assertTrue(all(c.industry == 'Tech' for c in filtered))
        self.assertTrue(len(filtered) > 0)

    def test_filter_by_quoted_name(self):
        filtered = apply_filter(self.companies, 'name="Alpha Corp"')
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].name, 'Alpha Corp')

    def test_filter_and(self):
        filtered = apply_filter(self.companies, 'industry=Tech AND founded_year>=2000')
        self.assertTrue(all(c.industry == 'Tech' and c.founded_year >= 2000 for c in filtered))

    def test_filter_or(self):
        filtered = apply_filter(self.companies, 'industry=Tech OR name="Beta Group"')
        names = [c.name for c in filtered]
        self.assertIn('Beta Group', names)
        self.assertTrue(any(c.industry == 'Tech' for c in filtered))

    def test_filter_by_nested_field(self):
        filtered = apply_filter(self.companies, 'details__company_type=Public')
        self.assertTrue(
            all(hasattr(c, 'details') and c.details.company_type == 'Public' for c in filtered),
        )

    def test_filter_by_numeric_related_field(self):
        filtered = apply_filter(self.companies, 'revenue>1000000')
        self.assertTrue(
            any(any(f.revenue > 1_000_000 for f in c.financials.all()) for c in filtered),
        )

    def test_filter_by_multiword_value_unquoted(self):
        filtered = apply_filter(self.companies, 'name=Alpha Corp')
        # Should still match "Alpha Corp" (unquoted multiword)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].name, 'Alpha Corp')

    def test_filter_by_simple_field_chunked(self):
        queryset = SearchQuerySet(self.companies)
        chunks = queryset.filter_chunked('industry=Tech', chunk_size=2)
        filtered = [c for chunk in chunks for c in chunk]
        expected = [c for c in self.companies if c.industry == 'Tech']
        self.assertEqual(
            sorted([c.pk for c in filtered]),
            sorted([c.pk for c in expected]),
        )

    def test_filter_by_quoted_name_chunked(self):
        queryset = SearchQuerySet(self.companies)
        chunks = queryset.filter_chunked('name="Alpha Corp"', chunk_size=2)
        filtered = [c for chunk in chunks for c in chunk]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].name, 'Alpha Corp')

    def test_filter_and_chunked(self):
        queryset = SearchQuerySet(self.companies)
        chunks = queryset.filter_chunked('industry=Tech AND founded_year>=2000', chunk_size=2)
        filtered = [c for chunk in chunks for c in chunk]
        self.assertTrue(all(c.industry == 'Tech' and c.founded_year >= 2000 for c in filtered))

    def test_filter_or_chunked(self):
        queryset = SearchQuerySet(self.companies)
        chunks = queryset.filter_chunked('industry=Tech OR name="Beta Group"', chunk_size=2)
        filtered = [c for chunk in chunks for c in chunk]
        names = [c.name for c in filtered]
        self.assertIn('Beta Group', names)
        self.assertTrue(any(c.industry == 'Tech' for c in filtered))

    def test_filter_by_nested_field_chunked(self):
        queryset = SearchQuerySet(self.companies)
        chunks = queryset.filter_chunked('details__company_type=Public', chunk_size=2)
        filtered = [c for chunk in chunks for c in chunk]
        self.assertTrue(
            all(hasattr(c, 'details') and c.details.company_type == 'Public' for c in filtered),
        )
