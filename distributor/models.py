from django.db import models


class App(models.Model):
    image_name = models.CharField(max_length=200)
    image_version = models.CharField(max_length=200)
    environment_vars = models.JSONField(null=True)

    def __str__(self):
        return f'App Image: {self.image_name}:{self.image_version}'


class Database(models.Model):
    image_name = models.CharField(max_length=200)
    image_version = models.CharField(max_length=200)
    environment_vars = models.JSONField(null=True)

    def __str__(self):
        return f'Database Image: {self.image_name}:{self.image_version}'
