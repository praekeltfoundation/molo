from django.db import models


# Create your models here.
class App1Model(models.Model):
    name = models.CharField(max_length=255)
    gender = models.CharField(default='unknown', max_length=255)
