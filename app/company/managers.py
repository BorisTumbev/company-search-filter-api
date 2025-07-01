from django.db import models

from .queryset import SearchQuerySet


class CompanyManager(models.Manager):
    def all_with_related(self):
        return SearchQuerySet(
            list(
                self.select_related('details').prefetch_related('financials')
            )
        )
