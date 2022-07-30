from django.urls import path
from . import views

urlpatterns = [
    path('image', views.ImageApi.as_view()),
    path('upload', views.image_handle),
    path('info', views.ImageData.as_view()),
    path('r18', views.ImageR18.as_view()),
    path('random', views.random_image),
    path('tool',views.Tool.as_view()),
]