from django.db import models
from users.models import User

class HistoryDoc(models.Model):
    title = models.CharField(max_length=30)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(null=True)

class CurrDoc(models.Model):
    history_doc = models.ForeignKey(HistoryDoc, on_delete=models.CASCADE, related_name='curr_docs')
    title = models.CharField(max_length=30)  
    updated_at = models.DateTimeField(auto_now_add=True)

class BackLink(models.Model):
    src = models.ForeignKey(CurrDoc, on_delete=models.CASCADE, related_name='backlink_src')
    dst = models.ForeignKey(CurrDoc, on_delete=models.CASCADE, related_name='backlink_dst')

class Generation(models.Model):
    title = models.ForeignKey(HistoryDoc, on_delete=models.CASCADE, related_name='generations')
    generation = models.IntegerField()


