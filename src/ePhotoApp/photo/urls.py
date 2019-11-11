from django.urls import path
from django.conf.urls import url
from . import views
from .models import Photo

urlpatterns = [
    # url('/', views.index, name='index'),
    path('', views.index, name='index'),
	path('index', views.index, name='index'),
    path('gallery', views.gallery, name='gallery'),
    path('game', views.game, name='game'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    # path('photo/', views.photo_list, name='photo_list'),
    url('upload', views.upload, name='upload'),
    path('<uuid:name>', views.preview, name='preview'),
    path('<uuid:name>/edit', views.edit, name='edit'),
    #path('gallery', views.get_query, name='get_query'),
]