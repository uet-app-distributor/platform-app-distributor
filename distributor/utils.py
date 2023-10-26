import os
import json
import base64
import string
import random
import requests

from logger import logger
from google.cloud import storage
from jinja2 import Environment, FileSystemLoader, select_autoescape

from settings import (
    APP_CONFIG_TEMPLATE,
    CLOUD_CONFIG_TEMPLATE,
    DISTRIBUTOR_GCS_BUCKET,
    CUSTOMER_APPS_GCS_FOLDER,
    CUSTOMER_MANAGED_DEPLOY_WORKFLOW,
    DEPLOYMENT_REPO,
    DEPLOYMENT_REPO_OWNER,
    DEPLOYMENT_WORKFLOW_FILE,
)


DEFAULT_TEMPLATE_DIR = "distributor/templates"


def append_random_suffix(content):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(8))
    return f"{content}_{random_string}"


class TemplateGenerator:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(DEFAULT_TEMPLATE_DIR),
            autoescape=select_autoescape(),
        )

    def generate_from_template(self, template, template_vars):
        template = self.env.get_template(template)
        output = template.render(template_vars)
        return output


class CustomerAppInfo:
    def __init__(self, raw_config):
        self.raw_config = raw_config
        self.customer_name = raw_config["app_owner"]
        self.customer_app = raw_config["app_name"]
        self.enabled_frontend = raw_config["enabled_frontend"]
        self.enabled_backend = raw_config["enabled_backend"]
        self.enabled_database = raw_config["enabled_database"]
        self.customer_managed = raw_config["customer_managed"]

        try:
            if self.enabled_frontend:
                frontend_config = raw_config["frontend"]
                self.fe_github_user = frontend_config["github_user"]
                self.fe_github_repo = frontend_config["github_repo"]
                self.fe_build_image = frontend_config["image"]
                self.fe_build_image_version = frontend_config["version"]
                self.fe_build_dir = frontend_config["static_dir"]
                self.fe_build_env = frontend_config["env"]

            if self.enabled_backend:
                backend_config = raw_config["backend"]
                self.be_github_user = backend_config["github_user"]
                self.be_github_repo = backend_config["github_repo"]
                self.be_runtime = backend_config["image"]
                self.be_runtime_version = backend_config["version"]

            if self.enabled_database:
                self.db_image = raw_config["database"]["image"]

            if self.customer_managed:
                cloud_config = raw_config["cloud_config"]
                self.cloud_provider = cloud_config["provider"]

                if self.cloud_provider == "aws":
                    self.aws_access_key_id = cloud_config["aws_access_key_id"]
                    self.aws_secret_access_key = cloud_config["aws_secret_access_key"]

        except Exception as error:
            logger.info("Invalid customer app configurations.")
            logger.error(error)

    def contain(self, key):
        return key in self.raw_config


