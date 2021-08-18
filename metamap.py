import os
from pymm import Metamap
import subprocess

METAMAP_PATH = '<PATH TO METAMAP>'
CLINICAL_TEXT_FILE = '<PATH TO CLINICAL TEXT FILE>'
COMPRESSED_FILE = '<Where to save the compressed form of MetaMap output>'
SEMANTIC_FILE_PATH = '<PATH TO SEMANTIC FILE>' #This file contains the full meanings of the semantic abbreviations given in the MetaMap output. 

METAMAP_VERSION = '2020' 
DEBUG=False
CONVERT_UTF8=True
use_only_snomed=True #Whether or not to use only SNOMED CT in MetaMap extraction
timeout=50 #Timeout for extraction


if use_only_snomed:
    print('Using only SNOMED CT for extraction...')

DIR = '<DIR where CLINICAL_TEXT_FILE is located>'


output_file = os.path.join(DIR,'metamap_output.txt') #This is where the MetaMap (XML for now) output will be saved. TO DO: Use JSON instead.
input_file = output_file = os.path.join(DIR,'metamap_input.txt') #No need to change this. Nothing happens with it.

if METAMAP_VERSION=='2018':
    #For MetaMap 2018
    mm = Metamap(METAMAP_PATH,output_file,input_file,use_only_snomed,debug=DEBUG)
elif METAMAP_VERSION=='2020':
    #For MetaMap 2020
    mm = Metamap(METAMAP_PATH,output_file,input_file,use_only_snomed,debug=DEBUG)
else:
    raise Exception(f'For now we only have METAMAP 2018 and 2020!')



def conv_command(input_file):
    print('----Code to convert file---')
    cmd = ['java','-jar','replace_utf8.jar']
    output_file = input_file.split('.')[0]+'conv.'+input_file.split('.')[1]
    cmd+=[input_file,'>',output_file]
    return ' '.join(cmd)
  

if not os.path.exists(CLINICAL_TEXT_FILE.split('.')[0]+'conv.'+CLINICAL_TEXT_FILE.split('.')[1]):
    if METAMAP_VERSION!='2020' or CONVERT_UTF8:
        raise Exception(f"You need to run the code to convert the file and replace utf-8.\n{conv_command(CLINICAL_TEXT_FILE)}")
    else:
        old_file=CLINICAL_TEXT_FILE
        new_file=CLINICAL_TEXT_FILE.split('.')[0]+'conv.'+CLINICAL_TEXT_FILE.split('.')[1]
        cmd=['cp',old_file,new_file]
        
        proc_ = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc_.wait()

def read_lines(file_name, fast_forward_to, batch_size):
    sentences = list()
    with open(file_name, 'r',) as fp:
        
        f=fp.readlines()
        return f
        '''
        for idx, line in enumerate(f):
            sentences.append(line.strip())
            if (idx+1) % batch_size == 0:
                yield sentences
                sentences.clear()
        '''     

def save(concept,sem_dict):
    with open(COMPRESSED_FILE,'a+') as f:
        print('---------------------------------------------------',file=f)
        print (f'CUI: {concept.cui}\n Score: {concept.score}\n Concept matched: {concept.matched} \n Semantic type(s): {concept.semtypes}\n Semantic meaning: {[sem_dict[a] for a in concept.semtypes]}\n Is_mapping(from pymm): {concept.ismapping}\n',file=f)
        print('---------------------------------------------------',file=f)
        

print('Loading sematic types abbreviations...')
sem_dict={}
with open(SEMANTIC_FILE_PATH,'r') as f:
    sem = f.readlines()
    for s in sem:
        sem_dict.update({s.split('|')[0].strip():s.split('|')[2].strip()})
print('Status: Done...')

#m = mm.is_alive()
#assert m

'''
mmos = mm.parse(['there is sign of lung tumour'])

for idx, mmo in enumerate(mmos):
   for jdx, concept in enumerate(mmo):
     print (concept.cui, concept.score, concept.matched)
     print (concept.semtypes, concept.ismapping)
'''

print(f'Extracting file from MetaMap... \n File: {CLINICAL_TEXT_FILE}')
mmos = mm.parse(CLINICAL_TEXT_FILE, timeout=timeout)
print("Status: Done...")
print('Compressing & Saving extraction...')
for idx, mmo in enumerate(mmos):
    for jdx, concept in enumerate(mmo):
        #print(concept)
        save(concept,sem_dict)
print("Status: Done...") 
print('ALL DONE')   






#/mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/publiclinuxmain2018/publicmm/bin/metamap18 -c -Q 4 -y -K --sldi -I --XMLf1 --negex /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/rsample3clean.txt /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/metamap_output.txt
   
#java -jar replace_utf8.jar /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/rsample3.txt > /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/rsample3.txt
