"""
Here it shows the base implementation needed for plugin developers to develop deployment plugins.
Deployment plugin would exposes only three interfaces which is then used by mlflow to serve user
requests.

1. Client class subclassed from :py:class:`BaseDeploymentClient`
2. :py:func:`run_local` for test run the deployment on local system
3. :py:func:`target_help` for displaying the help message about the plugin
"""

import abc


def run_local(target, name, model_uri, flavor=None, config=None):
    """
    Deploys the specified model locally, for testing. This function should be defined
    within the module specified by the plugin author.

    :param target: Which target to use. This information is used to call the appropriate plugin
    :param name:  Unique name to use for deployment. If another deployment exists with the same
                     name, create_deployment will raise a
                     `:py:class:mlflow.exceptions.MlflowException`
    :param model_uri: URI of model to deploy
    :param flavor: (optional) Model flavor to deploy. If unspecified, default flavor is chosen.
    :param config: (optional) Dict containing updated target-specific config for the deployment
    :return: None
    """
    raise NotImplementedError("This function should be implemented in the deployment plugin. It is"
                              "kept here only for documentation purpose and shouldn't be used in"
                              "your application")


def target_help():
    """
    Return a string containing detailed documentation on the current deployment target, to be
    displayed when users invoke the ``mlflow deployments help -t <target-name>`` CLI. This
    method should be defined within the module specified by the plugin author.
    The string should contain:

    * An explanation of target-specific fields in the ``config`` passed to ``create_deployment``,
      ``update_deployment``
    * How to specify a ``target_uri`` (e.g. for AWS SageMaker, ``target_uri`` have a scheme of
      "sagemaker://<aws-cli-profile-name>", where aws-cli-profile-name is the name of an AWS
      CLI profile https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html)
    * Any other target-specific details.

    """
    raise NotImplementedError("This function should be implemented in the deployment plugin. It is"
                              "kept here only for documentation purpose and shouldn't be used in"
                              "your application")


class BaseDeploymentClient(abc.ABC):
    """
    Base class exposing Python model deployment APIs. Plugin implementors should define
    target-specific deployment logic via a subclass of ``BaseDeploymentClient`` within the
    plugin module, and customize the method docstrings

    .. Note::
        In case of exceptions, plugins must raise an ``MlflowException`` instead of native
        python exceptions

    .. Note::
        The plugin should only have one child class of
        :py:class:`BaseDeploymentClient` else it throws.
    """

    def __init__(self, target_uri):
        self.target_uri = target_uri

    @abc.abstractmethod
    def create_deployment(self, name, model_uri, flavor=None, config=None):
        """
        Deploy a model to the specified target. By default, this method should block until
        deployment completes (i.e. until it's possible to perform inference with the deployment).
        In the case of conflicts (e.g. if it's not possible to create the specified deployment
        without due to conflict with an existing deployment), raises a
        `:py:class:mlflow.exceptions.MlflowException`. See target-specific plugin documentation
        for additional detail on support for asynchronous deployment and other configuration.

        :param name: Unique name to use for deployment. If another deployment exists with the same
                     name, create_deployment will raise a
                     `:py:class:mlflow.exceptions.MlflowException`
        :param model_uri: URI of model to deploy
        :param flavor: (optional) Model flavor to deploy. If unspecified, a default flavor
                       will be chosen.
        :param config: (optional) Dict containing updated target-specific configuration for the
                       deployment
        :return: Dict corresponding to created deployment, which must contain the 'name' key.
        """
        pass

    @abc.abstractmethod
    def update_deployment(self, name, model_uri=None, flavor=None, config=None):
        """
        Update the deployment with the specified name. You can update the URI of the model, the
        flavor of the deployed model (in which case the model URI must also be specified), and/or
        any target-specific attributes of the deployment (via `config`). By default, this method
        should block until deployment completes (i.e. until it's possible to perform inference
        with the updated deployment). See target-specific plugin documentation for additional
        detail on support for asynchronous deployment and other configuration.

        :param name: Unique name of deployment to update
        :param model_uri: URI of a new model to deploy.
        :param flavor: (optional) new model flavor to use for deployment. If provided,
                       `model_uri` must also be specified. If `flavor` is unspecified but
                       `model_uri` is specified, a default flavor will be chosen and the
                       deployment will be updated using that flavor.
        :param config: (optional) dict containing updated target-specific configuration for the
                       deployment
        :return: None
        """
        pass

    @abc.abstractmethod
    def delete_deployment(self, name):
        """
        Delete the deployment with name `name` from the specified target. Deletion should be
        idempotent (i.e. deletion should not fail if retried on a non-existent deployment).

        :param name: Name of deployment to delete
        :return: None
        """
        pass

    @abc.abstractmethod
    def list_deployments(self):
        """
        List deployments. This method is expected to return an unpaginated list of all
        deployments (an alternative would be to return a dict with a 'deployments' field
        containing the actual deployments, with plugins able to specify other fields, e.g.
        a next_page_token field, in the returned dictionary for pagination, and to accept
        a `pagination_args` argument to this method for passing pagination-related args).

        :return: A list of dicts corresponding to deployments. Each dict is guaranteed to
                 contain a 'name' key containing the deployment name. The other fields of
                 the returned dictionary and their types may vary across deployment targets.
        """
        pass

    @abc.abstractmethod
    def get_deployment(self, name):
        """
        Returns a dictionary describing the specified deployment, throwing a
        `py:class:mlflow.exception.MlflowException` if no deployment exists with the provided
        ID.
        The dict is guaranteed to contain an 'name' key containing the deployment name.
        The other fields of the returned dictionary and their types may vary across
        deployment targets.

        :param name: ID of deployment to fetch
        """
        pass

    @abc.abstractmethod
    def predict(self, deployment_name, df):
        """
        Compute predictions on the pandas DataFrame ``df`` using the specified deployment.
        Note that the input/output types of this method matches that of `mlflow pyfunc predict`
        (we accept a pandas DataFrame as input and return either a pandas DataFrame,
        pandas Series, or numpy array as output).

        :param deployment_name: Name of deployment to predict against
        :param df: Pandas DataFrame to use for inference
        :return: A pandas DataFrame, pandas Series, or numpy array
        """
        pass
