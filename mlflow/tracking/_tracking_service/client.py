"""
Internal package providing a Python CRUD interface to MLflow experiments and runs.
This is a lower level API than the :py:mod:`mlflow.tracking.fluent` module, and is
exposed in the :py:mod:`mlflow.tracking` module.
"""

import os
from collections import OrderedDict
from itertools import zip_longest
from typing import List, Optional

from mlflow.entities import (
    ExperimentTag,
    Metric,
    Param,
    RunStatus,
    RunTag,
    TraceRequestMetadata,
    TraceStatus,
    TraceTag,
    ViewType,
)
from mlflow.entities.dataset_input import DatasetInput
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import INVALID_PARAMETER_VALUE, ErrorCode
from mlflow.store.artifact.artifact_repository_registry import get_artifact_repository
from mlflow.store.tracking import GET_METRIC_HISTORY_MAX_RESULTS, SEARCH_MAX_RESULTS_DEFAULT
from mlflow.tracking._tracking_service import utils
from mlflow.tracking.metric_value_conversion_utils import convert_metric_value_to_float_if_possible
from mlflow.utils import chunk_list
from mlflow.utils.async_logging.run_operations import RunOperations, get_combined_run_operations
from mlflow.utils.mlflow_tags import MLFLOW_USER
from mlflow.utils.string_utils import is_string_type
from mlflow.utils.time import get_current_time_millis
from mlflow.utils.uri import add_databricks_profile_info_to_artifact_uri
from mlflow.utils.validation import (
    MAX_ENTITIES_PER_BATCH,
    MAX_METRICS_PER_BATCH,
    MAX_PARAMS_TAGS_PER_BATCH,
    PARAM_VALIDATION_MSG,
    _validate_experiment_artifact_location,
    _validate_run_id,
)


