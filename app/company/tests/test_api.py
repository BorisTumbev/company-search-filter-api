from django.core.cache import cache
from rest_framework.test import APITestCase

from ..utils.common.fields import get_cache_key_from_request


class TestCompanyApi(APITestCase):
    fixtures = ['test_companies.json']
    URL = '/api/v1/companies/'

    def setUp(self):
        cache.clear()  # Always clear cache to ensure test isolation

    def test_filter_by_name(self):
        response = self.client.get(self.URL, {'filter': 'name="Alpha Corp"'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Alpha Corp')

    def test_filter_and_sort(self):
        response = self.client.get(self.URL, {'filter': 'industry=Tech', 'sort': '-founded_year'})
        self.assertEqual(response.status_code, 200)
        data = response.data
        # Should be sorted by founded_year descending, and all are Tech
        years = [c['founded_year'] for c in data]
        self.assertEqual(years, sorted(years, reverse=True))
        self.assertTrue(all(c['industry'] == 'Tech' for c in data))

    def test_api_caching(self):
        params = {'filter': 'industry=Tech'}
        # First call - not cached
        response1 = self.client.get(self.URL, params)
        self.assertEqual(response1.status_code, 200)
        # Manually change cache for this key
        cache_key = get_cache_key_from_request(response1.wsgi_request)
        cache.set(cache_key, [{'name': 'CACHED'}], timeout=600)
        # Second call - should hit cache
        response2 = self.client.get(self.URL, params)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data, [{'name': 'CACHED'}])

    def test_combined_search_filter_sort(self):
        params = {
            'search': 'industry:Tech',
            'filter': 'founded_year>=2000',
            'sort': '-name',
        }
        response = self.client.get(self.URL, params)
        self.assertEqual(response.status_code, 200)
        names = [c['name'] for c in response.data]
        self.assertEqual(names, sorted(names, reverse=True))
        self.assertTrue(
            all(c['industry'] == 'Tech' and c['founded_year'] >= 2000 for c in response.data),
        )
