from collections.abc import Iterable

import sqlalchemy
from sqlalchemy import func
from sqlalchemy.sql.sqltypes import VARCHAR, BOOLEAN

from potion_shop.utils.exceptions import ContentFormatException
from potion_shop.utils.exceptions import InvalidDatabaseOperation
from potion_shop.utils.exceptions import ItemNotFound

'''
converts query (result of DBOperator.get methods)
    to dictionary (if 1 result)
    or list of dictionaries (if multiple results)
'''
def query_to_dict(query_obj) -> [dict] or dict:
    results = [query_obj.to_dict()] \
            if not isinstance(query_obj, Iterable) \
            else [result.to_dict() for result in query_obj]

    return results[0] if len(results) == 1 else results

class DBOperator:
    '''
    Functions to access & edit the DB
    '''
    def __init__(self, session, data_object):
        self._session = session
        self._data_object = data_object
        self._table = self._session.query(self._data_object)

    def is_empty(self):
        ''' returns True if table (self._data_object) is empty
                    False if table contains at least one row '''
        return False if self._table.first() else True

    def get_all(self):
        return self._table

    def get_by_id(self, id:int):
        row = self._table.get(id)
        if not row:
            raise ItemNotFound(message='Unable to find resource with given ID')
        else:
            return row

    def get_by_column_exact(self, column_name:str, search_value, object=None):
        try:
            if not object:
                object = self._table
            # only returns exact matches
            return object.filter(
                getattr(self._data_object, column_name) == search_value
            )
        except AttributeError:
            raise ItemNotFound(message=f'Table does not contain column: {column_name}')

    def get_by_column(self, column_name:str, search_value, object=None):
        if not object:
            object = self._table
        try:
            # separating based on search_value type so that
            # searching for string will return partial & case-insensitive matches
            # but searching for numeric will require exact matches
            search_type = None
            for col in self._data_object.__table__.columns:
                if col.name.lower() == column_name:
                    search_type = col.type
            # if search_type not found, then column_name does not exist
            # in the table. raise AttributeError
            if not search_type:
                raise AttributeError

            if type(search_type) == VARCHAR:
                return object.filter(
                    func.lower(getattr(self._data_object, column_name)).startswith(search_value.lower())
                )
            elif type(search_type) == BOOLEAN:
                # exact match for boolean comparison is 0/1, but should be
                # able to search by human-readable True/False (case-insensitive)
                if search_value.lower() in {'false','f','no','n'}:
                    return object.filter(
                        getattr(self._data_object, column_name) == sqlalchemy.sql.false()
                    )
                elif search_value.lower() in {'true','t','yes','y'}:
                    return object.filter(
                        getattr(self._data_object, column_name) == sqlalchemy.sql.true()
                    )
                else:
                    # bad input, but still need return type for formatting
                    # empty query (should be fast)
                    return object.filter(sqlalchemy.sql.false())
            else:
                # exact matches only for any other type
                # (shouldn't match int(15) to searches for int(1))
                return self.get_by_column_exact(column_name, search_value, object)

        except AttributeError:
            raise ItemNotFound(message=f'Table does not contain column: {column_name}')

    def update_by_id(self, id:int, to_save:dict):
        row = self.get_by_id(id)

        if not isinstance(to_save, dict):
            raise ContentFormatException('Content must be of type dict')

        try:
            with self._session.begin():
                row.update(self._session, self._data_object, to_save)
        except:
            raise InvalidDatabaseOperation('Error occurred while updating database')

    def add(self, obj: list or 'data_object'):
        if not isinstance(obj, list) and not isinstance(obj, self._data_object):
            raise ContentFormatException('Attempting to add an invalid object type to table')

        try:
            if isinstance(obj, list):
                with self._session.no_autoflush:
                    self._session.add_all(obj)
                    self._session.flush()

                    for item in obj:
                        self._session.refresh(item)

                return [o.to_dict() for o in obj]

            else:  # if isinstance(obj, self._data_object):
                with self._session.begin():
                    obj.save(self._session)
                self._session.refresh(obj)

                return obj.to_dict()
        except:
            self._session.rollback()
            raise InvalidDatabaseOperation('Error occurred while updating database')

    def delete_by_id(self, id:int):
        obj = self.get_by_id(id)

        try:
            with self._session.begin():
                obj.remove(self._session)
        except:
            raise InvalidDatabaseOperation('Error occurred while updating database')
