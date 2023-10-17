import os
import json
import requests

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from google.cloud import storage

from logger import logger
from distributor.utils import (
    Template,
    CustomerAppInfo,
    DeploymentManager,
    append_random_suffix,
)
from settings import (
    APP_CONFIG_TEMPLATE,
    DISTRIBUTOR_GCS_BUCKET,
    CUSTOMER_APPS_GCS_FOLDER,
    CUSTOMER_MANAGED_DEPLOY_WORKFLOW,
    DEPLOYMENT_REPO,
    DEPLOYMENT_REPO_OWNER,
    DEPLOYMENT_WORKFLOW_FILE,
)


def index(request):
    return HttpResponse("This is distributor.")


@csrf_exempt
def distribute(request):
    def extract_environment_vars(raw_env):
        result_env = {}
        lines = raw_env.strip().split("\n")
        for line in lines:
            key, value = line.split("=")
            result_env[key] = value
        return result_env

    def prepare_template_vars():
        template_vars = {
            "app_name": raw_config["app_name"],
            "app_owner": raw_config["app_owner"],
            "enabled_frontend": raw_config["enabled_frontend"],
            "enabled_backend": raw_config["enabled_backend"],
            "enabled_database": raw_config["enabled_database"],
        }

        if template_vars["enabled_frontend"]:
            template_vars.update(
                {
                    "frontend_image": raw_config["frontend"]["image"],
                    "frontend_image_version": raw_config["frontend"]["version"],
                    "frontend_static_dir": raw_config["frontend"]["static_dir"],
                    "frontend_env_vars": extract_environment_vars(
                        raw_config["frontend"]["env"]
                    )
                    if raw_config["frontend"]["env"]
                    else "",
                }
            )

        if template_vars["enabled_backend"]:
            template_vars.update(
                {
                    "backend_image": raw_config["backend"]["image"],
                    "backend_image_version": raw_config["backend"]["version"],
                }
            )

        if template_vars["enabled_database"]:
            template_vars["database_image"] = raw_config["database"]["image"]

        return template_vars

    raw_config = json.loads(request.body)
    app_info = CustomerAppInfo(raw_config)
    deployer = DeploymentManager(app_info)

    app_blob = deployer.app_blob

    app_config = deployer.generate_app_config()
    deployer.upload_app_config()
    deployer.trigger_deployment_workflow()

    return HttpResponse("Succeed")
