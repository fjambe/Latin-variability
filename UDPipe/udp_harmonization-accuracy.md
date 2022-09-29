# UDPIPE - Accuracy scores after treebank harmonization

Models have been trained with:
* fastText embeddings
* optimized parameters (see [UDPipe_initial-accuracy](https://github.com/fjambe/Latin-variability/blob/main/UDPipe/udpipe_initial-accuracy.md))
* [harmonized version](https://github.com/fjambe/Latin-variability/tree/main/harmonization/harmonized-treebanks) of train & test data

The evaluation is carried out through UDPipe `--accuracy` option.

||`ITTB-HM-ftemb_opt.udpipe`||`LLCT-HM-ftemb_opt.udpipe`||`Perseus-HM-ftemb_opt.udpipe`||`PROIEL-HM-ftemb_opt.udpipe`||`UDante-HM-ftemb_opt.udpipe`||
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
||LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|
|ITTB|**82.62%**|**84.27%**|45.29%|53.64%|44.57%|54.39%|40.97%|51.24%|61.77%|67.50%|
|LLCT|41.76%|47.99%|**93.16%**|**94.05%**|44.10%|51.91%|46.93%|56.65%|43.10%|49.84%|
|Perseus|40.30%|50.67%|49.01%|55.45%|**62.46%**|**66.77%**|50.24%|59.35%|43.52%|54.15%|
|PROIEL|45.36%|53.29%|50.44%|57.58%|52.73%|59.18%|**75.28%**|**78.44%**|45.56%|54.31%|
|UDante|51.75%|58.44%|39.04%|47.73%|35.85%|45.23%|32.60%|44.25%|**54.64%**|**61.58%**|
