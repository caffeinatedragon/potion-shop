# How to Get an Auth Token
When using the Potion Shop API, you will need to get a valid token to use with certain routes. This API uses JWT tokens using the `RS256` algorithm.

This project uses the [PyJWT library](https://pyjwt.readthedocs.io/en/latest/usage.html) to assist in decoding and validating token format.

## Pytests / Local Testing
A dummy public/private key set has been created using a [JWT encoder](https://jwt.io/) and is used in the pytest suite.

When using the pytest config file (`config/pytests/config_pytest.yml`), the API will use the public key defined in `config/pytest/test_public_key.pem` when validating tokens and private key defined in `config/pytest/test_key.pem` to create sample tokens.

Using the keys, you can generate new tokens either by using the pyjwt module (such as the `create_token` method in [tests/auth_token.py](../potion-shop/tests/auth_token.py) or using a [JWT encoder](https://jwt.io/).

## A Note about Actually Using This
The sample keys used in this project are the default sample keys used by [https://jwt.io/](https://jwt.io/) when you select `RS256` algorithm. They are **NOT** meant for real use.

In a real application, you would not save the private key in this project (or potentially would not even have access to the private key). You would only use the public key.
