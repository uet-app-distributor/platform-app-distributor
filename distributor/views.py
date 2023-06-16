from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .utils import Template

import json
import hashlib


DEFAULT_CONFIGURATION_TEMPLATE_FILE = 'configuration.yaml.j2'


def index(request):
    return HttpResponse("This is distributor.")


def generate_configration_file(config):
    def prepare_template_vars():
        return {
            'frontend_image': config['frontend']['image'],
            'frontend_version': config['frontend']['version'],
            'backend_image': config['backend']['image'],
            'backend_version': config['backend']['version'],
            'database_image': config['database']['image']
        }

    def prepare_output_filename():
        return hashlib.md5(config['project'].encode())

    template_generator = Template()
    template_vars = prepare_template_vars()
    config_filename = prepare_output_filename()
    template_generator.generate_from_template(DEFAULT_CONFIGURATION_TEMPLATE_FILE,
                                              template_vars,
                                              config_filename)
    return config_filename


def upload():
    pass


def trigger_deployment():
    pass


@csrf_exempt
def distribute(request):
    app_config = json.loads(request.body)

    # Generate configuration file
    config_file = generate_configration_file(app_config)

    # Upload generated file to Cloud Storage
    # upload(config_file)
    print(config_file)

    # Trigger Github Actions deployment workflow
    trigger_deployment()

    return HttpResponse("Succeed")
