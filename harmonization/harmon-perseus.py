#!/usr/bin/env python3

'''
Harmonization script for Perseus Latin treebank.
Usage: python3 harmon-perseus.py train/test
'''

import sys
import udapi
import udapi.block.ud.la.addmwt
import udapi.block.ud.convert1to2
import udapi.block.ud.setspaceafterfromtext
import udapi.block.ud.fixpunct


split = sys.argv[1] # train/test
UD_folder = '/home/federica/Desktop/latin/UD_devbranch' # path to the folder containing all UD Latin treebanks
filename = f'{UD_folder}/UD_Latin-Perseus-dev/la_perseus-ud-{split}.conllu'
output_folder = '/home/federica/Desktop/latin/harmonization/harmonized-treebanks'
doc = udapi.Document(filename)		


determiners = ['aliqualis', 'aliqui', 'alius', 'alter', 'alteruter', 'ambo', 'ceterus', 'complura', 'complures', 'cunctus', 'eiusmodi', 'hic', 'huiusmodi', 'idem', 'ille', 'ipse', 'iste', 'meus', 'multus', 'neuter', 'nonnullus', 'noster', 'nullus', 'omnis', 'paucus', 'plerusque', 'qualis', 'quamplures', 'quantus', 'quantuslibet', 'qui', 'quicumque', 'quidam', 'quilibet', 'quispiam', 'quisquam', 'quisque', 'quot', 'reliquus', 'solus', 'suus', 'talis', 'tantus', 'tot', 'totidem', 'totus', 'tuus', 'uester', 'vester', 'voster', 'ullus', 'uniuersus', 'unusquisque', 'uterque']


