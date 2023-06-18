from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .utils import Template

import json
import base64


DEFAULT_CONFIGURATION_TEMPLATE_FILE = 'configuration.yaml.j2'


def index(request):
    return HttpResponse("This is distributor.")


def generate_configration_file(config):
    def prepare_template_vars():
        return {
            'project':                  config['project'],
            'description':              config['description'],
            'frontend_image':           config['frontend']['image'],
            'frontend_image_version':   config['frontend']['version'],
            'backend_image':            config['backend']['image'],
            'backend_image_version':    config['backend']['version'],
            'database_image':           config['database']['image']
        }

    def prepare_output_filename():
        project = config['project']
        project_encode = base64.b64encode(project.encode('ascii'))
        return f'{project}_{project_encode.decode("ascii")[:8]}'

    template_generator = Template()
    template_vars = prepare_template_vars()
    config_filename = prepare_output_filename()
    print(config_filename)
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
