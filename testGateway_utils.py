import unittest
import gateway_rpt_utils

class testGateway_utils(unittest.TestCase):

    def testCharsOnly(self):
        """
        Test munging for characters only
        """

        data = gateway_rpt_utils.munge_data(gateway=False,docs=False)

        self.assertEquals(data['2010/12/31']['00']['Chars'], 2179)
        self.assertEquals(len(data['2010/12/31']['00'].keys()), 1)
        self.assertEquals(len(data['2010/12/31'].keys()), 24)
        self.assertEquals(len(data.keys()), 20)
