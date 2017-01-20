from subprocess import getoutput
import operator
import json
from . import jalali
from datetime import datetime


def raw_output(interface='wlp3s0'):
    """ it return a vnstat as json object """
    cmd = 'vnstat -i %s --json' % (interface,)
    vnstat_out = getoutput(cmd)
    vnstat_json = json.loads(vnstat_out)


    return vnstat_json

def traffic():
    """ reformat data

    add persian (jalali) date
    add date as object
    sort data by date
    add total of rx + tx
    """

    data = raw_output()
    for interface in data['interfaces']:
        for traffic_type in ['days', 'months', 'hours']:
            for record in interface['traffic'][traffic_type]:
                # if day not specified in date it replaced with 1
                # usually it happens in month data
                if 'day' not in record['date']: record['date']['day'] = 1

                date_string = '%d/%d/%d' % (record['date']['year'],
                                            record['date']['month'], record['date']['day'])
                record['date'] = datetime(record['date']['year'],
                                          record['date']['month'], record['date']['day'])
                record['jdate'] = jalali.Gregorian(date_string)

                record['total'] = record['rx'] + record['tx']
            for record in interface['traffic']['tops']:
                record['total'] = record['rx'] + record['tx']
            interface['traffic'][traffic_type].sort(key=lambda x: x.get('date'))
    return data

def change_unit(data,to_unit='M'):
    """ change traffic unit from KiB to MiB or GiB """
    data = data.copy()
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

def rx_sum():
    """ return sum of rx traffic's """
    traffic_json = traffic()
    sum = 0
    for i in traffic_json['days']:
        sum = sum + i['rx']
    return sum
