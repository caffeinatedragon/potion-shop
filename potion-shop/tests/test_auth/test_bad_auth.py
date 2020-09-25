from datetime import datetime
import re

import pytest

from tests.helpers.temp_application import client
from tests.helpers.auth_token import create_token, token

test_url = '/v1/potions/types'
valid_data = {'related_stat': 'Health', 'color': 'red'}

@pytest.mark.parametrize('header', [
    None,
    {'Authorization': ''}
])
def test_no_token(client, header):
    response = client.post(test_url, headers=header, json=valid_data, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Missing Authorization Header' in response.json['description']

    response = client.put(f'{test_url}/1', headers=header, json={'color':'purple'}, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Missing Authorization Header' in response.json['description']

    response = client.delete(f'{test_url}/1', headers=header, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Missing Authorization Header' in response.json['description']

@pytest.mark.parametrize('bad_token', [
    'helloworld',
    'Bearer',
    'Bearer ',
    'bearer',
    'bearer ',
    'Bearer multiple values',
    f'{create_token(token, adjust_times=True)} thatwasvalidbutthisisnt'
])
def test_invalid_token_format(client, bad_token):
    bad_token = {'Authorization': bad_token}
    response = client.post(test_url, headers=bad_token, json=valid_data, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Invalid Authorization Header' in response.json['description']

    response = client.put(f'{test_url}/1', headers=bad_token, json={'color':'purple'}, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Invalid Authorization Header' in response.json['description']

    response = client.delete(f'{test_url}/1', headers=bad_token, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Invalid Authorization Header' in response.json['description']

@pytest.mark.parametrize('bad_token', [
    'Bearer helloworld',
    'bearer iam.nota.validtoken'
])
def test_bad_jwt(client, bad_token):
    bad_token = {'Authorization': bad_token}
    response = client.post(test_url, headers=bad_token, json=valid_data, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Error Decoding Token' in response.json['description']

    response = client.put(f'{test_url}/1', headers=bad_token, json={'color':'purple'}, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Error Decoding Token' in response.json['description']

    response = client.delete(f'{test_url}/1', headers=bad_token, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Error Decoding Token' in response.json['description']

@pytest.mark.parametrize('bad_token', [
    create_token({
      'sub': '1234567890',
      'name': 'Jane Doe',
      'admin': True
    }),
    create_token({
      'sub': '1234567890',
      'name': 'Jane Doe',
      'admin': True,
      'iat': 1516239022,
      'nbf': 1588115206
    }),
    create_token({
      'sub': '1234567890',
      'name': 'Jane Doe',
      'admin': True,
      'iat': 1516239022,
      'exp': 1588116029,
    })
])
def test_missing_required_token_fields(client, bad_token):
    # this test is for if any fields in the token
    # that are automatically checked by PyJWT are missing
    #   ex: 'exp', 'iat', 'nbf'
    auth_header = {'Authorization': bad_token}
    missing_claim = re.compile('Error Decoding Token: Token is missing the "(\w+)" claim')

    response = client.post(test_url, headers=auth_header, json=valid_data, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert missing_claim.match(response.json['description'])

    response = client.put(f'{test_url}/1', headers=auth_header, json={'color':'purple'}, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert missing_claim.match(response.json['description'])

    response = client.delete(f'{test_url}/1', headers=auth_header, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert missing_claim.match(response.json['description'])

@pytest.mark.parametrize('bad_token', [
    {
      'sub': '1234567890',
      'admin': True,
      'iat': 631152000,  # 01/01/1990 @ 12:00am (UTC)
      'exp': 631324800,  # 01/03/1990 @ 12:00am (UTC)
      'nbf': 631238400   # 01/02/1990 @ 12:00am (UTC)
    },
    {
      'name': 'Jane Doe',
      'admin': True,
      'iat': 631152000,  # 01/01/1990 @ 12:00am (UTC)
      'exp': 631324800,  # 01/03/1990 @ 12:00am (UTC)
      'nbf': 631238400   # 01/02/1990 @ 12:00am (UTC)
    },
    {
      'sub': '1234567890',
      'name': 'Jane Doe',
      'iat': 631152000,  # 01/01/1990 @ 12:00am (UTC)
      'exp': 631324800,  # 01/03/1990 @ 12:00am (UTC)
      'nbf': 631238400   # 01/02/1990 @ 12:00am (UTC)
    }
])
def test_missing_other_token_fields(client, bad_token):
    # this test is for if any fields in the token
    # that are NOT checked by PyJWT are missing
    #   ex: 'sub', 'user'
    auth_header = {'Authorization': create_token(bad_token)}

    response = client.post(test_url, headers=auth_header, json=valid_data, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert response.json['description'] == 'Invalid JWT Credentials'

    response = client.put(f'{test_url}/1', headers=auth_header, json={'color':'purple'}, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert response.json['description'] == 'Invalid JWT Credentials'

    response = client.delete(f'{test_url}/1', headers=auth_header, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert response.json['description'] == 'Invalid JWT Credentials'

@pytest.mark.parametrize('expired_token', [
    create_token({
      'sub': '1234567890',
      'name': 'Jane Doe',
      'admin': True,
      'iat': 2556057600,   # 12/31/2050 @ 12:00am (UTC)
      'nbf': 2556057600,   # 12/31/2050 @ 12:00am (UTC)
      'exp': 946598400     # 12/31/1999 @ 12:00am (UTC)
    }, adjust_times=False),
    create_token({
      'sub': '1234567890',
      'name': 'Jane Doe',
      'admin': True,
      'iat': 946598400,    # 12/31/1999 @ 12:00am (UTC)
      'nbf': 2556057600,   # 12/31/2050 @ 12:00am (UTC)
      'exp': 2556057600    # 12/31/2050 @ 12:00am (UTC)
    }, adjust_times=False)
])
def test_expired_token(client, expired_token):
    auth_header = {'Authorization': expired_token}

    response = client.post(test_url, headers=auth_header, json=valid_data, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Error Decoding Token' in response.json['description']

    response = client.put(f'{test_url}/1', headers=auth_header, json={'color':'purple'}, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Error Decoding Token' in response.json['description']

    response = client.delete(f'{test_url}/1', headers=auth_header, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Error Decoding Token' in response.json['description']


@pytest.mark.parametrize('not_admin', [
    create_token({
      'sub': '1234567890',
      'name': 'Jane Doe',
      'admin': False,
      'iat': 2556057600,   # 12/31/2050 @ 12:00am (UTC)
      'nbf': 2556057600,   # 12/31/2050 @ 12:00am (UTC)
      'exp': 946598400     # 12/31/1999 @ 12:00am (UTC)
    }, adjust_times=True),
    create_token({
      'sub': '1234567890',
      'name': 'Jane Doe',
      'iat': 946598400,    # 12/31/1999 @ 12:00am (UTC)
      'nbf': 2556057600,   # 12/31/2050 @ 12:00am (UTC)
      'exp': 2556057600    # 12/31/2050 @ 12:00am (UTC)
    }, adjust_times=True)
])
def test_not_admin(client, not_admin):
    auth_header = {'Authorization': not_admin}

    response = client.post(test_url, headers=auth_header, json=valid_data, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Invalid JWT Credentials' in response.json['description']

    response = client.put(f'{test_url}/1', headers=auth_header, json={'color':'purple'}, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Invalid JWT Credentials' in response.json['description']

    response = client.delete(f'{test_url}/1', headers=auth_header, as_response=True)
    assert response.status_code == 401
    assert response.json['title'] == '401 Unauthorized'
    assert 'Invalid JWT Credentials' in response.json['description']
