# Stanza - Accuracy scores after treebank harmonization

Models have been trained with:
* fastText embeddings
* default parameters
* [harmonized version](https://github.com/fjambe/Latin-variability/tree/main/harmonization/harmonized-treebanks) of train, dev & test data

The evaluation is carried out through UD `conll18_ud_eval.py` script.

||ITTB||LLCT||Perseus||PROIEL||UDante||
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
||LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|
|`la_ittb-hm_parser.pt`|||||||||||
|`la_llct-hm_parser.pt`|||||||||||
|`la_perseus-hm_parser.pt`|49.83%|60.02%|37.46%|48.16%|**58.33%**|**67.94%**|55.85%|65.01%|38.74%|51.84%|
|`la_proiel-hm_parser.pt`|51.46%|61.25%|42.26%|56.12%|47.19%|58.50%|**80.75%**|**84.31%**|40.92%|53.17%|
|`la_udante-hm_parser.pt`|63.11%|72.05%|43.86%|56.28%|53.05%|63.77%|53.05%|63.86%|**57.91%**|**67.22%**|
