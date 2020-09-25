import pytest

from tests.helpers.temp_application import client
from tests.helpers.data_manager import prepopulate
from tests.helpers.data_manager import delete_all

descriptions = [
    'The red Potion restores 25% of the drinker\'s Health.',
    'The red Hi-Potion restores 50% of the drinker\'s Health.',
    'The red Full Potion restores 100% of the drinker\'s Health.',
    'The blue Potion restores 25% of the drinker\'s Mana.',
    'The blue Hi-Potion restores 50% of the drinker\'s Mana.',
    'The blue Full Potion restores 100% of the drinker\'s Mana.',
    'The green Potion restores 25% of the drinker\'s Stamina.',
    'The green Hi-Potion restores 50% of the drinker\'s Stamina.',
    'The green Full Potion restores 100% of the drinker\'s Stamina.'
]

def test_describe_all(client):
    prepopulate()
    response = client.get('/v1/potions/describe')
    assert response == descriptions
    delete_all()

@pytest.mark.parametrize('index',[1,3,8,2])
def test_describe_one(client,index):
    prepopulate()
    # index for DB starts with 1, index for python list starts with 0
    response = client.get(f'/v1/potions/describe/{index}')
    assert response == descriptions[index-1]
    delete_all()

def test_describe_empty(client):
    response = client.get('/v1/potions/describe', as_response=True)
    assert response.status_code == 200
    assert response.json == None

    response = client.get('/v1/potions/describe/1', as_response=True)
    assert response.status_code == 404
    assert response.json['description'] == 'Unable to find resource with given ID'
