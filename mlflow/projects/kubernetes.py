import yaml
import json
import logging
import docker
import os
import time
import kubernetes
from datetime import datetime

_logger = logging.getLogger(__name__)


def push_image_to_registry(image, registry, namespace):
    repository = namespace + '/' + image
    if registry:
        repository = registry + '/' + repository
    client = docker.from_env()
    image = client.images.get(name=image)
    image.tag(repository)
    _logger.info("=== Pushing docker image %s ===", repository)
    client.images.push(repository=repository)


def _get_kubernetes_job_definition(image, image_namespace, job_namespace, command, resources,
                                   env_vars, job_template=None):
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
    job_name = "{}-{}".format(image.replace(':', '-'), timestamp)
    _logger.info("=== Creating Job %s ===", job_name)
    enviroment_variables = ""
    if os.environ.get('AZURE_STORAGE_ACCESS_KEY'):
        env_vars['AZURE_STORAGE_ACCESS_KEY'] = os.environ['AZURE_STORAGE_ACCESS_KEY']
    if os.environ.get('AZURE_STORAGE_CONNECTION_STRING'):
        env_vars['AZURE_STORAGE_CONNECTION_STRING'] = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    for key in env_vars.keys():
        enviroment_variables += "   - name: {name}\n".format(name=key)
        enviroment_variables += "     value: \"{value}\"\n".format(value=env_vars[key])
    enviroment_variables = yaml.load("env:\n" + enviroment_variables)
    if not job_template:
        job_template = (
            "apiVersion: batch/v1\n"
            "kind: Job\n"
            "metadata:\n"
            "  name: 'job_name-timestamp'\n"
            "  namespace: 'job_namespace'\n"
            "spec:\n"
            "  template:\n"
            "    spec:\n"
            "      containers:\n"
            "      - name: 'container_name'\n"
            "        image: 'image_namespace/image_name'\n"
            "        command: 'command'\n"
            "      restartPolicy: Never\n"
            "  backoffLimit: 4\n"
        )
        job_template = yaml.load(job_template)
    job_template['metadata']['name'] = job_name
    job_template['metadata']['namespace'] = job_namespace
    job_template['spec']['template']['spec']['containers'][0]['name'] = image.replace(':', '-')
    job_template['spec']['template']['spec']['containers'][0]['image'] = "{}/{}".format(
                                                                            image_namespace,
                                                                            image)
    job_template['spec']['template']['spec']['containers'][0]['command'] = command
    job_template['spec']['template']['spec']['containers'][0]['env'] = enviroment_variables.get(
                                                                                            'env')
    if resources:
        job_template['spec']['template']['spec']['containers'][0]['resources'] = resources.get(
                                                                                    'resources')
    return job_template


def _get_run_command(parameters):
    command = ['mlflow',  'run', '.', '--no-conda']
    for key, value in parameters.items():
        command.extend(["-P", "%s=%s" % (key, value)])
    return command


def run_kubernetes_job(image, image_namespace, job_namespace, parameters, env_vars,
                       kube_context, job_template=None):
    command = _get_run_command(parameters)
    job_definition = _get_kubernetes_job_definition(image=image, image_namespace=image_namespace,
                                                    job_namespace=job_namespace, command=command,
                                                    resources=None, env_vars=env_vars,
                                                    job_template=job_template)
    job_name = job_definition['metadata']['name']
    kubernetes.config.load_kube_config(context=kube_context)
    api_instance = kubernetes.client.BatchV1Api()
    api_response = api_instance.create_namespaced_job(namespace=job_namespace,
                                                      body=job_definition, pretty=True)
    job_status = api_response.status
    while job_status.start_time is None:
        _logger.info("Waiting for Job to start")
        time.sleep(5)
        api_response = api_instance.read_namespaced_job_status(job_name,
                                                               job_namespace,
                                                               pretty=True)
        job_status = api_response.status
    _logger.info("Job started at %s", job_status.start_time)
    return job_name


def monitor_job_status(job_name, job_namespace):
    api_instance = kubernetes.client.CoreV1Api()
    pods = api_instance.list_namespaced_pod(job_namespace, pretty=True,
                                            label_selector="job-name={0}".format(job_name))
    pod = pods.items[0]
    while pod.status.phase == "Pending":
        _logger.info("Waiting for pod to start")
        time.sleep(5)
        pod = api_instance.read_namespaced_pod_status(pod.metadata.name,
                                                      job_namespace,
                                                      pretty=True)
    _logger.info("Pod running")
    api_instance = kubernetes.client.CoreV1Api()
    for line in api_instance.read_namespaced_pod_log(pod.metadata.name, job_namespace,
                                                     follow=True, _preload_content=False).stream():
        _logger.info(line.rstrip().decode("utf-8"))
