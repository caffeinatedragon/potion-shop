from aumbry import Attr, YamlConfig

class PotionConfig(YamlConfig):
    __mapping__ = {
        'gunicorn': Attr('gunicorn', dict),
        'swagger' : Attr('swagger', dict),
        'database': Attr('database', dict),
        'authentication': Attr('authentication', dict),
        'logging': Attr('logging', dict)
    }

    def __init__(self):
        self.gunicorn = {}
        self.swagger = {}
        self.database = {}
        self.authentication = {}
        self.logging = {}
