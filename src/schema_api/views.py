from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from schematools.contrib.django.models import Dataset

from .utils import filter_on_scope, simplify_json


class RootView(View):
    """Root page of the server."""

    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "online"})


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "name"

    def get_queryset(self):
        return Dataset.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:

            # Simplify JSON by replacing inlined table with tabel ref
            json_queryset = [simplify_json(dataset.schema) for dataset in page]
            return self.get_paginated_response(json_queryset)

        json_queryset = [simplify_json(dataset.schema) for dataset in queryset]
        return Response(json_queryset)

    def retrieve(self, request, name):
        datasets = self.get_queryset()
        dataset = get_object_or_404(datasets, name=name)

        return Response(dataset.schema)

    @action(detail=True, url_path=r"(?P<vmajor>\w+)")
    def version(self, request, name, vmajor):
        datasets = self.get_queryset()
        dataset = get_object_or_404(datasets, name=name)
        try:
            dataset_vmajor = dataset.schema.get_version(vmajor)
        except Exception as e:
            raise e

        # Filter on scope if provided in the request
        scope = self.request.query_params.get("scope")
        if scope:
            scoped_schema = filter_on_scope(dataset_vmajor, scope)
            return Response(scoped_schema)

        return Response(dataset_vmajor.json_data())
