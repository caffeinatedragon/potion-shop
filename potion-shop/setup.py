from setuptools import setup, find_packages

setup(
    name='potion-shop',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'aumbry==0.10.0',
        'cryptography==3.1',
        'falcon==2.0.0',
        'falcon-swagger-ui==1.1.2',
        'gunicorn==20.0.4',
        'psycopg2==2.8.4', # Try using psycopg2-binary if you're experiencing problems
        'PyJWT==1.7.1',
        'PyYAML==5.1.2',
        'sqlalchemy==1.3.12'
    ]
)
