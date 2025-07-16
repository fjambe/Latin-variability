#!/usr/bin/env python3

import sys
import stanza
from stanza.utils.conll import CoNLL

# usage: python3 room_newmodels_HM.py treebank-to-parse.conllu model 
# the name of the treebank must be specified with capital letters, if present (e.g., ITTB and not ittb)

# exploiting my newly trained models with fastText embeddings (already converted to required .pt format) 
# it can be used with a pipeline on pretokenized text to reprocess parts of the document

treebank = sys.argv[1]
model = sys.argv[2].lower()

doc = CoNLL.conll2doc(f"/lnet/work/people/gamba/GitHub/syntactic-harmonization/harmonized-treebanks/UD_Latin-{treebank}/HM-la_{treebank.lower()}-ud-test.conllu")

nlp = stanza.Pipeline(lang='la', \
                      processors='tokenize,pos,lemma,depparse', \
                      tokenize_pretokenized=True, \
                      lemma_model_path=f'/lnet/work/people/gamba/sz-training/stanza/harmo-models/la_{model}-lemmatizer.pt', \
                      pos_model_path=f'/net/work/people/gamba/sz-training/stanza/harmo-models/la_{model}-tagger.pt', \
                      pos_pretrain_path='/lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt', \
                      depparse_model_path=f'/lnet/work/people/gamba/sz-training/stanza/harmo-models/la_{model}-parser.pt', \
                      depparse_pretrain_path='/lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt', \
                      download_method=None)

doc = nlp(doc)

CoNLL.write_doc2conll(doc, f"/lnet/work/people/gamba/sz-training/stanza/THESIS-output_HM_conllus/THESIS-sz_{treebank.lower()}-by-{model}-model.conllu")
