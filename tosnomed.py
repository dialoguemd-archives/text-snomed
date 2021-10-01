from Authentication import *
import pandas as pd
import requests
import os, re
import argparse
import json
import time

#Adapted from https://github.com/HHS/uts-rest-api/blob/master/samples/python/retrieve-cui-or-code.py


def beautify_time(time_):
    #Idea from Yasafova Daria
    hr = time_//(3600)
    mins = (time_-(hr*3600))//60
    rest = time_ -(hr*3600) - (mins*60)
    sp = ""
    if hr >=1:
        sp += '{} hours'.format(hr)
    if mins >=1:
        sp += ' {} mins'.format(mins)
    if rest >=1:
        sp += ' {} seconds'.format(rest)
    
    if sp=='':
        sp = time_
    #print(sp)
    return sp


#for testing
to_search = 'Indication of (contextual qualifier)'
cui = 'C0015967'
#--------------


apikey = 'PUT YOUR API KEY HERE'
AuthClient = Authentication(apikey)

###################################
#get TGT for our session
###################################

tgt = AuthClient.gettgt()
uri = "https://uts-ws.nlm.nih.gov/rest"


def get_snomed_mapping(cui):
    content_endpoint = f"/content/2020AA/CUI/{cui}/atoms?sabs=SNOMEDCT_US&language=ENG&ttys=PT"

   ##ticket is the only parameter needed for this call - paging does not come into play because we're only asking for one Json object
    query = {'ticket':AuthClient.getst(tgt)}

    try:
        r = requests.get(uri+content_endpoint,params=query)
    except Exception:
       
        return None
    r.encoding = 'utf-8'
    items  = json.loads(r.text)
    #print(items)
    if 'error' not in list(items.keys()):
        try:
            results = [{'SNOMED ID':it['sourceConcept'].split('/')[-1],'SNOMED term':it['name']} for it in items["result"]]
        except Exception:
            raise Exception(items)
     
        return results
    else:
        return None
  