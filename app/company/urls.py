from .api import CompanyApi
from django.urls import path

urlpatterns = [
    path('companies/', CompanyApi.as_view(), name='company'),
]
