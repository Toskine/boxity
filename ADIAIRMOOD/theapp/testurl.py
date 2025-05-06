import datetime
import json
import requests

from theapp.models import Atmo

def printDetails(attributes):
    print("Code : " + str(attributes["code_qual"]))
    print("Couleur : " + str(attributes["coul_qual"]))
    print("Ville : " + attributes["lib_zone"])
    theTimestamp = int(str(attributes["date_ech"])[0:10])
    print("Date : " + str(datetime.datetime.fromtimestamp(theTimestamp)))


'''
print(datetime.datetime.now().timestamp())
print(int("1643846400000"[0:10]))
print(datetime.datetime.fromtimestamp(int("1643846400000"[0:10])))
exit()
'''
'''data = requests.get("https://www.lillemetropole.fr/votre-metropole/competences/developpement-durable/qualite-de-lair")
data = requests.get("https://atmo-hdf.fr/index.php?option=com_atmo&view=widgets_indices&tmpl=widgets&communes=59350&auto=true&speed=4000")

data = requests.get("https://services8.arcgis.com/rxZzohbySMKHTNcy/ArcGIS/rest/services/ind_hdf_3j/FeatureServer/0/query?where=1%3D1+AND+date_ech+%3C%3D+DATE+%272022-02-03+00%3A00%3A00%27+AND+date_ech+%3E%3D+DATE+%272022-02-02+00%3A00%3A00%27+AND+%28code_zone%3D%2759350%27%29&outFields=code_qual,code_zone,coul_qual,lib_qual,lib_zone,date_ech&orderByFields=date_ech&f=pjson")
'''
data = requests.get("https://services8.arcgis.com/rxZzohbySMKHTNcy/ArcGIS/rest/services/ind_hdf_3j/FeatureServer/0/query?where=1%3D1+AND+date_ech+%3C%3D+DATE+%272022-02-04+00%3A00%3A00%27+AND+date_ech+%3E%3D+DATE+%272022-02-03+00%3A00%3A00%27+AND+%28code_zone%3D%2759350%27%29&outFields=code_qual,code_zone,coul_qual,lib_qual,lib_zone,date_ech&orderByFields=date_ech&f=pjson")

if(data.status_code != 200) :
    print("Pas bon :(")
    exit()
print("parsing...")

theData = json.loads(data.text)
printDetails(theData["features"][0]["attributes"])

now = datetime.datetime.now()
atmo = Atmo.objects.filter(quand = now)
print(atmo)
print("end")
