from unittest import main, TestLoader

from sprintkit.gps import Coordinates
from sprintkit.errors import SandboxError

from fixtures import SandboxResourceTest
import params


class PerimeterTests(SandboxResourceTest):
    
    def setUp(self):
        from sprintkit.services import Perimeter
        config = self.get_Config()
        self.perimeter = Perimeter(params.coord_inside, 2000, config)

    def test_check_with_valid_mdn(self):
        result = self.perimeter.check(params.valid_mdn)
        self.assertTrue(isinstance(result, tuple))

    def test_inside_with_valid_mdn(self):
        status = self.perimeter.inside(params.valid_mdn)
        self.assertTrue(isinstance(status, bool))
    
    def test_inside_with_invalid_mdn(self):
        self.assertRaises(SandboxError, self.perimeter.inside, 
                          params.invalid_mdn)
    
    def test_inside_with_invalid_radius(self):
        from sprintkit.services import Perimeter
        config = self.get_Config()
        self.perimeter = Perimeter(params.coord_inside, 1000, config)
        self.assertRaises(SandboxError, self.perimeter.inside, 
                          params.invalid_mdn)

    def test_inside_with_invalid_key(self):
        self.perimeter.config['key'] = 'INVALIDKEY'
        self.assertRaises(SandboxError, self.perimeter.inside, params.valid_mdn)
    
    def test_inside_with_invalid_secret(self):
        self.perimeter.config['secret'] = 'INVALIDSECRET'
        self.assertRaises(SandboxError, self.perimeter.inside, params.valid_mdn)

def perimeter_suite():
    suite = TestLoader().loadTestsFromTestCase(PerimeterTests)
    return suite


if __name__ == "__main__":
    main(defaultTest="perimeter_suite")


