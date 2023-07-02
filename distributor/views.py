import json

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from google.cloud import storage

from .utils import Template, prepare_random_suffix


DEFAULT_CONFIGURATION_TEMPLATE_FILE = 'configuration.yaml.j2'
DEFAULT_GCS_BUCKET = 'uet-app-distributor'
DEFAULT_GCS_CUSTOMER_APPS = 'customer_apps'


def index(request):
    return HttpResponse("This is distributor.")


@csrf_exempt
def distribute(request):
    def generate_config():
        def prepare_template_vars():
            return {
                'project':                  raw_config['project'],
                'description':              raw_config['description'],
                'frontend_image':           raw_config['frontend']['image'],
                'frontend_image_version':   raw_config['frontend']['version'],
                'backend_image':            raw_config['backend']['image'],
                'backend_image_version':    raw_config['backend']['version'],
                'database_image':           raw_config['database']['image']
            }

        template_generator = Template()
        template_vars = prepare_template_vars()
        app_config = template_generator.generate_from_template(DEFAULT_CONFIGURATION_TEMPLATE_FILE, template_vars)
        return app_config

    def upload_to_gcs():
        storage_client = storage.Client()
        bucket = storage_client.bucket(DEFAULT_GCS_BUCKET)
        if bucket.exists():
            blob_name = f"{DEFAULT_GCS_CUSTOMER_APPS}/{prepare_random_suffix(app_config)}"
            blob = bucket.blob(blob_name)
            blob.upload_from_string(app_config, if_generation_match=0)
            print(f"Blob {blob_name} uploaded to {DEFAULT_GCS_BUCKET}.")
        else:
            print(f"Bucket {DEFAULT_GCS_BUCKET}.")

    def trigger_deployment():
        print("Triggering deploy...")
        pass

    raw_config = json.loads(request.body)
    app_config = generate_config()
    upload_to_gcs()
    trigger_deployment()
    return HttpResponse("Succeed")
