from django.contrib import admin
from .models import Labels, Images, Albums

# Register your models here.
admin.site.register(Labels)
admin.site.register(Images)
admin.site.register(Albums)