#!/usr/bin/env python3

'''
Harmonization script for UDante Latin treebank.
Usage: python3 harmon-udante.py train/dev/test
'''

import sys
import udapi

split = sys.argv[1] # train/dev/test
UD_folder = '/home/federica/Desktop/latin/UD_devbranch' # path to the folder containing all UD Latin treebanks
filename = f'{UD_folder}/UD_Latin-UDante-dev/la_udante-ud-{split}.conllu'
output_folder = '/home/federica/Desktop/latin/GITHUB/Latin-variability/harmonization/harmonized-treebanks'
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
			
	# relative clauses
	if node.deprel == 'acl:relcl' and node.parent.feats['PronType'] == 'Rel':
		pron = node.parent
		if pron.deprel != 'root':
			if node.upos != 'AUX': # sum
				node.parent = pron.parent
				if pron.deprel == 'nsubj':
					node.deprel = 'csubj'
				elif pron.deprel == 'nsubj:pass':
					node.deprel = 'csubj:pass'
				elif pron.deprel == 'dislocated:nsubj':
					node.deprel = 'dislocated:csubj'
				elif pron.deprel == 'obj':
					node.deprel = 'ccomp'
				elif pron.udeprel == 'advmod' or pron.udeprel == 'obl':
					node.deprel = 'advcl'
				elif pron.udeprel == 'advcl' or pron.deprel == 'conj':
					node.deprel = pron.deprel
				else:
					continue
					
				pron.parent = node
				if pron.feats['Case'] == 'Nom':
					if node.feats['Voice'] == 'Pass' and node.lemma[-1] != 'r': # non-deponent verb
						pron.deprel = 'nsubj:pass'
					else:
						pron.deprel = 'nsubj'
				elif pron.feats['Case'] == 'Acc':
					pron.deprel = 'obj'
				elif pron.feats['Case'] == 'Abl':
					pron.deprel = 'obl'
				elif pron.upos == 'ADV':
					continue # pron.deprel does not change
					
			else:
				node.deprel = 'cop'
				if pron.deprel == 'nsubj':
					node.deprel = 'csubj'
				elif pron.deprel == 'nsubj:pass':
					node.deprel = 'csubj:pass'
				elif pron.deprel == 'dislocated:nsubj':
					node.deprel = 'dislocated:csubj'
				elif pron.deprel == 'obj':
					node.deprel = 'ccomp'
				elif pron.udeprel == 'advmod' or pron.udeprel == 'obl':
					node.deprel = 'advcl'
				elif pron.udeprel == 'advcl' or pron.deprel == 'conj':
					node.deprel = pron.deprel
				else:
					continue
				
				
	# cmpr
	if node.sdeprel == 'cmpr':
		node.deprel = node.deprel[:-1]
				
with open(f'{output_folder}/UD_Latin-UDante/HM-la_udante-ud-{split}.conllu', 'w') as output:
	output.write(doc.to_conllu_string())
