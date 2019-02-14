from .models import Sample
import django_filters
from django import forms


class SampleFilter(django_filters.FilterSet):
    class Meta:
        model = Sample
        fields = ['md5', 'sha1', 'sha2', 'name', 'size', 'file_type']
    md5 = django_filters.CharFilter(label='MD5', lookup_expr='icontains')
    sha1 = django_filters.CharFilter(label='SHA1', lookup_expr='icontains')
    sha2 = django_filters.CharFilter(label='SHA2', lookup_expr='icontains')
    name = django_filters.CharFilter(label='File name', lookup_expr='icontains')
    size_gt = django_filters.NumberFilter(label='Size', field_name='size', lookup_expr='gt')
    size_lt = django_filters.NumberFilter(label='Size', field_name='size', lookup_expr='lt')
    # uploaded_on = django_filters.DateTimeFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'YYYY/MM/DD'}))
    # reemplazar por un combo con las opciones existentes (las puedo sacar desde el config manager para no queriar la DB
    file_type = django_filters.CharFilter(label='File type', lookup_expr='icontains')
