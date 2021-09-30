import pandas as pd
from langdetect import detect
import re,os


def cleanhtml(raw_html):
    # https://stackoverflow.com/a/12982689/11814682
    #cleanr = re.compile('<.*?>')
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def preprocess_sentence(w):
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
   w=re.sub(r'[^a-zA-Z]','',w,flags=re.UNICODE) #only for langdetect
   w=re.sub('[0-9]+','',w) #only for langdetect
   #w=re.sub(r'[a-zA-Z ]+:[ “"«]','',w)
   #w=re.sub(r'[^A-Za-z0-9\s\’\-\.,]+','',w)
   
   #w = re.sub(r"[;@#'?!&$]+\ *", " ", w)   
   w= re.sub(r'[\․●□•☑☐�≥ⓝ💤☺😭↑◆®…😊▪↓©ø!"#$%&\(\)\*\+;<=>?@\[\]^_`‘→{|}~«»”“]+','',w)
   w=re.sub(r'^[\․●□•☑☐�≥ⓝ💤☺😭↑◆®…😊▪↓©ø!"#$%&\(\)\*\+;<=>?@\[\]^_`‘→{|}~«»”“,\.-]','',w)
   #w = re.sub(r'^[0-9,\-\. ]+','',w)
   w = re.sub(r' [ ]+',' ',w)
   #w = re.sub(r' [0-9]+ [-,] [0-9]+',' ',w)
   #w = re.sub(r' [0-9]+ [0-9 ]+ [0-9]+',' ',w)
   w=re.sub(r' - ',' ',w)
   w = re.sub(r' [ ]+',' ',w)
   w = re.sub(r"' '",'',w)
   w=re.sub(r'\.[ \.]+','. ',w)
    
   return w
   

def get_lang(s):
  n_en=0
  n_fr=0
  n_undefined=0
  count=0

  for b in str(s).split(' '):

    a=preprocess_sentence(b)
    
    if a!=' ' and a!='':
      try:
        lang = detect(a)
      except Exception:
        print(f'Before: {b}')
      
        print(f'After: {a}')
        raise Exception(f'Problem with:{a}')
      count+=1
      if lang=='en':
        n_en+=1
      elif lang=='fr':
        n_fr+=1
      else:
        n_undefined+=1

  #print(f'English: {n_en} | French: {n_fr} | Undefined language {n_undefined} | Total: {count}')
  return f'{n_en}|{n_fr}|{n_undefined}|{count}'
 
def main_lang(s):
  a = s.split('|')
  n_en=int(a[0])
  n_fr=int(a[1])
  if n_en > n_fr:
    return 'English'
  elif n_fr > n_en:
    return 'French'
  else:
    return 'English and French' 
   

df = pd.read_csv('all_text.tsv',sep='\t')

df['langs'] = df['text'].apply(lambda x: get_lang(x))
df['main language'] = df['langs'].apply(lambda x: main_lang(x))

df.to_csv('ALL_LANG.tsv', sep='\t')
