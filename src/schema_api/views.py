from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import viewsets
from rest_framework.response import Response
from schematools.contrib.django.models import Dataset

from .utils import simplify_json


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

    def retrieve(self, request, name=None):
        datasets = self.get_queryset()
        dataset = get_object_or_404(datasets, name=name)

        return Response(dataset.schema.json_data())
