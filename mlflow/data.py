from __future__ import print_function

import os
import click
from six.moves import urllib

from mlflow.tracking.utils import _download_artifact_from_uri

class DownloadException(Exception):
    pass

def is_uri(string):
    parsed_uri = urllib.parse.urlparse(string)
    return len(parsed_uri.scheme) > 0


def download_uri(uri, output_path):
    return _download_artifact_from_uri(artifact_uri=uri, output_path=output_path)


@click.command("download")
@click.argument("uri")
@click.option("--output-path", "-o", metavar="PATH",
              help="Output path into which to download the artifact.")
def download(uri, output_path):
    """
    Download the artifact at the specified DBFS or S3 URI into the specified local output path, or
    the current directory if no output path is specified.
    """
    if output_path is None:
        output_path = os.path.basename(uri)
    download_uri(uri, output_path)
