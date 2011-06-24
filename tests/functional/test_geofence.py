from unittest import TestCase, TestSuite, makeSuite, main, TestLoader
from uuid import uuid4

from sprintkit.gps import SPRINTHQ
from sprintkit.services import Fence

from fixtures import SandboxResourceTest
import params

class GeoFenceTests(SandboxResourceTest):

    def setUp(self):
        from sprintkit.services import GeoFence
        config = self.get_Config()
        self.geofence = GeoFence(config)

    def test_fences(self):
        fences = self.geofence.fences()
        self.assertTrue(isinstance(fences, list))

    def test_add_fence(self):
        name = uuid4().hex
        fence = self.geofence.add_fence(name, '0600', '1600', SPRINTHQ, 2000, 5, 
                                        'SMTWHF', 'both')
        delete_result = self.geofence.delete_fence(fence)
        self.assertTrue(isinstance(fence, Fence))
    
    def test_delete_fence(self):
        name = uuid4().hex
        fence = self.geofence.add_fence(name, '0600', '1600', SPRINTHQ, 2000, 5, 
                                        'SMTWHF', 'both')
        delete_result = self.geofence.delete_fence(fence)
        self.assertEqual(delete_result['message'], 'FENCE_DELETED')

    def test_activate(self):
        name = uuid4().hex
        fence = self.geofence.add_fence(name, '0600', '1600', SPRINTHQ, 2000, 5, 
                                        'SMTWHF', 'both')
        result = fence.activate()
        delete_result = self.geofence.delete_fence(fence)
        self.assertEqual(result['Message'], 'FENCE_ACTIVATED')

    def test_deactivate(self):
        name = uuid4().hex
        fence = self.geofence.add_fence(name, '0600', '1600', SPRINTHQ, 2000, 5, 
                                        'SMTWHF', 'both')
        result = fence.deactivate()
        delete_result = self.geofence.delete_fence(fence)
        self.assertEqual(result['Message'], 'FENCE_DEACTIVATED')

    def test_get_devices(self):
        name = uuid4().hex
        fence = self.geofence.add_fence(name, '0600', '1600', SPRINTHQ, 2000, 5, 
                                        'SMTWHF', 'both')
        devices = fence.devices()
        result = self.geofence.delete_fence(fence)
        self.assertTrue(isinstance(devices, dict))

    def test_add_device(self):
        name = uuid4().hex
        fence = self.geofence.add_fence(name, '0600', '1600', SPRINTHQ, 2000, 5, 
                                        'SMTWHF', 'both')
        device = fence.add_device(params.valid_mdn)
        delete_result = self.geofence.delete_fence(fence)
        self.assertTrue(isinstance(device, dict))

    def test_delete_device(self):
        name = uuid4().hex
        fence = self.geofence.add_fence(name, '0600', '1600', SPRINTHQ, 2000, 5, 
                                        'SMTWHF', 'both')
        fence.add_device(params.valid_mdn)
        result = fence.delete_device(params.valid_mdn)

        delete_result = self.geofence.delete_fence(fence)

    def test_get_recipients(self):
        name = uuid4().hex
        fence = self.geofence.add_fence(name, '0600', '1600', SPRINTHQ, 2000, 5, 
                                        'SMTWHF', 'both')
        recipients = fence.recipients()
        delete_result = self.geofence.delete_fence(fence)
        self.assertTrue(isinstance(recipients, dict))

    def test_add_recipient(self):
        name = uuid4().hex
        fence = self.geofence.add_fence(name, '0600', '1600', SPRINTHQ, 2000, 5, 
                                        'SMTWHF', 'both')
        result = fence.add_recipient(params.valid_mdn)
        delete_result = self.geofence.delete_fence(fence)
        self.assertEqual(result['Message'], 'RECIPIENT_ADDED')

    def test_delete_recipient(self):
        name = uuid4().hex
        fence = self.geofence.add_fence(name, '0600', '1600', SPRINTHQ, 2000, 5, 
                                        'SMTWHF', 'both')
        result = fence.add_recipient(params.valid_mdn)
        delete_status = fence.delete_recipient(params.valid_mdn)
        delete_result = self.geofence.delete_fence(fence)
        self.assertEqual(delete_status['Message'], 'RECIPIENT_DELETED')


def geofence_suite():
    suite = TestLoader().loadTestsFromTestCase(GeoFenceTests)
    return suite


if __name__ == "__main__":
    main(defaultTest="geofence_suite")


