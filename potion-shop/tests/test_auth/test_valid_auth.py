import json
import pytest

from tests.helpers.temp_application import client
from tests.helpers.auth_token import create_token, token
from tests.helpers.data_manager import delete_all

test_url = '/v1/potions/types'
valid_data = {'related_stat': 'Health', 'color': 'red'}

def test_valid_auth_token(client):
    delete_all()
    response = client.post(test_url,
        headers={'Authorization': create_token(token, adjust_times=True)},
        json=valid_data, as_response=True)
    assert response.status_code == 201
    delete_all()

@pytest.mark.parametrize('bearer_case', [
    'Bearer', 'bearer', 'BEARER', 'bEaReR'
])
def test_bearer_case_insensitive(client, bearer_case):
    delete_all()
    token_value = create_token(token, adjust_times=True)[7:] # removes 'Bearer '
    response = client.post(test_url,
        headers={'Authorization': f'{bearer_case} {token_value}'},
        json=valid_data, as_response=True)
    assert response.status_code == 201

@pytest.mark.parametrize('url', [test_url, '/swagger'])
def test_valid_no_auth_routes(client,url):
    delete_all()
    # valid header
    response = client.get(url,
        headers={'Authorization': create_token(token, adjust_times=True)}, as_response=True)
    assert response.status_code == 200
    # invalid header
    response = client.get(url,
        headers={'Authorization': 'notvalid'}, as_response=True)
    assert response.status_code == 200
    # no header
    response = client.get(url, as_response=True)
    assert response.status_code == 200
