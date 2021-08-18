import os
from pymm import Metamap
import subprocess



filename ='rsample1.txt'   
METAMAP_VERSION = '2020' 
DEBUG=False
CONVERT_UTF8=True
use_only_snomed=False

if use_only_snomed:
    print('Using only SNOMED CT for extraction...')
DIR = 'C:/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/public_mm_win32_main_2014/public_mm/bin/'
DIR_FOR_RANDOM = '/mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/'   
CLINICAL_TEXT_FILE = os.path.join(DIR_FOR_RANDOM,filename)
output_file = f"/mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/metamap_output{filename.split('.txt')[0][-1]}.txt"
input_file = '/mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/metamap_input.txt'

if METAMAP_VERSION=='2018':
    #For MetaMap 2018
    mm = Metamap('/mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/publiclinuxmain2018/publicmm/bin/metamap18',output_file,input_file,use_only_snomed,debug=DEBUG)
elif METAMAP_VERSION=='2020':
    #For MetaMap 2020
    mm = Metamap('/mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/public_mm/bin/metamap20',output_file,input_file,use_only_snomed,debug=DEBUG)
else:
    raise Exception(f'For now we only have METAMAP 2018 and 2020!')

COMPRESSED_FILE = os.path.join(DIR_FOR_RANDOM,f"metamap_compressed{filename.split('.txt')[0][-1]}.txt")

timeout=50


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
with open('SemanticTypes.txt','r') as f:
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
'''    
BATCH_SIZE = 32
last_checkpoint=0
#try:
for i, sentences in enumerate(read_lines(CLINICAL_TEXT_FILE, last_checkpoint, BATCH_SIZE)):
    print(sentences)
    timeout = 0.33*BATCH_SIZE
    try_again = False
    #try:
    mmos = mm.parse(sentences, timeout=timeout)
    
    except MetamapStuck:
        # Try with larger timeout
        print ("Metamap Stuck !!!; trying with larger timeout")
        try_again = True
    except Exception:
        print ("Exception in mm; skipping the batch")
        #traceback.print_exc(file=sys.stdout)
        continue
    

    if try_again:
        timeout = BATCH_SIZE*2
        try:
            mmos = mm.parse(sentences, timeout=timeout)
        except MetamapStuck:
            # Again stuck; Ignore this batch
            print ("Metamap Stuck again !!!; ignoring the batch")
            continue
        except Exception:
            print ("Exception in mm; skipping the batch")
            #traceback.print_exc(file=sys.stdout)
            continue
    
    for idx, mmo in enumerate(mmos):
        for jdx, concept in enumerate(mmo):
            print(sentences[idx])
            save(sentences[idx], concept)

    curr_checkpoint = (i+1)*BATCH_SIZE + last_checkpoint
    record_checkpoint(curr_checkpoint)
'''   

#/mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/publiclinuxmain2018/publicmm/bin/metamap18 -c -Q 4 -y -K --sldi -I --XMLf1 --negex /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/rsample3clean.txt /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/metamap_output.txt
   
#java -jar replace_utf8.jar /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/rsample3.txt > /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/rsample3.txt