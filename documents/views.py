from django.shortcuts import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

class DocsPost(APIView) : 
    def post(self, request, format = None):
        serializer = HistoryDocSerializer(data = request.data)
        if serializer.is_valid() :
            history_doc = serializer.save()
            
            generations_data = request.data.get('generations')
            generations_list = []
            
            for i in generations_data :
                generation_serializer = GenerationSerializer(
                    data = i,
                    context = {'history_doc' : history_doc})

                if generation_serializer.is_valid():
                    generation = generation_serializer.save()
                    generations_list.append(generation)
            
            history_doc.generations.set(generations_list)

            return Response({'message' : 'success' , 'data' : serializer.data},  status=status.HTTP_201_CREATED)
        
        error_data = {
            'message': 'Failed to create Doc',
            'errors': serializer.errors
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    

    
class DocDetail(APIView):
     def get(self, request, title, format =None):
        try:
            latest_doc = HistoryDoc.objects.filter(title=title).latest('created_at')
            serializer = HistoryDocSerializer(latest_doc)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except HistoryDoc.DoesNotExist:
            return Response({'message': 'Document does not exist'}, status=status.HTTP_404_NOT_FOUND)

#     def patch(self, request, title):
#         docs = HistoryDoc.objects.filter(title=title).order_by('-updated_at')

#         if docs.exists():
#             doc = docs.first()  # 가장 최신 업데이트 문서 선택

#             serializer = HistoryDocSerializer(instance=doc, data=request.data)
            
#             if serializer.is_valid():
#                 updated_doc = serializer.save()

#                 doc.author = updated_doc.author
#                 doc.content = updated_doc.content
#                 updated_doc.generations.set(doc.generations)
#                 doc.save()

#                 return Response(serializer.data)
            
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({'message': 'No document found with the given title'}, status=status.HTTP_404_NOT_FOUND)