from unittest import main, TestLoader

from sprintkit.errors import SandboxError

from fixtures import SandboxResourceTest
import params


class SMSTests(SandboxResourceTest):
 
    def setUp(self):
        from sprintkit.services import SMS
        config = self.get_Config()
        self.sms = SMS(config)

    def test_send_with_valid_mdn(self):
        self.sms.send(params.valid_mdn, 'hello')
    
    def test_send_with_spaces_in_msg(self):
        self.sms.send(params.valid_mdn, 'hello there')
    
    def test_send_with_long_msg(self):
        self.sms.send(params.valid_mdn, 'a'*165)
   
    def test_send_with_invalid_mdn(self):
        self.assertRaises(SandboxError, self.sms.send, '123456789', 'hello')
    
    def test_send_with_invalid_key(self):
        self.sms.config['key'] = 'INVALIDKEY'
        self.assertRaises(SandboxError, self.sms.send, params.valid_mdn, 'hello')
    
    def test_send_with_invalid_secret(self):
        self.sms.config['secret'] = 'INVALIDSECRET'
        self.assertRaises(SandboxError, self.sms.send, params.valid_mdn, 'hello')


def sms_suite():
    suite = TestLoader().loadTestsFromTestCase(SMSTests)
    return suite


if __name__ == "__main__":
    main(defaultTest="sms_suite")


