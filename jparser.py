import json
import pandas as pd
from tosnomed import get_snomed_mapping



#{CUI, term, preferred,semantic_type,is_abbrv [1,0],is_neg[1,0]}


print('Loading sematic types abbreviations...')
sem_dict={}
with open('SemanticTypes.txt','r') as f:
    sem = f.readlines()
    for s in sem:
        sem_dict.update({s.split('|')[0].strip():s.split('|')[2].strip()})
print('Status: Done...')

  
def load_AA(doc):
    result=[]
    aas= doc["AAs"]
    if aas!=[]:
        for aa in aas:
            snomed_map_ = get_snomed_mapping(aa['AACUIs'])
            if snomed_map_!=None:
                out={}
                out['CUI'] = aa['AACUIs']
                out['snomed_map']= snomed_map_
                out['term'] = aa['AAExp'] + f" ({aa['AAText']})"
                out['is_abbrv']=1
                out['is_neg']=0
                result.append(out)
    return result
    
def load_Negation(doc):
    result=[]
    negs= doc["Negations"]
    if negs!=[]:
        for neg in negs:
            out={}
            out['is_abbrv']=0
            neg_trigger = neg['NegTrigger']
            for neg_c in neg['NegConcepts']:
                out['CUI'] = neg_c['NegConcCUI']
            out['UMLS_term'] = neg_trigger + ' '+neg_c['NegConcMatched']
            out['is_neg']=1
            result.append(out)
    return result
  

def load_Utterances(doc):
    result=[]
    utts= doc["Utterances"]
    if utts!=[]:
        for utt in utts:
           
            utt_text = utt['UttText']
            utt_phrases = utt['Phrases']
            if utt_phrases!=[]:
                for utt_phrase in utt_phrases:
                    utt_p = utt_phrase['PhraseText']
                    mappings = utt_phrase['Mappings']
                    if mappings!=[]:
                        for mapping in mappings:
                            mp_candidates = mapping['MappingCandidates']
                            mp_score = mapping['MappingScore']
                            for mp_cd in mp_candidates:
                                snomed_map = get_snomed_mapping(mp_cd['CandidateCUI'])
                                if snomed_map!=None:
                                    out={}
                                    out['CUI'] = mp_cd['CandidateCUI']
                                    out['snomed_map']= snomed_map
                                    out['UMLS_term'] = mp_cd['CandidateMatched']
                                    #out['preferred'] = mp_cd['CandidatePreferred']
                                    
                                    out['score'] = mp_score
                                    out['semantic_types'] = [sem_dict[a] for a in mp_cd['SemTypes']]
                                    out['is_neg'] = int(mp_cd['Negated'])
                                    out['phrase'] = utt_p
                                    out['utterance'] = utt_text                            
                                    result.append(out)
                                
                            
                    
                    
            
          
    return result
    
    
  
def convert(JSON_FILE,OUTPUT_FILE):
    #print(f'Working on conversion...')
    documents=[]
    with open(JSON_FILE) as fp:
        documents = json.load(fp)['AllDocuments']

     
    if documents!=[]:
        final_result=[]
        for document in documents:
            #print(document)
            result = load_AA(document['Document'])
            result+=load_Utterances(document['Document'])
            final_result.extend(result)
        if final_result==[]:
            raise Exception('Final result is empty!')
        else:
            with open(OUTPUT_FILE,'w+') as f:
                json.dump(final_result,f)
                
            '''
            OUTPUT_FILE_JSONL = OUTPUT_FILE.split('.json')[0]+'.jsonl'
            with open(OUTPUT_FILE_JSONL,'w+') as f:
                for res in final_result:
                    json.dump(res,f)
                    f.write('\n')
            '''
