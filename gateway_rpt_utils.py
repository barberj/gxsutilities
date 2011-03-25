# gateway_rpt_utils.py
"""
This module munges data from flat files created by sql queries.

Author  Justin Barber 
Email   barber(dot)justin(at)gmail.com
Version .01
"""

import os, os.path, re, types

def get_daily_reports(path):
    """
    Pass a path to directory where reports are kept for parsing.
    Returns a fully qualified path to files if only a relative path is passed.
    """

    files = os.listdir(path)
    abspath_files = []
    for f in files:
        abspath_files.append(os.path.abspath('%s\\%s'%(path,f)))
    return abspath_files

def formGatewayCommsByTime(gateway, data_tuples_list):
    """
    Tuples are immutable so we have to create a new tuple
    given the gateway and data associated with it.

    Format ( YYYY/MM/DD, HH, Gateway, Docs, Chars )
    """
    gatewayCommsByTime = []

    for data_tuple in data_tuples_list:
        gatewayCommsByTime.append( (data_tuple[0], data_tuple[1], gateway, int(data_tuple[2]), int(data_tuple[3])) )
    return gatewayCommsByTime
    

def parse_file_for_comm_data(rpt):
    """
    Return a list of tuples:
    [(Date in format YYYY/MM/DD, HH24, DocCount, CharacterCount), ...]
    Presumably there will only be one tuple for Date, HH pair.
    """

    # Open file and perform regular expression search 
    # using the Parentheses Symbolic Group Name. We do
    # this so we can match the whole line, but have the items
    # automatically split out for us.
    with open(rpt,"r") as f:
        data = f.read()
    commsByTime = re.findall("(?P<date>[0-9]{4}/[0-9]{2}/[0-9]{2}) (?P<hh>[0-9]{2}),(?P<docs>[0-9]+),(?P<chars>[0-9]+)\n",data)

    # We need to get the gateway this data is for.
    # Assumed each file only has data for one gateway. 
    gateway = re.findall("DATE \(YYYY/MM/DD HH24\),(?P<gateway>[a-zA-Z0-9 ]+) Docs,chars\n",data)[0]

    # Create new tuple with gateway included
    return formGatewayCommsByTime(gateway, commsByTime)

def munge_all_data(path="sample_sql"):
    """
    Create a report that doesn't care about the protocol.
    It will show statistics (either/both doc or characters) by day and hour.
    """
    data = []

    reports = get_daily_reports(path)
    for report in reports:
        data.extend(parse_file_for_comm_data(report))

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
        from datetime import datetime
        date = datetime.now()
        name = '%s%02i%02i.csv' % (date.year, date.month, date.day)

    with open(name,"w") as rpt:
        rpt_data = write_dictionary(data)
        rpt.write(rpt_data)

def create_report(data=munge_all_data,docs=True,chars=True,gateway=True,rptFormat='CSV'):
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

    # Lets create our nice organized struct.
    # Date dictionary whose keys will be to Hours in the Day.
    # Hours in the Day will point to Gateways or just Doc and Char counts. 
    # If gateway=False then the Hours in the Day only point to Doc/Char counts.
    dates = {}

    for piece in data:
        if not dates.has_key(piece[0]):
            if gateway:
                if chars and docs:
                    dates[piece[0]]={piece[1]:{piece[2]:{'Docs':piece[3],'Chars':piece[4]}}}
                elif chars:
                    dates[piece[0]]={piece[1]:{piece[2]:{'Chars':piece[4]}}}
                else:
                    dates[piece[0]]={piece[1]:{piece[2]:{'Docs':piece[3]}}}
            else:
                if chars and docs:
                    dates[piece[0]]={piece[1]:{'Docs':piece[3],'Chars':piece[4]}}
                elif chars:
                    dates[piece[0]]={piece[1]:{'Chars':piece[4]}}
                else:
                    dates[piece[0]]={piece[1]:{'Docs':piece[3]}}
        else:
            if not dates[piece[0]].has_key(piece[1]):
                if gateway:
                    if chars and docs:
                        dates[piece[0]][piece[1]]={piece[2]:{'Docs':piece[3],'Chars':piece[4]}}
                    elif chars:
                        dates[piece[0]][piece[1]]={piece[2]:{'Chars':piece[4]}}
                    else:
                        dates[piece[0]][piece[1]]={piece[2]:{'Docs':piece[3]}}
                else:
                    if chars and docs:
                        dates[piece[0]][piece[1]]={'Docs':piece[3],'Chars':piece[4]}
                    elif chars:
                        dates[piece[0]][piece[1]]={'Chars':piece[4]}
                    else:
                        dates[piece[0]][piece[1]]={'Docs':piece[3]}
            else:
                Hour = dates[piece[0]][piece[1]]
                if gateway:
                    if not Hour.has_key(piece[2]):
                        if chars and docs:
                            Hour[piece[2]]={'Docs':piece[3],'Chars':piece[4]}
                        elif chars:
                            Hour[piece[2]]={'Chars':piece[4]}
                        else:
                            Hour[piece[2]]={'Docs':piece[3]}
                else:
                    if chars:
                        Hour['Chars'] += piece[4]
                    if docs:
                        Hour['Docs'] += piece[3]
    
    write_report(dates,rptFormat)
    return dates

def test_function(*args):
    print 'Argument Type ', type(args)
    print 'Argument Lenght ',len(args)
    for arg in args:
        print arg
        
if __name__ == "__main__":
    #masticated_mess = munge_all_data("sample_sql") 
    #masticated_mess = munge_all_data() 
    create_report(gateway=False,docs=False)
