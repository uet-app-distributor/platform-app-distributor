from django.db import models


class Runtime(models.Model):
    image_name = models.CharField(max_length=200)
    image_version = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.image_name}:{self.image_version}'
