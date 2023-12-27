# documents/serializers.py
from rest_framework import serializers
from .models import HistoryDoc, Generation
from users.models import User

class HistoryDocSerializer(serializers.ModelSerializer):
    generation = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = HistoryDoc
        fields = ['id', 'title', 'generation', 'updated_at', 'created_at', 'author', 'content']

    def get_generation(self, obj):
        generations = Generation.objects.filter(title=obj).values_list('generation', flat=True)
        return list(generations)

    def get_author(self, obj):
        return obj.author.name