import os
import re
import pandas as pd
import sys, getopt
from pathlib import Path
from tqdm import tqdm
from langdetect import detect
from random import sample

ABOUT = '''
This takes the following arguments
--file or -f
    path to CSV file with the patient records, just like the one given for this project.
    Each row is a patient record.
--output_dir or -o
    Optional. Directory to save the preprocessed patient records. If not given, then the current working directory is used.
--check_lang or -l
    Default False.
    Whether or not to check the language of the patient record. If True, the language code ('en','fr','undefined') will be appended to the patient file
    
--columns or -c
    Columns to use from the CSV files for the patient records. Should be a string with columns seperated by |
    For example, if you want to consider the 'CONCERN', 'HISTORY' and 'PHYSICAL_EXAM' columns then pass:
    -- columns 'CONCERN|HISTORY|PHYSICAL_EXAM'
    
    If the columns are not passed, it uses the default columns: 'CONCERN|HISTORY|ASSESSMENT_AND_PLAN|PHYSICAL_EXAM|DX_DESCRIPTIONS'
--txt or -t
    Default False.
    Set to true if your patient records are in TXT files instead of CSV with columns.
    
--keep_only_en or -e
    Default False
    Whether or not to keep only patient records detected as English
'''

def read_txt(f,enc='utf8'):
    with open(f,'r',encoding=enc) as out_:
        return[o_ for o_ in out_.readlines()]
def read(f):
    try:
        df=pd.read_csv(f,keep_default_na=False)
    except Exception:
        try:
            df=pd.read_csv(f,sep='\t')
        except Exception:
            raise Exception(f'Could not read file {f}')
    return df
     
def cleanhtml(raw_html):
    # https://stackoverflow.com/a/12982689/11814682
    #cleanr = re.compile('<.*?>')
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

     
def preprocess_sentence(w):
   w = cleanhtml(w)
   #w=re.sub(r"DISCLAIMER The Add Diagnosis’ function is used solely for data analysis purposes, and thus does not represent an official diagnosis for the patient\. As a result, the content will never be communicated with the patient during or after the consultation, excluding if the medical file is requested\.The collected diagnoses suggestions merely serve as a method to improve and target internal medical protocols, training, and support based on the results of these outcome measures\.ASSESSMENT",'ASSESSMENT',w)
   w=re.sub(r"DISCLAIMER[\w\W]+ASSESSMENT",'ASSESSMENT',w)
   w=re.sub(r"DISCLAIMER[\w\W]+support based on the results of these outcome measures.",'ASSESSMENT',w)
   w=re.sub(r"AVERTISSEMENT[\w\W]+ÉVALUATION ",'ÉVALUATION ',w,flags=re.UNICODE)
   w= re.sub(r'^[\w\W]+Reason for consultation','Reason for consultation ',w)
   w=re.sub(r'^[\w\W]+Raison de consultation','Raison de consultation ',w,flags=re.UNICODE)
   w=re.sub(r'(.)PLAN(.\s)',r'\1\nPLAN\n\2',w)
   w=re.sub(r'([a-z])([A-Z][a-z])',r'\1. \2',w)
   #w= re.sub(r'PLAN',' PLAN ',w)
   
   w= w.strip()
   w = cleanhtml(w)
   #w=re.sub(r'[\n\r\t]+',' ',w)
   #w=re.sub(r'[a-zA-Z ]+:[ “"«]','',w)
   #w=re.sub(r'[^A-Za-z0-9\s\’\-\.,]+','',w)
   
   #w = re.sub(r"[;@#'?!&$]+\ *", " ", w)   
   w= re.sub(r'[\․●□•☑☐�≥ⓝ💤☺😭↑◆®…😊▪↓©ø!"#$%&\(\)\*\+;<=>?@\[\]^_`‘→{|}~«»”“]+','',w)
   #w = re.sub(r'^[0-9,\-\. ]+','',w)
   w = re.sub(r' [ ]+',' ',w)
   #w = re.sub(r' [0-9]+ [-,] [0-9]+',' ',w)
   #w = re.sub(r' [0-9]+ [0-9 ]+ [0-9]+',' ',w)
   w=re.sub(r' - ',' ',w)
   w = re.sub(r' [ ]+',' ',w)
   w = re.sub(r"' '",'',w)
   w=re.sub(r'\.[ \.]+','. ',w)
   w=re.sub(r'\.([a-zA-Z])',r'. \1',w)
    
   return w

