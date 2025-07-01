from rest_framework import serializers

from .models import Company, CompanyDetails, FinancialData


class CompanyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetails
        fields = ['company_type', 'size', 'ceo_name', 'headquarters']


class FinancialDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialData
        fields = ['year', 'revenue', 'net_income']


class CompanySerializer(serializers.ModelSerializer):
    details = CompanyDetailsSerializer(read_only=True)
    financials = FinancialDataSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ['name', 'country', 'industry', 'founded_year', 'details', 'financials']
