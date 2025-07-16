#!/bin/bash

# Script to train ITTB model (lemm, pos, parse) with Stanza, using default parameters, pretrained fastText Facebook embeddings and harmonised train data.
# To be executed in stanza main folder

source ../bin/activate
source ./scripts/config.sh

# lemmatizer
python3 -m stanza.utils.datasets.prepare_lemma_treebank UD_Latin-ITTB
python3 -m stanza.utils.training.run_lemma UD_Latin-ITTB --save_dir ./harmo-models

# pos tagger
python3 -m stanza.utils.datasets.prepare_pos_treebank UD_Latin-ITTB
python3 -m stanza.utils.training.run_pos UD_Latin-ITTB --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt --save_dir ./harmo-models

# parser
python3 -m stanza.utils.datasets.prepare_depparse_treebank UD_Latin-ITTB --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt
python3 -m stanza.utils.training.run_depparse UD_Latin-ITTB --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt --save_dir ./harmo-models

# renaming models
cd ./harmo-models
mv la_ittb_lemmatizer.pt la_ittb_hm-lemmatizer.pt
mv la_ittb_tagger.pt la_ittb_hm-tagger.pt
mv la_ittb_parser.pt la_ittb_hm-parser.pt
cd ..

# producing a parsed file (i.e. parsing test data) for each treebank
python3 room_newmodels_HM.py ITTB ittb_hm
python3 room_newmodels_HM.py LLCT ittb_hm
python3 room_newmodels_HM.py Perseus ittb_hm
python3 room_newmodels_HM.py PROIEL ittb_hm
python3 room_newmodels_HM.py UDante ittb_hm
