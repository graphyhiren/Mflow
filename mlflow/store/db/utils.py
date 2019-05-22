import os

import logging


_logger = logging.getLogger(__name__)


def _get_package_dir():
    """Returns directory containing MLflow python package."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(current_dir, os.pardir, os.pardir))


def _get_alembic_config(db_url, alembic_dir=None):
    """
    Constructs an alembic Config object referencing the specified database and migration script
    directory.

    :param db_url Database URL, like sqlite:///<absolute-path-to-local-db-file>. See
    https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls for a full list of valid
    database URLs.
    :param alembic_dir Path to migration script directory. Uses canonical migration script
    directory under mlflow/alembic if unspecified. TODO: remove this argument in MLflow 1.1, as
    it's only used to run special migrations for pre-1.0 users to remove duplicate constraint
    names.
    """
    from alembic.config import Config
    final_alembic_dir = os.path.join(_get_package_dir(), 'alembic')\
        if alembic_dir is None else alembic_dir
    config = Config(os.path.join(final_alembic_dir, 'alembic.ini'))
    config.set_main_option('script_location', final_alembic_dir)
    config.set_main_option('sqlalchemy.url', db_url)
    return config


def _upgrade_db(url):
    """
    Upgrade the schema of an MLflow tracking database to the latest supported version.
    version. Note that schema migrations can be slow and are not guaranteed to be transactional -
    we recommend taking a backup of your database before running migrations.

    :param url Database URL, like sqlite:///<absolute-path-to-local-db-file>. See
    https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls for a full list of valid
    database URLs.
    """
    # alembic adds significant import time, so we import it lazily
    from alembic import command
    _logger.info("Updating database tables at %s", url)
    config = _get_alembic_config(url)
    command.upgrade(config, 'heads')


def _upgrade_db_for_pre_1_users(url):
    """
    Upgrades the schema of an MLflow tracking database created prior to MLflow 1.0, removing
    duplicate constraint names. TODO: remove this method in MLflow 1.1.
    """
    # alembic adds significant import time, so we import it lazily
    from alembic import command
    _logger.info("Updating database tables at %s in preparation for MLflow 1.0 schema migrations",
                 url)
    alembic_dir = os.path.join(_get_package_dir(), 'temporary_db_migrations_for_pre_1_users')
    config = _get_alembic_config(url, alembic_dir)
    command.upgrade(config, 'heads')
    command.stamp(config, "base")
