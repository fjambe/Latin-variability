# Stanza - Accuracy scores after treebank harmonization

Models have been trained with:
* fastText embeddings
* default parameters
* [harmonized version](https://github.com/fjambe/Latin-variability/tree/main/harmonization/harmonized-treebanks) of train, dev & test data

The evaluation is carried out through UD `conll18_ud_eval.py` script.

||`la_ittb-hm_parser.pt`||`la_llct-hm_parser.pt`||`la_perseus-hm_parser.pt`||`la_proiel-hm_parser.pt`||`la_udante-hm_parser.pt`||
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
||LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|
|ITTB|**88.06%**|**90.02%**|45.97%|58.80%|49.83%|60.02%|51.46%|61.25%|63.11%|72.05%|
|LLCT|40.92|52.13%|**94.82%**|**96.06%**|37.46%|48.16%|42.26%|56.12%|43.86%|56.28%|
|Perseus|58.52%|67.74%|40.11%|53.09%|**58.33%**|**67.94%**|47.19%|58.50%|53.05%|63.77%|
|PROIEL|60.84%|69.56%|47.87%|60.70%|55.85%|65.01%|**80.75%**|**84.31%**|53.05%|63.86%|
|UDante|56.46%|66.26%|39.81%|52.55%|38.74%|51.84%|40.92%|53.17%|**57.91%**|**67.22%**|
