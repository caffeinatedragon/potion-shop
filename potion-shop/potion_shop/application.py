from pathlib import Path

import falcon
from falcon_swagger_ui import register_swaggerui_app

from potion_shop.database.db_utils import DatabaseManager
from potion_shop.database.flavors import PostgresServer
from potion_shop.database.models import Potions
from potion_shop.database.models import PotionTypes
from potion_shop.database.models import PotionPotency
from potion_shop.database.models import PotionInventory
from potion_shop.resources.database import BasicResource
from potion_shop.resources.potion_resource import PotionResource
from potion_shop.utils.exceptions import DatabaseConnectionError

# logging
from potion_shop.database.logging.manager import setup_logging

# middleware
from potion_shop.middleware.log_error import LogHTTPErrors
from potion_shop.middleware.stream_handler import StreamHandler
from potion_shop.middleware.oauth2 import OAuth2Middleware

class PotionApplication(falcon.API):
    def __init__(self, configuration):
        self.config = configuration

        # set up db connection & logging
        self._setup_db()

        # setup logging - default is 'WARNING' if not set
        logger, self.logging_level = setup_logging(self.config, self.manager)
        logger.info('STARTUP: Logging configured successfully')

        # configure middleware & initialize falcon.API object
        middleware = [
            StreamHandler(),
            LogHTTPErrors(),
            OAuth2Middleware(
                self.config.authentication,
                exempt_routes=[
                    '/swagger', '/static', '/static/v1', '/static/v1/swagger.yml'
                ],
                exempt_methods=['HEAD', 'OPTIONS', 'GET']
            )
        ]

        super().__init__(middleware=middleware)

        # set up Swagger UI
        self._register_swagger()

        # ------------------------
        # ------------------------
        #    Route Definitions
        # ------------------------
        # ------------------------

        # ----------------------
        #    CRUD operations
        # ----------------------
        self.add_route('/v1/potions',
            BasicResource(engine=self.manager, data_object=Potions))
        self.add_route('/v1/potions/{obj_id:int}',
            BasicResource(engine=self.manager, data_object=Potions),
            suffix='id')

        self.add_route('/v1/potions/types',
            BasicResource(engine=self.manager, data_object=PotionTypes))
        self.add_route('/v1/potions/types/{obj_id:int}',
            BasicResource(engine=self.manager, data_object=PotionTypes),
            suffix='id')

        self.add_route('/v1/potions/potency',
            BasicResource(engine=self.manager, data_object=PotionPotency))
        self.add_route('/v1/potions/potency/{obj_id:int}',
            BasicResource(engine=self.manager, data_object=PotionPotency),
            suffix='id')

        self.add_route('/v1/inventory',
            BasicResource(engine=self.manager, data_object=PotionInventory))
        self.add_route('/v1/inventory/{obj_id:int}',
            BasicResource(engine=self.manager, data_object=PotionInventory),
            suffix='id')

        # ----------------------
        #    More operations
        # ----------------------
        self.add_route('/v1/potions/describe',
            PotionResource(engine=self.manager))
        self.add_route('/v1/potions/describe/{obj_id:int}',
            PotionResource(engine=self.manager),
            suffix='id')

    def _register_swagger(self):
        STATIC_PATH = Path(self.config.swagger.get('directory')).resolve()
        self.add_static_route('/static', str(STATIC_PATH))
        register_swaggerui_app(
            self, '/swagger', '/static/v1/swagger.yml',
            # To restrict which operations are allowed on
            # the Swagger UI, use the config setting.
            # Note: Any commands run in the Swagger UI will
            #       actually run and change the database! Be careful!
            # config={
            #     'supportedSubmitMethods': ['GET']
            # }
        )

    # use the db credentials in the config file to connect
    # to the provided database. must be postgres.
    #
    # sets the 'self.manager' attribute to the connected DatabaseManager
    # if any part fails, will end program with DatabaseConnectionError
    def _setup_db(self):
        try:
            db_flavor = self.config.database.get('use').lower()
            print(f'Starting setup for {db_flavor} database...')
        except AttributeError:
            raise DatabaseConnectionError('[ERROR] No database supplied.')

        if db_flavor == 'postgres':
            connection = PostgresServer(
                host=self.config.database['server'],
                database_name=self.config.database['database'],
                username=self.config.database['username'],
                password=self.config.database['password']
            )
            self.connection_string = connection.connection_string
        else:
            raise DatabaseConnectionError(f'[ERROR] Unsupported DB Flavor: {db_flavor}')

        self.manager = DatabaseManager(connection=self.connection_string)
        self.manager.setup()

        print('DB Configured successfully')
