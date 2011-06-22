import unittest
import gateway_rpt_utils

class testGateway_utils(unittest.TestCase):

    def setUp(self):
        self.gateway = 'inbound_gvp' 
        self.dataByTime = [('2010/12/31', '00', '5', '2179'), ('2010/12/31', '01', '5', '21950')]

    def testCheckMissingHours(self):

        gatewayByTime = []

        rslt = gateway_rpt_utils.check_for_missing_hours(gatewayByTime,gateway,self.dataByTime[0][0],self.dataByTime[0][1]))
        self.assertEquals(rslt,[])


    def testGetReports(self):
        """
        Test the function that gets all the sql files to parse
        """
        import os

        files = gateway_rpt_utils.get_reports('sample_sql')
        self.assertEquals(len(files),20)
        self.assertEquals(os.path.basename(files[-1]),'daily_inbound_gvp.011911copy.txt')
        self.assertEquals(os.path.basename(files[0]),'daily_inbound_gvp.010111.txt')

    def testParse(self):
        """
        Test parsing the file
        """
        
        files = gateway_rpt_utils.get_reports('sample_sql')
        data = gateway_rpt_utils.parse_file_for_data(files[0])
        self.assertEquals(len(data),2)
        self.assertEquals(data[0],('2010/12/31', '00', 'inbound_gvp', 5, 2179))
        self.assertEquals(data[1],('2010/12/31', '01', 'inbound_gvp', 5, 21950))

    def testFormGatewayByTime(self):

        # Test without fill
        gatewayDataByTime = gateway_rpt_utils.formGatewayByTime(self.gateway, self.dataByTime, fill=False)

        self.assertEquals(len(gatewayDataByTime),2)
        self.assertEquals(gatewayDataByTime[0],('2010/12/31', '00', 'inbound_gvp', 5, 2179))
        self.assertEquals(gatewayDataByTime[1],('2010/12/31', '01', 'inbound_gvp', 5, 21950))

        # Test with fill
        gatewayDataByTime = gateway_rpt_utils.formGatewayByTime(self.gateway, self.dataByTime) 
        
        self.assertEquals(len(gatewayDataByTime),24)
        self.assertEquals(gatewayDataByTime[0],('2010/12/31', '00', 'inbound_gvp', 5, 2179))
        self.assertEquals(gatewayDataByTime[1],('2010/12/31', '01', 'inbound_gvp', 5, 21950))
        self.assertEquals(gatewayDataByTime[2],('2010/12/31', '02', 'inbound_gvp', 0, 0))

    def testCharsOnly(self):
        """
        Test munging for characters only
        """

        data = gateway_rpt_utils.munge_data(gateway=False,docs=False)

        self.assertEquals(data['2010/12/31']['00']['Chars'], 2179)
        self.assertEquals(len(data['2010/12/31']['00'].keys()), 1)
        self.assertEquals(len(data['2010/12/31'].keys()), 24)
        self.assertEquals(len(data.keys()), 20)
