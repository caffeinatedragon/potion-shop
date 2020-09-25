import pytest

from tests.helpers.temp_application import client
from tests.helpers.auth_token import create_token, token
from tests.helpers.data_manager import delete_all, prepopulate

valid_token = {'Authorization': create_token(token)}

urls = ['/v1/potions', '/v1/potions/types', '/v1/potions/potency', '/v1/inventory']

@pytest.mark.parametrize('url', urls)
@pytest.mark.parametrize('method',['get', 'delete'])
def test_unknown_id(client, url, method):
    delete_all()
    client_method = getattr(client, method)
    response = client_method(f'{url}/1', headers=valid_token, as_response=True)
    assert response.status_code == 404

@pytest.mark.parametrize('url', urls)
def test_post_to_id(client, url):
    response = client.post(f'{url}/1', headers=valid_token, json={'invalid':'invalid'}, as_response=True)
    assert response.status_code == 405

@pytest.mark.parametrize('url', urls)
def test_put_all(client, url):
    response = client.put(url, headers=valid_token, json={'invalid':'invalid'}, as_response=True)
    assert response.status_code == 405

@pytest.mark.parametrize('url', urls)
def test_delete_all(client, url):
    response = client.delete(url, headers=valid_token, as_response=True)
    assert response.status_code == 405

@pytest.mark.parametrize('url', urls)
def test_post_bad_json(client, url):
    response = client.post(url, headers=valid_token, json=1, as_response=True)
    assert response.status_code == 400
    assert response.json['title'] == 'Invalid Content'

    response = client.post(url, headers=valid_token, json={'invalid':'invalid'}, as_response=True)
    assert response.status_code == 400
    assert response.json['title'] == 'Invalid Content'

@pytest.mark.parametrize('url', urls)
def test_put_bad_json(client, url):
    prepopulate()

    # invalid json
    response = client.put(f'{url}/1', headers=valid_token, json=1, as_response=True)
    assert response.status_code == 400
    # invalid key
    response = client.put(f'{url}/1', headers=valid_token, json={'invalid':'invalid'}, as_response=True)
    assert response.status_code == 404

    delete_all()

@pytest.mark.parametrize('url', urls)
def test_methods_without_params(client, url):
    prepopulate()

    response = client.put(f'{url}/1', headers=valid_token, as_response=True)
    assert response.status_code == 400

    response = client.post(url, headers=valid_token, as_response=True)
    assert response.status_code == 400

@pytest.mark.parametrize('url,bad_value', [
    ('/v1/potions/potency', {'restores': 'sleep', 'prefix':None}),
    ('/v1/inventory', {'potion_id':1, 'price':8, 'in_stock':'No', 'amount':42})
])
def test_invalid_value_type(client, url, bad_value):
    prepopulate()

    response = client.put(f'{url}/1', headers=valid_token, json=bad_value, as_response=True)
    assert response.status_code in [400,404]

    response = client.post(url, headers=valid_token, json=bad_value, as_response=True)
    assert response.status_code in [400,404]

    delete_all()

def test_post_unknown_foreign_key(client):
    prepopulate()
    # can't create a valid potion if the potency/type don't exist!
    response = client.post('/v1/potions', headers=valid_token, json={'potency_id':9000, 'type_id':9000}, as_response=True)
    assert response.status_code == 400

def test_put_unknown_foreign_key(client):
    prepopulate()

    potion_exists = client.get('/v1/potions/1', as_response=True)
    assert potion_exists.status_code == 200

    response = client.put('/v1/potions/1', headers=valid_token, json={'potency_id':9000, 'type_id':9000}, as_response=True)
    assert response.status_code == 404

    delete_all()

@pytest.mark.parametrize('url,key', [
    ('/v1/potions/potency/1', 'potency_id'),
    ('/v1/potions/types/1', 'type_id')
])
def test_delete_foreign_key(client, url, key):
    prepopulate()

    # prepopulate should have created the thing
    response = client.get(url, as_response=True)
    assert response.status_code == 200
    # thing should be referenced as ForeignKey in Potions
    response = client.get(f'/v1/potions?{key}=1', as_response=True)
    assert response.status_code == 200
    assert len(response.json['results']) >= 1
    matched_potions = len(response.json['results'])

    # if you delete PotionType/Potency with Potion referencing it
    # should throw an error & not delete
    response = client.delete(url, headers=valid_token, as_response=True)
    assert response.status_code == 400

    # delete should not have removed the thing
    response = client.get(url, as_response=True)
    assert response.status_code == 200

    response = client.get(f'/v1/potions?{key}=1', as_response=True)
    assert response.status_code == 200
    assert len(response.json['results']) == matched_potions

    delete_all()

# can't have multiple potions with the same color
def test_potion_type_duplicate_color(client):
    prepopulate()

    response = client.post('/v1/potions/types', headers=valid_token, json={'related_stat':'sleep', 'color':'red'}, as_response=True)
    assert response.status_code == 400

    delete_all()
