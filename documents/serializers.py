from rest_framework import serializers
from .models import *

# class HistoryDocSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = HistoryDoc
#         fields = "__all__"
#         #read_only_fields = ['title']


class GenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = ('generation',) 

    def create(self, validated_data) :
        history_doc_title = self.context['history_doc']
        generation = Generation.objects.create(
            title = history_doc_title,
            generation = validated_data['generation']
        )
        return generation

class HistoryDocSerializer(serializers.ModelSerializer):
    generations = GenerationSerializer(many=True, read_only=True)  

    class Meta:
        model = HistoryDoc
        fields = ('id', 'title', 'updated_at', 'created_at', 'author', 'content', 'generations')

