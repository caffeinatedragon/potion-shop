import json

import falcon
from sqlalchemy.exc import IntegrityError, DataError

from potion_shop.database.operators import DBOperator, query_to_dict
from potion_shop.utils.exceptions import ContentFormatException
from potion_shop.utils.exceptions import InvalidDatabaseOperation
from potion_shop.utils.exceptions import ItemNotFound

'''
A resource for a SQLAlchemy table
that only supports GET operations
'''
class ReadOnlyResource:
    def __init__(self, engine, data_object):
        self._db = engine
        self._data_object = data_object

        # supported query parameters (search table criteria):
        # - limit (limits total number of results)
        # - any table column name (partial search for all matches)
        self._allowed_keys = {'limit'}
        self._allowed_keys.update([ col.name.lower() for col in self._data_object.__table__.columns])

    def _get_table(self):
        # call this at the start of each request transaction
        # to create a session for the DB
        return DBOperator(self._db.session, self._data_object)

    def _format_response(self, query_obj) -> str:
        '''
        converts query result to JSON in the format
            {'results:' [ query_results ]}
        if no results found, returns: {'results': []}
        '''
        # uncomment this if you want no results to return "404 Not Found"
        # if query_obj is None:
        #     raise falcon.HTTPNotFound(description='No results found for given resource')

        as_dict = query_to_dict(query_obj)
        response = {'results': [as_dict] \
                            if not isinstance(as_dict, list) \
                            else as_dict}

        return json.dumps(response, default=str)

    def _send_response(self, resp, obj=None, status=falcon.HTTP_200):
        if obj:
            resp.body = self._format_response(obj)
        resp.status = status


    # search the table for all matches to the search_params
    # search_params should be in the format of 'req.params'
    #   (a dictionary of {column_name: search_value, limit: integer})
    def _search_by(self, table:DBOperator, search_params:dict) -> 'query':
        # important: order of operations
        # - all filters
        # - then limit results

        # separate limit param to apply at the end
        limit_param = search_params.pop('limit', None)

        # apply all filters (search column for value)
        obj = table.get_all()
        for param,value in search_params.items():
            obj = table.get_by_column(param, value, obj)

        # apply limit if specified
        if limit_param:
            # will raise ValueError if invalid limit_param
            obj = obj.limit(limit_param)

        return obj

    def on_get(self, req, resp):
        table = self._get_table()
        if req.params:
            # allow search by query string (ex: /potions?type_id=2)
            query_keys = set(req.params.keys())
            if query_keys <= self._allowed_keys: # query_keys is subset of _allowed_keys
                # we're good. only allowed keys in query parameters
                try:
                    obj = self._search_by(table, req.params)
                    self._send_response(resp, obj)
                # ItemNotFound only raised if column doesn't exist in database,
                # which we already check for here with self._allowed_keys
                # except ItemNotFound as inf:
                #     raise falcon.HTTPNotFound(description=inf.message)
                except (ValueError, DataError):
                    raise falcon.HTTPBadRequest(description="Invalid value for 'limit' parameter.")
            else:
                raise falcon.HTTPBadRequest(description=f'Unsupported search parameters: {query_keys - self._allowed_keys}')

        # if no query parameters provided, return all
        else:
            self._send_response(resp, table.get_all())

    def on_get_id(self, req, resp, obj_id):
        table = self._get_table()

        try:
            obj = table.get_by_id(obj_id)
            self._send_response(resp, obj)
        except ItemNotFound as inf:
            raise falcon.HTTPNotFound(description=inf.message)


'''
A Basic resource for a SQLAlchemy table
that extends ReadOnlyResource to support
CRUD (Create Read Update Delete) operations:
    * GET and POST to the table
    * GET, PUT, DELETE by ID
    * GET by value in column
        - can search either for exact or partial matches
'''
class BasicResource(ReadOnlyResource):
    def __init__(self, engine, data_object):
        super().__init__(engine, data_object)

    def _load_req_stream(self, req) -> dict:
        try:
            return json.loads(req.context.body)
        except (json.JSONDecodeError, AttributeError):
            # AttributeError caused if there is not a 'body' attribute in req.context
            #   which should be set by the StreamHandler middleware
            # JSONDecodeError caused if body cannot be read as a JSON
            raise falcon.HTTPBadRequest(title='Invalid JSON',
                                        description='Please provide valid JSON.')

    def on_put_id(self, req, resp, obj_id):
        table = self._get_table()
        raw = self._load_req_stream(req)

        try:
            table.update_by_id(obj_id, raw)
            self._send_response(resp, status=falcon.HTTP_204) # successful, no content
        except (ItemNotFound, InvalidDatabaseOperation) as err:
            raise falcon.HTTPNotFound(description=err.message)
        except ContentFormatException as cfe:
            raise falcon.HTTPBadRequest(title='Invalid Content',
                description=cfe.message)

    def on_post(self, req, resp):
        table = self._get_table()
        raw = self._load_req_stream(req)

        # check for correct content format
        try:
            if isinstance(raw, dict):
                body = self._data_object(**raw)
            elif isinstance(raw, list):
                body = [self._data_object(**item) for item in raw]
            else:
                raise falcon.HTTPBadRequest(title='Invalid Content',
                    description='Content must be of type dict or list')
        except TypeError: # invalid number of args to data object constructor
            raise falcon.HTTPBadRequest(title='Invalid Content',
                    description='Content must match table layout')

        # update the table
        try:
            table.add(body)
            self._send_response(resp, body, falcon.HTTP_201) # created
        except (InvalidDatabaseOperation, ContentFormatException) as e:
            raise falcon.HTTPBadRequest(title='Database Error',
                description=e.message)

    def on_delete_id(self, req, resp, obj_id):
        table = self._get_table()
        try:
            table.delete_by_id(obj_id)
            self._send_response(resp, status=falcon.HTTP_204)
        except ItemNotFound as inf:
            raise falcon.HTTPNotFound(description=inf.message)
        except InvalidDatabaseOperation as e:
            raise falcon.HTTPBadRequest(title='Database Error',
                description=e.message)
