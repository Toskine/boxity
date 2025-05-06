from django.db import models
from django.utils import timezone

# Create your models here.

class Atmo(models.Model):
    quand = models.DateField()
    code = models.IntegerField()
    ville = models.CharField(max_length=32)
    couleur = models.CharField(max_length=7)
    def __str__(self):
        return str(self.quand) + " / " + self.ville + " / " + str(self.code)

class Batiment(models.Model):
    batiment_nom = models.CharField(max_length=100)
    def __str__(self):
        return self.batiment_nom

class Lieu(models.Model):
    batiment = models.ForeignKey(Batiment, on_delete=models.CASCADE)
    lieu_nom = models.CharField(max_length=50)
    def __str__(self):
        return self.lieu_nom

class Objet(models.Model):
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE)
    macaddress = models.CharField(max_length=32)
    def __str__(self):
        return self.macaddress

class adimaker(models.Model):
    day = models.DateTimeField(default=timezone.now)
    idd = models.CharField(max_length=100)
    temp = models.IntegerField(default=0.0)
    hum = models.IntegerField(default=0.0)
    pres = models.IntegerField(default=0.0)
    lum = models.IntegerField(default=0.0)
    bruit = models.IntegerField(default=0.0)

    day = str(day)
    def __str__(self):
        return self.day,self.idd,self.temp,self.hum,self.pres,self.lum,self.bruit

