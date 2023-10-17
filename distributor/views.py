import json

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from distributor.utils import (
    CustomerAppInfo,
    DeploymentManager,
)


def index(request):
    return HttpResponse("This is distributor.")


@csrf_exempt
def distribute(request):
    # Initialize necessary configurations
    raw_config = json.loads(request.body)

    app_info = CustomerAppInfo(raw_config)
    deployer = DeploymentManager(app_info)

    # Trigger deployment workflow
    deployer.deploy()

    return HttpResponse("Succeed")
