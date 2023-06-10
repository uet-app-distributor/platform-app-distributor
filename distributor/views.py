from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def generate_app_configuration(request):
    print(request.body)
    return HttpResponse("Printing request body")
