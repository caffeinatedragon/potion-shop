from sqlalchemy import inspect

class Base:
    '''
    This class is the base class for all of the data models.
    It contains functions for saving, updating, removing, and
    transforming into a dictionary from an ORM object.
    '''
    def save(self, session):
        '''
        A method to save the ORM object to the database.
        '''
        session.add(self)
        return self.to_dict()

    def update(self, session, data_obj, to_update):
        '''
        A method to update the ORM object in the database.
        '''
        session.query(data_obj).update(to_update)
        return self.to_dict()

    def remove(self, session):
        '''
        A method to delete the ORM object from the database.
        '''
        session.delete(self)
        return self.to_dict()

    def to_dict(self) -> dict:
        '''
        A method to transform the ORM object to a dictionary.
        '''
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}
