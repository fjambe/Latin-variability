#!/bin/bash

# Script to train Perseus model (lemm, pos, parse) with Stanza, using default parameters, pretrained fastText Facebook embeddings and harmonised train data.
# To be executed in stanza main folder

source ../bin/activate
source ./scripts/config.sh

# lemmatizer
python3 -m stanza.utils.datasets.prepare_lemma_treebank UD_Latin-Perseus
python3 -m stanza.utils.training.run_lemma UD_Latin-Perseus --save_dir ./harmo-models

# pos tagger
python3 -m stanza.utils.datasets.prepare_pos_treebank UD_Latin-Perseus
python3 -m stanza.utils.training.run_pos UD_Latin-Perseus --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt --save_dir ./harmo-models

# parser
python3 -m stanza.utils.datasets.prepare_depparse_treebank UD_Latin-Perseus --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt
python3 -m stanza.utils.training.run_depparse UD_Latin-Perseus --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt --save_dir ./harmo-models

# renaming models
cd ./harmo-models
mv la_perseus_lemmatizer.pt la_perseus_hm-lemmatizer.pt
mv la_perseus_tagger.pt la_perseus_hm-tagger.pt
mv la_perseus_parser.pt la_perseus_hm-parser.pt
cd ..

# producing a parsed file (i.e. parsing test data) for each treebank
python3 room_newmodels_HM.py ITTB perseus_hm
python3 room_newmodels_HM.py LLCT perseus_hm
python3 room_newmodels_HM.py Perseus perseus_hm
python3 room_newmodels_HM.py PROIEL perseus_hm
python3 room_newmodels_HM.py UDante perseus_hm
