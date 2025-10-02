from __future__ import annotations

from pathlib import Path

import pytest
from django.core.handlers.wsgi import WSGIRequest
from django.core.management import call_command
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory

from tests.utils import api_request_with_scopes, to_drf_request

HERE = Path(__file__).parent


@pytest.fixture
def here() -> Path:
    return HERE


@pytest.fixture()
def api_rf() -> APIRequestFactory:
    """Request factory for APIView classes"""
    return APIRequestFactory()


@pytest.fixture()
def api_request() -> WSGIRequest:
    """Return a very basic Request object. This can be used for the APIClient.
    The DRF views use a different request object internally, see `drf_request` for that.
    """
    return api_request_with_scopes([])


@pytest.fixture()
def drf_request(api_request) -> Request:
    """The wrapped WSGI Request as a Django-Rest-Framework request.
    This is the 'request' object that APIView.dispatch() creates.
    """
    return to_drf_request(api_request)


@pytest.fixture()
def api_client() -> APIClient:
    """Return a client that has unhindered access to the API views"""
    api_client = APIClient()
    api_client.default_format = "json"  # instead of multipart
    return api_client


@pytest.fixture()
def common_headers(request) -> dict:
    return {
        "X-Correlation-ID": request.node.name,
        "X-User": "foobar",
        "X-Task-Description": "unittest",
    }


@pytest.fixture()
def dataset_fixture(here):
    dataset_path = here / "files/datasets/bomen.json"
    args = [dataset_path]
    call_command("import_schemas", *args, dry_run=False)


@pytest.fixture()
def scope_fixture(here):
    scope_fp_mdw = here / "files/scopes/fp_mdw.json"
    scope_openbaar = here / "files/scopes/openbaar.json"
    args = [scope_fp_mdw, scope_openbaar]
    call_command("import_scopes", *args)


@pytest.fixture()
def publisher_fixture(here):
    publisher_path = here / "files/publishers/benk.json"
    args = [publisher_path]
    call_command("import_publishers", *args)


@pytest.fixture()
def profile_fixture(here):
    profile_path = here / "files/profiles/brkdataportaalgebruiker.json"
    args = [profile_path]
    call_command("import_profiles", *args)
