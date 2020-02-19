import unittest
from ..onsched_service import OnSchedService

class TestOnSchedService(unittest.TestCase):
    def test_locations(self):
        service = OnSchedService(client_id='DemoUser', client_secret='DemoUser')
