from rest_framework import serializers

from .models import ChangelogItem


class ChangelogItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangelogItem
        fields = "__all__"