class TrackingServiceClient:
    """
    Client of an MLflow Tracking Server that creates and manages experiments and runs.
    """

    _artifact_repos_cache = OrderedDict()

    def __init__(self, tracking_uri):
        """
        Args:
            tracking_uri: Address of local or remote tracking server.
        """
        self.tracking_uri = tracking_uri
        # NB: Fetch the tracking store (`self.store`) upon client initialization to ensure that
        # the tracking URI is valid and the store can be properly resolved. We define `store` as a
        # property method to ensure that the client is serializable, even if the store is not
        # self.store
        self.store

    @property
    def store(self):
        return utils._get_store(self.tracking_uri)

    def get_run(self, run_id):
        """Fetch the run from backend store. The resulting :py:class:`Run <mlflow.entities.Run>`
        contains a collection of run metadata -- :py:class:`RunInfo <mlflow.entities.RunInfo>`,
        as well as a collection of run parameters, tags, and metrics --
        :py:class:`RunData <mlflow.entities.RunData>`. In the case where multiple metrics with the
        same key are logged for the run, the :py:class:`RunData <mlflow.entities.RunData>` contains
        the most recently logged value at the largest step for each metric.

        Args:
            run_id: Unique identifier for the run.

        Returns:
            A single :py:class:`mlflow.entities.Run` object, if the run exists. Otherwise,
            raises an exception.

        """
        _validate_run_id(run_id)
        return self.store.get_run(run_id)

    def get_metric_history(self, run_id, key):
        """Return a list of metric objects corresponding to all values logged for a given metric.

        Args:
            run_id: Unique identifier for run.
            key: Metric name within the run.

        Returns:
            A list of :py:class:`mlflow.entities.Metric` entities if logged, else empty list.
        """

        # NB: Paginated query support is currently only available for the RestStore backend.
        # FileStore and SQLAlchemy store do not provide support for paginated queries and will
        # raise an MlflowException if the `page_token` argument is not None when calling this
        # API for a continuation query.
        history = self.store.get_metric_history(
            run_id=run_id,
            metric_key=key,
            max_results=GET_METRIC_HISTORY_MAX_RESULTS,
            page_token=None,
        )
        token = history.token
        # Continue issuing queries to the backend store to retrieve all pages of
        # metric history.
        while token is not None:
            paged_history = self.store.get_metric_history(
                run_id=run_id,
                metric_key=key,
                max_results=GET_METRIC_HISTORY_MAX_RESULTS,
                page_token=token,
            )
            history.extend(paged_history)
            token = paged_history.token
        return history

    def create_run(self, experiment_id, start_time=None, tags=None, run_name=None):
        """Create a :py:class:`mlflow.entities.Run` object that can be associated with
        metrics, parameters, artifacts, etc.
        Unlike :py:func:`mlflow.projects.run`, creates objects but does not run code.
        Unlike :py:func:`mlflow.start_run`, does not change the "active run" used by
        :py:func:`mlflow.log_param`.

        Args:
            experiment_id: The ID of the experiment to create a run in.
            start_time: If not provided, use the current timestamp.
            tags: A dictionary of key-value pairs that are converted into
                :py:class:`mlflow.entities.RunTag` objects.
            run_name: The name of this run.

        Returns:
            :py:class:`mlflow.entities.Run` that was created.

        """

        tags = tags if tags else {}

        # Extract user from tags
        # This logic is temporary; the user_id attribute of runs is deprecated and will be removed
        # in a later release.
        user_id = tags.get(MLFLOW_USER, "unknown")

        return self.store.create_run(
            experiment_id=experiment_id,
            user_id=user_id,
            start_time=start_time or get_current_time_millis(),
            tags=[RunTag(key, value) for (key, value) in tags.items()],
            run_name=run_name,
        )

    def create_trace(
        self,
        experiment_id,
        timestamp_ms,
        execution_time_ms,
        status,
        request_metadata=None,
        tags=None,
    ):
        """Create a trace object and log in the backend store.

        Args:
            experiment_id: String id of the experiment for this run.
            timestamp_ms: int, start time of the trace, in milliseconds.
            execution_time_ms: int, duration of the trace, in milliseconds.
            status: string, status of the trace.
            request_metadata: dict, metadata of the trace.
            tags: dict, tags of the trace.

        Returns:
            The created Trace object.
        """
        request_metadata = request_metadata or {}
        tags = tags or {}

        return self.store.create_trace(
            experiment_id=experiment_id,
            timestamp_ms=timestamp_ms,
            execution_time_ms=execution_time_ms,
            status=TraceStatus.from_string(status),
            request_metadata=[
                TraceRequestMetadata(key, value) for (key, value) in request_metadata.items()
            ],
            tags=[TraceTag(key, value) for (key, value) in tags.items()],
        )

    def get_trace_info(self, request_id):
        """
        Get the trace matching the `request_id`.

        Args:
            request_id: String id of the trace to fetch.

        Returns:
            The fetched Trace object, of type ``mlflow.entities.TraceInfo``.
        """
        return self.store.get_trace_info(request_id)

    def search_experiments(
        self,
        view_type=ViewType.ACTIVE_ONLY,
        max_results=SEARCH_MAX_RESULTS_DEFAULT,
        filter_string=None,
        order_by=None,
        page_token=None,
    ):
        """Search for experiments that match the specified search query.

        Args:
            view_type: One of enum values ``ACTIVE_ONLY``, ``DELETED_ONLY``, or ``ALL``
                defined in :py:class:`mlflow.entities.ViewType`.
            max_results: Maximum number of experiments desired. Certain server backend may apply
                its own limit.
            filter_string: Filter query string (e.g., ``"name = 'my_experiment'"``), defaults to
                searching for all experiments. The following identifiers, comparators, and logical
                operators are supported.

                Identifiers
                  - ``name``: Experiment name
                  - ``creation_time``: Experiment creation time
                  - ``last_update_time``: Experiment last update time
                  - ``tags.<tag_key>``: Experiment tag. If ``tag_key`` contains
                    spaces, it must be wrapped with backticks (e.g., ``"tags.`extra key`"``).

                Comparators for string attributes and tags
                  - ``=``: Equal to
                  - ``!=``: Not equal to
                  - ``LIKE``: Case-sensitive pattern match
                  - ``ILIKE``: Case-insensitive pattern match

                Comparators for numeric attributes
                  - ``=``: Equal to
                  - ``!=``: Not equal to
                  - ``<``: Less than
                  - ``<=``: Less than or equal to
                  - ``>``: Greater than
                  - ``>=``: Greater than or equal to

                Logical operators
                  - ``AND``: Combines two sub-queries and returns True if both of them are True.

            order_by: List of columns to order by. The ``order_by`` column can contain an optional
                ``DESC`` or ``ASC`` value (e.g., ``"name DESC"``). The default ordering is ``ASC``,
                so ``"name"`` is equivalent to ``"name ASC"``. If unspecified, defaults to
                ``["last_update_time DESC"]``, which lists experiments updated most recently first.
                The following fields are supported:

                - ``experiment_id``: Experiment ID
                - ``name``: Experiment name
                - ``creation_time``: Experiment creation time
                - ``last_update_time``: Experiment last update time

            page_token: Token specifying the next page of results. It should be obtained from
                a ``search_experiments`` call.

        Returns:
            A :py:class:`PagedList <mlflow.store.entities.PagedList>` of
            :py:class:`Experiment <mlflow.entities.Experiment>` objects. The pagination token
            for the next page can be obtained via the ``token`` attribute of the object.

        """
        return self.store.search_experiments(
            view_type=view_type,
            max_results=max_results,
            filter_string=filter_string,
            order_by=order_by,
            page_token=page_token,
        )

    def get_experiment(self, experiment_id):
        """
        Args:
            experiment_id: The experiment ID returned from ``create_experiment``.

        Returns:
            :py:class:`mlflow.entities.Experiment`
        """
        return self.store.get_experiment(experiment_id)

    def get_experiment_by_name(self, name):
        """
        Args:
            name: The experiment name.

        Returns:
            :py:class:`mlflow.entities.Experiment`
        """
        return self.store.get_experiment_by_name(name)

    def create_experiment(self, name, artifact_location=None, tags=None):
        """Create an experiment.

        Args:
            name: The experiment name. Must be unique.
            artifact_location: The location to store run artifacts. If not provided, the server
                picks an appropriate default.
            tags: A dictionary of key-value pairs that are converted into
                :py:class:`mlflow.entities.ExperimentTag` objects.

        Returns:
            Integer ID of the created experiment.

        """
        _validate_experiment_artifact_location(artifact_location)

        return self.store.create_experiment(
            name=name,
            artifact_location=artifact_location,
            tags=[ExperimentTag(key, value) for (key, value) in tags.items()] if tags else [],
        )

    def delete_experiment(self, experiment_id):
        """Delete an experiment from the backend store.

        Args:
            experiment_id: The experiment ID returned from ``create_experiment``.

        """
        self.store.delete_experiment(experiment_id)

    def restore_experiment(self, experiment_id):
        """Restore a deleted experiment unless permanently deleted.

        Args:
            experiment_id: The experiment ID returned from ``create_experiment``.

        """
        self.store.restore_experiment(experiment_id)

    def rename_experiment(self, experiment_id, new_name):
        """Update an experiment's name. The new name must be unique.

        Args:
            experiment_id: The experiment ID returned from ``create_experiment``.

        """
        self.store.rename_experiment(experiment_id, new_name)

    def log_metric(
        self, run_id, key, value, timestamp=None, step=None, synchronous=True
    ) -> Optional[RunOperations]:
        """Log a metric against the run ID.

        Args:
            run_id: The run id to which the metric should be logged.
            key: Metric name. This string may only contain alphanumerics, underscores (_),
                dashes (-), periods (.), spaces ( ), and slashes (/). All backend stores will
                support keys up to length 250, but some may support larger keys.
            value: Metric value or single-item ndarray / tensor. Note that some special values such
                as +/- Infinity may be replaced by other values depending on the store. For example,
                the SQLAlchemy store replaces +/- Inf with max / min float values. All backend
                stores will support values up to length 5000, but some may support larger values.
            timestamp: Time when this metric was calculated. Defaults to the current system time.
            step: Training step (iteration) at which was the metric calculated. Defaults to 0.
            synchronous: *Experimental* If True, blocks until the metric is logged successfully. If
                False, logs the metric asynchronously and returns a future representing the logging
                operation.

        Returns:
            When synchronous=True, returns None. When synchronous=False, returns
            :py:class:`mlflow.RunOperations` that represents future for logging operation.

        """
        timestamp = timestamp if timestamp is not None else get_current_time_millis()
        step = step if step is not None else 0
        metric_value = convert_metric_value_to_float_if_possible(value)
        metric = Metric(key, metric_value, timestamp, step)
        if synchronous:
            self.store.log_metric(run_id, metric)
        else:
            return self.store.log_metric_async(run_id, metric)

    def log_param(self, run_id, key, value, synchronous=True):
        """Log a parameter (e.g. model hyperparameter) against the run ID. Value is converted to
        a string.

        Args:
            run_id: ID of the run to log the parameter against.
            key: Name of the parameter.
            value: Value of the parameter.
            synchronous: *Experimental* If True, blocks until the parameters are logged
                successfully. If False, logs the parameters asynchronously and
                returns a future representing the logging operation.

        Returns:
            When synchronous=True, returns parameter value.
            When synchronous=False, returns :py:class:`mlflow.RunOperations` that
            represents future for logging operation.

        """
        param = Param(key, str(value))
        try:
            if synchronous:
                self.store.log_param(run_id, param)
                return value
            else:
                return self.store.log_param_async(run_id, param)
        except MlflowException as e:
            if e.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE):
                msg = f"{e.message}{PARAM_VALIDATION_MSG}"
                raise MlflowException(msg, INVALID_PARAMETER_VALUE)
            else:
                raise e

    def set_experiment_tag(self, experiment_id, key, value):
        """Set a tag on the experiment with the specified ID. Value is converted to a string.

        Args:
            experiment_id: String ID of the experiment.
            key: Name of the tag.
            value: Tag value (converted to a string).
        """
        tag = ExperimentTag(key, str(value))
        self.store.set_experiment_tag(experiment_id, tag)

    def set_tag(self, run_id, key, value, synchronous=True) -> Optional[RunOperations]:
        """Set a tag on the run with the specified ID. Value is converted to a string.

        Args:
            run_id: String ID of the run.
            key: Tag name. This string may only contain alphanumerics, underscores
                (_), dashes (-), periods (.), spaces ( ), and slashes (/).
                All backend stores will support keys up to length 250, but some may
                support larger keys.
            value: Tag value, but will be string-ified if not.
                All backend stores will support values up to length 5000, but some
                may support larger values.
            synchronous: *Experimental* If True, blocks until the tag is logged
                successfully. If False, logs the tag asynchronously and
                returns a future representing the logging operation.

        Returns:
            When synchronous=True, returns None.
            When synchronous=False, returns :py:class:`mlflow.RunOperations` object
            that represents future for logging operation.

        """
        tag = RunTag(key, str(value))
        if synchronous:
            self.store.set_tag(run_id, tag)
        else:
            return self.store.set_tag_async(run_id, tag)

    def delete_tag(self, run_id, key):
        """Delete a tag from a run. This is irreversible.

        Args:
            run_id: String ID of the run
            key: Name of the tag

        """
        self.store.delete_tag(run_id, key)

    def update_run(self, run_id, status=None, name=None):
        """Update a run with the specified ID to a new status or name.

        Args:
            run_id: The ID of the Run to update.
            status: The new status of the run to set, if specified. At least one of ``status`` or
                ``name`` should be specified.
            name: The new name of the run to set, if specified. At least one of ``name`` or
                ``status`` should be specified.

        """
        # Exit early
        if status is None and name is None:
            return

        run = self.get_run(run_id)
        status = status or run.info.status
        self.store.update_run_info(
            run_id=run_id,
            run_status=RunStatus.from_string(status),
            end_time=run.info.end_time,
            run_name=name,
        )

    def log_batch(
        self, run_id, metrics=(), params=(), tags=(), synchronous=True
    ) -> Optional[RunOperations]:
        """Log multiple metrics, params, and/or tags.

        Args:
            run_id: String ID of the run.
            metrics: If provided, List of Metric(key, value, timestamp) instances.
            params: If provided, List of Param(key, value) instances.
            tags: If provided, List of RunTag(key, value) instances.
            synchronous: *Experimental* If True, blocks until the metrics/tags/params are logged
                successfully. If False, logs the metrics/tags/params asynchronously
                and returns a future representing the logging operation.

        Raises:
            MlflowException: If any errors occur.

        Returns:
            When synchronous=True, returns None.
            When synchronous=False, returns :py:class:`mlflow.RunOperations` that
            represents future for logging operation.

        """
        if len(metrics) == 0 and len(params) == 0 and len(tags) == 0:
            return

        param_batches = chunk_list(params, MAX_PARAMS_TAGS_PER_BATCH)
        tag_batches = chunk_list(tags, MAX_PARAMS_TAGS_PER_BATCH)

        # When given data is split into one or more batches, we need to wait for all the batches.
        # Each batch logged returns run_operations which we append to this list
        # At the end we merge all the run_operations into a single run_operations object and return.
        # Applicable only when synchronous is False
        run_operations_list = []

        for params_batch, tags_batch in zip_longest(param_batches, tag_batches, fillvalue=[]):
            metrics_batch_size = min(
                MAX_ENTITIES_PER_BATCH - len(params_batch) - len(tags_batch),
                MAX_METRICS_PER_BATCH,
            )
            metrics_batch_size = max(metrics_batch_size, 0)
            metrics_batch = metrics[:metrics_batch_size]
            metrics = metrics[metrics_batch_size:]

            if synchronous:
                self.store.log_batch(
                    run_id=run_id, metrics=metrics_batch, params=params_batch, tags=tags_batch
                )
            else:
                run_operations_list.append(
                    self.store.log_batch_async(
                        run_id=run_id,
                        metrics=metrics_batch,
                        params=params_batch,
                        tags=tags_batch,
                    )
                )

        for metrics_batch in chunk_list(metrics, chunk_size=MAX_METRICS_PER_BATCH):
            if synchronous:
                self.store.log_batch(run_id=run_id, metrics=metrics_batch, params=[], tags=[])
            else:
                run_operations_list.append(
                    self.store.log_batch_async(
                        run_id=run_id, metrics=metrics_batch, params=[], tags=[]
                    )
                )

        if not synchronous:
            # Merge all the run operations into a single run operations object
            return get_combined_run_operations(run_operations_list)

    def log_inputs(self, run_id: str, datasets: Optional[List[DatasetInput]] = None):
        """Log one or more dataset inputs to a run.

        Args:
            run_id: String ID of the run
            datasets: List of :py:class:`mlflow.entities.DatasetInput` instances to log.

        Raises:
            MlflowException: If any errors occur.

        Returns:
            None
        """
        if datasets is None or len(datasets) == 0:
            return

        self.store.log_inputs(run_id=run_id, datasets=datasets)

    def _record_logged_model(self, run_id, mlflow_model):
        from mlflow.models import Model

        if not isinstance(mlflow_model, Model):
            raise TypeError(
                "Argument 'mlflow_model' should be of type mlflow.models.Model but was "
                f"{type(mlflow_model)}"
            )
        self.store.record_logged_model(run_id, mlflow_model)

    def _get_artifact_repo(self, run_id):
        # Attempt to fetch the artifact repo from a local cache
        cached_repo = TrackingServiceClient._artifact_repos_cache.get(run_id)
        if cached_repo is not None:
            return cached_repo
        else:
            run = self.get_run(run_id)
            artifact_uri = add_databricks_profile_info_to_artifact_uri(
                run.info.artifact_uri, self.tracking_uri
            )
            artifact_repo = get_artifact_repository(artifact_uri)
            # Cache the artifact repo to avoid a future network call, removing the oldest
            # entry in the cache if there are too many elements
            if len(TrackingServiceClient._artifact_repos_cache) > 1024:
                TrackingServiceClient._artifact_repos_cache.popitem(last=False)
            TrackingServiceClient._artifact_repos_cache[run_id] = artifact_repo
            return artifact_repo

    def log_artifact(self, run_id, local_path, artifact_path=None):
        """
        Write a local file or directory to the remote ``artifact_uri``.

        Args:
            local_path: Path to the file or directory to write.
            artifact_path: If provided, the directory in ``artifact_uri`` to write to.
        """
        artifact_repo = self._get_artifact_repo(run_id)
        if os.path.isdir(local_path):
            dir_name = os.path.basename(os.path.normpath(local_path))
            path_name = (
                os.path.join(artifact_path, dir_name) if artifact_path is not None else dir_name
            )
            artifact_repo.log_artifacts(local_path, path_name)
        else:
            artifact_repo.log_artifact(local_path, artifact_path)

    def log_artifacts(self, run_id, local_dir, artifact_path=None):
        """Write a directory of files to the remote ``artifact_uri``.

        Args:
            local_dir: Path to the directory of files to write.
            artifact_path: If provided, the directory in ``artifact_uri`` to write to.

        """
        self._get_artifact_repo(run_id).log_artifacts(local_dir, artifact_path)

    def list_artifacts(self, run_id, path=None):
        """List the artifacts for a run.

        Args:
            run_id: The run to list artifacts from.
            path: The run's relative artifact path to list from. By default it is set to None
                or the root artifact path.

        Returns:
            List of :py:class:`mlflow.entities.FileInfo`

        """
        return self._get_artifact_repo(run_id).list_artifacts(path)

    def download_artifacts(self, run_id, path, dst_path=None):
        """Download an artifact file or directory from a run to a local directory if applicable,
        and return a local path for it.

        Args:
            run_id: The run to download artifacts from.
            path: Relative source path to the desired artifact.
            dst_path: Absolute path of the local filesystem destination directory to which to
                download the specified artifacts. This directory must already exist.
                If unspecified, the artifacts will either be downloaded to a new
                uniquely-named directory on the local filesystem or will be returned
                directly in the case of the LocalArtifactRepository.

        Returns:
            Local path of desired artifact.

        """
        return self._get_artifact_repo(run_id).download_artifacts(path, dst_path)

    def set_terminated(self, run_id, status=None, end_time=None):
        """Set a run's status to terminated.

        Args:
            status: A string value of :py:class:`mlflow.entities.RunStatus`. Defaults to "FINISHED".
            end_time: If not provided, defaults to the current time.
        """
        end_time = end_time if end_time else get_current_time_millis()
        status = status if status else RunStatus.to_string(RunStatus.FINISHED)
        self.store.update_run_info(
            run_id,
            run_status=RunStatus.from_string(status),
            end_time=end_time,
            run_name=None,
        )

    def delete_run(self, run_id):
        """
        Deletes a run with the given ID.
        """
        self.store.delete_run(run_id)

    def restore_run(self, run_id):
        """
        Restores a deleted run with the given ID.
        """
        self.store.restore_run(run_id)

    def search_runs(
        self,
        experiment_ids,
        filter_string="",
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=SEARCH_MAX_RESULTS_DEFAULT,
        order_by=None,
        page_token=None,
    ):
        """Search experiments that fit the search criteria.

        Args:
            experiment_ids: List of experiment IDs, or a single int or string id.
            filter_string: Filter query string, defaults to searching all runs.
            run_view_type: One of enum values ACTIVE_ONLY, DELETED_ONLY, or ALL runs
                defined in :py:class:`mlflow.entities.ViewType`.
            max_results: Maximum number of runs desired.
            order_by: List of columns to order by (e.g., "metrics.rmse"). The ``order_by`` column
                can contain an optional ``DESC`` or ``ASC`` value. The default is ``ASC``.
                The default ordering is to sort by ``start_time DESC``, then ``run_id``.
            page_token: Token specifying the next page of results. It should be obtained from
                a ``search_runs`` call.

        Returns:
            A :py:class:`PagedList <mlflow.store.entities.PagedList>` of
            :py:class:`Run <mlflow.entities.Run>` objects that satisfy the search expressions.
            If the underlying tracking store supports pagination, the token for the next page may
            be obtained via the ``token`` attribute of the returned object.

        """
        if isinstance(experiment_ids, int) or is_string_type(experiment_ids):
            experiment_ids = [experiment_ids]
        return self.store.search_runs(
            experiment_ids=experiment_ids,
            filter_string=filter_string,
            run_view_type=run_view_type,
            max_results=max_results,
            order_by=order_by,
            page_token=page_token,
        )
