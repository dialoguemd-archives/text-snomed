# text-snomed
Extracting SNOMED CT concepts from free-form text.

## Usage of MetaMap extractor
1. You first have to follow this [guide](https://metamap.nlm.nih.gov/Installation.shtml) to install the MetaMap to your local computer. Also, start the `SKR/Medpost Part-of-Speech Tagger Server` and the `Word Sense Disambiguation (WSD) Server`
2. Set up `pymm` by downloading it [here](https://github.com/chrisemezue/pymm) and doing the following:
  ```
  cd pymm
  python setup.py install
  ```
## Using text-snomed
Here is my guide to my work on building SNOMED expressions from patient record data. The guide is divided into sections, with files that wrap functionalities together.
### Pre-requisites
1. Create and activate a virtual environment.
2. Install the [requirements.txt](https://drive.google.com/file/d/1SZ1qNXVaqiibt8OOXmZYqcnqC5HtX_qY/view?usp=sharing) file.
### Preprocessing the patient records
The first - and most important prerequisite - is to pre-process the patient records. This is important for the Metamap to capture the correct medical concept. 

This is handled by the `preprocess.py` file.
```python
'''
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
```
1. The function above creates a *patient record* by merging the columns specified by`--columns` then pre-processing them.
2. The`--check_lang` will give you approximate language in the patient record.
3. Another  important thing the function does is to separate each sentence (or independent information about the patient) line by line. This helps Metamap better extract the medical concepts.

```bash
python preprocess.py --file <PATIENT FILE OR DIRECTORY> --output_dir ./data/output/ --check_lang
```

### Extracting medical concepts from patient records with Metamap
This is handled by the `metamap.py` file.
```bash
python metamap.py --patient_record /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/data/output/patient6_en.txt --metamap /mnt/c/Users/USER/Desktop/MASTERS/MILA/DIALOGUE/public_mm/bin/metamap20 --output_dir /mnt/c/Users/USER/Desktop/PRETTY --parse --keep_temp
```

```python
'''
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
```
1. - Before the patient record file is passed to Metamap, all its non-ASCII characters should be replaced with its ASCII equivalent using the [replaceutf8 jar file](https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/additional-tools/ReplaceUTF8.html) provided by Metamap. We wrapped everything conveniently in the program so you don't have to do anything. The TEMP directory is used to store the temporary files from the replaceutf8 command. You can decide to keep them if you want using the `--keep_temp` argument.
2. You must start the SKR/Medpost Part-of-Speech Tagger Server and the Word Sense Disambiguation (WSD) Server (optional) before running this.

### SnomedClassifier
SnomedClassifier is the model built and trained to identify the relationship between a medical phrase and the extracted medical concepts. The model architecture is inspired by [this paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7233039/).
1. I used `dmis-lab/biobert-base-cased-v1.2` pretrained weights for the embedding representation. This is a pretrained [BioBert](https://academic.oup.com/bioinformatics/article/36/4/1234/5566506) model, further finetuned on PubMed 1M dataset. Further details about the model can be found [here](https://github.com/dmis-lab/biobert).
2. I froze the embedding model during training, so that SnomedClassifier only updates the weights of the BiLSTM and fully-connected layers.

```python
METAMAP_PATH = '<PATH TO METAMAP>'
CLINICAL_TEXT_FILE = '<PATH TO CLINICAL TEXT FILE>'
COMPRESSED_FILE = '<Where to save the compressed form of MetaMap output>'
SEMANTIC_FILE_PATH = '<PATH TO SEMANTIC FILE>' #This file contains the full meanings of the semantic abbreviations given in the MetaMap output. 

METAMAP_VERSION = '2020' #[Option of 2020 or 2018. You have to install the correct MetaMap for the version you choose]
DEBUG=False
CONVERT_UTF8=True
use_only_snomed=True #Whether or not to use only SNOMED CT in MetaMap extraction
timeout=50 #Timeout for extraction
```
`METAMAP_PATH` refers to the path to the MetaMap (ending in `/bin/metamap`).  

`SEMANTIC_FILE_PATH` is the path to [this file](https://metamap.nlm.nih.gov/Docs/SemanticTypes_2018AB.txt).

4. Run `metamap.py`


**Important**: MetaMap18 does not rcognize non-ASCII characters. So if you're using MetaMap18, you need to convert it using [this](https://metamap.nlm.nih.gov/ReplaceUTF8.shtml). MetaMap20 already has this issue taken care of. But it's safe to always convert your `CLINICAL_TEXT_FILE` first. 
> If you set `CONVERT_UTF8` to True, it prints the code for the conversion on your terminal.e 

The `pymm` folder is my adaptation of [this repository](https://github.com/smujjiga/pymm).


- - - -
Correspondence to chris.emezue@gmail.com

