#!/usr/bin/env python3

import sys
import stanza
from stanza.utils.conll import CoNLL

# usage: python3 room_newmodels_MM.py treebank-to-parse.conllu model
# the name of the treebank must be specified with capital letters, if present (e.g., ITTB and not ittb)

# exploiting the newly trained morpho-harmo-models with fastText embeddings (already converted to required .pt format)
# it can be used with a pipeline on pretokenized text to reprocess parts of the document

treebank = sys.argv[1]
model = sys.argv[2].lower()

doc = CoNLL.conll2doc(f"/lnet/work/people/gamba/GitHub/morpho_harmonization/morpho-harmonized-treebanks/UD_Latin-{treebank}/MM-la_{treebank.lower()}-ud-test.conllu")

nlp = stanza.Pipeline(lang='la', \
                      processors='tokenize,lemma,pos,depparse', \
                      tokenize_pretokenized=True, \
                      lemma_model_path=f'/lnet/work/people/gamba/sz-training/stanza/morphoharmo/mm-harmo-models-feb24/la_{model}-lemmatizer.pt', \
                      pos_model_path=f'/lnet/work/people/gamba/sz-training/stanza/morphoharmo/mm-harmo-models-feb24/la_{model}-tagger.pt', \
                      pos_pretrain_path='/lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt', \
                      depparse_model_path=f'/lnet/work/people/gamba/sz-training/stanza/morphoharmo/mm-harmo-models-feb24/la_{model}-parser.pt', \
                      depparse_pretrain_path='/lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300-converted.pt', \
                      download_method=None)

doc = nlp(doc)

CoNLL.write_doc2conll(doc, f"/lnet/work/people/gamba/sz-training/stanza/morphoharmo/output_MM_conllus-feb24/stanza_{treebank.lower()}-by-{model}-model.conllu")
