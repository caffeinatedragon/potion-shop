import pytest

from tests.helpers.temp_application import client
from tests.helpers.data_manager import prepopulate
from tests.helpers.data_manager import delete_all
from tests.helpers.data_manager import get_db_session

from potion_shop.database.operators import DBOperator, query_to_dict
from potion_shop.database.models import PotionTypes
from potion_shop.utils.exceptions import ItemNotFound, ContentFormatException


POTIONS      = '/v1/potions'
POTION_TYPE  = '/v1/potions/types'
POTENCY      = '/v1/potions/potency'
INVENTORY    = '/v1/inventory'
EMPTY        = []

@pytest.mark.parametrize('limit',[-5, 0, 2, 4, 9, 9000])
def test_search_limit(client, limit):
    prepopulate()
    max_potions = len(client.get(POTIONS)['results'])

    if limit >= 0:
        resp = client.get(f'{POTIONS}?limit={limit}')
        assert len(resp['results']) == min(limit, max_potions)
    else:
        resp = client.get(f'{POTIONS}?limit={limit}', as_response=True)
        assert resp.status_code == 400
        assert resp.json['description'] == "Invalid value for 'limit' parameter."
    delete_all()

def test_search_invalid_key(client):
    prepopulate()
    resp = client.get(f'{POTIONS}?invalidkey=bad', as_response=True)
    assert resp.status_code == 400
    assert resp.json['description'] == "Unsupported search parameters: {'invalidkey'}"
    delete_all()

@pytest.mark.parametrize('method', [
    DBOperator(get_db_session(), PotionTypes).get_by_column_exact,
    DBOperator(get_db_session(), PotionTypes).get_by_column
])
def test_search_for_unknown_column(client, method):
    with pytest.raises(ItemNotFound):
        exact_match = query_to_dict(method('notacolumn', 'test'))

def test_bad_add():
    with pytest.raises(ContentFormatException):
        DBOperator(get_db_session(), PotionTypes).add(12769)


@pytest.mark.parametrize('search,actual', [
    (True,True), ('Yes',True), ('y',True), ('tRue',True), ('T',True),
    (False,False), ('No',False), ('n',False), ('nO',False), ('N',False)
])
def test_search_for_bool(client, search, actual):
    prepopulate()
    all_inventory = client.get(INVENTORY)
    search_on_sale = client.get(f'{INVENTORY}?on_sale={search}')

    all_on_sale = [{'id':inv['id'] for inv in all_inventory['results'] if inv['on_sale'] == actual}]
    search_results = [{'id':inv['id'] for inv in search_on_sale['results']}]

    assert all_on_sale == search_results
    delete_all()

def test_search_for_bool_invalid(client):
    prepopulate()

    bad_search = client.get(f'{INVENTORY}?on_sale=badvalue')
    assert bad_search['results'] == EMPTY

    delete_all()

def test_search_for_number(client):
    prepopulate()
    # prepopulate sets all Inventory.price = 15

    search_partial = client.get(f'{INVENTORY}?price=1')
    assert search_partial['results'] == EMPTY

    search_good = client.get(f'{INVENTORY}?price=15')
    all_inventory = client.get(INVENTORY)
    assert search_good['results'] == all_inventory['results']

    delete_all()

def test_search_for_string(client):
    prepopulate()
    search_exact = client.get(f'{POTION_TYPE}?color=red')
    assert len(search_exact['results']) == 1

    search_partial = client.get(f'{POTION_TYPE}?color=r')
    assert search_exact == search_partial

    # prepopulate colors = red,blue,green = all have 'e'
    # but none should show up when you search for 'e' because
    # search is a startswith() based search
    search_middle = client.get(f'{POTION_TYPE}?color=e')
    assert search_middle['results'] == EMPTY

    # search should be case-insensitive
    search_case = client.get(f'{POTION_TYPE}?color=RED')
    assert search_case == search_exact

    delete_all()

def test_search_multiple_keys(client):
    prepopulate()

    # prepopulate sets all Inventory.price = 15, so these are identical queries
    inventory1 = client.get(f'{INVENTORY}?price=15&limit=7')
    inventory2 = client.get(f'{INVENTORY}?limit=7')
    assert inventory1['results'] == inventory2['results']

    delete_all()
