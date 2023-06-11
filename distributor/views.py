from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import json


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@csrf_exempt
def generate_app_configuration(request):
    body = json.loads(request.body)
    print(body)
    return HttpResponse("Printing request body")
