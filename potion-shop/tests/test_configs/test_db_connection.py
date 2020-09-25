import copy
import pytest

from tests.helpers.temp_application import get_config
from potion_shop.application import PotionApplication
from potion_shop.database.db_utils import DatabaseManager
from potion_shop.database.flavors import PostgresServer
from potion_shop.utils.exceptions import DatabaseConnectionError

conn = {
    'host': '127.0.0.1',
    'database_name': 'postgres',
    'username': 'postgresuser',
    'password': 'securepassword',
    'port': 5432
}

def test_postgres_connection_string():
    expected = f'postgres+psycopg2://{conn["username"]}:{conn["password"]}@{conn["host"]}:{conn["port"]}/{conn["database_name"]}'
    expected_no_port = f'postgres+psycopg2://{conn["username"]}:{conn["password"]}@{conn["host"]}/{conn["database_name"]}'

    postgres = PostgresServer(
        host=conn['host'],
        database_name=conn['database_name'],
        username=conn['username'],
        password=conn['password'],
        port=conn['port']
    )
    assert postgres.connection_string == expected

    postgres_no_port = PostgresServer(
        host=conn['host'],
        database_name=conn['database_name'],
        username=conn['username'],
        password=conn['password'],
    )
    assert postgres_no_port.connection_string == expected_no_port

@pytest.mark.parametrize('field', ['host','database_name','username','password'])
def test_missing_fields_postgres(field):
    missing = copy.deepcopy(conn)
    del missing[field]

    with pytest.raises(TypeError):
        not_in_params = PostgresServer(**missing)

# by sending a dummy postgres connection, should attempt to
# connect using connection_string, but will fail in db_utils.DatabaseManager
# because the DB does not exist. will raise DatabaseConnectionError
def test_dummy_postgres_connection_fails():
    cfg = get_config()
    cfg.database = {
        'use':'postgres',
        'database': conn['database_name'],
        'server': conn['host'],
        'username': conn['username'],
        'password': conn['password']
    }
    with pytest.raises(DatabaseConnectionError):
        api = PotionApplication(cfg)

def test_no_use_key():
    cfg = get_config()
    cfg.database = {
        'database': conn['database_name'],
        'server': conn['host'],
        'username': conn['username'],
        'password': conn['password']
    }
    with pytest.raises(DatabaseConnectionError):
        api = PotionApplication(cfg)

def test_unsupported_db_type():
    cfg = get_config()
    cfg.database = {'use':'sqlserver'}

    with pytest.raises(DatabaseConnectionError):
        api = PotionApplication(cfg)

def test_empty_db_in_config():
    cfg = get_config()
    cfg.database = {}

    with pytest.raises(DatabaseConnectionError):
        api = PotionApplication(cfg)

def test_no_db_in_config():
    cfg = get_config()
    del cfg.database

    with pytest.raises(DatabaseConnectionError):
        api = PotionApplication(cfg)
