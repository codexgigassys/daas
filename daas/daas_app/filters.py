import django_filters
from django_filters.widgets import RangeWidget

from .models import Sample
from .utils.choices import FILE_TYPE_CHOICES, REDIS_JOB_CHOICES


class SampleFilter(django_filters.FilterSet):
    class Meta:
        model = Sample
        fields = ['md5', 'sha1', 'sha2', 'name', 'size', 'file_type']
    md5 = django_filters.CharFilter(label='MD5', lookup_expr='icontains')
    sha1 = django_filters.CharFilter(label='SHA1', lookup_expr='icontains')
    sha2 = django_filters.CharFilter(label='SHA2', lookup_expr='icontains')
    name = django_filters.CharFilter(label='File name', lookup_expr='icontains')
    size_gte = django_filters.NumberFilter(label='Minimum Size', field_name='size', lookup_expr='gte')
    size_lte = django_filters.NumberFilter(label='Maximum Size', field_name='size', lookup_expr='lte')
    uploaded_on = django_filters.DateTimeFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'MM/DD/YYYY'}))
    file_type = django_filters.TypedChoiceFilter(choices=FILE_TYPE_CHOICES)
    task__status = django_filters.TypedChoiceFilter(choices=REDIS_JOB_CHOICES,
                                                    label='Status')
    result__processed_on = django_filters.DateTimeFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'MM/DD/YYYY'}))
