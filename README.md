# text-snomed
The Project on extracting SNOMED CT concepts from free-form text

# Usage
You first have to follow this [guide](https://metamap.nlm.nih.gov/Installation.shtml) to install the MetaMap to your local computer.
In `metamap.py` you provide the following parameters:
```[python]
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
`METAMAP_PATH` refers to the path to the MetaMap (ending in `<parent directory>/bin/metamap`).  

`SEMANTIC_FILE_PATH` is the path to [this file](https://metamap.nlm.nih.gov/Docs/SemanticTypes_2018AB.txt).

Important: MetaMap18 does not rcognize non-ASCII characters. So if you're using MetaMap18, you need to convert it using [this](https://metamap.nlm.nih.gov/ReplaceUTF8.shtml).

