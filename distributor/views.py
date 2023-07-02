import os
import json
import requests

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from google.cloud import storage

from .utils import Template, append_random_suffix


DEFAULT_CONFIGURATION_TEMPLATE_FILE = 'configuration.yaml.j2'
DEFAULT_GCS_BUCKET = 'uet-app-distributor'
DEFAULT_GCS_CUSTOMER_APPS = 'customer_apps'
DEFAULT_DEPLOYMENT_REPO = 'platform-job-centre'
DEFAULT_DEPLOYMENT_REPO_OWNER = 'uet-app-distributor'
DEFAULT_DEPLOYMENT_WORKFLOW_FILE = 'application-deployment.yaml'


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
            blob = bucket.blob(app_blob_name)
            blob.upload_from_string(app_config, if_generation_match=0)
            print(f"Blob {app_blob_name} uploaded to {DEFAULT_GCS_BUCKET}.")
        else:
            print(f"Bucket {DEFAULT_GCS_BUCKET}.")

    def trigger_deployment():
        owner = DEFAULT_DEPLOYMENT_REPO_OWNER
        repo = DEFAULT_DEPLOYMENT_REPO
        workflow_file = DEFAULT_DEPLOYMENT_WORKFLOW_FILE
        github_actions_api_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.getenv('GITHUB_ACTIONS_ACCESS_TOKEN')}"
        }
        data = {
            "app_config": app_blob_name
        }
        print(requests.post(github_actions_api_url, data=data, headers=headers).text)

    raw_config = json.loads(request.body)
    app_config = generate_config()
    app_blob_name = f"{DEFAULT_GCS_CUSTOMER_APPS}/{append_random_suffix(raw_config['project'])}"
    upload_to_gcs()
    trigger_deployment()
    return HttpResponse("Succeed")
