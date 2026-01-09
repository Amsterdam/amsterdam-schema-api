from rest_framework import serializers

from .models import ChangelogItem


class ChangelogItemSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = ChangelogItem
        fields = "__all__"

    def get_description(self, obj):
        return obj.description()
