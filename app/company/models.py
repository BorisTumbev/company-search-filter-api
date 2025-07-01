from django.db import models

from .managers import CompanyManager


class Company(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    founded_year = models.IntegerField()

    objects = CompanyManager()

    def __str__(self):
        return self.name


class FinancialData(models.Model):
    company = models.ForeignKey(
        Company, related_name="financials", on_delete=models.CASCADE
    )
    year = models.IntegerField()
    revenue = models.BigIntegerField()
    net_income = models.BigIntegerField()

    def __str__(self):
        return f"{self.company.name} - {self.year}"


class CompanyDetails(models.Model):
    company = models.OneToOneField(
        Company, related_name="details", on_delete=models.CASCADE
    )
    company_type = models.CharField(max_length=100)
    size = models.CharField(max_length=100)
    ceo_name = models.CharField(max_length=255)
    headquarters = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.company.name} Details"
