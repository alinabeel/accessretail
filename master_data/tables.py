import django_tables2 as tables
from .models import Category
from django_tables2 import Column, Table


class CategoryTable(tables.Table):
    class Meta:
        model = Category
        fields = ("name",'code','parent','description','is_active' )
        per_page = 30
        name = Column(accessor='name', verbose_name='Name')

