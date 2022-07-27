from django.urls import path
from . import label_views

urlpatterns = [
    path('label',label_views.LabelApi.as_view()),
]