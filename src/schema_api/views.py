from django.http import JsonResponse
from django.views import View
from rest_framework import viewsets

from .models import Dataset
from .serializers import DatasetSerializer


class RootView(View):
    """Root page of the server."""

    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "online"})


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
