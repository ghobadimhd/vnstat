from subprocess import getoutput
import json
import jalali

def traffic(interface='wlp3s0',date='p'):
    """ """
    cmd = 'vnstat -i %s --json' % (interface,)
    vnstat_out = getoutput(cmd)
    vnstat_json = json.loads(vnstat_out)
    traf_list = vnstat_json['interfaces'][0]['traffic']
    if date == 'p':
        for day in traf_list['days']:
            day_date = '%s/%s/%s' % (day['date']['year'],day['date']['month'],day['date']['day'])
            day['pdate'] = jalali.Gregorian(day_date).persian_string()

    return traf_list


def rx_sum(index='k'):
    """ return sum of rx traffic's """
    traffic_json = traffic()
    sum = 0
    for i in traffic_json['days']:
        sum = sum + i['rx']
    return sum
