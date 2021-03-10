from django.db import models

# Create your models here.

class imagen(models.Model):
    imagen = models.ImageField(upload_to="imagenes")
