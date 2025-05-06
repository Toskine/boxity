from audioop import add
import datetime
import json
import requests
from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.template import loader
from django.db.models import Q
from .models import Batiment, Lieu, Objet, adimaker


def on2(value):
    if(value>0):
        return str(value)
    return "0" + str(value)


def index(request):
    return render(request, "theapp/index.html")

def batiments(request):
    batiments_list = Batiment.objects.order_by('batiment_nom')[:10]
    template = loader.get_template('theapp/batiments.html')
    context = { 'batiments_list' : batiments_list, }
    return HttpResponse(template.render(context, request))


def batiment(request, id_batiment):
    try:
        batiment = Batiment.objects.get(pk=id_batiment)
    except Batiment.DoesNotExist:
        raise Http404("Batiment inexistant.")
    lieux_list = Lieu.objects.filter(batiment_id = id_batiment).order_by('lieu_nom')
    return render(request, "theapp/batiment.html", {'batiment': batiment, 'lieux_list': lieux_list })


def lieu(request, id_lieu):
    try:
        lieu = Lieu.objects.get(pk=id_lieu)
    except Lieu.DoesNotExist:
        raise Http404("Lieu inexistant")
    try:
        batiment = Batiment.objects.get(pk=lieu.batiment_id)
    except Batiment.DoesNotExist:
        raise Http404("Batiment inexistant")

    objets_list = Objet.objects.filter(lieu_id = id_lieu)
    
    idd = adimaker.objects.last()
    temp = adimaker.objects.last()
    hum = adimaker.objects.last()
    pres = adimaker.objects.last()
    lum = adimaker.objects.last()
    bruit = adimaker.objects.last()
    
    context = { 'idd': idd,
                'temp': temp,
                'hum': hum,
                'pres': pres,
                'lum': lum,
                'bruit': bruit,
                'batiment': batiment,
                'lieu': lieu,
                'objets_list': objets_list }

    return render(request, "theapp/lieu.html", context)

def objet(request):
    return render(request, "theapp/objet.html")
'''
def objet(request):
    return HttpResponse("Here's the text of the web page.")
'''