# Iterate over all nodes in the document (in all trees)
for node in doc.nodes:

	# node shifting: nec, neque
	if node.form == 'ne' and node.prev_node.form in ['c', 'que']:
		conj = node.prev_node
		conj.shift_after_node(node)
		conj.parent = node.parent
		node.root.text = None
		node.root.text = node.root.get_sentence()	
	

	# X upos
	if node.upos == 'X':
		# train data
		if node.form == 'quom': # one occurrence is tagged 'X'
			node.lemma, node.upos = 'cum', 'SCONJ'
		elif node.lemma in ['accedo', 'attero', 'exsecror', 'mitto']:
			node.upos = 'VERB'
		elif node.lemma == 'haudquaquam':
			node.upos = 'ADV'
		# test data
		if node.form == ',':
			node.upos, node.xpos = 'PUNCT', 'u--------'
		elif node.lemma == 'que':
			node.upos = 'CCONJ'
		elif node.lemma == 'prendo':
			node.upos = 'VERB'
		elif node.form == 'thraecium':
			node.lemma, node.upos = 'thraecius', 'ADJ'
		elif node.form == 'perperam':
			node.upos = 'ADV'
		
			
	if node.next_node and node.next_node.form == '.' and not node.no_space_after:
		node.misc['SpaceAfter'] = 'No'
	if node.form in ['.', ',', ';', ':', '(', ')', '?', '!']:
		node.upos = 'PUNCT'
	if node.lemma in ['allium', 'Alii']:
		node.lemma = 'alius'
	if node.lemma == 'solus' and node.upos == 'ADV':
		node.lemma = node.form # solum
	if node.lemma == 'cottidie':
		node.lemma = 'cotidie'
	if node.lemma in ['bis', 'semel'] and node.upos == 'NUM':
		node.upos = 'ADV'
	if node.lemma == 'flaminius':
		node.lemma = node.lemma.capitalize()
	if node.lemma == 'Pomptinus':
		node.upos = 'PROPN'
	if node.deprel == ['appos', 'advmod'] and node.lemma in ['aut', 'et', 'que', 'sed']:
		node.deprel = 'cc'
	if node.lemma == 'neve':
		node.upos, node.deprel = 'CCONJ', 'cc'
	if node.lemma == 'qualis' and node.deprel == 'mark':
		node.deprel = 'advcl:pred'
	if node.upos == 'ADV':
		if node.deprel == 'mark' and node.lemma in ['ne', 'ni', 'quam', 'quamvis', 'quasi', 'quando', 'quoniam', 'siquidem', 'tamquam', 'ut']:
			node.upos = 'SCONJ'
		elif node.lemma == 'vel':
			if node.deprel == 'cc':
				node.upos = 'CCONJ'
			elif node.deprel == 'advmod':
				subseq = [d for d in node.root.descendants if node < d]
				vel = next((s for s in subseq if s.lemma == 'vel'), False)
				if vel:
					node.upos, node.deprel = 'CCONJ', 'cc'
				else:
					node.upos, node.deprel = 'ADV', 'advmod:emph'
	if node.lemma == 'ut' and node.upos == 'SCONJ' and node.deprel == 'case':
		node.deprel = 'mark'
	if node.form == 'invicem':
		node.upos = 'PRON'
		node.feats = 'Compound=Yes|InflClass=Ind|PronType=Rcp'
		adposition = [k for k in node.children if k.upos == 'ADP']
		obj = [s for s in node.siblings if s.deprel == 'obj']
		if adposition:
			node.deprel = 'obl'
		elif obj:
			node.deprel = 'obl:arg'
		else:
			node.deprel = 'obj'

	
	# MWT
	company = udapi.block.ud.la.addmwt.AddMwt()
	company.process_node(node)
	# postprocessing of abbreviation+dot combinations, that in the previous step were provisionally treated like MWTs
	# MWT line is removed, so that in the end they have been simply tokenised
	if node.multiword_token:
		mwt = node.multiword_token
		if mwt.form.endswith('.') and len(mwt.form) > 1 and mwt.form != '...':
			mwt.remove()
			
	# setting SpaceAfter=No when relevant
	space = udapi.block.ud.setspaceafterfromtext.SetSpaceAfterFromText()
	space.process_tree(node.root)
	
	
	# reattach cc and punct to second conjunct
	conv = udapi.block.ud.convert1to2.Convert1to2()
	conv.reattach_coordinations(node)
	
	
	# i-j
	if 'j' in node.lemma.lower():
		node.lemma = node.lemma.replace('J', 'I').replace('j', 'i')

		
	# discourse particles	
	if node.lemma == 'verus' and node.upos == 'ADV':
		if node.form.lower() == 'vero': 
			node.lemma = 'vero'
		elif node.form.lower() == 'verum':
			node.lemma = 'verum'
	if node.lemma in ['ergo', 'vero'] and node.deprel == 'advmod':
		node.upos, node.deprel = 'ADV', 'discourse'
	elif node.lemma in ['enim', 'equidem', 'igitur', 'itaque', 'nam', 'namque', 'nempe', 'num', 'quidem'] and node.deprel in ['advmod', 'cc', 'mark']:
		node.upos, node.deprel = 'PART', 'discourse'
	elif node.lemma == 'ecce' and node.deprel == 'advmod':
		node.upos = 'PART'
		if node.parent.upos == 'VERB':
			node.deprel = 'discourse'
		else:
			node.deprel = 'advmod:emph'
	elif node.lemma == 'o' and node.deprel == 'advmod':
		node.upos, node.deprel = 'PART', 'advmod:emph'
	elif node.lemma == 'an' and node.deprel == 'cc': # an as interrogative particle, not conjunction 
		sib = [s for s in node.siblings if s.lemma == '?']
		if sib:
			node.upos, node.deprel = 'PART', 'discourse'
					
	
	# ADVerbs
	if node.lemma == 'etiam':
		node.upos = 'ADV'
	if node.deprel == 'advmod' and node.upos != 'ADV':
		if node.feats['Case'] == 'Dat':
			node.deprel = 'obl:arg'
		elif node.lemma in ['atque', 'aut', 'autem', 'neu', 'que', 'sed', 'sive']:
			node.deprel = 'cc'
		elif node.form.lower() == 'quod' and node.parent.form == 'si' and node.deprel == 'advmod': #quod si
			node.parent = node.parent.parent
			node.deprel = 'mark'
		elif node.upos == 'SCONJ':
			node.deprel = 'mark'
		elif node.lemma in ['etiam']:
			node.upos, node.deprel = 'ADV', 'advmod:emph'
		elif node.lemma == 'quoque':
			node.upos, node.deprel = 'ADV', 'discourse'
		elif node.form == 'patres':
			node.deprel = 'vocative'
		elif node.form.lower() in ['et', 'nec', 'uel', 'vel']:
			x = next((s for s in node.siblings if s.form == node.form), None)
			if x:
				node.deprel = 'cc' # conjiunction 'et'
			else: 
				node.deprel = 'advmod:emph' # adverbial 'et'
		elif node.feats['Case'] == 'Loc':
			node.deprel = 'obl'
		elif [d for d in node.descendants if d.lemma == 'tamquam']:
			node.deprel = 'advcl:cmp'
	# quid
	if node.form.lower() == 'quid' and node.deprel == 'advmod':
		node.upos, node.lemma, node.feats = 'ADV', node.form, ''
		node.feats['PronType'] = 'Rel'
	# locative and temporal adverbs
	if node.form in ['alibi', 'foris', 'hic', 'hinc', 'huc', 'ibi', 'ibidem', 'illuc', 'inde', 'procul', 'qua', 'quo', 'ubi', 'ubicumque', 'ubique', 'unde', 'undique'] and node.form == node.lemma and node.deprel == 'advmod':
		node.deprel = 'advmod:lmod'
		node.feats['AdvType'] = 'Loc'
	if node.form in ['ante', 'cotidie', 'hodie', 'iam', 'interim', 'nonnunquam', 'nunc', 'olim', 'post', 'postea', 'pridem', 'prius', 'quando', 'quandoque', 'saepe', 'semper', 'tum', 'tunc'] and node.form == node.lemma and node.deprel == 'advmod':
		node.deprel = 'advmod:tmod'
		node.feats['AdvType'] = 'Tim'
	# negation	
	if node.lemma in ['haud', 'non'] and node.deprel != 'conj':
		node.upos, node.deprel = 'PART', 'advmod:neg'
	# (mostly locative and instrumental) ablatives inappropriately annotated as adverbials 
	if node.feats['Case'] in ['Abl', 'Acc'] and node.deprel == 'advmod' or node.form.lower() in ['domi', 'humi', 'romae']:
		node.deprel = 'obl'

	
	# interjections & vocative
	if node.upos == 'INTJ' and node.deprel in ['advmod', 'vocative']:
		node.deprel = 'discourse'
	if node.feats['Case'] == 'Voc' and node.deprel == 'advmod':
		node.deprel = 'vocative'
		
	
	# PROPNs
	# restoring PROPNs in a trivial way
	if node.lemma[0].isupper() and node.upos in ['NOUN', 'X'] and not node.lemma.startswith('X'):
		node.upos = 'PROPN'
		if len(node.form) == 1 and node.feats['Case'] == '': # restoring morpho features
			node.feats = node.parent.feats
			
			
	# NUMerals
	if node.upos == 'NUM' and node.parent.upos == 'NUM' and node.deprel == 'nummod' and node.parent.lemma != 'mille':
		node.deprel = 'flat'
	if node.lemma in ['duo', 'ter', 'quater', 'quinque', 'sex', 'septem', 'octo', 'novem', 'decem'] and node.upos == 'ADJ':
		node.upos = 'NUM'
		if node.deprel == 'amod':
			node.deprel = 'nummod'
		
		
	# DETerminers
	if node.lemma == 'qui' and node.upos == 'NOUN':
		node.upos, node.feats['PronType'] = 'PRON', 'Rel'
	if node.feats == node.parent.feats:
		if (node.upos == 'PRON' and node.deprel == 'nmod') or (node.lemma in determiners and node.lemma != 'qui' and node.deprel in ['amod', 'nmod']):
			node.upos, node.deprel = 'DET', 'det'
	if node.lemma in determiners and node.lemma != 'qui' and node.deprel not in ['advmod', 'mark'] and node.upos != 'ADV':
		node.upos = 'DET'
	if node.lemma in determiners and node.deprel == 'amod' and node.feats['Case'] == node.parent.feats['Case'] and node.feats['Gender'] == node.parent.feats['Gender'] and node.feats['Number'] == node.parent.feats['Number']:
		node.deprel = 'det'
	if node.lemma in ['quot', 'tot', 'totidem'] and node.deprel in ['nmod', 'nummod']:
		node.deprel = 'det'
		if node.upos == 'ADV':
			node.upos = 'DET'
	if node.deprel == 'nmod' and node.lemma in determiners and node.feats == node.parent.feats:
		node.deprel = 'det'
	if node.form.lower() == 'nescio' and node.lemma == 'nescio' and node.next_node.lemma in ['qui', 'quis'] and node.next_node.upos != 'ADV' and node.next_node.deprel != 'fixed':
		fix = node.next_node
		kids = [k for k in fix.children if k.lemma != 'nescio']
		if fix.deprel in ['det', 'nmod']:
			node.deprel = 'det'
		else:
			node.deprel = fix.deprel
		fix.deprel = 'fixed'
		node.parent = fix.parent
		fix.parent = node
		if kids:
			for k in kids:
				k.parent = node	
	if node.upos == 'DET' and node.feats['Degree'] == 'Sup':
		node.feats['Degree'] = 'Abs'	
		
		
	# AUXiliaries
	if node.lemma == 'sum' and node.deprel in ['aux', 'aux:pass', 'cop']:
		node.upos = 'AUX'
	
	# Degree
	if node.feats['Degree'] == 'Sup':
		node.feats['Degree'] = 'Abs'	

	# (indirect) objects
	if node.deprel == 'iobj':
		node.deprel = 'obl:arg'
	if node.deprel == 'obj' and node.feats['Case'] == 'Dat':
		node.deprel = 'obl'
	
		
	# nsubj:pass 	
	if node.deprel == 'nsubj' and node.parent.feats['Voice'] == 'Pass':
		if node.parent.lemma[-1] != 'r': # except deponent verbs
			node.deprel = 'nsubj:pass'
		
		
	# nmod
	if node.feats['Case']=='Gen' and node.parent.upos == 'NOUN' and node.upos in ['ADJ', 'DET', 'NOUN'] and node.deprel == 'amod' and node.parent.feats['Case']!='Gen':
		node.deprel = 'nmod'
	
	
	# participles (always treated as verbs) changed to adjectives when nominal predicates
	if node.deprel == 'cop' and node.parent.feats['VerbForm'] == 'Part':
		node.parent.upos = 'ADJ' # e.g. notus, doctus, tutus
		node.parent.feats['Tense'] = ''
		node.parent.feats['Voice'] = ''
		node.parent.feats['Aspect'] = ''
		if 'ens' not in node.parent.form:
			no_ending = node.parent.form.rpartition('t')[0] # reconstructing lemma
			node.parent.lemma = no_ending + 'tus'
		else: # ad hoc for Perseus data - it does not take into account inflected present participles
			node.parent.lemma = node.parent.form
		
			
	# gerundives
	if node.deprel.startswith('nsubj') and node.parent.feats['VerbForm'] == 'Gdv':
		sib = [s for s in node.siblings if s.deprel == 'case']
		if sib:
			sib[0].deprel = 'mark'
			node.deprel = 'nsubj:pass'
			if node.parent.deprel not in ['advcl', 'root', 'conj']:
				if node.parent.upos in ['VERB']: # no ADJ occurrences
					node.parent.deprel = 'advcl'
				elif node.parent.upos == 'NOUN':
					node.parent.deprel = 'acl'			
					
					
	# COMPLEX CONSTRUCTIONS
	
	# advcl
	if node.deprel == 'mark' and node.parent.deprel == 'advmod':
		node.parent.deprel = 'advcl'
	
	# xcomp
	if node.deprel == 'xcomp':
		if node.parent.lemma in ['cogo', 'cupio', 'decerno', 'desidero', 'dico', 'dubito', 'iubeo', 'malo', 'metuo', 'moneo', 'scio', 'statuo', 'studeo', 'timeo', 'vereor']: # list not exhaustive
			node.deprel = 'ccomp'
		if node.feats['VerbForm'] == 'Part':
			adp = [k for k in node.children if k.deprel == 'case']
			if adp:
				node.deprel = 'obl'
			if node.feats['Case'] == 'Dat':
				node.deprel = 'obl'
	
	# Relative clauses
	if node.lemma == 'qui' and node.upos == 'PRON':
		node.feats['PronType'] = 'Rel'
	if node.parent.deprel == 'acl' and node.lemma in ['qui', 'ubi']:
		node.parent.deprel = 'acl:relcl'
	if node.deprel == 'acl':
		dependents = [d for d in node.descendants if d.lemma == 'qui' and node.upos == 'PRON']
		if dependents:
			node.deprel = 'acl:relcl'
	if node.deprel == 'ccomp':
		for d in node.descendants:
			if d.lemma == 'qui' and d.upos == 'PRON':
				qui_kids = [k for k in d.children if k.deprel == 'acl:relcl']
				if node.feats['VerbForm'] == 'Fin' and not qui_kids and d.parent.deprel != 'acl:relcl':
					node.deprel = 'acl:relcl'
					break
				elif node.upos != 'VERB' and not qui_kids and d.parent.deprel != 'acl:relcl':
					node.deprel = 'acl:relcl'
					break
	
	
	# absolute ablative
	if node.parent.deprel == 'advcl' and node.parent.feats['Case'] == 'Abl' and node.feats['Case'] == 'Abl' and node.deprel.startswith('nsubj'):
		case = [s for s in node.siblings if s.deprel == 'case']
		if len(case) == 0:
			node.parent.deprel = 'advcl:abs'
		
		
	# comparative clauses
	if node.deprel == 'advcl:cmpr':
		node.deprel = 'advcl:cmp'	
	if node.lemma == 'magis':
		node.upos, node.feats = 'ADV', ''
		node.feats['Degree'] = 'Cmp'
	if node.parent.deprel == 'advcl' and node.lemma in ['quam', 'quemadmodum', 'sicut', 'tamquam', 'velut'] and node.upos == 'SCONJ':
		node.parent.deprel = 'advcl:cmp'
		if node.lemma == 'quam':
			node.feats = 'ConjType=Cmpr|PronType=Rel'
	# ut
	if node.lemma == 'ut' and node.parent.deprel == 'advcl':
		if node.parent.feats['Mood'] == 'Ind' and node.lemma in ['aio', 'consto', 'dico', 'infero', 'possum', 'praeadico', 'puto', 'scio', 'soleo', 'tabesco', 'video']: # ut dixi
			node.parent.deprel = 'advcl:cmp'
	if node.lemma == 'ut' and node.parent.upos not in ['AUX', 'VERB']:
		tobe = [s for s in node.siblings if s.deprel == 'cop']
		if not tobe:
			node.parent.deprel = 'advcl:cmp'
		# no 'dictum est' comparative clauses et similia, no comparative clauses w/ nominal predicates are found
	
	
	# passive periphrastic
	if node.lemma == 'sum' and node.parent.feats['VerbForm'] == 'Gdv' and node.deprel == 'cop':
		node.upos, node.deprel = 'AUX', 'aux:pass'

	
	# parataxis, mostly used for coordination		
	if node.deprel == 'parataxis' and node.lemma not in ['aio', 'dico', 'inquam', 'moneo', 'quaeso']:
		brackets = [k for k in node.children if k.form in ['(', ')']]
		if not brackets:
			node.deprel = 'conj'
	if node.deprel == 'advmod' and node.upos == 'VERB' and node.prev_node.form == ',' and node.next_node.form == ',':
		node.deprel = 'parataxis'

		
	# xcomp --> flat
	if node.deprel == 'xcomp' and node.upos == 'NOUN' and node.parent.upos == 'PROPN':
		name = node.parent
		node.deprel = name.deprel
		name.deprel = 'nmod'
		node.parent = name.parent
		name.parent = node


		
