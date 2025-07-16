#!/bin/bash

# Script to train Perseus model (lemm, pos, parse) with Stanza, using default parameters, pretrained fastText Facebook embeddings and morphologically harmonised train data.
# To be executed in stanza main folder

# Updated treebanks, as of Feb 5th, 2024

source /lnet/work/people/gamba/sz-training/bin/activate
source /lnet/work/people/gamba/sz-training/stanza/scripts/config.sh

# lemmatizer
python3 -m stanza.utils.datasets.prepare_lemma_treebank UD_Latin-Perseus
python3 -m stanza.utils.training.run_lemma UD_Latin-Perseus --save_dir /lnet/work/people/gamba/sz-training/stanza/morphoharmo/mm-harmo-models-feb24

# pos tagger
python3 -m stanza.utils.datasets.prepare_pos_treebank UD_Latin-Perseus
python3 -m stanza.utils.training.run_pos UD_Latin-Perseus --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt --save_dir /lnet/work/people/gamba/sz-training/stanza/morphoharmo/mm-harmo-models-feb24

# parser
python3 -m stanza.utils.datasets.prepare_depparse_treebank UD_Latin-Perseus --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt
python3 -m stanza.utils.training.run_depparse UD_Latin-Perseus --wordvec_pretrain_file /lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt --save_dir /lnet/work/people/gamba/sz-training/stanza/morphoharmo/mm-harmo-models-feb24

# renaming models
cd /lnet/work/people/gamba/sz-training/stanza/morphoharmo/mm-harmo-models-feb24
mv la_perseus_lemmatizer.pt la_perseus_mm_feb24-lemmatizer.pt
mv la_perseus_tagger.pt la_perseus_mm_feb24-tagger.pt
mv la_perseus_parser.pt la_perseus_mm_feb24-parser.pt
cd ..
cd ..

# producing a parsed file (i.e. parsing test data) for each treebank
python3 ./morphoharmo/room_newmodels_MM-feb24.py ITTB perseus_mm_feb24
python3 ./morphoharmo/room_newmodels_MM-feb24.py LLCT perseus_mm_feb24
python3 ./morphoharmo/room_newmodels_MM-feb24.py Perseus perseus_mm_feb24
python3 ./morphoharmo/room_newmodels_MM-feb24.py PROIEL perseus_mm_feb24
python3 ./morphoharmo/room_newmodels_MM-feb24.py UDante perseus_mm_feb24
