# Logging
Logs will be stored in the same PostgreSQL database as the Potions table. The minimum log level is set in [../config/config.yml](../config/config.yml). All logs with a level greater than or equal to that level will be stored in the Runtime Logs table.

## Table Schema
Column          | Type      | Description
-------------   | --------- | ------------------
log_id          | int       | ID for log
created_at      | datetime  | Timestamp when log happened
level           | varchar   | Logging level (info, warning, error, ...)
trace           | varchar   | The full traceback printout
msg             | varchar   | The log message body
request_route   | varchar   | Request route that caused the log
request_headers | json      | Headers of request that caused the log
request_body    | json      | Body of request that caused the log
response_status | varchar   | Response status of request (ex: '404 not found')
response_body   | json      | Response body
