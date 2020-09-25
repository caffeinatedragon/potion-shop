import datetime

from sqlalchemy import Column
from sqlalchemy.types import DATETIME, BIGINT, VARCHAR, INTEGER
from sqlalchemy.dialects.postgresql import JSON, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

from potion_shop.database.base import Base

LoggingModel = declarative_base(cls=Base)

# a table for capturing runtime logs
# since it uses the postgres JSON type, must be connected to a
# PostgreSQL database or else will raise type errors
class Log(LoggingModel):
    __tablename__ = 'runtime_logs'
    log_id = Column(BIGINT().with_variant(INTEGER, 'sqlite'), primary_key=True)
    created_at = Column(DATETIME().with_variant(TIMESTAMP, 'postgresql'))
    level = Column(VARCHAR)           # logging level (info, warning, error, ...)
    trace = Column(VARCHAR)           # the full traceback printout
    msg = Column(VARCHAR)             # the log message body
    request_route = Column(VARCHAR)   # route log is from
    request_headers = Column(JSON)    # any headers sent in request
    request_body = Column(JSON)       # request body
    response_status = Column(VARCHAR) # response status (ex: '404 not found')
    response_body = Column(JSON)      # response body

    def __init__(self, level=None, trace=None, msg=None, request_route=None,
                request_headers=None, request_body=None, response_status=None,
                response_body=None):
        self.created_at = datetime.datetime.now()
        self.level = level
        self.trace = trace
        self.msg = msg
        self.request_route = request_route
        self.request_headers = request_headers
        self.request_body = request_body
        self.response_status = response_status
        self.response_body = response_body

    def __repr__(self):
        return f"<Log: {self.created_at.strftime('%m/%d/%Y-%H:%M:%S')} - {self.msg[:50]}>"
