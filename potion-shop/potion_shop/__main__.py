import aumbry
from gunicorn.app.base import BaseApplication
from gunicorn.workers.sync import SyncWorker

from potion_shop.application import PotionApplication
from potion_shop.configuration import PotionConfig

class CustomWorker(SyncWorker):

    def handle_quit(self, sig, frame):
        self.app.application.stop(sig)
        super().handle_quit(sig, frame)

    def run(self):
        self.app.application.start()
        super().run()


class GunicornApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


cfg = aumbry.load(
    aumbry.FILE,
    PotionConfig,
    {
        'CONFIG_FILE_PATH': './config/config.yml'
    }
)

app = PotionApplication(cfg)
guinicorn_app = GunicornApplication(app, cfg.gunicorn)
guinicorn_app.run()
