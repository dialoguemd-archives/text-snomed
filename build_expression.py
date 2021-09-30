import os
import json
import torch
import torchtext
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix,f1_score
from transformers import AutoTokenizer, AutoModel
import scispacy
import spacy
import random
import sys, getopt
from pathlib import Path
from tqdm import tqdm
#nlp = spacy.load("en_ner_bionlp13cg_md")
nlp = spacy.load("en_core_sci_md")
device = torch.device('cuda' if True and torch.cuda.is_available() else 'cpu')



ABOUT = '''
This takes the following arguments
--file or -f
    Parsed output file from Metamap or directory containing the files.
--ckpt or -c
    Model checkpoint
--output_dir or -o
    Optional. Directory to save the expressions. If not given, then the parent directory of --file will be used.
--class_map or -l
    The class map JSON file. Required.
'''


def encode_text(text):
  return tokenizer.encode(text = text,return_tensors = 'pt')

#This part adapted from https://towardsdatascience.com/bert-text-classification-using-pytorch-723dfb8b6b5b


# Save and Load Functions

def save_checkpoint(save_path, model, optimizer, valid_loss):

    if save_path == None:
        return
    
    state_dict = {'model_state_dict': model.state_dict(),
                  'optimizer_state_dict': optimizer.state_dict(),
                  'valid_loss': valid_loss}
    
    torch.save(state_dict, save_path)
    #print(f'Model saved to ==> {save_path}')


def load_checkpoint(load_path, model):

    state_dict = torch.load(load_path)
    print(f'Model loaded from <== {load_path}')
    
    model.load_state_dict(state_dict['model_state_dict'])
    
    return model


def save_metrics(save_path, train_loss_list, valid_loss_list, global_steps_list):

    if save_path == None:
        return
    
    state_dict = {'train_loss_list': train_loss_list,
                  'valid_loss_list': valid_loss_list,
                  'global_steps_list': global_steps_list}
    
    torch.save(state_dict, save_path)
    #print(f'Model saved to ==> {save_path}')


def load_metrics(load_path):

    if load_path==None:
        return
    
    state_dict = torch.load(load_path)
    print(f'Model loaded from <== {load_path}')
    
    return state_dict['train_loss_list'], state_dict['valid_loss_list'], state_dict['global_steps_list']


def compute_metrics(labels,probs):
  preds = F.log_softmax(probs)
  acc_preds = torch.argmax(preds,dim=1).squeeze().cpu().tolist()
  labels = labels.squeeze().cpu().tolist()
  acc = accuracy_score(labels,acc_preds)
  f1 = f1_score(labels,acc_preds,average='micro')
  return {'f1': f1, 'accuracy':acc} 


class SnomedClassifier(nn.Module):

    def __init__(self, model_type,NUM_CLASSES,dimension=128,num_layers=1,dropout=0.2):
        super(SnomedClassifier, self).__init__()
        
        
        self.BERT_Embedding_model = AutoModel.from_pretrained(model_type)
        self.dimension = dimension
        self.lstm = nn.LSTM(input_size=1,    #Because we are concatenating two BioBERT embeddings
                            hidden_size=self.dimension,
                            num_layers=num_layers,
                            bidirectional=True)
        
        self.dropout = nn.Dropout(p=dropout)
        self.fc = nn.Linear(1536*self.dimension*2, NUM_CLASSES)
        
        #Freeze BioBert which is used as embedding model
        for param in self.BERT_Embedding_model.parameters():
          param.requires_grad = False

    def forward(self, text1,text2):

        #text1 and text2 here are tokenized by BioBert's tokenizer

        res1 = self.BERT_Embedding_model.forward(input_ids=text1).pooler_output #768 dimensions
        res2 = self.BERT_Embedding_model.forward(input_ids=text2).pooler_output #768 dimensions

        final_emb = torch.cat((res1, res2), 1)
        final_emb=final_emb.unsqueeze(1)
        final_emb=final_emb.transpose(2,1)
      
        output, (h_n, c_n) = self.lstm(final_emb)
        flattened = output.view(output.size(0),-1)
        text_fea = self.fc(flattened)
        text_fea=self.dropout(text_fea)
        log_probs = torch.squeeze(text_fea, 1)
        
        return log_probs
    


def predict_relationship(model,tokenizer,sent1, sent2,classDict):
  softmax = nn.Softmax(dim=1)
  model.eval()
  with torch.no_grad():
    sent1_ = tokenizer.encode(sent1)
    sent2_ = tokenizer.encode(sent2)
    sent1_ , sent2_= torch.LongTensor(sent1_).unsqueeze(0).to(device), torch.LongTensor(sent2_).unsqueeze(0).to(device)
    output = model.forward(sent1_,sent2_)
    preds=softmax(output)
    rel_preds = torch.argmax(preds,dim=1).squeeze().cpu()
    rel = list(classDict.keys())[list(classDict.values()).index(rel_preds)] #https://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary  
    return rel    


