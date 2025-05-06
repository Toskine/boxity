from django.urls import path

from .views import index, batiment, batiments, lieu, objet

urlpatterns = [
    # /theapp
    path('', index, name="index"),    
    path('batiments/', batiments, name="batiments"),
   
    # /theapp/x/
    path('<int:id_batiment>/', batiment, name="batiment"),
    
    # /theapp/x/y/
    path('<int:id_lieu>/lieu/', lieu, name="lieu"),
    
    # /theapp/x/y/z
    #path('<int:id_batiment>/<int:id_lieu>/<int:id_objet>/', objet, name='objet'),
]

