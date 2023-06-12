from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import json


def index(request):
    return HttpResponse("This is distributor.")


def generate_configration_file():
    pass


def upload():
    pass


def trigger_deployment():
    pass


@csrf_exempt
def distribute(request):
    # Generate configuration file
    generate_configration_file()

    # Upload generated file to Cloud Storage
    upload()

    # Trigger Github Actions deployment workflow
    trigger_deployment()

    return HttpResponse("Succeed")
