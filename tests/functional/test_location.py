from unittest import main, TestLoader

from sprintkit.errors import SandboxError
from sprintkit.gps import Gps2dFix

from fixtures import SandboxResourceTest
import params


class LocationTests(SandboxResourceTest):

    def setUp(self):
        from sprintkit.services import Location
        config = self.get_Config()
        self.location = Location(config)

    def test_locate_valid_mdn(self):
        fix = self.location.locate(params.valid_mdn)
        self.assertTrue(isinstance(fix, Gps2dFix))
    
    def test_locate_with_invalid_mdn(self):
        self.assertRaises(SandboxError, self.location.locate, '1111111')

    def test_locate_with_invalid_key(self):
        self.location.config['key'] = 'INVALIDKEY'
        self.assertRaises(SandboxError, self.location.locate, params.valid_mdn)
    
    def test_locate_with_invalid_secret(self):
        self.location.config['secret'] = 'INVALIDSECRET'
        self.assertRaises(SandboxError, self.location.locate, params.valid_mdn)


def test_suite():
    suite = TestLoader().loadTestsFromTestCase(LocationTests)
    return suite


if __name__ == "__main__":
    main(defaultTest="test_suite")


