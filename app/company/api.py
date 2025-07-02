from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .models import Company
from .serializers import CompanySerializer


class CompanyApi(GenericAPIView):
    """
    GET /api/v1/companies?sort=industry,-founded_year

    Returns sorted list of companies based on one or more fields.
    Supports descending sort with a '-' prefix.
    """

    serializer_class = CompanySerializer

    def get_queryset(self):
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
        return companies

    def get(self, request, *args, **kwargs):
        companies = self.get_queryset()
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)