def preprocess_sentence_rn(w):
   #w=re.sub(r"DISCLAIMER The Add Diagnosis’ function is used solely for data analysis purposes, and thus does not represent an official diagnosis for the patient\. As a result, the content will never be communicated with the patient during or after the consultation, excluding if the medical file is requested\.The collected diagnoses suggestions merely serve as a method to improve and target internal medical protocols, training, and support based on the results of these outcome measures\.ASSESSMENT",'ASSESSMENT',w)
   w=re.sub(r"DISCLAIMER[\w\W]+ASSESSMENT",'ASSESSMENT',w)
   w=re.sub(r"DISCLAIMER[\w\W]+support based on the results of these outcome measures.",'ASSESSMENT',w)
   w=re.sub(r"AVERTISSEMENT[\w\W]+ÉVALUATION ",'ÉVALUATION ',w,flags=re.UNICODE)
   w= re.sub(r'^[\w\W]+Reason for consultation','Reason for consultation ',w)
   w=re.sub(r'^[\w\W]+Raison de consultation','Raison de consultation ',w,flags=re.UNICODE)
  
   w= re.sub(r'PLAN',' PLAN ',w)
   
   w= w.strip()
   w = cleanhtml(w)
   w=re.sub(r'[\n\r\t]+',' ',w)
   #w=re.sub(r'[a-zA-Z ]+:[ “"«]','',w)
   #w=re.sub(r'[^A-Za-z0-9\s\’\-\.,]+','',w)
   
   #w = re.sub(r"[;@#'?!&$]+\ *", " ", w)   
   w= re.sub(r'[\․●□•☑☐�≥ⓝ💤☺😭↑◆®…😊▪↓©ø!"#$%&\(\)\*\+;<=>?@\[\]^_`‘→{|}~«»”“]+','',w)
   #w = re.sub(r'^[0-9,\-\. ]+','',w)
   w = re.sub(r' [ ]+',' ',w)
   #w = re.sub(r' [0-9]+ [-,] [0-9]+',' ',w)
   #w = re.sub(r' [0-9]+ [0-9 ]+ [0-9]+',' ',w)
   w=re.sub(r' - ',' ',w)
   w = re.sub(r' [ ]+',' ',w)
   w = re.sub(r"' '",'',w)
   w=re.sub(r'\.[ \.]+','. ',w)
    
   return w
 

    
def separate(s):
    s = re.sub(r'(\w+)‣(\w+)','\1\n\2',s)
    return s
    
def preprocess_all(w):
    w = preprocess_sentence(w)
    w= re.sub(r'(\w)\.(\W)',r'\1.\n\2',w)
    w= re.sub(r'^[ \r]+','',w,flags=re.UNICODE)
    w = re.sub(r'\n[\n]+','\n',w,flags=re.UNICODE)
    w = separate(w)
    return w


def is_number(x):
    try:
        s=int(x)
        return True
    except Exception:
        return False



def fast_detect_lang(s,num=7):
    cands = [a for a in s.split('\n') if a.strip()!='' and len(a.split(' '))>3]
    ids = [i for i in range(len(cands))]
    if ids!=[]:
        if len(cands)<=num:
            num = len(cands)-1
        val = sample(ids,num)
        try:
            lang_detected = [detect(cands[v]) for v in val]
        except Exception:
            return '_undefined'
        en = len([l for l in lang_detected if l=='en'])
        fr = len([l for l in lang_detected if l=='fr'])
        if en > fr:
            #It is a largely English document
            return '_en'
        else:
            #It is a largely French document
            return '_fr'
    else:
        return '_undefined'
 
 

