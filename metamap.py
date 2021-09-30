import os,re
from pymm import Metamap
import subprocess
from tqdm import tqdm
from jparser import convert
import sys, getopt,shutil
from pathlib import Path
import multiprocessing
from joblib import Parallel, delayed

ABOUT = '''
This takes the following arguments
--patient_record or -p
    path to patient record file or a directory containing patient files.
--output_dir or -o
    Optional. Directory to save the JSON-parsed Metamap output.
   
--metamap or -m
    Metamap path. 

--mmi or -i
    Whether or not to use MMI.
    Default: False.
    If you set this to True, then --parse should be False and vice versa.
  
--parse or -j
    Whether or not to parse the metamap output into a JSON output.
    Default: False
--use_neg or -n
    Whether or not to consider the negative markers when parsing.
    Default: False
    
--keep_temp or -k:
    Keep TEMP directory.
    Default: False.
    If False, the TEMP directory will be deleted after operation.
--use_multiprocessing or -m
    Default False
    Whether or not to use multiprocessing
    
'''

#python metamap.py --patient_record /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/data/output/patient6_en.txt --metamap /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/public_mm/bin/metamap20 --output_dir /mnt/c/Users/USER/Desktop/PRETTY --parse --keep_temp

def conv_command(input_file):
    print('----Code to convert file---')
    cmd = ['java','-jar','replace_utf8.jar']
    output_file = input_file.split('.')[0]+'conv.'+input_file.split('.')[1]
    cmd+=[input_file,'>',output_file]
    return ' '.join(cmd)
  
def read_lines(file_name, fast_forward_to, batch_size):
    sentences = list()
    with open(file_name, 'r',) as fp:
        
        f=fp.readlines()
        return f
def replace_utf8(input_file,filepart,TEMP_DIR):
    cmd = ['java','-jar','replace_utf8.jar']
    output_file_save = os.path.join(TEMP_DIR,f'{filepart}')
    with open(output_file_save,'w+') as o_f:
        cmd+=[input_file]
        proc = subprocess.Popen(cmd , stdout=o_f, stderr=subprocess.PIPE)
        proc.wait()
    return output_file_save
        

def extract(file,TEMP_DIR,useMMI,OUTPUT_METAMAP_DIR,METAMAP_PATH,DEBUG,use_only_snomed,OUTPUT_PARSED_DIR,PARSE,USED_PATIENT_FILES):
    
    ERR_FILES=[]
    filepart = str(Path(file).name).split('.txt')[0]

    CLINICAL_TEXT_FILE = replace_utf8(file,filepart+'.txt',TEMP_DIR)

    if useMMI:
        output_file = os.path.join(OUTPUT_METAMAP_DIR,f"{filepart}_mmi.json")
    else: 
        output_file = os.path.join(OUTPUT_METAMAP_DIR,f"{filepart}.json")

    if output_file not in USED_PATIENT_FILES:
        try:
            mm = Metamap(METAMAP_PATH,use_only_snomed,debug=DEBUG,usemmi=useMMI)
        except Exception as metamap_error:
            raise Exception(f'Problem loading Metamap. See error below. \n {metamap_error}')

        timeout=1000

        try:
            mmos = mm.parse(CLINICAL_TEXT_FILE,output_file,timeout=timeout)
            
            if PARSE:
                json_output= os.path.join(OUTPUT_PARSED_DIR,f"{filepart}.json")
                convert(output_file,json_output)
            
        except Exception as e:
            print(e)
            ERR_FILES.append(file)
            pass
        return ERR_FILES
    else:
        return []
        
            

