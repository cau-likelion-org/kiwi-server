from rest_framework import serializers
from .models import HistoryDoc, Generation, CurrDoc
from users.models import User
import boto3
import os
import uuid
from django.conf import settings




class GenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = ['generation']


class HistoryDocSerializer(serializers.ModelSerializer):
    generations = GenerationSerializer(many=True)
    author = serializers.SerializerMethodField()
    titleMatched = serializers.SerializerMethodField()

    class Meta:
        model = HistoryDoc
        fields = ['id', 'title', 'generations', 'updated_at', 'created_at', 'author', 'content', 'titleMatched']

    def get_generations(self, obj):
        generations = Generation.objects.filter(title=obj).values_list('generation', flat=True)
        return list(generations)

    def create(self, validated_data):
        generations_data = validated_data.pop('generations')
        author = self.context['request'].user
        title = validated_data.get('title')
        
        history_data = {**validated_data, 'author': author}
        history_doc = HistoryDoc.objects.create(**history_data)
        
        for generation_data in generations_data:
            Generation.objects.create(title=history_doc, **generation_data)
        
        curr_doc = CurrDoc.objects.filter(history_doc__title=history_doc.title).first()
       
        if curr_doc is None:
            curr_doc = CurrDoc.objects.create(history_doc=history_doc, title= title)
        else:  
            curr_doc.history_doc = history_doc
            curr_doc.title = title
            curr_doc.save()

        return history_doc

    def get_author(self, obj):
        return obj.author.name
    
    def get_titleMatched(self, obj):
        keyword = self.context.get('keyword','')
        #print("Keyword:", keyword)
        return keyword == obj.title
    


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
    

    def create(self, validated_data):
        #print(validated_data)
        image_obj = validated_data['image']
        #print(image_obj)  
        #print(type(image_obj))  
        extension = os.path.splitext(image_obj.name)[1]

        random_uuid = str(uuid.uuid4())
        new_image_name = random_uuid + extension

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID_S3,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_S3,
            region_name=settings.AWS_REGION,
        )

        response = s3_client.put_object(
            Body=image_obj.read(),
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=new_image_name,  
            ContentType=image_obj.content_type,
            ContentDisposition='inline',
            CacheControl=settings.AWS_S3_OBJECT_PARAMETERS['CacheControl'],
        )
        #print(response)
        url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{new_image_name}" 
        #print(url) 
        return {'image': url}
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['image'] = instance['image']  
        return ret