import os
import json
import requests

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from google.cloud import storage

from logger import logger
from distributor.utils import Template, append_random_suffix
from settings import (
    APP_CONFIG_TEMPLATE,
    DISTRIBUTOR_GCS_BUCKET,
    CUSTOMER_APPS_GCS_FOLDER,
    DEPLOYMENT_REPO,
    DEPLOYMENT_REPO_OWNER,
    DEPLOYMENT_WORKFLOW_FILE
)


def index(request):
    return HttpResponse("This is distributor.")


@csrf_exempt
def distribute(request):

    def extract_environment_vars(raw_env):
        result_env = {}
        lines = raw_env.strip().split('\n')
        for line in lines:
            key, value = line.split('=')
            result_env[key] = value
        return result_env

    def prepare_template_vars():
        template_vars = {
            'app_name': raw_config['app_name'],
            'app_owner': raw_config['app_owner'],
            'enabled_frontend': raw_config['enabled_frontend'],
            'enabled_backend': raw_config['enabled_backend'],
            'enabled_database': raw_config['enabled_database'],
        }

        if template_vars['enabled_frontend']:
            template_vars.update({
                'frontend_image': raw_config['frontend']['image'],
                'frontend_image_version': raw_config['frontend']['version'],
                'frontend_static_dir': raw_config['frontend']['static_dir'],
                'frontend_env_vars': extract_environment_vars(raw_config['frontend']['env']) if raw_config['frontend']['env'] else ""
            })

        if template_vars['enabled_backend']:
            template_vars.update({
                'backend_image': raw_config['backend']['image'],
                'backend_image_version': raw_config['backend']['version']
            })

        if template_vars['enabled_database']:
            template_vars['database_image'] = raw_config['database']['image']

        return template_vars

    def generate_config():
        template_generator = Template()
        template_vars = prepare_template_vars()
        app_config = template_generator.generate_from_template(APP_CONFIG_TEMPLATE, template_vars)
        return app_config

    def upload_app_config():
        storage_client = storage.Client()
        bucket = storage_client.bucket(DISTRIBUTOR_GCS_BUCKET)
        if bucket.exists():
            blob = bucket.blob(app_blob_name)
            blob.upload_from_string(app_config)
            logger.info(f"Blob {app_blob_name} uploaded to bucket {DISTRIBUTOR_GCS_BUCKET}.")

            if "frontend" in raw_config:
                if raw_config['frontend']['env']:
                    blob = bucket.blob(f"{app_blob_name}.env")
                    blob.upload_from_string(raw_config['frontend']['env'])
                    logger.info(f"Env blob {app_blob_name}.env uploaded to bucket {DISTRIBUTOR_GCS_BUCKET}.")
        else:
            logger.info(f"Bucket {DISTRIBUTOR_GCS_BUCKET} does not exist.")

    def trigger_deployment():
        deployment_workflow_url = f"https://api.github.com/repos/{DEPLOYMENT_REPO_OWNER}/{DEPLOYMENT_REPO}/actions/workflows/{DEPLOYMENT_WORKFLOW_FILE}/dispatches"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.getenv('GITHUB_ACTIONS_ACCESS_TOKEN')}"
        }
        data = {
            "ref": "main",
            "inputs": {
                "customer_app_blob": f"gs://{DISTRIBUTOR_GCS_BUCKET}/{app_blob_name}",
                "customer_app_name": raw_config["app_name"],
                "be_github_user": raw_config["backend"]["github_user"] if raw_config['enabled_backend'] else "none",
                "be_github_repo": raw_config["backend"]["github_repo"] if raw_config['enabled_backend'] else "none",
                "fe_github_user": raw_config["frontend"]["github_user"] if raw_config['enabled_frontend'] else "none",
                "fe_github_repo": raw_config["frontend"]["github_repo"] if raw_config['enabled_frontend'] else "none",
            }
        }
        logger.info(data)
        response = requests.post(deployment_workflow_url, data=json.dumps(data), headers=headers)
        logger.info(response.text)

    raw_config = json.loads(request.body)
    app_blob_name = f"{CUSTOMER_APPS_GCS_FOLDER}/{raw_config['app_owner']}/{raw_config['app_name']}"
    app_config = generate_config()
    upload_app_config()
    trigger_deployment()
    return HttpResponse("Succeed")
