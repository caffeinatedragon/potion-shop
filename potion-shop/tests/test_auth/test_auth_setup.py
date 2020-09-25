from pathlib import Path

import aumbry
import pytest
from pytest_falcon_client import make_client

from potion_shop.application import PotionApplication

from tests.helpers.temp_application import get_config
from tests.helpers.auth_token import create_token, token

def create_custom_auth_setup_api(auth_value):
    cfg = get_config()
    cfg.authentication = auth_value
    return PotionApplication(cfg)

def test_no_auth_setup(make_client):
    with pytest.raises(FileNotFoundError):
        api = create_custom_auth_setup_api({})

    with pytest.raises(FileNotFoundError):
        api = create_custom_auth_setup_api({'public_key': ''})

def test_auth_config_does_not_exist(make_client):
    with pytest.raises(FileNotFoundError):
        file_doesnt_exist = str(Path('./notafile.txt'))
        api = create_custom_auth_setup_api({'public_key': file_doesnt_exist})

def test_auth_file_invalid(make_client):
    # create temp file
    empty_file = Path('./empty.txt')
    empty_file.touch()
    assert empty_file.exists()

    # set service to use temp file as auth public key
    api = create_custom_auth_setup_api({'public_key': empty_file})
    client = make_client(api)

    # fail on attempt to use a valid token
    response = client.post('/v1/potions/types',
        headers={'Authorization': create_token(token, adjust_times=True)},
        json={'related_stat': 'Health', 'color': 'red'}, as_response=True)
    assert response.status_code == 401
    assert response.json['description'] == 'Error Decoding Token: Unable to Read Key. Contact System Admin.'

    # remove temp file
    empty_file.unlink()
    assert not empty_file.exists()
