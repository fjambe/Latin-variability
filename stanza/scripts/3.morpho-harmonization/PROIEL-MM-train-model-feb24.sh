#!/bin/bash

# Script to train PROIEL model (lemm, pos, parse) with Stanza, using default parameters, pretrained fastText Facebook embeddings and morphologically harmonised train data.
# To be executed in stanza main folder

# Updated treebanks, as of Feb 5th, 2024

source /lnet/work/people/gamba/sz-training/bin/activate
source /lnet/work/people/gamba/sz-training/stanza/scripts/config.sh

# lemmatizer
python3 -m stanza.utils.datasets.prepare_lemma_treebank UD_Latin-PROIEL
python3 -m stanza.utils.training.run_lemma UD_Latin-PROIEL --save_dir ./morphoharmo/mm-harmo-models-feb24

# pos tagger
python3 -m stanza.utils.datasets.prepare_pos_treebank UD_Latin-PROIEL
python3 -m stanza.utils.training.run_pos UD_Latin-PROIEL --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt --save_dir ./morphoharmo/mm-harmo-models-feb24

# parser
python3 -m stanza.utils.datasets.prepare_depparse_treebank UD_Latin-PROIEL --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt
python3 -m stanza.utils.training.run_depparse UD_Latin-PROIEL --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt --save_dir ./morphoharmo/mm-harmo-models-feb24

# renaming models
cd ./morphoharmo/mm-harmo-models-feb24
mv la_proiel_lemmatizer.pt la_proiel_mm_feb24-lemmatizer.pt
mv la_proiel_tagger.pt la_proiel_mm_feb24-tagger.pt
mv la_proiel_parser.pt la_proiel_mm_feb24-parser.pt
cd ..
cd ..

# producing a parsed file (i.e. parsing test data) for each treebank
python3 ./morphoharmo/room_newmodels_MM-feb24.py ITTB proiel_mm_feb24
python3 ./morphoharmo/room_newmodels_MM-feb24.py LLCT proiel_mm_feb24
python3 ./morphoharmo/room_newmodels_MM-feb24.py Perseus proiel_mm_feb24
python3 ./morphoharmo/room_newmodels_MM-feb24.py PROIEL proiel_mm_feb24
python3 ./morphoharmo/room_newmodels_MM-feb24.py UDante proiel_mm_feb24
