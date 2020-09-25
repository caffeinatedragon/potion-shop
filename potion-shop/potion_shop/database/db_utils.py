from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from potion_shop.database.models import DataModel
from potion_shop.utils.exceptions import DatabaseConnectionError

class DatabaseManager:
    def __init__(self, connection=None):
        self.connection = connection
        # create_engine will not recreate an existing table
        self.engine = create_engine(self.connection)
        self.session = scoped_session(
            sessionmaker(
                bind=self.engine,
                autocommit=True
            )
        )

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session):
        self._session = session

    def setup(self):
        try:
            print('Connecting to DB...')
            DataModel.metadata.create_all(self.engine, checkfirst=True)
            print('Connected!')
        except Exception as e:
            raise DatabaseConnectionError(f'Could not connect to DB: {e}')
