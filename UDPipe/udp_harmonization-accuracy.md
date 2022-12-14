# UDPIPE - Accuracy scores after treebank harmonization

Models have been trained with:
* fastText embeddings
* optimized parameters (see [UDPipe_initial-accuracy](https://github.com/fjambe/Latin-variability/blob/main/UDPipe/udpipe_initial-accuracy.md))
* [harmonized version](https://github.com/fjambe/Latin-variability/tree/main/harmonization/harmonized-treebanks) of train & test data

||`ITTB-HM-ftemb_opt.udpipe`||`LLCT-HM-ftemb_opt.udpipe`||`Perseus-HM-ftemb_opt.udpipe`||`PROIEL-HM-ftemb_opt.udpipe`||`UDante-HM-ftemb_opt.udpipe`||
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
||LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|
|ITTB|**82.62%**|**84.27%**|45.29%|53.64%|44.57%|54.39%|40.97%|51.24%|61.77%|67.50%|
|LLCT|41.76%|47.99%|**93.16%**|**94.05%**|44.10%|51.91%|46.93%|56.65%|43.10%|49.84%|
|Perseus|40.30%|50.67%|49.01%|55.45%|**62.46%**|**66.77%**|50.24%|59.35%|43.52%|54.15%|
|PROIEL|45.36%|53.29%|50.44%|57.58%|52.73%|59.18%|**75.28%**|**78.44%**|45.56%|54.31%|
|UDante|51.75%|58.44%|39.04%|47.73%|35.85%|45.23%|32.60%|44.25%|**54.64%**|**61.58%**|


### Accuracy scores after treebank concatenation

Model trained on the concatenation of all harmonised treebanks.

||`all-HM.udpipe model`||
| --- | :---: | :---: |
||LAS|UAS|
|ITTB|82.67%|84.50%|
|LLCT|91.80%|92.77%|
|Perseus|67.22%|71.47%|
|PROIEL|74.53%|77.94%|
|UDante|59.56%|66.07%|

### Accuracy scores after removing deprel subtypes

Models have been trained with the same settings as above, except that **all deprel subtypes have been removed frm harmonised data**.


||`ITTB-HM-ftemb_opt.udpipe`||`LLCT-HM-ftemb_opt.udpipe`||`Perseus-HM-ftemb_opt.udpipe`||`PROIEL-HM-ftemb_opt.udpipe`||`UDante-HM-ftemb_opt.udpipe`||
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
||LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|
|ITTB|**83.68%**|**85.48%**|44.82%|53.88%|45.06%|54.99%|41.14%|52.72%|60.02%|65.93%|
|LLCT|41.78%|49.06%|**92.93%**|**93.78%**|46.05%|52.71%|44.67%|55.21%|44.44%|52.41%|
|Perseus|42.54%|53.66%|50.02%|55.98%|**63.67%**|**67.86%**|50.60%|60.53%|44.85%|55.83%|
|PROIEL|47.22%|55.38%|51.09%|58.12%|53.95%|60.41%|**75.04%**|**78.26%**|45.62%|54.09%|
|UDante|53.06%|60.10%|39.85%|49.13%|36.00%|46.52%|33.85%|47.53%|**51.57%**|**58.38%**|

