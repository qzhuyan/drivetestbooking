#coding=utf-8
#!/usr/bin/python
import requests
import sys
import time
import json
from optparse import OptionParser
from datetime import datetime
#from datetime import date
from slacker import Slacker
import nexmo


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


def filter_booking(pno, locationId, from_date, to_date, vehicle=2):
    closest_o = None
    closest = datetime.strptime('2030-12-31T00:00:00', '%Y-%m-%dT%H:%M:%S')
    targets = []
    targets_on_weekends = []
    payload = {'occasionBundleQuery': {'vehicleTypeId': vehicle, 'startDate': '2018-03-20T22:00:00.000Z', 'tachographTypeId': 1, 'occasionChoiceId': 1, 'languageId': 4, 'locationId': locationId, 'examinationTypeId': 0}, 'bookingSession': {'examinationTypeId': 12, 'licenceId': 5, 'ignoreDebt': False, 'socialSecurityNumber': pno, 'bookingModeId': 0}}


    resp = requests.post("https://fp.trafikverket.se/Boka/occasion-bundles",
                  headers=headers,
                  data=json.dumps(payload)
    )

    if resp.ok:
        r = resp.json()
        for d in r['data']:
            for o in d['occasions']:
                available_slot = datetime.strptime(o['duration']['start'].split('+')[0], '%Y-%m-%dT%H:%M:%S')

                if (available_slot < closest):
                    closest = available_slot
                    closest_o = o

                if (available_slot > from_date) and (available_slot < to_date ):
                    targets.append(o)
                    if (o['increasedFee'] == True or o['increasedFee'] == "True"):
                        targets_on_weekends.append(o)

        return {'closest': closest_o ,
                'targets': targets,
                'weekends' : targets_on_weekends
        }

def check_throttle(length):
    resp = requests.get("https://api.keyvalue.xyz/3e93f797/lastts")
    if float(resp.text) + length < time.time():
        requests.post("https://api.keyvalue.xyz/3e93f797/lastts/%s" % (int(time.time())))
        return True
    else:
        return False

def maybe_sms_notify(smsclient, sms_text):
    Isthrottled = check_throttle(3600)
    if smsclient and not Isthrottled:
        smsclient.send_message({
            'from': 'Nexmo',
            'to': mobile,
            'text': sms_text
        })
    else:
        print "sms notify *skipped*, msg %s" % (sms_text)


def slack_notify(slack, channel, msg, parse = 'full'):
    if None == slack:
        print("slack notify *skipped*: #%s : %s" % (channel, msg))
    else:
        slack.chat.post_message(channel, msg, parse)

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

def notify_user(result, slack_user, slack, sms_number = None, sms_server = None):
    # notify weekend bomb!
    for o in result['weekends']:
        msg = ":omg-panda: , we find a spot in weekend! @%s *%s* :omg-panda:" % (slack_user, json.dumps(o))
        slack_notify(slack, '#general', msg1, parse='full')

    # notify target hits
    if len(result['targets']) != 0:
        msg = ":omg-panda: :car: :car: :car: @%s \n %s" % (user, '\n'.join([ slack_fmt(t) for t in targets]))
        slack_notify(slack, '#general', msg1, parse='full')
        maybe_sms_notify(slack, "Hello, we find at least one available slot for you:" ++ slack_fmt(targets[0]))

    ## liveness notify, server side
    closest_o = result['closest']
    closest_datetime = datetime.strptime(closest_o['duration']['start'].split('+')[0], '%Y-%m-%dT%H:%M:%S')
    msg = "closest date: *%s* \n %s" % (str(closest_datetime), json.dumps(closest_o))
    slack_notify(slack, '#drivers', msg)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--pno", dest="pno",
                      help="personal number", default = '')

    parser.add_option("-l", "--locations", dest="loc",
                      help="locations, comma sepreated", default = 'Sollentuna,Norrtälje 2')

    parser.add_option("-s", "--secret", dest="tkn",
                      help="slack secret token", default = None)

    parser.add_option("-t", "--to", dest="todate",
                      help="to date,  2018-04-07", default = '')

    parser.add_option("-f", "--from", dest="fromdate",
                      help="from date, 2018-03-12", default = 'now')

    parser.add_option("-v", "--vehicle", dest="vehicle",
                      type="int",
                      help="vehicle type: 2:manual 4:auto", default = 2)

    parser.add_option("-u", "--user", dest="user",
                      type="string",
                      help="@user in slack", default = 'here')

    parser.add_option("-m", "--mobile", dest="mobile",
                      type="string",
                      help="mobile number that receive sms", default = None)

    parser.add_option("-a", "--nexmo_key", dest="nexmo_key",
                      type="string",
                      help="nexmo key for sms sending", default = None)

    parser.add_option("-b", "--nexmo_secret", dest="nexmo_secret",
                      type="string",
                      help="nexmo secret for sms sending", default = None)


    (options, args) = parser.parse_args()

    pno = options.pno
    assert(pno!='')
    locations = options.loc.split(',')
    assert(len(locations) != 0)
    token = options.tkn
    assert(token!='')
    vehicle = options.vehicle
    if 'now' == options.fromdate:
        from_date = datetime.now()
    else:
        from_date = datetime.strptime(options.fromdate, "%Y-%m-%d")

    to_date = datetime.strptime(options.todate, "%Y-%m-%d")

    if token:
        slack = Slacker(token)
    else:
        slack = None

    if options.nexmo_key and options.nexmo_secret:
        nexmo = nexmo.Client(key = options.nexmo_key,
                             secret = options.nexmo_secret)
    else:
        nexmo = None

    slack_user = options.user

    for l in get_locations_objs(pno):
        if l['name'] in locations:
            loc_id = l['id']
            print("targeting for %s in %s" % (pno,  loc_id))
            try:
                result = filter_booking(pno, loc_id, from_date, to_date, vehicle)
                notify_user(result, slack_user, slack, options.mobile, nexmo)
            except Exception as e:
                print("Oops fail to filter bookings", str(e))
