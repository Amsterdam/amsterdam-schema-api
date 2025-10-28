from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory


def api_request_with_scopes(scopes: list[str], data=None) -> Request:
    request = APIRequestFactory().get("/v1/dummy/", data=data)
    request.accept_crs = None  # for DSOSerializer, expects to be used with DSOViewMixin
    request.response_content_crs = None

    return request


def to_drf_request(api_request):
    """Turns an API request into a DRF request."""
    request = Request(api_request)
    request.accepted_renderer = JSONRenderer()
    return request
