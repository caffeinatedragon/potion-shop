import pytest
from pytest_falcon_client import make_client

from tests.helpers.temp_application import get_config
from tests.helpers.data_manager import delete_all

from potion_shop.application import PotionApplication
from potion_shop.database.db_utils import DatabaseManager
from potion_shop.database.flavors import PostgresServer
from potion_shop.database.logging.models import Log
from potion_shop.database.operators import DBOperator, query_to_dict

def _get_logger(config):
    # get db session from config
    connection = PostgresServer(
        host=config.database['server'],
        database_name=config.database['database'],
        username=config.database['username'],
        password=config.database['password']
    )
    manager = DatabaseManager(connection=connection.connection_string)
    manager.setup()
    session = manager.session

    # make sure we're starting with empty logging table
    session.execute('TRUNCATE TABLE "runtime_logs" RESTART IDENTITY;')
    logger = DBOperator(session, Log)
    assert logger.is_empty()

    return logger

# make a bad request that causes an ERROR level log
# make sure the log is included in the logging DB
def _error_logged_to_db(make_client, api, logger):
    client = make_client(api)
    resp = client.get('/', as_response=True)
    assert resp.status_code == 404

    all_logs = query_to_dict(logger.get_all())
    if type(all_logs) != list:
        all_logs = [all_logs]

    found = False
    for i in range(len(all_logs)):
        if all_logs[i]['level'] == 'ERROR':
            assert all_logs[i]['response_status'] == '404 Not Found'
            found = True

    assert found

# if log level not specified in config, should default to WARNING
def test_default_log(make_client):
    cfg = get_config()
    cfg.logging = {}
    logger = _get_logger(cfg)

    # start falcon API
    api = PotionApplication(cfg)
    assert api.logging_level == 'WARNING'

    # since level is 'warning', should NOT show startup INFO log
    assert logger.is_empty()

    _error_logged_to_db(make_client, api, logger)
    delete_all()

# pytest config is set to logging,level INFO:
# on startup should see the startup info-level log
def test_log_level_info(make_client):
    cfg = get_config()
    cfg.logging = {
        'level':'INFO'
    }

    logger = _get_logger(cfg)

    # start falcon API
    api = PotionApplication(cfg)
    assert api.logging_level == 'INFO'

    # since level is 'info', should show startup INFO log
    assert not logger.is_empty()
    all_logs = query_to_dict(logger.get_all())

    assert type(all_logs) == dict
    assert all_logs['msg'] == 'STARTUP: Logging configured successfully'
    assert all_logs['level'] == 'INFO'

    _error_logged_to_db(make_client, api, logger)
    delete_all()
