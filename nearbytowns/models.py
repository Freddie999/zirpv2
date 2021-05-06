from django.contrib.gis.db import models


# Create your models here.

class Town(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField()
    comm_champ = models.CharField(max_length=100)
    comm_champ_number = models.CharField(max_length=50)

class Search(models.Model):
    address = models.CharField(max_length=200, null=True)
    date = models.DateTimeField(auto_now_add=True)
    #town =  models.ForeignKey(Town, null=True)

    def __str__(self):
        return self.address

