#!/usr/bin/env python3

import sys
import stanza
from stanza.utils.conll import CoNLL

# usage: python3 room_pretrainedmodels.py treebank-to-parse.conllu package
# the name of the treebank must be specified with capital letters, if present (e.g., ITTB and not ittb) 

# exploiting pretrained Stanza models
# it can be used with a pipeline on pretokenized text to reprocess parts of the document

treebank = sys.argv[1]
package = sys.argv[2]  # ittb (default), perseus or proiel

doc = CoNLL.conll2doc(f"/home/gamba/ud-treebanks-v2.10/UD_Latin-{treebank}/la_{treebank.lower()}-ud-test.conllu")

nlp = stanza.Pipeline(lang='la', processors='tokenize,pos,lemma,depparse', package=f'{package}', tokenize_pretokenized=True)

doc = nlp(doc)

CoNLL.write_doc2conll(doc, f"stanza_{treebank.lower()}-by-{package}-model.conllu")