class DeploymentManager:
    def __init__(self, app_info):
        self.app_info = app_info
        self.app_blob = f"{CUSTOMER_APPS_GCS_FOLDER}/{app_info.customer_name}/{app_info.customer_app}"
        self.cloud_blob = f"{CUSTOMER_APPS_GCS_FOLDER}/{app_info.customer_name}/{app_info.customer_app}-tfvars.env"
        self.default_headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.getenv('GITHUB_ACTIONS_ACCESS_TOKEN')}",
        }

    def _extract_environment_vars(self, raw_env):
        result_env = {}
        lines = raw_env.strip().split("\n")

        for line in lines:
            key, value = line.split("=")
            result_env[key] = value

        return result_env

    def _prepare_template_vars(self, config_template):
        if config_template == APP_CONFIG_TEMPLATE:
            template_vars = {
                "app_name": self.app_info.customer_app,
                "app_owner": self.app_info.customer_name,
                "enabled_frontend": self.app_info.enabled_frontend,
                "enabled_backend": self.app_info.enabled_backend,
                "enabled_database": self.app_info.enabled_database,
            }

            if template_vars["enabled_frontend"]:
                frontend_config = {
                    "frontend_image": self.app_info.fe_build_image,
                    "frontend_image_version": self.app_info.fe_build_image_version,
                    "frontend_static_dir": self.app_info.fe_build_dir,
                    "frontend_env_vars": self._extract_environment_vars(
                        self.app_info.fe_build_env
                    )
                    if self.app_info.fe_build_env
                    else "",
                }
                template_vars.update(frontend_config)

            if template_vars["enabled_backend"]:
                backend_config = {
                    "backend_image": self.app_info.be_runtime,
                    "backend_image_version": self.app_info.be_runtime_version,
                }
                template_vars.update(backend_config)

            if template_vars["enabled_database"]:
                template_vars["database_image"] = self.app_info.db_image

        elif config_template == CLOUD_CONFIG_TEMPLATE:
            template_vars = {
                "aws_access_key_id": self.app_info.aws_access_key_id,
                "aws_secret_access_key": self.app_info.aws_secret_access_key,
            }

        return template_vars

    def _generate_config(self, config_template):
        generator = TemplateGenerator()
        template_vars = self._prepare_template_vars(config_template)
        config = generator.generate_from_template(config_template, template_vars)
        return config

    def _prepare_workflow_id(self):
        return (
            CUSTOMER_MANAGED_DEPLOY_WORKFLOW
            if self.app_info.customer_managed
            else DEPLOYMENT_WORKFLOW_FILE
        )

    def _prepare_backend_inputs(self):
        backend_inputs = {
            "be_github_user": "none",
            "be_github_repo": "none",
        }

        if self.app_info.enabled_backend:
            backend_inputs = {
                "be_github_user": self.app_info.be_github_user,
                "be_github_repo": self.app_info.be_github_repo,
            }

        return backend_inputs

    def _prepare_frontend_inputs(self):
        frontend_inputs = {
            "fe_github_user": "none",
            "fe_github_repo": "none",
        }

        if self.app_info.enabled_frontend:
            frontend_inputs = {
                "fe_github_user": self.app_info.fe_github_user,
                "fe_github_repo": self.app_info.fe_github_repo,
            }

        return frontend_inputs

    def _prepare_customer_managed_infra_inputs(self):
        return {
            "customer_name": self.app_info.customer_name,
            "customer_provider": self.app_info.cloud_provider,
            "customer_credential_file": f"gs://{DISTRIBUTOR_GCS_BUCKET}/{self.cloud_blob}",
        }

    def _upload_app_config(self, app_config):
        storage_client = storage.Client()
        bucket = storage_client.bucket(DISTRIBUTOR_GCS_BUCKET)

        if bucket.exists():
            blob = bucket.blob(self.app_blob)
            blob.upload_from_string(app_config)

            logger.info(f"Found Distributor bucket: {DISTRIBUTOR_GCS_BUCKET}")
            logger.info(f"Uploaded blob {self.app_blob} to Distributor bucket.")

            if self.app_info.enabled_frontend:
                if self.app_info.fe_build_env:
                    blob = bucket.blob(f"{self.app_blob}.env")
                    blob.upload_from_string(self.app_info.fe_build_env)
                    logger.info(f"Uploaded env blob to Distributor bucket.")
        else:
            logger.info(f"Bucket {DISTRIBUTOR_GCS_BUCKET} does not exist.")

    def _upload_cloud_config(self, cloud_config):
        storage_client = storage.Client()
        bucket = storage_client.bucket(DISTRIBUTOR_GCS_BUCKET)

        if bucket.exists():
            blob = bucket.blob(self.cloud_blob)
            blob.upload_from_string(cloud_config)

            logger.info(f"Found Distributor bucket: {DISTRIBUTOR_GCS_BUCKET}")
            logger.info(f"Uploaded blob {self.cloud_blob} to Distributor bucket.")
        else:
            logger.info(f"Bucket {DISTRIBUTOR_GCS_BUCKET} does not exist.")

    def _trigger_deployment_workflow(self):
        # Prepare workflow URL
        workflow_id = self._prepare_workflow_id()
        workflow_url = f"https://api.github.com/repos/{DEPLOYMENT_REPO_OWNER}/{DEPLOYMENT_REPO}/actions/workflows/{workflow_id}/dispatches"

        # Prepare workflow inputs
        inputs = {
            "customer_app_blob": f"gs://{DISTRIBUTOR_GCS_BUCKET}/{self.app_blob}",
            "customer_app_name": self.app_info.customer_app,
            "customer_name": self.app_info.customer_name,
        }

        frontend_inputs = self._prepare_frontend_inputs()
        backend_inputs = self._prepare_backend_inputs()

        inputs.update(frontend_inputs)
        inputs.update(backend_inputs)

        if self.app_info.customer_managed:
            cloud_infra_inputs = self._prepare_customer_managed_infra_inputs()
            inputs.update(cloud_infra_inputs)

        data = {"ref": "main", "inputs": inputs}

        logger.info(data)

        # Trigger deployment
        try:
            response = requests.post(
                workflow_url, data=json.dumps(data), headers=self.default_headers
            )

            logger.info(response.text)

        except Exception as error:
            logger.error(error)

    def deploy(self):
        # Generate and upload app config YAML file
        app_config = self._generate_config(APP_CONFIG_TEMPLATE)
        self._upload_app_config(app_config)

        # Generate and upload cloud config tfvars file
        if self.app_info.customer_managed:
            cloud_config = self._generate_config(CLOUD_CONFIG_TEMPLATE)
            self._upload_cloud_config(cloud_config)

        # Deploy
        self._trigger_deployment_workflow()
