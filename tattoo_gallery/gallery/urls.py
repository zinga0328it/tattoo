from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.gallery_list, name='list'),
    path('tattoo/<int:pk>/', views.tattoo_detail, name='detail'),
    
    # API per le pagine HTML statiche
    path('api/tattoos/', views.api_tattoos, name='api_tattoos'),
    path('api/tattoo/<int:pk>/', views.api_tattoo_detail, name='api_tattoo_detail'),
    path('api/artist/<str:username>/', views.api_artist_tattoos, name='api_artist_tattoos'),
]
