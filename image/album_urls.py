from django.urls import path
from . import album_views

urlpatterns = [
    path('album',album_views.AlbumApi.as_view()),
    path('image',album_views.AlbumData.as_view()),
    path('cover', album_views.AlbumCover.as_view()),
]