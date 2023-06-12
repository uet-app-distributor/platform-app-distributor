from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .models import App, Database

import json


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@csrf_exempt
def add_configuration(request):
    config = json.loads(request.body)
    app_config = get_app_config(config['appSpec'])
    app_config.save()
    database_config = get_database_config(config['databaseSpec'])
    database_config.save()
    return HttpResponse("Configuration is added successfully.")


def get_app_config(config):
    return App(image_name=config['image'],
               image_version=config['version'],
               environment_vars=config['env'])


def get_database_config(config):
    return Database(image_name=config['image'],
                    image_version=config['version'],
                    environment_vars=config['env'])
