from django.core.cache import cache
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .models import Company
from .serializers import CompanySerializer
from .utils.common.fields import get_cache_key_from_request


class CompanyApi(GenericAPIView):
    """
    GET /api/v1/companies?sort=industry,-founded_year

    Returns sorted list of companies based on one or more fields.
    Supports descending sort with a '-' prefix.
    """

    serializer_class = CompanySerializer

    def get_queryset(self):
        pass

    def get(self, request, *args, **kwargs):
        cache_key = get_cache_key_from_request(request)
        cache_data = cache.get(cache_key)
        if cache_data:
            return Response(cache_data)

        raw_search = self.request.query_params.get('search')
        sort_param = self.request.query_params.get('sort')
        filter_param = self.request.query_params.get('filter')
        sort_fields = [f.strip() for f in sort_param.split(',') if f.strip()] if sort_param else []
        companies = Company.objects.all_with_related()

        if raw_search:
            companies = companies.search(raw_search)
        if filter_param:
            companies = companies.filter(filter_param)
        if sort_fields:
            companies = companies.sort(sort_fields)

        serializer = self.get_serializer(companies, many=True)

        cache.set(cache_key, serializer.data, timeout=600)  # Cache for 10 minutes
        return Response(serializer.data)
