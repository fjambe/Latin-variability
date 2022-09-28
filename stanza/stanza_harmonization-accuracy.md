# Stanza - Accuracy scores after treebank harmonization

Models have been trained with:
* fastText embeddings
* default parameters
* [harmonized version](https://github.com/fjambe/Latin-variability/tree/main/harmonization/harmonized-treebanks) of train, dev & test data

The evaluation is carried out through UD `conll18_ud_eval.py` script.

||ITTB||LLCT||Perseus||PROIEL||UDante||
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
||LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|
|`la_ittb-HM_parser.pt`|||||||||||
|`la_llct-HM_parser.pt`|||||||||||
|`la_perseus-HM_parser.pt`|49.83%|60.02%|37.46%|48.16%|**58.33%**|**67.94%**|55.85%|65.01%|38.74%|51.84%|
|`la_proiel-HM_parser.pt`|||||||||||
|`la_udante-HM_parser.pt`|63.11%|72.05%|43.86%|56.28%|53.05%|63.77%|53.05%|63.86%|**57.91%**|**67.22%**|
