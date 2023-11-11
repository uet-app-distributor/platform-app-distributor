APP_CONFIG_TEMPLATE = "configuration.yaml.j2"
CLOUD_CONFIG_TEMPLATE = "cloud-configurations.tfvars.j2"

DISTRIBUTOR_GCS_BUCKET = "uet-app-distributor"
CUSTOMER_APPS_GCS_FOLDER = "customer_apps"

DEPLOYMENT_REPO = "platform-job-centre"
DEPLOYMENT_REPO_OWNER = "uet-app-distributor"
DEPLOYMENT_WORKFLOW_FILE = "deploy-customer-app.yaml"

CUSTOMER_MANAGED_DEPLOY_WORKFLOW_AWS = "deploy-customer-app-dedicated-infra.yaml"
CUSTOMER_MANAGED_DEPLOY_WORKFLOW_GCP = "deploy-customer-app-dedicated-infra-gcp.yaml"

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
