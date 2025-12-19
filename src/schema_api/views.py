from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from schematools.contrib.django.models import Dataset, Profile, Publisher, Scope
from schematools.exceptions import DatasetTableNotFound, DatasetVersionNotFound
from schematools.types import DatasetSchema

import schema_api.openapi.schema as schema

from .models import ChangelogItem
from .serializers import ChangelogItemSerializer
from .utils import simplify_json


class RootView(View):
    """Root page of the server."""

    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "online"})


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "name"

    def get_queryset(self):
        return Dataset.objects.all()

    @schema.list_datasets_schema
    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:

            # Simplify JSON by replacing inlined table with tabel ref
            json_queryset = [simplify_json(dataset.schema) for dataset in page]
            return self.get_paginated_response(json_queryset)

        json_queryset = [simplify_json(dataset.schema) for dataset in queryset]
        return Response(json_queryset)

    @schema.retrieve_datasets_schema
    def retrieve(self, request, name):
        datasets = self.get_queryset()
        dataset = get_object_or_404(datasets, name=name)
        dataset_schema = dataset.schema

        # Scope filtering
        scopes_param = request.query_params.getlist("scopes")
        if scopes_param:

            # Transform url safe scope ids to regular ids
            scopes = [scope.replace("_", "/").upper() for scope in scopes_param]
            dataset_schema = DatasetSchema.filter_on_scopes(dataset_schema, scopes)

        return Response(dataset_schema)

    @schema.retrieve_datasets_schema_v
    @action(detail=True, url_path=r"(?P<vmajor>v\d{1,3})")
    def version(self, request, name, vmajor):
        datasets = self.get_queryset()
        dataset = get_object_or_404(datasets, name=name)
        dataset_schema = dataset.schema

        # Scope filtering
        scopes_param = request.query_params.getlist("scopes")
        if scopes_param:

            # Transform url safe scope ids to regular ids
            scopes = [scope.replace("_", "/").upper() for scope in scopes_param]
            dataset_schema = DatasetSchema.filter_on_scopes(dataset_schema, scopes)

        try:
            dataset_vmajor = dataset_schema.get_version(vmajor)
        except DatasetVersionNotFound as e:
            return Response(status=404, data={"detail": str(e)})

        return Response(dataset_vmajor.json_data())

    @schema.retrieve_datasets_schema_v_t
    @action(detail=True, url_path=r"(?P<vmajor>v\d{1,3})/(?P<table_id>\w+)")
    def table(self, request, name, vmajor, table_id):
        datasets = self.get_queryset()
        dataset = get_object_or_404(datasets, name=name)
        dataset_schema = dataset.schema

        # Scope filtering
        scopes_param = request.query_params.getlist("scopes")
        if scopes_param:

            # Transform url safe scope ids to regular ids
            scopes = [scope.replace("_", "/").upper() for scope in scopes_param]
            dataset_schema = DatasetSchema.filter_on_scopes(dataset_schema, scopes)

        try:
            dataset_vmajor = dataset_schema.get_version(vmajor)
            try:
                dataset_table = dataset_vmajor.get_table_by_id(table_id)
            except DatasetTableNotFound:
                return Response(status=404, data={"detail": f"Table '{table_id}' not found."})
        except DatasetVersionNotFound as e:
            return Response(status=404, data={"detail": str(e)})
        return Response(dataset_table.json_data())


class BaseViewSet(viewsets.ReadOnlyModelViewSet):

    def list(self, request):
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            json_queryset = [item.schema for item in page]
            return self.get_paginated_response(json_queryset)

        json_queryset = [item.schema for item in self.queryset]
        return Response(json_queryset)

    def retrieve(self, request, pk):
        item = get_object_or_404(self.queryset, pk=pk)

        return Response(item.schema)


@extend_schema_view(
    list=schema.list_scope_schema,
    retrieve=schema.retrieve_scope_schema,
)
class ScopeViewSet(BaseViewSet):
    queryset = Scope.objects.all()


@extend_schema_view(
    list=schema.list_publisher_schema,
    retrieve=schema.retrieve_publisher_schema,
)
class PublisherViewSet(BaseViewSet):
    queryset = Publisher.objects.all()


@extend_schema_view(
    list=schema.list_profile_schema,
    retrieve=schema.retrieve_profile_schema,
)
class ProfileViewSet(BaseViewSet):
    queryset = Profile.objects.all()


class ChangelogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChangelogItem.objects.all()
    serializer = ChangelogItemSerializer(queryset, many=True)

    def list(self, request):
        page = self.paginate_queryset(self.serializer.data)
        if page is not None:
            return self.get_paginated_response(self.serializer.data)
        return Response(self.serializer.data)
