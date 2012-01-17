from datetime import datetime, timedelta
import unittest
import gateway_rpt_utils

class testGateway_utils(unittest.TestCase):

    def setUp(self):
        self.gateway = 'inbound gvp'
        self.dataByTime = [('2010/12/31', '00', '5', '2179'), ('2010/12/31', '01', '5', '21950')]

        dt1 = datetime.strptime('2010/12/31 00','%Y/%m/%d %H')
        dt2 = datetime.strptime('2010/12/31 01','%Y/%m/%d %H')
        self.gwbt1 = (dt1, 'inbound gvp', 5, 2179)
        self.gwbt2 = (dt2, 'inbound gvp', 5, 21950)


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
        self.assertEquals(data[0], self.gwbt1)
        self.assertEquals(data[1], self.gwbt2)

    def testFormGatewayByDateTime(self):

        gatewayByDateTimes = gateway_rpt_utils.formGatewayByDateTime(self.gateway, self.dataByTime)

        self.assertEquals(len(gatewayByDateTimes),2)
        self.assertEquals(gatewayByDateTimes[0], self.gwbt1)
        self.assertEquals(gatewayByDateTimes[1], self.gwbt2)

    def testFillMissingDT(self):

        gatewayByDateTimes = gateway_rpt_utils.formGatewayByDateTime(self.gateway, self.dataByTime)
        self.assertEquals(gatewayByDateTimes[0], self.gwbt1)
        filled = gateway_rpt_utils.fill_missing_dt(gatewayByDateTimes)
        for i in range(2,24):
            self.assertEquals(filled[i], (self.gwbt1[0]+timedelta(hours=i),self.gwbt1[1],0,0))

    def testCharsOnly(self):
        """
        Test munging for characters only
        """

        data = gateway_rpt_utils.munge_data(gateway=False,docs=False)

        self.assertEquals(data['2010/12/31']['00']['Chars'], 2179)
        self.assertEquals(len(data['2010/12/31']['00'].keys()), 1)
        self.assertEquals(len(data['2010/12/31'].keys()), 2)
        self.assertEquals(len(data.keys()), 20)

        data = gateway_rpt_utils.munge_data(gateway=False,docs=False,fill=True)

        self.assertEquals(len(data['2010/12/31']['00'].keys()), 1)
        self.assertEquals(len(data['2010/12/31'].keys()), 24)
