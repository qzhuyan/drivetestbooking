#coding=utf-8
#!/usr/bin/python
import requests
import sys
import json
from optparse import OptionParser
from datetime import datetime
#from datetime import date
from slacker import Slacker


headers = { 'Cookie' : 'FpsExternalIdentity=5E9B30DC76D67400DC3C3186FC26E49C941CBA2865BD32DF8162E789CF418CD6194BB20A242628AD35EFC018758D43B8630BD4EE126056C18B002DF191ED5743E6C20F9627E00E18A35DC7EAB343746DC0746D6FFE2549BD441F289B7363012C70722E68009063A2B2E0E31F0F1B02FC6BFA398F2F70EEF578EE8331BB2097CE39168FBC3C5C6AB2B9978508F5DF2F47; _ga=GA1.2.827753902.1505159041; _gid=GA1.2.1445140.1505551432',
            'Origin' : 'https://fp.trafikverket.se',
            'Accept-Encoding' : 'gzip, deflat, abr',
            'Accept-language' : 'en-Us,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Content-Type': 'application/json' ,
            'Accept': 'application/json, text/javascript, */*; q=0.01' ,
            'Referer': 'https://fp.trafikverket.se/Boka/' ,
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive'
}


def slack_fmt(o):
    return "%s, *%s* >> %s, :moneybag: %s" % (o['date'], o['time'], o['locationName'], o['cost'])


def filter_booking(pno, locationId, slack, from_date, to_date):
    closest_o = None
    closest = datetime.strptime('2030-12-31T00:00:00', '%Y-%m-%dT%H:%M:%S')
    targets=[]

    payload = {'occasionBundleQuery': {'vehicleTypeId': 2, 'startDate': '2018-03-20T22:00:00.000Z', 'tachographTypeId': 1, 'occasionChoiceId': 1, 'languageId': 4, 'locationId': locationId, 'examinationTypeId': 0}, 'bookingSession': {'examinationTypeId': 12, 'licenceId': 5, 'ignoreDebt': False, 'socialSecurityNumber': pno, 'bookingModeId': 0}}


    resp = requests.post("https://fp.trafikverket.se/Boka/occasion-bundles",
                  headers=headers,
                  data=json.dumps(payload)
    )

    if resp.ok:
        r = resp.json()
        for d in r['data']:
            for o in d['occasions']:
                #if not o['locationName'] in locations:
                #    next

                available_slot = datetime.strptime(o['duration']['start'].split('+')[0], '%Y-%m-%dT%H:%M:%S')

                if (available_slot < closest):
                    closest = available_slot
                    closest_o = o

                if (available_slot > from_date) and (available_slot < to_date ):
                    targets.append(o)
                if (o['increasedFee'] == True or o['increasedFee'] == "True"):
                    msg1 = ":omg-panda: , we find a spot in weekend! @william *%s* :omg-panda:" % (json.dumps(o))
                    slack.chat.post_message('#general', msg1, parse='full')

        if len(targets) != 0:
            msg1 = ":omg-panda: :car: :car: :car: @william \n %s" % ('\n'.join([ slack_fmt(t) for t in targets]))
            slack.chat.post_message('#general', msg1, parse='full')

        msg = "closest date: *%s* \n %s" % (str(closest), json.dumps(closest_o))
        print(msg)
        slack.chat.post_message('#drivers', msg)


def get_locations_objs(pno):
    payload_search = { u'bookingSession':
                       { u'examinationTypeId': 0,
                         u'licenceId': u'5',
                         u'ignoreDebt': False,
                         u'rescheduleTypeId': u'0',
                         u'socialSecurityNumber': pno,
                         u'bookingModeId': 0}
    }
    resp = requests.post("https://fp.trafikverket.se/Boka/search-information",
                  headers=headers,
                  data=json.dumps(payload_search)
    )
    return resp.json()['data']['locations']

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--pno", dest="pno",
                      help="personal number", default = '')
    parser.add_option("-l", "--locations", dest="loc",
                      help="locations, comma sepreated", default = u'Sollentuna,Norrtälje 2')

    parser.add_option("-s", "--secret", dest="tkn",
                      help="slack secret token", default = '')

    parser.add_option("-t", "--to", dest="todate",
                      help="to date,  2018-04-07", default = '')

    parser.add_option("-f", "--from", dest="fromdate",
                      help="from date, 2018-03-12", default = 'now')

    (options, args) = parser.parse_args()

    pno = options.pno
    assert(pno!='')
    locations = options.loc.split(',')
    assert(len(locations) != 0)
    token = options.tkn
    assert(token!='')

    if 'now' == options.fromdate:
        from_date = datetime.now()
    else:
        from_date = datetime.strptime(options.fromdate, "%Y-%m-%d")

    to_date = datetime.strptime(options.todate, "%Y-%m-%d")

    slack = Slacker(token)

    for l in get_locations_objs(pno):
        if l['name'] in locations:
            loc_id = l['id']
            print("targeting for %s in %s" % (pno,  loc_id))
            try:
                filter_booking(pno, loc_id, slack, from_date, to_date)
            except Exception as e:
                print("Oops fail to filter bookings", str(e))
