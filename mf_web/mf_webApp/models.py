from django.db import models

# Create your models here.


class Patient(models.Model):
    patient = models.CharField(max_length=50)
    study_desc = models.CharField(max_length=50)
    series_desc = models.CharField(max_length=50)
    series_id = models.CharField(max_length=50)

class Curves(models.Model):
    id_patient = models.ForeignKey(Patient)
    area_rest = models.FloatField()
    peak_rest = models.FloatField()
    slope_rest = models.FloatField()
    area_stress = models.FloatField()
    peak_stress = models.FloatField()
    slope_stress = models.FloatField()
    coefficent = models.FloatField()

