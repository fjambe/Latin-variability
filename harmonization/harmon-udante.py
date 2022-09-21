#!/usr/bin/env python3

'''
Harmonization script for UDante Latin treebank.
Usage: python3 harmon-udante.py train/dev/test
'''

import sys
import udapi
import udapi.block.ud.la.addmwt
import udapi.block.ud.convert1to2

split = sys.argv[1] # train/dev/test
UD_folder = 'path/to/folder/containing/all/UD/Latin/treebanks'
filename = f'{UD_folder}/UD_Latin-UDante-dev/la_udante-ud-{split}.conllu'
output_folder = '/path/to/folder/where/output/is/stored'
doc = udapi.Document(filename)


# Iterate over all nodes in the document (in all trees)
for node in doc.nodes:

	if node.lemma == 'ecce':
		node.upos = 'PART'
	
	# adverbs	
	if node.deprel == 'advmod:lmod':
		if node.lemma in ['adhuc', 'deinde', 'praeterea']:
			node.deprel = 'advmod'
		if node.lemma == 'ergo':
			node.deprel = 'discourse'
		
	if node.form in ['ante', 'cotidie', 'hodie', 'iam', 'interim', 'nonnunquam', 'nunc', 'olim', 'post', 'postea', 'pridem', 'prius', 'quando', 'quandoque', 'saepe', 'semper', 'tum', 'tunc'] and node.form == node.lemma and node.deprel == 'advmod':
		node.deprel = 'advmod:tmod'
		node.feats['AdvType'] = 'Tim'		
	if node.form in ['alibi', 'foris', 'hic', 'hinc', 'huc', 'ibi', 'ibidem', 'illuc', 'inde', 'procul', 'qua', 'quo', 'ubi', 'ubicumque', 'ubique', 'unde', 'undique'] and node.form == node.lemma and node.deprel == 'advmod':
		node.deprel = 'advmod:lmod'
		node.feats['AdvType'] = 'Loc'
			
			
	# errors
	if node.deprel == 'amod' and node.upos == 'NOUN':
		if node.feats['Case'] == node.parent.feats['Case']:
			node.deprel = 'appos'
		else:
			node.deprel = 'nmod'
				
with open(f'{output_folder}/HM-la_udante-ud-{split}.conllu', 'w') as output:
	output.write(doc.to_conllu_string())
