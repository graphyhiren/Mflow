from six.moves import urllib

from mlflow.exceptions import MlflowException
from mlflow.store.artifact_repo import ArtifactRepository


class RunsArtifactRepository(ArtifactRepository):
    """
    Handles artifacts associated with a Run via URIs of the form
      `runs:/<run_id>/run-relative/path/to/artifact`.
    It is a light wrapper that resolves the artifact path to an absolute URI then instantiates
    and uses the artifact repository for that URI.

    The relative path part of ``artifact_uri`` is expected to be in posixpath format, so Windows
    users should take special care when constructing the URI.
    """

    def __init__(self, artifact_uri):
        from mlflow.tracking.artifact_utils import get_artifact_uri
        from mlflow.store.artifact_repository_registry import get_artifact_repository
        (run_id, artifact_path) = RunsArtifactRepository.parse_runs_uri(artifact_uri)
        uri = get_artifact_uri(run_id, artifact_path)
        assert urllib.parse.urlparse(uri).scheme != "runs"  # avoid an infinite loop
        super(RunsArtifactRepository, self).__init__(artifact_uri)
        self.repo = get_artifact_repository(uri)

    @staticmethod
    def parse_runs_uri(run_uri):
        parsed = urllib.parse.urlparse(run_uri)
        if parsed.scheme != "runs":
            raise MlflowException("Not a proper runs:/ URI: %s" % run_uri)
        # hostname = parsed.netloc  # TODO: support later

        path = parsed.path
        if not path.startswith('/') or len(path) <= 1:
            raise MlflowException("Not a proper runs:/ URI: %s" % run_uri)
        path = path[1:]

        path_parts = path.split('/')
        run_id = path_parts[0]
        if run_id == '':
            raise MlflowException("Not a proper runs:/ URI: %s" % run_uri)

        artifact_path = '/'.join(path_parts[1:]) if len(path_parts) > 1 else None
        artifact_path = artifact_path if artifact_path != '' else None

        return run_id, artifact_path

    def get_path_module(self):
        import posixpath
        return posixpath

    def log_artifact(self, local_file, artifact_path=None):
        """
        Log a local file as an artifact, optionally taking an ``artifact_path`` to place it in
        within the run's artifacts. Run artifacts can be organized into directories, so you can
        place the artifact in a directory this way.

        :param local_file: Path to artifact to log
        :param artifact_path: Directory within the run's artifact directory in which to log the
                              artifact
        """
        self.repo.log_artifact(local_file, artifact_path)

    def log_artifacts(self, local_dir, artifact_path=None):
        """
        Log the files in the specified local directory as artifacts, optionally taking
        an ``artifact_path`` to place them in within the run's artifacts.

        :param local_dir: Directory of local artifacts to log
        :param artifact_path: Directory within the run's artifact directory in which to log the
                              artifacts
        """
        self.repo.log_artifacts(local_dir, artifact_path)

    def list_artifacts(self, path):
        """
        Return all the artifacts for this run_uuid directly under path. If path is a file, returns
        an empty list. Will error if path is neither a file nor directory.

        :param path: Relative source path that contain desired artifacts

        :return: List of artifacts as FileInfo listed directly under path.
        """
        self.repo.list_artifacts(path)

    def _download_file(self, remote_file_path, local_path):
        """
        Download the file at the specified relative remote path and saves
        it at the specified local path.

        :param remote_file_path: Source path to the remote file, relative to the root
                                 directory of the artifact repository.
        :param local_path: The path to which to save the downloaded file.
        """
        self.repo._download_file(remote_file_path, local_path)
