from .internal import internal_api_urlpatterns as _internal_api_urlpatterns
from .public import public_api_urlpatterns as _public_api_urlpatterns

api_urlpatterns = _internal_api_urlpatterns + _public_api_urlpatterns
