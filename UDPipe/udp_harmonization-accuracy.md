# UDPIPE - Accuracy scores after treebank harmonization

Models have been trained with:
* fastText embeddings
* optimized parameters (see [UDPipe_initial-accuracy](https://github.com/fjambe/Latin-variability/blob/main/UDPipe/udpipe_initial-accuracy.md))
* [harmonized version](https://github.com/fjambe/Latin-variability/tree/main/harmonization/harmonized-treebanks) of train & test data

||`ITTB-HM-ftemb_opt.udpipe`||`LLCT-HM-ftemb_opt.udpipe`||`Perseus-HM-ftemb_opt.udpipe`||`PROIEL-HM-ftemb_opt.udpipe`||`UDante-HM-ftemb_opt.udpipe`||
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
||LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|
|ITTB|**83.83%**|**85.51%**|43.80%|51.45%|43.17%|53.12%|40.46%|51.33%|61.68%|67.39%|
|LLCT|43.12%|48.55%|**93.11%**|**93.88%**|47.31%|54.13%|46.69%|55.23%|41.56%|49.05%|
|Perseus|42.73%|53.54%|48.69%|55.24%|**63.80%**|**68.38%**|49.98%|59.25%|43.59%|54.23%|
|PROIEL|46.77%|55.39%|50.37%|57.48%|53.11%|59.88%|**75.78%**|**78.87%**|46.13%|55.15%|
|UDante|53.06%|59.95%|38.51%|46.69%|35.59%|45.64%|30.72%|44.11%|**54.50%**|**61.02%**|


### Accuracy scores after treebank concatenation

Model trained on the concatenation of all harmonised treebanks.

Parameters set as for the training of ITTB (largest treebank) described above.

||`all-HM.udpipe model`||
| --- | :---: | :---: |
||LAS|UAS|
|ITTB|82.67%|84.50%|
|LLCT|91.80%|92.77%|
|Perseus|67.22%|71.47%|
|PROIEL|74.53%|77.94%|
|UDante|59.56%|66.07%|

### Accuracy scores after removing deprel subtypes

Models have been trained with the same settings as above, except that **all deprel subtypes have been removed from harmonised data**.


||`ITTB-HM-ftemb_opt.udpipe`||`LLCT-HM-ftemb_opt.udpipe`||`Perseus-HM-ftemb_opt.udpipe`||`PROIEL-HM-ftemb_opt.udpipe`||`UDante-HM-ftemb_opt.udpipe`||
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
||LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|
|ITTB|**83.68%**|**85.48%**|44.82%|53.88%|45.06%|54.99%|41.14%|52.72%|60.02%|65.93%|
|LLCT|41.78%|49.06%|**92.93%**|**93.78%**|46.05%|52.71%|44.67%|55.21%|44.44%|52.41%|
|Perseus|42.54%|53.66%|50.02%|55.98%|**63.67%**|**67.86%**|50.60%|60.53%|44.85%|55.83%|
|PROIEL|47.22%|55.38%|51.09%|58.12%|53.95%|60.41%|**75.04%**|**78.26%**|45.62%|54.09%|
|UDante|53.06%|60.10%|39.85%|49.13%|36.00%|46.52%|33.85%|47.53%|**51.57%**|**58.38%**|
