import json
import falcon

from potion_shop.database.models import Potions
from potion_shop.database.models import PotionTypes
from potion_shop.database.models import PotionPotency
from potion_shop.database.operators import DBOperator

class PotionResource:
    def __init__(self, engine):
        self._db = engine

    def _send_response(self, resp, obj=None, status=falcon.HTTP_200):
        if obj:
            resp.body = json.dumps(obj, default=str)
        resp.status = status

    def _get_potion_description(self, potion_id):
        potion, potion_type, potency = self._db.session.query(Potions,PotionTypes,PotionPotency) \
                .filter(Potions.id == potion_id) \
                .filter(Potions.potency_id == PotionPotency.id) \
                .filter(Potions.type_id == PotionTypes.id) \
                .first()

        # format the prefix for the potion description nicely
        prefix = potency.prefix
        if not prefix:
            prefix = ''
        elif not potency.prefix.endswith('-') and not potency.prefix.endswith(' '):
            prefix += ' ' # add a trailing space

        return f'The {potion_type.color} {prefix.title()}Potion restores {potency.restores * 100:.0f}% of the drinker\'s {potion_type.related_stat.title()}.'

    def on_get(self, req, resp):
        descriptions = []
        potions_op = DBOperator(self._db.session, Potions)
        if potions_op.is_empty():
            self._send_response(resp, descriptions)

        # ids should be sequential, but any could be deleted
        # so need to get the actual ids for all potions here.
        potion_ids = [p.id for p in potions_op.get_all()]
        for obj_id in potion_ids:
            descriptions.append(self._get_potion_description(obj_id))

        self._send_response(resp, descriptions)

    def on_get_id(self, req, resp, obj_id):
        try:
            description = self._get_potion_description(obj_id)
            self._send_response(resp, description)
        except TypeError:
            raise falcon.HTTPNotFound(description='Unable to find resource with given ID')
