from rest_framework.urlpatterns import format_suffix_patterns

from .api import api_urlpatterns
from .index import index_urlpatterns
from .sample import sample_urlpatterns
from .statistics import statistics_urlpatterns

urlpatterns = format_suffix_patterns(api_urlpatterns + index_urlpatterns + sample_urlpatterns + statistics_urlpatterns)
