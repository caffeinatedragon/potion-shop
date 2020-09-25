import logging
import traceback

from potion_shop.database.logging.models import Log, LoggingModel
from potion_shop.utils.exceptions import DatabaseConnectionError

def get_logger():
    return logging.getLogger('potion_shop_logger')

# sets up logging with postgres & standard stderr log,
# returns logging level (config.logging['level'] or 'WARNING' (default))
#
# Must call AFTER db_manager's .setup() method run (db session established)
# logs should be stored in postgres (using JSON value type)
def setup_logging(config, db_manager) -> (logging.Logger, str):
    # set up the logging DB table
    # default logging level is WARNING
    logging_level = config.logging.get('level') or 'WARNING'
    print(f'Logging Level set to: {logging_level}')

    logger = get_logger()

    # sanity check to clear existing loggers
    if (logger.hasHandlers()): # pragma: no cover
        logger.handlers.clear()

    logger.setLevel(logging_level)
    logger.addHandler(SQLAlchemyHandler(db_manager))

    return logger, logging_level

class SQLAlchemyHandler(logging.Handler):
    # A very basic logger that commits a LogRecord to a SQL DB
    def __init__(self, manager):
        super().__init__()
        self._db = manager
        try:
            LoggingModel.metadata.create_all(self._db.engine, checkfirst=True)
            print('Initialized Logging Table')
        except Exception as e: # pragma: no cover
            # should never get here since intiializing logging happens
            # AFTER initializing the DB to create all other tables
            raise DatabaseConnectionError(message=f'Could not initialize Logging Table: {e}')

    def emit(self, record):
        trace = traceback.format_exc() if record.__dict__.get('exc_info') else None

        # any key not in record.__dict__ will return None
        log = Log(
            level = record.__dict__.get('levelname'),
            trace = trace,
            msg = record.__dict__.get('msg'),
            request_route = record.__dict__.get('request_route'),
            request_headers = record.__dict__.get('request_headers'),
            request_body = record.__dict__.get('request_body'),
            response_status = record.__dict__.get('response_status'),
            response_body = record.__dict__.get('response_body')
        )

        # comment this to stop printing every time a log is saved to the DB
        print(log)

        try:
            session = self._db.session
            with session.begin():
                log.save(session)
            session.refresh(log)
        except Exception as e: # pragma: no cover
            # this should never happen (hopefully)
            print(f'Error saving log: {e}')
