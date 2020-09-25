from potion_shop.database.db_utils import DatabaseManager
from potion_shop.database.flavors import PostgresServer
from potion_shop.database.logging.models import Log
from potion_shop.database.models import Potions
from potion_shop.database.models import PotionTypes
from potion_shop.database.models import PotionPotency
from potion_shop.database.models import PotionInventory
from potion_shop.database.operators import DBOperator

from tests.helpers.temp_application import get_config

'''
creates a DB session using the config
'''
def get_db_session():
    config = get_config()
    connection = PostgresServer(
        host=config.database['server'],
        database_name=config.database['database'],
        username=config.database['username'],
        password=config.database['password']
    )
    manager = DatabaseManager(connection=connection.connection_string)
    manager.setup()

    return manager.session

'''
Deletes all database entires
Order matters because of foreign keys!
    correct order:
        DELETE FROM potion_inventory;
        DELETE FROM potions;
        DELETE FROM potion_types;
        DELETE FROM potion_potency;

runtime_logs can be deleted at any time
'''
def delete_all():
    session = get_db_session()
    delete_order = [PotionInventory, Potions, PotionTypes, PotionPotency, Log]
    for table in delete_order:
        session.execute(f'TRUNCATE TABLE "{table.__table__}" RESTART IDENTITY CASCADE;')

'''
creates a set of Potions, PotionTypes, PotionPotency, and PotionInventory
items so that tests for other operations can use them.
'''
def prepopulate():
    delete_all() # make sure starting with empty database
    session = get_db_session()

    pt_op = DBOperator(session, PotionTypes)
    pp_op = DBOperator(session, PotionPotency)
    p_op  = DBOperator(session, Potions)
    i_op  = DBOperator(session, PotionInventory)

    assert pt_op.is_empty()
    assert pp_op.is_empty()
    assert p_op.is_empty()
    assert i_op.is_empty()

    # create PotionTypes
    potion_types = [
        {'related_stat': 'Health',  'color':'red'},
        {'related_stat': 'Mana',    'color':'blue'},
        {'related_stat': 'Stamina', 'color':'green'}
    ]
    pt_op.add([PotionTypes(**item) for item in potion_types])
    assert pt_op.get_all().count() == len(potion_types)

    # create PotionPotency
    potencies = [
        {'restores': 0.25, 'prefix': None},
        {'restores': 0.50, 'prefix': 'Hi-'},
        {'restores': 1.00, 'prefix': 'Full'}
    ]
    pp_op.add([PotionPotency(**item) for item in potencies])
    assert pp_op.get_all().count() == len(potencies)

    total_potions = len(potencies) * len(potion_types)

    # Create Potions for all combinations of potency/type
    potions = []
    for i in range(len(potion_types)):
        for j in range(len(potencies)):
            # PostgreSQL IDs start at 1 not 0
            potions.append(Potions(type_id=i+1, potency_id=j+1))
    p_op.add(potions)
    assert p_op.get_all().count() == total_potions

    # create inventory
    inventory = [
        PotionInventory(potion_id=i+1, price=15, amount=10) for i in range(len(potions))
    ]
    i_op.add(inventory)
    assert i_op.get_all().count() == total_potions
