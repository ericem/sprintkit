from unittest import TestCase
from os.path import join, dirname, abspath


class SandboxResourceTest(TestCase):

    def get_Config(self):
        from sprintkit.services import Config
        config_path = join(dirname(abspath(__file__)), 'sprintkit.conf')
        config = Config(config_path)
        config.load()
        return config

