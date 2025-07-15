#!usr/bin/env python3

'''
Script employed to detect differences between two files, as in one of them some corrections were made manually.
'''

# field indexes
ID = 0
FORM = 1
LEMMA = 2
UPOS = 3
XPOS = 4
FEATS = 5
HEAD = 6
DEPREL = 7

import sys
from collections import defaultdict
import pprint

split = sys.argv[1] # train, dev, test
before = f'/lnet/work/people/gamba/GitHub/harmonization/harmonized-treebanks/UD_Latin-PROIEL/HM-la_proiel-ud-{split}.conllu'
after = f'/lnet/work/people/gamba/GitHub/morpho_harmonization/morpho-harmonized-treebanks/TEMP-PROIEL/HM-la_proiel-ud-{split}.conllu'

def difference(feats1, feats2):
    feats1 = feats1.split('|')
    feats2 = feats2.split('|')
    F1 = set(feats1)
    F2 = set(feats2)
    feats_diff = F1.symmetric_difference(F2)
    if not len(feats_diff) == 0: # safety check
        before = [f for f in feats_diff if f in feats1]
        after = [f for f in feats_diff if f in feats2]
        return before, after

store_dict = defaultdict(list)

with open(before, 'r') as before, open(after, 'r') as after:

    before_content = before.readlines()
    after_content = after.readlines()

    if len(before_content) != len(after_content):
        print('Warning: the number of lines does not coincide in the two files.')
        print(len(before_content), len(after_content))

    sent_id = None
    for before_sent, after_sent in zip(before_content, after_content):
        # store sent_id and ignore non-token lines
        if (before_sent[0] == '#' and after_sent[0] == '#') or (before_sent == '\n' and after_sent == '\n'): # not a token line
            if before_sent.startswith('# sent_id'):
               sent_id = before_sent.split(' = ')[1].strip()
        else:
            # collect diverging morphological features
            before_sent = before_sent.split('\t')
            after_sent = after_sent.split('\t')
            address = sent_id + '#' + before_sent[ID]
            if before_sent[FEATS] != after_sent[FEATS]:
                before, after = difference(before_sent[FEATS], after_sent[FEATS])
                # store information in a 4-items tuple
                info = (address, before_sent[LEMMA], before, after)
                if 'ConjType=Cmpr' not in after:
                    store_dict['feats_info'].append(info)

            # now collect diverging UPOS tags
            if before_sent[UPOS] != after_sent[UPOS]:
                store_dict['upos_info'].append((address, before_sent[LEMMA], before_sent[UPOS], after_sent[UPOS]))

pprint.PrettyPrinter(width=150).pprint(store_dict)
