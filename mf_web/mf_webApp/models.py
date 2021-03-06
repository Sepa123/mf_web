from django.db import models

# Create your models here.

class Patient(models.Model):
    patient = models.CharField(max_length=50)
    study_desc = models.CharField(max_length=50)
    series_desc = models.CharField(max_length=50)
    series_id = models.CharField(max_length=50)
    
class Curve(models.Model):
    id_patient = models.ForeignKey('Patient',on_delete=models.CASCADE)
    zone = models.CharField(max_length=12)
    area_rest = models.FloatField()
    peak_rest = models.FloatField()
    slope_rest = models.FloatField()
    area_stress = models.FloatField()
    peak_stress = models.FloatField()
    slope_stress = models.FloatField()
    coefficent = models.FloatField()

class CurveDivide(models.Model):
    id_patient = models.ForeignKey('Patient',on_delete=models.CASCADE)
    zone = models.CharField(max_length=12)
    partition = models.IntegerField()
    area_rest = models.FloatField()
    peak_rest = models.FloatField()
    slope_rest = models.FloatField()
    area_stress = models.FloatField()
    peak_stress = models.FloatField()
    slope_stress = models.FloatField()
    coefficent = models.FloatField()