def main(args):

    DEBUG=False
    CONVERT_UTF8=False
    use_only_snomed=True
    useMMI = False
    OUTPUT_DIR = None
    HOME_FILE=None
    METAMAP_PATH = None
    PARSE=False
    USE_NEG=False
    KEEP_TEMP = False
    USE_MULT = False
    PATIENT_FILES=[]
    
    
    try:
        opts, args = getopt.getopt(args,'p:o:m:ijnkm',["patient_record =","output_dir =","metamap =","mmi","parse","use_neg","keep_temp","use_multiprocessing"])
    except getopt.GetoptError as e:
        print ('metamap.py'+'\n'+ABOUT)
        sys.exit(2)

    for opt, arg in opts:
        opt=opt.strip()
        if opt in ['--patient_record','-p']:
            HOME_FILE = arg
        elif opt in ["--output_dir", "-o"]:
            OUTPUT_DIR= arg
        elif opt in ["--metamap", "-m"]:
            METAMAP_PATH= arg
        elif opt in ["--parse", "-j"]:
            PARSE=True
        elif opt in ["--use_neg", "-n"]:
            USE_NEG=True
        elif opt in ["--mmi", "-i"]:
            useMMI=True
        elif opt in ["--keep_temp", "-k"]:
            KEEP_TEMP=True
        elif opt in ["--use_multiprocessing", "-m"]:
            USE_MULT=True
        
    if METAMAP_PATH==None:
        raise Exception(f'Metamap path not specified!')
    if not os.path.exists(METAMAP_PATH):
        raise Exception(f'Metamap path does not exist. The Metamap path specified was {METAMAP_PATH}')
        
    if PARSE:
        if useMMI:
            raise Exception(f'Cannot use MMI when --parse is set because parsing cannot be done on MMI output.')
    
    if HOME_FILE==None:
        raise Exception(f"--patient_record (-p) cannot be empty!")
        
    if not os.path.exists(HOME_FILE):
        
        HOME_FILE = os.path.join(os.getcwd(),HOME_FILE)
        if not os.path.exists(HOME_FILE):
            raise Exception(f'Could not find the given patient record file.')
    
    if OUTPUT_DIR ==None:
        OUTPUT_DIR = Path(HOME_FILE).parent.absolute()
    elif not os.path.exists(OUTPUT_DIR):
        raise Exception(f'Output directory {OUTPUT_DIR} does not exist. Please create the directory and run again.')
        
        
    if os.path.isdir(HOME_FILE):
        #It is a dir containing the patient record files.
        files = [f.name for f in os.scandir(HOME_FILE)]
        PATIENT_FILES = [os.path.join(HOME_FILE,f) for f in files]
    else:
        #It is a single file
        PATIENT_FILES = [HOME_FILE]
        
    if use_only_snomed:
        print('Using only SNOMED CT for extraction...')

    
    
    ERR_FILES=[]
    
    #TEMP DIR
    TEMP_DIR = os.path.join(OUTPUT_DIR,'TEMP')
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    
    
    OUTPUT_METAMAP_DIR = os.path.join(OUTPUT_DIR,'FROM_METAMAP')
    if not os.path.exists(OUTPUT_METAMAP_DIR):
        os.makedirs(OUTPUT_METAMAP_DIR)
    
    if PARSE:
        OUTPUT_PARSED_DIR = os.path.join(OUTPUT_DIR,'PARSED_OUTPUT')
        if not os.path.exists(OUTPUT_PARSED_DIR):
            os.makedirs(OUTPUT_PARSED_DIR)
    USED_PATIENT_FILES = list(set([f.name for f in os.scandir(OUTPUT_PARSED_DIR)]))
    
    if not USE_MULT:
        with tqdm(total = len(PATIENT_FILES)) as pbar:
            for file in PATIENT_FILES:
                
                filepart = str(Path(file).name).split('.txt')[0]
                
                CLINICAL_TEXT_FILE = replace_utf8(file,filepart+'.txt',TEMP_DIR)

                if useMMI:
                    output_file = os.path.join(OUTPUT_METAMAP_DIR,f"{filepart}_mmi.json")
                else: 
                    output_file = os.path.join(OUTPUT_METAMAP_DIR,f"{filepart}.json")
                
                if output_file not in USED_PATIENT_FILES:
            
                    try:
                        mm = Metamap(METAMAP_PATH,use_only_snomed,debug=DEBUG,usemmi=useMMI)
                    except Exception as metamap_error:
                        raise Exception(f'Problem loading Metamap. See error below. \n {metamap_error}')
                  
                    timeout=1000

                    try:
                        mmos = mm.parse(CLINICAL_TEXT_FILE,output_file,timeout=timeout)
                        
                        if PARSE:
                            json_output= os.path.join(OUTPUT_PARSED_DIR,f"{filepart}.json")
                            convert(output_file,json_output)
                        
                    except Exception as e:
                        print(e)
                        ERR_FILES.append(file)
                        continue
                        
                
                pbar.update(1)
    else: 
        num_cores=multiprocessing.cpu_count()
        print(f'Using multiprocessing with {num_cores} cores.')
        ERR_FILES = Parallel(n_jobs=num_cores)(delayed(extract)(file,TEMP_DIR,useMMI,OUTPUT_METAMAP_DIR,METAMAP_PATH,DEBUG,use_only_snomed,OUTPUT_PARSED_DIR,PARSE,USED_PATIENT_FILES) for file in tqdm(PATIENT_FILES))
        ERR_FILES  =[e for e in ERR_FILES if e!=[]]
        
        
    if ERR_FILES!=[]:
    
        print(f'I had issues working on the following files: \n {ERR_FILES}')
        
    if not KEEP_TEMP:
        shutil.rmtree(TEMP_DIR)


if __name__ == "__main__":
   main(sys.argv[1:])  

#'/mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/public_mm/bin/metamap20'
#/mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/publiclinuxmain2018/publicmm/bin/metamap18 -c -Q 4 -y -K --sldi -I --XMLf1 --negex /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/rsample3clean.txt /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/metamap_output.txt
   
#java -jar replace_utf8.jar /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/rsample3.txt > /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/random/rsample3.txt