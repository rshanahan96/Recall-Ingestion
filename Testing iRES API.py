import requests
import json
import pandas as pd
import time
import random
import numpy as np
import string
import urllib
import re
import datetime

auth_user = 'rshanahan96@gmail.com'
auth_key = 'Awvy3crfuWCct4XC'
headers = {'authorization-user': auth_user, 'authorization-key': auth_key}

# payload format comes directly from the iRES documentation 
req_payload = {"displaycolumns":"recallinitiationdt,productdescriptiontxt,productshortreasontxt,codeinformation","filter":"[ {'centercd':['CDER']}]", "start":1,"rows":2500,"sort":"productid","sortorder":"desc"}
formatted_payload = urllib.parse.quote_plus(json.dumps(req_payload))

def unique_sig():
    return ''.join(np.random.permutation(list(string.ascii_lowercase + string.ascii_uppercase)))[:5]

r = requests.post('https://www.accessdata.fda.gov/rest/iresapi/recalls/?signature{}&payLoad={}'.format(unique_sig() + '0123456789', formatted_payload), 
                  headers=headers)

data = r.json()

# This is mainly Will's handiwork that I copied. 
#I edited it today to write the df to json instead of csv
ndc = []
non_ndc = []

for res in data['RESULT']:
    desc = res['PRODUCTDESCRIPTIONTXT']
    ndc_strings = re.findall(r'\d{4,5}-\d{3,4}-\d{1,2}', desc)
    if len(ndc_strings) > 0:
        ndc += [(res, ndc_strings)]
    else:
        non_ndc += [res]
out = []
for rec in ndc:
    dt = datetime.datetime.strptime(rec[0]['RECALLINITIATIONDT'], '%d-%b-%Y')
    dt_string = datetime.datetime.strftime(dt, '%Y-%m-%d')
    for pk_ndc in rec[1]:
        out += [[
           dt_string,
            pk_ndc,
            rec[0]['PRODUCTDESCRIPTIONTXT'],
            rec[0]['PRODUCTSHORTREASONTXT'],
            rec[0]['CODEINFORMATION']
        ]]

df = pd.DataFrame(out, columns=['date', 'ndc', 'product', 'reason', 'code_info'])
current_date = datetime.datetime.now()
# You'll probably have to edit the path for df 
df.to_json('recalls-{}.json'.format(datetime.datetime.strftime(current_date,'%Y-%m-%d')))

print(df)
