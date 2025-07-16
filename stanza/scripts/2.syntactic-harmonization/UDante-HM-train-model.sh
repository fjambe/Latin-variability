#!/bin/bash

# Script to train UDante model (lemm, pos, parse) with Stanza, using default parameters, pretrained fastText Facebook embeddings and harmonised train data.
# To be run in stanza main folder

source ../bin/activate
source ./scripts/config.sh

# lemmatizer
python3 -m stanza.utils.datasets.prepare_lemma_treebank UD_Latin-UDante
python3 -m stanza.utils.training.run_lemma UD_Latin-UDante --save_dir ./harmo-models

# pos tagger
python3 -m stanza.utils.datasets.prepare_pos_treebank UD_Latin-UDante
python3 -m stanza.utils.training.run_pos UD_Latin-UDante --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt --save_dir ./harmo-models

# parser
python3 -m stanza.utils.datasets.prepare_depparse_treebank UD_Latin-UDante --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt
python3 -m stanza.utils.training.run_depparse UD_Latin-UDante --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt --save_dir ./harmo-models

# renaming models
cd ./harmo-models
mv la_udante_lemmatizer.pt la_udante_hm-lemmatizer.pt
mv la_udante_tagger.pt la_udante_hm-tagger.pt
mv la_udante_parser.pt la_udante_hm-parser.pt
cd ..

# producing a parsed file (i.e. parsing test data) for each treebank
python3 room_newmodels_HM.py ITTB udante_hm
python3 room_newmodels_HM.py LLCT udante_hm
python3 room_newmodels_HM.py Perseus udante_hm
python3 room_newmodels_HM.py PROIEL udante_hm
python3 room_newmodels_HM.py UDante udante_hm

