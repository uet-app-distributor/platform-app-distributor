from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .models import App

import json


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@csrf_exempt
def generate_configuration(request):
    config = json.loads(request.body)
    app_config = App(image_name=config['appSpec']['image'],
                     image_version=config['appSpec']['version'],
                     environment_vars=config['appSpec']['env'])
    app_config.save()
    return HttpResponse("Printing request body")
