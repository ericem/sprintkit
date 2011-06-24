from unittest import main, TestLoader

from fixtures import SandboxResourceTest
import params

class AccountTests(SandboxResourceTest):
    
    def setUp(self):
        from sprintkit.services import Account
        config = self.get_Config()
        self.account = Account(config)

    def test_get_devices(self):
        devices = self.account.get_devices()
        self.assertTrue(isinstance(devices, dict))

    def test_add_device(self):
        #self.fail('Test disabled for your protection. Be careful!')
        result = self.account.add_device(params.optin_mdn)
        self.assertTrue(isinstance(result, dict))

    def test_delete_device(self):
        #self.fail('Test disabled for your protection. Be careful!')
        result = self.account.delete_device(params.optin_mdn)
        self.assertTrue(isinstance(result, dict))


def account_suite():
    suite = TestLoader().loadTestsFromTestCase(AccountTests)
    return suite


if __name__ == "__main__":
    main(defaultTest="account_suite")


