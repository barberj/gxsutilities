# gateway_rpt_utils.py
"""
This module munges data from flat files created by sql queries.

Author  Justin Barber
Email   barber(dot)justin(at)gmail.com
Version .01
"""

import os, os.path, re, types
from datetime import datetime, timedelta

# TY :: http://pingbacks.wordpress.com/2010/12/21/python-logging-tutorial/
import logging
logging.root.level = logging.DEBUG

def get_reports(path):
    """
    Pass a path to directory where reports are kept for parsing.
    Returns a fully qualified path to files.
    """

    files = os.listdir(path)
    abspath_files = []
    for f in files:
        abspath_files.append(os.path.abspath(r'%s\%s'%(path,f)))
    return abspath_files

def fill_missing_dt(GatewayByDateTimes):
    """
    If a Date is missing an hour add it with 0 values
    """

    last = None
    filled = []

    for gwbdt in GatewayByDateTimes:
        if not last:
            if gwbdt[0].hour != 0:
                for i in range(0, gwbdt[0].hour):
                    filled.append((gwbdt[0] + timedelta(hours=i),gwbdt[1],0,0))
        else:
            # We sorted so we can assume gwbdt is larger then last
            # Timedelta returns in seconds
            delta = (gwbdt[0] - last[0]).seconds / 3600
            for i in range(1,int(delta)):
                newdt = last[0] + timedelta(hours=i)
                filled.append((last[0] + timedelta(hours=i),last[1],0,0))

        # for range exludes last item in range so lets append it
        last = gwbdt
        filled.append(gwbdt)

    if last[0].hour != 23:
        filled.append((datetime(last[0].year,last[0].month,last[0].day,23,0),gwbdt[1],0,0))
        filled = fill_missing_dt(filled)
    print filled

    return filled

def formGatewayByDateTime(gateway, data_tuples_list):
    """
    Tuples are immutable so we have to create a new tuple
    given the gateway and data associated with it.

    Format ( datetime object, Gateway, Docs, Chars )

    If fill is passed then missing hours are added with data
    counts of 0.
    """
    gatewayByDateTime = []

    for data_tuple in data_tuples_list:
        # datetime will be easier to fill against
        dt = datetime.strptime('%s %s' % (data_tuple[0], data_tuple[1]), "%Y/%m/%d %H")
        gatewayByDateTime.append( (dt, gateway, int(data_tuple[2]), int(data_tuple[3])))
    return gatewayByDateTime

def parse_file_for_data(rpt):
    """
    Return a list of tuples:
    [ GatewayByDateTimeTuple, ...]
    Presumably there will only be one tuple for Date, HH pair.
    """

    # Open file and perform regular expression search
    # using the Parentheses Symbolic Group Name. We do
    # this so we can match the whole line, but have the items
    # automatically split out for us.
    with open(rpt,"r") as f:
        data = f.read()
    dataByTime = re.findall("(?P<date>[0-9]{4}/[0-9]{2}/[0-9]{2}) (?P<hh>[0-9]{2}),(?P<docs>[0-9]+),(?P<chars>[0-9]+)\n",data)

    # We need to get the gateway this data is for.
    # Assumed each file only has data for one gateway.
    gateway = re.findall("DATE \(YYYY/MM/DD HH24\),(?P<gateway>[a-zA-Z0-9 ]+) Docs,chars\n",data)[0]

    # Create new tuple with gateway included
    return formGatewayByDateTime(gateway, dataByTime)

def parse_files(path="sample_sql"):
    """
    Create a report that doesn't care about the protocol.
    It will show statistics (either/both doc or characters) by day and hour.
    """
    data = []

    reports = get_reports(path)
    for report in reports:
        data.extend(parse_file_for_data(report))

    # Exclude duplicates lazily by turning it into a set
    # and then back into a list.
    data = list(set(data))

    return data

def write_dictionary(data,*args):
    """
    Function that recursively digs data out of a dictionary
    """

    key_list = []
    if args:
        key_list = list(args)

    retVal = ""

    if type(data)==types.DictType:
        for key in sorted(data.iterkeys()):
            temp = key_list[:]
            temp.append(key)
            new_args = tuple(temp)
            retVal += write_dictionary(data[key],*new_args)
    else:
        # Print ... no further recursion
        retVal = ""
        for key in key_list:
            if key:
                retVal += key + ","
        retVal += str(data) +"\n"
        return retVal
    return retVal

def write_report(data,rptFormat='CSV',name=None):
    """
    Given the data dictionary write out the report.

    Doesn't care what the data is aslong as the struct is a dictionary.
    """

    if not type(data) == types.DictType:
        raise Exception("Report expects a dictionary to write out")

    if not name:
        date = datetime.now()
        name = '%s%02i%02i.csv' % (date.year, date.month, date.day)

    with open(name,"w") as rpt:
        rpt_data = write_dictionary(data)
        rpt.write(rpt_data)

def munge_data(data=parse_files,docs=True,chars=True,gateway=True,fill=False):
    """
    Takes the raw data and creates a report.
    A callable can be passed in leu of the data to generate data.
    If docs is True then Doc counts will be shown in report.
    If chars is True then Character counts will be shown in report.
    If gateway is True then Character and Doc counts will be shown per gateway in report.
    """

    import types

    if type(data) == types.FunctionType:
        data = data()

    # Lets organize our data
    data.sort()

    if fill:
        # We need to fill in the missing date times for our data
        data = fill_missing_dt(data)

    # Lets create our nice organized struct.
    # Date dictionary whose keys will be to Hours in the Day.
    # Hours in the Day will point to Gateways or just Doc and Char counts.
    # If gateway=False then the Hours in the Day only point to Doc/Char counts.
    dates = {}

    # need to update using setdefault
    for dt, gwy_nm, doc_cnt, char_cnt in data:
        # set up our entry
        _entry = {}

        # are we storing characters and documents?
        if chars:
            _entry['Chars'] = char_cnt
        if docs:
            _entry['Docs'] = doc_cnt

        # are we storing by gateway?
        if gateway:
            _entry = {gw_nm:_entry}

        # add our date entry passing the hour entry as default
        date_entry = dates.setdefault(dt.date().strftime('%Y/%m/%d'),{}).setdefault(dt.strftime('%H'),_entry)

    return dates

def test_function(*args):
    print 'Argument Type ', type(args)
    print 'Argument Lenght ',len(args)
    for arg in args:
        print arg

if __name__ == "__main__":
    #masticated_mess = parse_files("sample_sql")
    #masticated_mess = parse_files()
    dates = munge_data(gateway=False,docs=False)
    write_report(dates)