def main(args):
    try:
        opts, args = getopt.getopt(args,'f:o:c:lte',["file =","output_dir =","columns =","check_lang","txt","keep_only_en"])
    except getopt.GetoptError as e:
        print ('preprocess.py --file <CSV file containing patient records> --output_dir <path to dir to save preprocessed patient records>' +'\n'+ABOUT)
        sys.exit(2)
    OUTPUT_DIR = None
    HOME_FILE=None
    CHECK_LANG = False
    COLUMNS=None
    IS_TXT =False
    KEEP_ONLY_EN=False
    
    for opt, arg in opts:
        opt=opt.strip()
        if opt in ['--file','-f']:
            HOME_FILE = arg
        elif opt in ["--output_dir", "-o"]:
            OUTPUT_DIR= arg
        elif opt in ['--check_lang','-l']:
            CHECK_LANG = True
        elif opt in ['--columns','-c']:
            COLUMNS = arg
        elif opt in ['--txt','-t']:
            IS_TXT=True
        elif opt in ['--keep_only_en','-e']:
            KEEP_ONLY_EN=True
            
    if KEEP_ONLY_EN and not CHECK_LANG:
        print(f'Checking language has been set to True since you specified to keep only English.')
        CHECK_LANG=True
    
    if HOME_FILE==None:
        raise Exception(f"--file or -f cannot be empty")
        
    if not os.path.exists(HOME_FILE):
        
        HOME_FILE = os.path.join(os.getcwd(),HOME_FILE)
        if not os.path.exists(HOME_FILE):
            raise Exception(f'CSV file for patient records not given')
    
    if OUTPUT_DIR ==None:
        OUTPUT_DIR = Path(HOME_FILE).parent.absolute()
    elif not os.path.exists(OUTPUT_DIR):
        raise Exception(f'Output directory {OUTPUT_DIR} does not exist. Please create the directory and run again.')
        
        
    if os.path.isdir(HOME_FILE):
        #It is a dir containing CSVs of patient data
        files = [f.name for f in os.scandir(HOME_FILE)]
        if not IS_TXT:
            dfs = [read(os.path.join(HOME_FILE,f)) for f in files]
            df = pd.concat(dfs)
        else:
            df=[]
            for f in files:
                df.append('\n'.join(read_txt(os.path.join(HOME_FILE,f))))
    else:
        #It is a single file
        if not IS_TXT:
            df = read(HOME_FILE)
        else:
            df = ['\n'.join(read_txt(HOME_FILE))]
    
    #We have our pandas DataFrame of patient records.
    #Preprocess and save output. 
    #Option to check language. CHECK_LANG
    if not IS_TXT:
        if COLUMNS == None:
            COLUMNS = ['CONCERN', 'HISTORY','ASSESSMENT_AND_PLAN', 'PHYSICAL_EXAM','DX_DESCRIPTIONS']
        else:
            COLUMNS = [c.strip() for c in COLUMNS.split('|') if c!=' ' and c!='']
        try:
            df=df[COLUMNS]
        except Exception:
            raise Exception(f'Error with columns: {COLUMNS}.\n Please check that the columns chosen exist in the CSV file')
        
        print(f'Using columns: {COLUMNS}')
        df['text'] = df[COLUMNS[0]].astype(str)
        for col in COLUMNS[1:]:
            df['text'] = df['text'] + '\n'+df[col].astype(str)
        
        df = df[df['text']!='']
        all_sents = df['text'].tolist()
        all_sents = [a for a in all_sents]
    else:
        all_sents = df
    print(f'Extracting patient records...')
    with tqdm(total = len(all_sents)) as pbar:
        for i in range(len(all_sents)):
            filename = f'patient{i}'
            if CHECK_LANG:
                lang_det = fast_detect_lang(all_sents[i])
                filename=filename+lang_det+'.txt'
                if KEEP_ONLY_EN:
                    if lang_det!='_en':
                        filename=None
            else:
                filename+='.txt'
              
            if filename!=None:
                with open(os.path.join(OUTPUT_DIR,filename),'w+',encoding='utf8') as f:
                    f.write(preprocess_all(all_sents[i]))
            pbar.update(1)
    print(f'Saved patient records to {OUTPUT_DIR}')
    print('ALL DONE!')      
if __name__ == "__main__":
   main(sys.argv[1:])  

