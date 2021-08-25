# text-snomed
Extracting SNOMED CT concepts from free-form text.

# Usage of MetaMap extractor
1. You first have to follow this [guide](https://metamap.nlm.nih.gov/Installation.shtml) to install the MetaMap to your local computer. Also, start the `SKR/Medpost Part-of-Speech Tagger Server` and the `Word Sense Disambiguation (WSD) Server`
2. Set up `pymm` by downloading it [here](https://drive.google.com/drive/folders/1sd9vmx49SxYncOoC2AXLPudO3lo5p5VH?usp=sharing) and doing the following:
  ```
  cd pymm
  python setup.py install
  ```

3. In `metamap.py` you provide the following parameters:

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

