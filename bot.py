#!/usr/bin/python
import requests
import sys
import json
from datetime import datetime
from slacker import Slacker

"""
curl 'https://fp.trafikverket.se/Boka/occasion-bundles' -H 'Cookie: FpsExternalIdentity=5E9B30DC76D67400DC3C3186FC26E49C941CBA2865BD32DF8162E789CF418CD6194BB20A242628AD35EFC018758D43B8630BD4EE126056C18B002DF191ED5743E6C20F9627E00E18A35DC7EAB343746DC0746D6FFE2549BD441F289B7363012C70722E68009063A2B2E0E31F0F1B02FC6BFA398F2F70EEF578EE8331BB2097CE39168FBC3C5C6AB2B9978508F5DF2F47; _ga=GA1.2.827753902.1505159041; _gid=GA1.2.1445140.1505551432' -H 'Origin: https://fp.trafikverket.se' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.8' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36' -H 'Content-Type: application/json' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: https://fp.trafikverket.se/Boka/' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data-binary '{"bookingSession":{"socialSecurityNumber":"19876543-1234","licenceId":5,"bookingModeId":0,"ignoreDebt":false,"examinationTypeId":12},"occasionBundleQuery":{"startDate":"2017-11-30T22:00:00.000Z","locationId":1000134,"languageId":4,"vehicleTypeId":2,"tachographTypeId":1,"occasionChoiceId":1,"examinationTypeId":0}}' --compressed
"""

payload="""{"bookingSession":{"socialSecurityNumber":"xxxxxxx-yyyy","licenceId":5,"bookingModeId":0,"ignoreDebt":false,"examinationTypeId":12},"occasionBundleQuery":{"startDate":"2018-03-20T22:00:00.000Z","locationId":1000134,"languageId":4,"vehicleTypeId":2,"tachographTypeId":1,"occasionChoiceId":1,"examinationTypeId":0}}"""

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

resp = requests.post("https://fp.trafikverket.se/Boka/occasion-bundles",
              headers=headers,
              data=payload
)

closest = datetime.strptime('2030-12-31T00:00:00', '%Y-%m-%dT%H:%M:%S')
closest_o = None

from_date = datetime(2018,3,21)
to_date = datetime(2018,4,30)
location = 'Sollentuna'

Token = 'xoxp-193218011604-192501269952-242345626964-0c0c8a25d6c431bacb22fc8047f2f233'
slack = Slacker(Token)

targets=[]

def slack_fmt(o):
    return "%s, *%s* >> %s, :moneybag: %s" % (o['date'], o['time'], o['locationName'], o['cost'])

if resp.ok:
    r = resp.json()
    for d in r['data']:
        for o in d['occasions']:
            if o['locationName'] != location:
                next

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
    slack.chat.post_message('#drivers', msg)