def main(args):

    NUM_CLASSES=96
    BATCH_SIZE=128

    INPUT1_COL_NAME='source'
    INPUT2_COL_NAME='target'
    RELATIONSHIP_COL_NAME='relationshipID'
    model_type = 'dmis-lab/biobert-base-cased-v1.2'
    tokenizer = AutoTokenizer.from_pretrained(model_type)
    
    OUTPUT_DIR = None
    HOME_FILE=None
    CHECK_LANG = False
    COLUMNS=None
    CKPT_FILE=None
    CLASS_MAP=None
    PATIENT_FILES=[]
    
    try:
        opts, args = getopt.getopt(args,'f:o:c:l:',["file =","output_dir =","ckpt =","class_map ="])
    except getopt.GetoptError as e:
        print ('build_expression.py' +'\n'+ABOUT)
        sys.exit(2)
    
    
    for opt, arg in opts:
        opt=opt.strip()
        if opt in ['--file','-f']:
            HOME_FILE = arg
        elif opt in ["--output_dir", "-o"]:
            OUTPUT_DIR= arg
        elif opt in ["--ckpt", "-c"]:
            CKPT_FILE= arg
        elif opt in ["--class_map", "-l"]:
            CLASS_MAP= arg
        
    if CLASS_MAP==None:
        raise Exception(f'Class map (--class_map) is required.')
    
    if not os.path.exists(CLASS_MAP):
        print(f'The class file provided {CLASS_MAP} does not exist.')   
    
    if CKPT_FILE==None:
        raise Exception(f'Model checkpoint file is required.')
    
    if not os.path.exists(CKPT_FILE):
        raise Exception(f'The ckpt file provided {CKPT_FILE} does not exist.')
    
    if HOME_FILE==None:
        raise Exception(f"--file cannot be empty!")
        
    if not os.path.exists(HOME_FILE):
        
        HOME_FILE = os.path.join(os.getcwd(),HOME_FILE)
        if not os.path.exists(HOME_FILE):
            raise Exception(f'Could not find the given file (or directory).')
    
    if OUTPUT_DIR ==None:
        OUTPUT_DIR = Path(HOME_FILE).parent.absolute()
    elif not os.path.exists(OUTPUT_DIR):
        raise Exception(f'Output directory {OUTPUT_DIR} does not exist. Please create the directory and run again.')
        
    BUILD_EXPRESSON_DIR = os.path.join(OUTPUT_DIR,'SNOMED_EXPRESSION')
    if not os.path.exists(BUILD_EXPRESSON_DIR):
        os.makedirs(BUILD_EXPRESSON_DIR)
     
    if os.path.isdir(HOME_FILE):
        #It is a dir containing the files we want.
        files = [f.name for f in os.scandir(HOME_FILE)]
        PATIENT_FILES = [os.path.join(HOME_FILE,f) for f in files]
    else:
        #It is a single file
        PATIENT_FILES = [HOME_FILE]
        

    with open(CLASS_MAP,'r') as fp:
      classDict= json.load(fp)

    #Define model
    model = SnomedClassifier(model_type,NUM_CLASSES).to(device)

    #Load model weights
    model = load_checkpoint(CKPT_FILE, model)

    model = model.to(device)
    with tqdm(total = len(PATIENT_FILES)) as pbar:
        for file in PATIENT_FILES:
            with open(file,'r',encoding='utf8') as fp:
                data = json.load(fp)
            filepart = str(Path(file).name).split('.json')[0]
            
            with open(os.path.join(BUILD_EXPRESSON_DIR,f'{filepart}_expression.txt'),'a+') as output_exp:
                DELIMITER = '\n\r    '
                unique_utterances = set([d['utterance'] for d in data])
                for utt in unique_utterances:
                  print(f'Builing SNOMED expression for utterance: [{utt}]',file=output_exp)
                  data_utt = [d for d in data if d['utterance']==utt]
                  #Getting root word from dependency parser
                  doc = nlp(utt)
                  root_word=''
                  for token in doc:
                    if str(token.dep_)=='ROOT':
                      root_word = token.text
                  if root_word=='':
                    raise Exception(f'Error in dependency parser. Did not get a ROOT word!')
                  random_focus = ''
                  focus_concept = [d['snomed_map'] for d in data_utt if root_word in d['phrase'].split(' ')]
                  if focus_concept==[]:
                      #Take a random concept as focus concept
                      ids=[i for i in range(len(data_utt))]
                      random.shuffle(ids)
                      focus_concept =  [data_utt[ids[0]]['snomed_map']]
                      random_focus = '(from random focus)'
                  #print(f'Focus concept: {focus_concept}')
                  others = [d['snomed_map'] for d in data_utt if d['snomed_map'] not in focus_concept]
                  for f_c in focus_concept:
                    for snomed_concept in f_c:
                      s=f"[{str(snomed_concept['SNOMED term'])}]"+' '+random_focus+DELIMITER
                      for other in others:
                        for oth in other:
                          s+=f"|{predict_relationship(model,tokenizer,utt,oth['SNOMED term'],classDict)}| = [{oth['SNOMED term']}],"
                        s+=DELIMITER
                      print(s,file=output_exp)
                    
                  print('-'*150,file=output_exp)
    print(f'All Done. Expressions are saved in {BUILD_EXPRESSON_DIR}')

if __name__ == "__main__":
   main(sys.argv[1:])  