# second round of corrections, after the first ones are in place		
for node in doc.nodes:	
		
	# PROPNs dependencies (flat, flat:name)
	# e.g.: Tarquinio Prisco, Servio Tullio, Q Titurium Sabinum legatum, Aemilio Papo imperatore, L. Valerio Flacco et C. Pomptino praetoribus
	if node.upos == 'PROPN':
		other_names = [k for k in node.children if k.upos == 'PROPN' and k.deprel == 'nmod']
		if len(other_names) > 0:
			other_names[0].parent = node.parent
			node.parent = other_names[0]
			other_names[0].deprel = node.deprel
			node.deprel = 'flat:name'
			if len(other_names) == 2: # three names
				other_names[1].parent = other_names[0]
				other_names[1].deprel = 'flat:name'
		elif node.prev_node.upos == 'PROPN' and node.deprel != 'flat:name':
			node.deprel = 'flat:name'
			if node.prev_node.deprel == 'flat:name':
				node.parent = node.prev_node.parent
			else:
				node.parent = node.prev_node

	
# third round of corrections						
for node in doc.nodes:		
			
	if node.upos == 'PROPN' and node.parent.upos == 'NOUN' and node.deprel == 'nmod' and node.feats['Case'] == node.parent.feats['Case']:
		if node.parent.precedes(node):  # NOUN - PROPN
			node.deprel = 'flat'
		elif node.precedes(node.parent): # PROPN - NOUN
			noun = node.parent
			node.parent = noun.parent 
			noun.parent = node
			node.deprel = noun.deprel
			noun.deprel = 'appos'			

	
	# fix non-projectivity of punctuation	
	pun = udapi.block.ud.fixpunct.FixPunct()
	pun.process_tree(node.root)
	
		
with open(f'{output_folder}/HM-la_perseus-ud-{split}.conllu', 'w') as output:
	output.write(doc.to_conllu_string())
