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

def format_data(data, unit='K'):
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
                record['unit'] = unit
            # calucate totla for tops
            for record in interface['traffic']['tops']:
                record['total'] = record['rx'] + record['tx']
                record['unit'] = unit
            interface['traffic'][traffic_type].sort(key=lambda x: x.get('date'))

def record_convert_unit(record, destination='K'):
    """ convert traffic unit of a record
        units are in Xib but we just save X in record
    """

    units = {'K':2**10, 'M':2**20, 'G':2**30}
    source = record['unit']
    # calulating divisor . divisor = source_unit / destination_unit
    divisor = units[source.upper()] / units[destination.upper()]

    record['rx'] = round(record['rx'] * divisor, 2)
    record['tx'] = round(record['tx'] * divisor, 2)
    record['total'] = round(record['total'] * divisor, 2)
    record['unit'] = destination.upper()

def convert_unit(data, destination='M'):
    """ convert traffic unit of each record
        units are in Xib but we just save X in record
    """

    for interface in data['interfaces']:
        for traffic_type in ['days', 'months', 'hours']:
            for record in interface['traffic'][traffic_type]:
                record_convert_unit(record, destination)

            for record in interface['traffic']['tops']:
                record_convert_unit(record, destination)

def rx_sum(data):
    """ return sum of rx traffic's """
    rx_traffic = 0
    for i in data['interfaces'][0]['traffic']['days']:
        rx_traffic = rx_traffic + i['rx']
    return rx_traffic

def get(data, traffic_set='days', interface=None):
    """get set of specific data like days , months
       if no interface specified it returns all interfaces data in format:
       {nick, [ tops ]}
       """

    if interface is None:
        return {item['nick']:item['traffic'][traffic_set] for item in data['interfaces']}
    else:
        iface_data = [item for item in data['interfaces'] if item['nick'] == interface][0]
        return iface_data['traffic'][traffic_set]

def get_days(data, interface=None):
    """ get daily traffic's
    if no interface specified it returns all interfaces data in format:
       {nick: [ days ]}
    """
    return get(data, 'days', interface)

def get_months(data, interface=None):
    """ get monthly traffic's
    if no interface specified it returns all interfaces data in format:
       {nick: [ months ]}
    """
    return get(data, 'months', interface)

def get_hours(data, interface=None):
    """ get hourly traffic's
    if no interface specified it returns all interfaces data in format:
       {nick: [ hours ]}
    """
    return get(data, 'hours', interface)

def get_tops(data, interface=None):
    """ get tops traffic's set
    if no interface specified it returns all interfaces data in format:
       {nick: [ tops ]}
    """
    return get(data, 'tops', interface)
