from unittest import main, TestLoader

from sprintkit.errors import SandboxError

from fixtures import SandboxResourceTest
import params



class PresenceTests(SandboxResourceTest):

    def setUp(self):
        from sprintkit.services import Presence
        config = self.get_Config()
        self.presence = Presence(config)

    def test_reachable_valid_mdn(self):
        status = self.presence.reachable(params.valid_mdn)
        self.assertTrue(isinstance(status, bool)) 
    
    def test_reachable_with_invalid_mdn(self):
        self.assertRaises(SandboxError, self.presence.reachable, 
                          params.invalid_mdn)

    def test_reachable_with_invalid_key(self):
        self.presence.config['key'] = 'INVALIDKEY'
        self.assertRaises(SandboxError, self.presence.reachable,
                          params.valid_mdn)
    
    def test_reachable_with_invalid_secret(self):
        self.presence.config['secret'] = 'INVALIDSECRET'
        self.assertRaises(SandboxError, self.presence.reachable, 
                          params.valid_mdn)


def presence_suite():
    suite = TestLoader().loadTestsFromTestCase(PresenceTests)
    return suite


if __name__ == "__main__":
    main(defaultTest="presence_suite")


