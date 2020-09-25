import copy
import pytest

from tests.helpers.temp_application import client
from tests.helpers.data_manager import prepopulate
from tests.helpers.data_manager import delete_all
from tests.helpers.auth_token import create_token, token


# token only required on non-GET requests
valid_token = {'Authorization': create_token(token)}

POTIONS      = '/v1/potions'
POTION_TYPE  = '/v1/potions/types'
POTENCY      = '/v1/potions/potency'
INVENTORY    = '/v1/inventory'
EMPTY        = []

def test_delete_all_helper(client):
    # starts empty
    resp = client.get(POTION_TYPE, as_response=True)
    assert resp.status_code == 200
    if resp.json['results']:
        delete_all()
        resp = client.get(POTION_TYPE, as_response=True)
        assert resp.status_code == 200

    assert resp.json['results'] == EMPTY

    # add some potions
    client.post(POTION_TYPE, headers=valid_token, json=[
        {'related_stat': 'Health',  'color':'red'},
        {'related_stat': 'Mana',    'color':'blue'}
    ])
    resp = client.get(POTION_TYPE, as_response=True)
    assert resp.status_code == 200
    assert len(resp.json['results']) == 2

    # use helper to delete from DB
    delete_all()

    # immediately run get again, should be empty
    resp = client.get(POTION_TYPE, as_response=True)
    assert resp.status_code == 200
    assert resp.json['results'] == EMPTY

def test_prepopulate_helper(client):
    prepopulate()

    resp = client.get(POTION_TYPE, as_response=True)
    assert resp.status_code == 200
    assert len(resp.json['results']) == 3

    resp = client.get(POTENCY, as_response=True)
    assert resp.status_code == 200
    assert len(resp.json['results']) == 3

    resp = client.get(POTIONS, as_response=True)
    assert resp.status_code == 200
    assert len(resp.json['results']) == 9

    resp = client.get(INVENTORY, as_response=True)
    assert resp.status_code == 200
    assert len(resp.json['results']) == 9

    delete_all()

    resp = client.get(POTION_TYPE, as_response=True)
    assert resp.status_code == 200
    assert resp.json['results'] == EMPTY

    resp = client.get(POTENCY, as_response=True)
    assert resp.status_code == 200
    assert resp.json['results'] == EMPTY

    resp = client.get(POTIONS, as_response=True)
    assert resp.status_code == 200
    assert resp.json['results'] == EMPTY

    resp = client.get(INVENTORY, as_response=True)
    assert resp.status_code == 200
    assert resp.json['results'] == EMPTY


# This is one big test because foreign key constraints
# require a specific order for creating/deleting items
# and pytest will call tests in randomized order
def test_crud(client):
    def value_equals(route, should_equal):
        response = client.get(route)

        if len(response['results']) > 0:
            assert len(response['results']) == 1
            results = response['results'][0]
            # create a copy of should_equal with all fields
            expected = copy.copy(should_equal)
            expected['id'] = 1
            assert results == expected
        else:
            assert should_equal == EMPTY
            assert response['results'] == EMPTY

    def search_by_col(route, column, value, should_equal):
        value_equals(f'{route}?{column}={value}', should_equal)

    def create(route, test_value):
        response = client.post(route, headers=valid_token, json=test_value)
        test_value.update({'id':1})
        value_equals(f'{route}/1', test_value)
        assert response['results'][0]['id'] == 1

    def update(route, test_value, update_value):
        client.put(f'{route}/1', headers=valid_token, json=update_value, expected_statuses=[204])
        test_value.update(update_value)
        value_equals(route, test_value)

    def delete(route):
        client.delete(f'{route}/1', headers=valid_token, expected_statuses=[204])
        response = client.get(route)
        assert len(response['results']) == 0


    DUMMY_POTION      = {'type_id': 1, 'potency_id': 1}
    DUMMY_POTION_TYPE = {'related_stat': 'Health',  'color':'red'}
    DUMMY_POTENCY     = {'restores': 0.25, 'prefix': None}
    DUMMY_INVENTORY   = {'potion_id':1, 'price':15, 'amount':10, 'on_sale':True}

    # make sure we're starting with an empty DB
    delete_all()

    value_equals(POTIONS, EMPTY)
    value_equals(POTION_TYPE, EMPTY)
    value_equals(POTENCY, EMPTY)
    value_equals(INVENTORY, EMPTY)

    # NOTE: need to create type & potency first, since potion
    #       needs existing objects for SQL foreign key
    create(POTION_TYPE,  DUMMY_POTION_TYPE)
    create(POTENCY,      DUMMY_POTENCY)
    create(POTIONS,      DUMMY_POTION)    # requires existing type & potency
    create(INVENTORY,    DUMMY_INVENTORY) # requires existing potion

    # search some stuff
    search_by_col(POTION_TYPE, 'color',    'red',   DUMMY_POTION_TYPE)
    search_by_col(POTION_TYPE, 'color',    'r',     DUMMY_POTION_TYPE) # supports partial matches
    search_by_col(POTENCY,     'restores', 0.25,    DUMMY_POTENCY)
    search_by_col(POTENCY,     'restores', 0.2,     EMPTY) # numbers do not partial match
    search_by_col(INVENTORY,   'on_sale', 'y',      DUMMY_INVENTORY) # bool search supports 'y'/'yes'/'t'/'true'
    search_by_col(INVENTORY,   'on_sale', 'false',  EMPTY) # bool search supports 'y'/'yes'/'t'/'true'

    # test update (PUT request)
    update(POTION_TYPE,    DUMMY_POTION_TYPE, {'color': 'purple'})
    update(INVENTORY,      DUMMY_INVENTORY,   {'price':20, 'amount':0, 'on_sale':False})

    # search by name
    search_by_col(POTION_TYPE, 'color',    'red',   EMPTY)
    search_by_col(POTION_TYPE, 'color',    'r',     EMPTY) # supports partial matches
    search_by_col(INVENTORY,   'price',    20,   DUMMY_INVENTORY)
    search_by_col(INVENTORY,   'price',    2,    EMPTY)
    search_by_col(INVENTORY,   'on_sale', 'no', DUMMY_INVENTORY) # bool search supports 'y'/'yes'/'t'/'true'

    # test delete (DELETE request)
    # make sure not to cause any ForeignKey errors
    # (tested for in test_invalid_methods.py)
    delete(INVENTORY)
    delete(POTIONS)
    delete(POTION_TYPE)
    delete(POTENCY)

    # all should be empty
    value_equals(POTIONS, EMPTY)
    value_equals(POTION_TYPE, EMPTY)
    value_equals(POTENCY, EMPTY)
    value_equals(INVENTORY, EMPTY)
