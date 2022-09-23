# UDPIPE - Accuracy scores after treebank harmonization

Models have been trained with:
* fastText embeddings
* optimized parameters (see [UDPipe_initial-accuracy](https://github.com/fjambe/Latin-variability/blob/main/UDPipe/udpipe_initial-accuracy.md))
* [harmonized version](https://github.com/fjambe/Latin-variability/tree/main/harmonization/harmonized-treebanks) of train & test data

The evaluation is carried out through UDPipe `--accuracy` option.

||ITTB||LLCT||Perseus||PROIEL||UDante||
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
||LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|LAS|UAS|
|`ITTB-HM_ftemb_opt.udpipe`|**82.62%**|**84.27%**|41.76%|47.99%|40.30%|50.67%|45.36%|53.29%|51.75%|58.44%|
|`LLCT-HM_ftemb_opt.udpipe`|45.29%|53.64%|**93.16%**|**94.05%**|49.01%|55.45%|50.44%|57.58%|39.04%|47.73%|
|`Perseus-HM_ftemb_opt.udpipe`|44.57%|54.39%|44.10%|51.91%|**62.46%**|**66.77%**|52.73%|59.18%|35.85%|45.23%|
|`PROIEL-HM_ftemb_opt.udpipe`|40.97%|51.24%|46.93%|56.65%|50.24%|59.35%|**75.28%**|**78.44%**|32.60%|44.25%|
|`UDante-HM_ftemb_opt.udpipe`|61.77%|67.50%|43.10%|49.84%|43.52%|54.15%|45.56%|54.31%|**54.64%**|**61.58%**|
