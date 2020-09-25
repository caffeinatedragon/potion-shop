import aumbry
import pytest
from pytest_falcon_client import make_client

from potion_shop.configuration import PotionConfig
from potion_shop.application import PotionApplication

def get_config():
    return aumbry.load(
        aumbry.FILE,
        PotionConfig,
        {
            'CONFIG_FILE_PATH': './config/pytest/config_pytest.yml'
        }
    )

'''
Add this fixture to all pytests that need to
run any API routes, and it will spin up the
API service. Make requests using 'client' object.
'''
@pytest.fixture
def client(make_client):
    cfg = get_config()
    api = PotionApplication(cfg)
    return make_client(api)
