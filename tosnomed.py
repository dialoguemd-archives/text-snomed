from Authentication import *
import pandas as pd
import requests
import os, re
import argparse
import json
import time

#Adapted from https://github.com/HHS/uts-rest-api/blob/master/samples/python/retrieve-cui-or-code.py
'''
parser = argparse.ArgumentParser(description='process user given parameters')
#parser.add_argument("-u", "--username", required =  True, dest="username", help = "enter username")
#parser.add_argument("-p", "--password", required =  True, dest="password", help = "enter passowrd")
parser.add_argument("-k", "--apikey", required = True, dest = "apikey", help = "enter api key from your UTS Profile")
parser.add_argument("-v", "--version", required =  False, dest="version", default = "current", help = "enter version example-2015AA")
parser.add_argument("-i", "--identifier", required =  True, dest="identifier", help = "enter identifier example-C0018787")
parser.add_argument("-s", "--source", required =  False, dest="source", help = "enter source name if known")

args = parser.parse_args()
'''


def beautify_time(time_):
   
    hr = time_//(3600)
    mins = (time_-(hr*3600))//60
    rest = time_ -(hr*3600) - (mins*60)
    #DARIA's implementation!
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


to_search = 'Indication of (contextual qualifier)'
cui = 'C0015967'


#apikey = args.apikey
apikey = 'f65d1ced-74a2-4654-a70f-af3679b4851b'
#version = args.version
#identifier = args.identifier
#source = args.source
AuthClient = Authentication(apikey)

###################################
#get TGT for our session
###################################

tgt = AuthClient.gettgt()
uri = "https://uts-ws.nlm.nih.gov/rest"


#content_endpoint = f"/search/current?string={to_search.lower()}&sabs={sabs}&returnIdType=code"

def get_snomed_mapping(cui):
    content_endpoint = f"/content/2020AA/CUI/{cui}/atoms?sabs=SNOMEDCT_US&language=ENG&ttys=PT"


    ##ticket is the only parameter needed for this call - paging does not come into play because we're only asking for one Json object
    query = {'ticket':AuthClient.getst(tgt)}
    #st_time = time.time()
    #print(st_time)
    try:
        r = requests.get(uri+content_endpoint,params=query)
    except Exception:
        #raise Exception('Could not retrieve the SNOMED details for {cui}')
        #print('Could not retrieve the SNOMED details for {cui}')
        return None

    #print(f"-----------Time taken to get results: {beautify_time(time.time()-st_time)}-----------")
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
      
    '''
    for it in : 
        print(f"SNOMED CODE: {it['sourceConcept'].split('/')[-1]}")
        print(f"Preferred name: {it['name']}")
        print('-'*30)
    #jsonData = items["result"]
    '''
    
#print(get_snomed_mapping('C0019919'))