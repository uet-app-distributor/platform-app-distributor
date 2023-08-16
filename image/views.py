from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .models import Runtime

import json


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@csrf_exempt
def add_runtime(request):
    config = json.loads(request.body)
    runtime_config = get_runtime_config(config['runtime'])
    runtime_config.save()
    return HttpResponse("Succeed")


def get_runtime_config(config):
    return Runtime(image_name=config['name'],
                   image_version=config['version'])
