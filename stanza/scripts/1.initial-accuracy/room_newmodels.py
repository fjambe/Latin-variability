#!/usr/bin/env python3

import sys
import stanza
from stanza.utils.conll import CoNLL

# usage: python3 room_newmodels.py treebank-to-parse.conllu model
# the name of the treebank must be specified with capital letters, if present (e.g., ITTB and not ittb) 

# exploiting my newly trained models with fastText embeddings (already converted to required .pt format) 
# it can be used with a pipeline on pretokenized text to reprocess parts of the document

treebank = sys.argv[1]
model = sys.argv[2].lower()

doc = CoNLL.conll2doc(f"/home/gamba/ud-treebanks-v2.10/UD_Latin-{treebank}/la_{treebank.lower()}-ud-test.conllu")  # TODO

nlp = stanza.Pipeline(lang='la', \
                      processors='tokenize,pos,lemma,depparse', \
                      tokenize_pretokenized=True, \
                      lemma_model_path=f'/home/gamba/stanza/saved_models/lemma/la_{model}_lemmatizer.pt', \
                      pos_model_path=f'/home/gamba/stanza/saved_models/pos/la_{model}_tagger.pt', \
                      pos_pretrain_path='/home/gamba/stanza/fasttext/Latin/cc.la.300-converted.pt', \
                      depparse_model_path=f'/home/gamba/stanza/saved_models/depparse/la_{model}_parser.pt', \
                      depparse_pretrain_path='/home/gamba/stanza/fasttext/Latin/cc.la.300-converted.pt')

doc = nlp(doc)

CoNLL.write_doc2conll(doc, f"stanza_{treebank.lower()}-by-{model}-model.conllu")  # TODO
