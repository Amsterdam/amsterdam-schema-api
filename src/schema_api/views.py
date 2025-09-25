from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from schematools.contrib.django.models import Dataset, Publisher, Scope
from schematools.exceptions import DatasetVersionNotFound

from .utils import simplify_json


class RootView(View):
    """Root page of the server."""

    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "online"})


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "id"

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

    def retrieve(self, request, id):
        datasets = self.get_queryset()
        dataset = get_object_or_404(datasets, name=id)

        return Response(dataset.schema)

    @action(detail=True, url_path=r"(?P<vmajor>\w+)")
    def version(self, request, id, vmajor):
        datasets = self.get_queryset()
        dataset = get_object_or_404(datasets, name=id)
        try:
            dataset_vmajor = dataset.schema.get_version(vmajor)
        except DatasetVersionNotFound as e:
            return Response(status=404, data={"detail": str(e)})

        return Response(dataset_vmajor.json_data())


class ScopeViewSet(viewsets.ReadOnlyModelViewSet):

    # currently, id = TOPDESKBV/FENI
    # / messes with url path
    # lookup_field = "name"

    def get_queryset(self):
        return Scope.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            json_queryset = [scope.schema for scope in page]
            return self.get_paginated_response(json_queryset)

        json_queryset = [dataset.schema for dataset in queryset]
        return Response(json_queryset)

    def retrieve(self, request, pk):
        scopes = self.get_queryset()
        scope = get_object_or_404(scopes, pk=pk)

        return Response(scope.schema)


class PublisherViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "id"

    def get_queryset(self):
        return Publisher.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            json_queryset = [publisher.schema for publisher in page]
            return self.get_paginated_response(json_queryset)

        json_queryset = [dataset.schema for dataset in queryset]
        return Response(json_queryset)

    def retrieve(self, request, id):
        publishers = self.get_queryset()
        publisher = get_object_or_404(publishers, name=id)

        return Response(publisher.schema)
