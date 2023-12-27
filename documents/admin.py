from django.contrib import admin
from .models import *

admin.site.register(HistoryDoc)
admin.site.register(CurrDoc)
admin.site.register(BackLink)
admin.site.register(Generation)