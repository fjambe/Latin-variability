# Stanza - Accuracy scores after treebank harmonization

Models have been trained with:
* fastText embeddings
* default parameters
* [harmonized version](https://github.com/fjambe/Latin-variability/tree/main/harmonization/harmonized-treebanks) of train, dev & test data

The evaluation is carried out through UD `conll18_ud_eval.py` script.

||`la_ittb-hm_parser.pt`||`la_llct-hm_parser.pt`||`la_perseus-hm_parser.pt`||`la_proiel-hm_parser.pt`||`la_udante-hm_parser.pt`||
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
||LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|
|ITTB|**88.60%**|**90.55%**|45.63%|58.74%|50.55%|61.47%|51.16%|60.72%|63.78%|72.96%|
|LLCT|40.84%|52.66%|**94.61%**|**95.81%**|37.82%|47.50%|40.97%|53.24%|43.64%|56.09%|
|Perseus|57.68%|67.85%|40.80%|53.88%|**58.41%**|**68.22%**|47.30%|58.68%|52.98%|64.06%|
|PROIEL|62.34%|71.27%|46.76%|59.92%|55.03%|65.25%|**80.57%**|**84.36%**|52.61%|63.91%|
|UDante|56.62%|67.27%|39.67%|52.97%|39.53%|52.98%|41.27%|52.41%|**57.92%**|**67.60%**|
