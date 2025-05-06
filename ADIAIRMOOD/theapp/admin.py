from django.contrib import admin

# Register your models here.
from .models import Atmo, Batiment, Lieu, Objet
admin.site.register(Atmo)
admin.site.register(Batiment)
admin.site.register(Lieu)
admin.site.register(Objet)
