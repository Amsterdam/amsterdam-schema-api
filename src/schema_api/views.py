from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import viewsets
from rest_framework.response import Response
from schematools.contrib.django.models import Dataset


class RootView(View):
    """Root page of the server."""

    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "online"})


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):

    def get_queryset(self):
        return Dataset.objects.all()

    def list(self, request):
        datasets = self.get_queryset()
        json_queryset = [dataset.schema.json_data() for dataset in datasets]

        return Response(json_queryset)

    def retrieve(self, request, pk=None):
        datasets = self.get_queryset()
        dataset = get_object_or_404(datasets, pk=pk)

        return Response(dataset.schema.json_data())
