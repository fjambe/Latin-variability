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
|ITTB|**84.16%**|**85.76%**|44.70%|53.70%|44.79%|54.81%|40.36%|50.22%|61.55%|67.58%|
|LLCT|41.28%|47.19%|**92.69%**|**93.58%**|45.24%|51.92%|44.22%|52.12%|44.69%|52.61%|
|Perseus|42.98%|54.56%|49.86%|56.41%|**63.35%**|**67.73%**|49.43%|58.53%|44.02%|55.13%|
|PROIEL|46.83%|55.62%|49.79%|56.96%|52.18%|58.84%|**75.19%**|**78.53%**|46.54%|55.22%|
|UDante|53.74%|60.56%|39.06%|48.36%|35.00%|45.47%|31.24%|43.29%|**51.65%**|**58.31%**|
