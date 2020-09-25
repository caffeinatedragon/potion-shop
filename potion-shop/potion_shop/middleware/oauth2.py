from pathlib import Path

import falcon
import jwt

'''
A Falcon Middleware to validate OAuth2/JWT tokens passed in header
of all requests to any API route. An invalid token will result
in a HTTP 401 Unauthorized response.

Any routes included in the optional 'exempt_routes' value in the
constructor will not check for a token and will allow any requests
for any request type.

Any methods included in the optional 'exempt_methods' value in the
constructor will not check for a token and will allow any requests
for the given method (default: all HEAD and OPTIONS requests)

code adapted from FalconAuth:
    https://github.com/loanzen/falcon-auth/blob/master/falcon_auth/backends.py
    NOTE: FalconAuth does not support RS256 JWT tokens, which is
    why I adapted the code instead of just using the package.
'''
class OAuth2Middleware:
    def __init__(self, config, exempt_routes:[str] = [], exempt_methods:[str] = ['head','options'], prefix='Bearer'):
        self._auth_header_prefix = prefix
        self._verify_claims = ['signature', 'iat', 'nbf', 'exp']
        self._required_claims = ['exp', 'iat', 'nbf']
        # app-specific, will require these fields in the decrypted token
        self._additional_required_fields = ['sub', 'name']

        self._exempt_routes = [e.lower() for e in exempt_routes] # force all to lowercase
        self._exempt_methods = [e.lower() for e in exempt_methods]
        # get the public key to use for decrypting tokens
        # if the file cannot be read, this will raise error
        try:
            self._public_key = Path(config['public_key']).read_text().strip()
        except:
            raise FileNotFoundError('Unable to read public_key from config')

    def process_request(self, req, resp):
        # skip for all exempt methods & routes
        if self._exempt_routes and req.relative_uri.lower() in self._exempt_routes:
            return
        if self._exempt_methods and req.method.lower() in self._exempt_methods:
            return

        # Validate the token in the Authorization header
        token = self._get_token_from_header(req.get_header('Authorization'))
        token = self._decode_token(token)
        if not self._token_is_valid(token):
            raise falcon.HTTPUnauthorized(description='Invalid JWT Credentials')

    def _decode_token(self, token):
        '''
        Decodes token using RS256 and self._public_key
        '''
        options = {f'verify_{claim}': True for claim in self._verify_claims}
        options.update(
            {f'require_{claim}':True for claim in self._required_claims}
        )

        try:
            return jwt.decode(token, self._public_key,
                              options=options,
                              verify=True,
                              algorithms=['RS256'])
        except jwt.InvalidTokenError as ex:
            raise falcon.HTTPUnauthorized(
                description=f'Error Decoding Token: {ex}')
        except ValueError:
            raise falcon.HTTPUnauthorized(
                description='Error Decoding Token: Unable to Read Key. Contact System Admin.')

    def _get_token_from_header(self, auth_header) -> str:
        '''
        Parses and returns Auth token from the request header. Raises
        `falcon.HTTPUnauthoried exception` with descriptive error message
        '''
        if not auth_header:
            raise falcon.HTTPUnauthorized(
                description='Missing Authorization Header')

        parts = auth_header.split()

        if parts[0].lower() != self._auth_header_prefix.lower():
            raise falcon.HTTPUnauthorized(
                description=f'Invalid Authorization Header: Must start with {self._auth_header_prefix}')

        elif len(parts) == 1:
            raise falcon.HTTPUnauthorized(
                description='Invalid Authorization Header: Token Missing')

        elif len(parts) > 2:
            raise falcon.HTTPUnauthorized(
                description='Invalid Authorization Header: Contains extra content')

        return parts[1] # token without leading prefix

    def _token_is_valid(self, token:dict) -> bool:
        '''
        Any additional app-specific checks go here
        in our case, we are only looking for tokens for routes
        the require admin-level access. so, we'll verify
        that the token has an 'admin' key and its value is True
        '''
        # all required fields exist in token
        for field in self._additional_required_fields:
            if not token.get(field):
                return False

        # if "ADMIN" in token and set to True, return True
        return 'admin' in token and token['admin'] == True
