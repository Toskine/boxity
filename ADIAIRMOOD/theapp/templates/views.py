from audioop import add
import datetime
import json
import requests
from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.template import loader
from django.db.models import Q
from .models import Atmo, Batiment, Lieu, Objet, adimaker


def on2(value):
    if(value>0):
        return str(value)
    return "0" + str(value)


def index(request):
    return render(request, "theapp/index.html")
'''
# Create your views here.
def index(request):
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)
    try:
      atmo = Atmo.objects.get(quand = now)
      print("Get from database: " + str(atmo))
    except Atmo.DoesNotExist:
      print("Loading from the web...")
      whenToday = str(now.year) + "-" + on2(now.month) + "-" + on2(now.day)
      whenTomorrow = str(tomorrow.year) + "-" + on2(tomorrow.month) + "-" + on2(tomorrow.day)
      data = requests.get("https://services8.arcgis.com/rxZzohbySMKHTNcy/ArcGIS/rest/services/ind_hdf_3j/FeatureServer/0/query?where=1%3D1+AND+date_ech+%3C%3D+DATE+%27" + whenTomorrow + "+00%3A00%3A00%27+AND+date_ech+%3E%3D+DATE+%27" + whenToday + "+00%3A00%3A00%27+AND+%28code_zone%3D%2759350%27%29&outFields=code_qual,code_zone,coul_qual,lib_qual,lib_zone,date_ech&orderByFields=date_ech&f=pjson")
      if(data.status_code != 200) :
        atmo = Atmo()
        atmo.quand = now
        atmo.ville = "Lille"
        atmo.code = 0
        atmo.couleur = "#AA0000"
        print("Couldn't get from web: " + str(atmo))
      else:
        theData = json.loads(data.text)
        atmo = Atmo()
        atmo.quand = now
        atmo.ville = theData["features"][0]["attributes"]["lib_zone"]
        atmo.code = theData["features"][0]["attributes"]["code_qual"]
        atmo.couleur = theData["features"][0]["attributes"]["coul_qual"]
        atmo.save()
        print("Get from web: " + str(atmo))
    template = loader.get_template('index.html')
    x = (8 - atmo.code) * 107 + 5
    context = { 'atmo' : atmo, 'x' : x,}
    return HttpResponse(template.render(context, request))
'''

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
    '''
    adi = adimaker.objects.latest

    idd = adi + "(idd)"
    temp = adi + "(temp)"
    hum = adi + "(hum)"
    pres = adi + "(pres)"
    lum = adi + "(lum)"
    bruit = adi + "(bryuit)"



    / order_by day (sans oublier le models) / essayer aved un seul truc genre 'temp' et voir si ca fonctionne pour 1 / ... allez courage
    '''
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


