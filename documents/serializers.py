from rest_framework import serializers
from .models import HistoryDoc, Generation, CurrDoc
from users.models import User


class GenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = ['generation']


class HistoryDocSerializer(serializers.ModelSerializer):
    generations = GenerationSerializer(many=True)
    author = serializers.SerializerMethodField()

    class Meta:
        model = HistoryDoc
        fields = ['id', 'title', 'generations', 'updated_at', 'created_at', 'author', 'content']

    def get_generations(self, obj):
        generations = Generation.objects.filter(title=obj).values_list('generation', flat=True)
        return list(generations)

    def create(self, validated_data):
        generations_data = validated_data.pop('generations')
        author = self.context['request'].user
        
        history_data = {**validated_data, 'author': author}
        history_doc = HistoryDoc.objects.create(**history_data)
        
        for generation_data in generations_data:
            Generation.objects.create(title=history_doc, **generation_data)

        CurrDoc.objects.update_or_create(
            title=history_doc.title,
            defaults={'historydoc': history_doc}
        )

        return history_doc

    def get_author(self, obj):
        return obj.author.name