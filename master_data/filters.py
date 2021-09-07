import django_filters as filters
from .models import Category

class CategoryListFilter(filters.FilterSet):
    class Meta:
        model = Category
        fields = ['name','code']
