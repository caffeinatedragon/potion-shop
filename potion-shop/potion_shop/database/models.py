from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import BIGINT
from sqlalchemy import BOOLEAN
from sqlalchemy import FLOAT
from sqlalchemy import INTEGER
from sqlalchemy import VARCHAR
from sqlalchemy.ext.declarative import declarative_base

from potion_shop.database.base import Base

DataModel = declarative_base(cls=Base)

'''
Potions:
Table describing different types of potions

Fields:
    id:             id for the given Potion
    potency_id:     ForeignKey to potion's potency
    type_id:        ForeignKey to potion type
'''
class Potions(DataModel):
    __tablename__ = 'potions'
    id = Column(BIGINT().with_variant(INTEGER, 'sqlite'),
                primary_key=True)
    potency_id = Column(BIGINT().with_variant(INTEGER, 'sqlite'),
                ForeignKey('potion_potency.id'))
    type_id = Column(BIGINT().with_variant(INTEGER, 'sqlite'),
                ForeignKey('potion_types.id'))

    def __init__(self, potency_id, type_id):
        self.id = None
        self.potency_id = potency_id
        self.type_id = type_id

'''
PotionPotency:
Table describing potency of potions as percentage of max stat

Fields:
    id:                 id for the given Potency
    restores:           amount of stat restored on potion use
    prefix:             prefix to add to potion description

Example:
Health Potion + Potency(restores=0.5, prefix='High') --> Health High Potion (restores 50% Max Health)
'''
class PotionPotency(DataModel):
    __tablename__ = 'potion_potency'
    id = Column(BIGINT().with_variant(INTEGER, 'sqlite'),
                primary_key=True)
    restores = Column(FLOAT, unique=True, nullable=False)
    prefix = Column(VARCHAR)

    def __init__(self, restores, prefix=None):
        self.id = None
        self.restores = restores
        self.prefix = prefix

'''
PotionTypes:
Table describing effect of different potion types

Fields:
    id:                 id for given PotionType
    related_stat:       what stat is affected by potion
    color:              color of potion (unique!)
'''
class PotionTypes(DataModel):
    __tablename__ = 'potion_types'
    id = Column(BIGINT().with_variant(INTEGER, 'sqlite'),
            primary_key=True)
    related_stat = Column(VARCHAR, nullable=False)
    color = Column(VARCHAR, nullable=False, unique=True)

    def __init__(self, related_stat, color):
        self.id = None
        self.related_stat = related_stat
        self.color = color

'''
PotionInventory:
Table describing price & amount of each potion available

Fields:
    id:              Unique identifier
    potion_id:       ForeignKey to potion's id
    price:           Cost of potion (gold)
    on_sale:         Whether item is currently on sale (default False)
    amount:          Number in stock
'''
class PotionInventory(DataModel):
    __tablename__ = 'potion_inventory'
    id = Column(BIGINT().with_variant(INTEGER, 'sqlite'),
                primary_key=True)
    potion_id = Column(BIGINT().with_variant(INTEGER, 'sqlite'),
                ForeignKey('potions.id'))
    price = Column(INTEGER, nullable=False)
    amount = Column(INTEGER, nullable=False)
    on_sale = Column(BOOLEAN, nullable=False)

    def __init__(self, potion_id, price, amount, on_sale=False):
        self.id = None
        self.potion_id = potion_id
        self.price = price
        self.on_sale = on_sale
        self.amount = amount
