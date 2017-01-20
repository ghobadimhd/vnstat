""" python frontend for vnstat cmd/tool """

from subprocess import getoutput
from datetime import datetime
import json
if __name__ == 'vnstat.vnstat':
    from . import jalali
else:
    import jalali



def read():
    """ it return a vnstat as json object """
    cmd = 'vnstat --json'
    vnstat_out = getoutput(cmd)
    data_json = json.loads(vnstat_out)
    return data_json

def format_data(data):
    """ reformat data
    add persian (jalali) date
    add date as object
    sort data by date
    add total of rx + tx

    args:
        data: dictionary create from json output
    """

    for interface in data['interfaces']:
        for traffic_type in ['days', 'months', 'hours']:
            for record in interface['traffic'][traffic_type]:
                # if day not specified in date it replaced with 1
                # usually it happens in month data
                if 'day' not in record['date']:
                    record['date']['day'] = 1
                date_string = '%d/%d/%d' % (record['date']['year'],
                                            record['date']['month'], record['date']['day'])
                record['date'] = datetime(record['date']['year'],
                                          record['date']['month'], record['date']['day'])
                record['jdate'] = jalali.Gregorian(date_string)

                record['total'] = record['rx'] + record['tx']
                # calucate totla for tops
            for record in interface['traffic']['tops']:
                record['total'] = record['rx'] + record['tx']
            interface['traffic'][traffic_type].sort(key=lambda x: x.get('date'))
    return data

def change_unit(data, to_unit='M'):
    """ change traffic unit from KiB to MiB or GiB """
    units = {'M':10**3, 'G':10**6}
    divisor = units[to_unit]
    for interface in data['interfaces']:
        for traffic_type in ['days', 'months', 'hours']:
            for record in interface['traffic'][traffic_type]:
                record['rx'] = record['rx'] / divisor
                record['tx'] = record['tx'] / divisor
                record['total'] = record['total'] / divisor
            for record in interface['traffic']['tops']:
                record['rx'] = record['rx'] / divisor
                record['tx'] = record['tx'] / divisor
                record['total'] = record['total'] / divisor
    return data

def rx_sum(data):
    """ return sum of rx traffic's """
    rx_traffic = 0
    for i in data['interfaces'][0]['traffic']['days']:
        rx_traffic = rx_traffic + i['rx']
    return rx_traffic
