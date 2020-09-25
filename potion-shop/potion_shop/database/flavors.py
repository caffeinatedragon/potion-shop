'''
This is a class to store and create the appropriate connection string. It
takes in the various parameters required by connection string.

Args:
    host:           hostname / ip address of postgres server
    database_name:  name of the db
    username:       username for connecting to db
    password:       password for connecting to db
    port:           [optional] port to use with host

'''
class PostgresServer:
    # python will raise TypeError if parameters (except port) are missing
    def __init__(self, host, database_name, username, password, port=None):
        # Scheme: 'postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>'
        if port:
            self.connection_string = f'{username}:{password}@{host}:{port}/{database_name}'
        else:
            self.connection_string = f'{username}:{password}@{host}/{database_name}'

    @property
    def connection_string(self):
        return self._connection_string

    @connection_string.setter
    def connection_string(self, connection_string):
        parsed = f'postgres+psycopg2://{connection_string}'
        self._connection_string = parsed
