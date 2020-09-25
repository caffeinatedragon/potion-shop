from datetime import datetime, timedelta
from pathlib import Path

import jwt

from tests.helpers.temp_application import get_config

key = Path(get_config().authentication['key']).read_text().strip()

token = {
  'sub': '1234567890',
  'name': 'Jane Doe',
  'admin': True,
  'iat': 631152000,  # 01/01/1990 @ 12:00am (UTC)
  'exp': 631324800,  # 01/03/1990 @ 12:00am (UTC)
  'nbf': 631238400   # 01/02/1990 @ 12:00am (UTC)
}

'''
creates token to use in the Authorization header

optional parameter 'adjust_times'
if True:
    will change the timestamps in the payload to match
    when the test is being run (valid timestamps)
if False:
    will not change timestamps, so all will be invalid.
'''
def create_token(payload, adjust_times=True, prefix='Bearer'):
    now = datetime.utcnow()

    if 'iat' in payload and adjust_times:
        payload['iat'] = now

    if 'nbf' in payload and adjust_times:
        payload['nbf'] = now + timedelta(seconds=0)

    if 'exp' in payload and adjust_times:
        payload['exp'] = now + timedelta(seconds=24 * 60 * 60)

    token = jwt.encode(payload, key, algorithm='RS256').decode('utf-8')
    return f'Bearer {token}'

'''
if you want to get a valid token for pytests for testing,
uncomment this print statement and run the following command:

$ python3 potion-shop/tests/helpers/auth_token.py

NOTE: Your working directory must be the root folder of the project.
'''
# print(create_token(token))
