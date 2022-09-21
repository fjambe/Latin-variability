#!/usr/bin/env python3

'''
Harmonization script for PROIEL Latin treebank.
Usage: python3 harmon-proiel.py train/dev/test
'''

import sys, re
import udapi
import udapi.block.ud.la.addmwt
import udapi.block.ud.convert1to2
import udapi.block.ud.setspaceafterfromtext
import udapi.block.ud.fixpunct

split = sys.argv[1] # train/dev/test
UD_folder = 'path/to/folder/containing/all/UD/Latin/treebanks'
filename = f'{UD_folder}/UD_Latin-PROIEL/la_proiel-ud-{split}.conllu'
output_folder = '/path/to/folder/where/output/is/stored'
doc = udapi.Document(filename)


determiners = ['aliqualis', 'aliqui', 'alius', 'alter', 'alteruter', 'ambo', 'ceterus', 'complura', 'complures', 'cunctus', 'eiusmodi', 'hic', 'huiusmodi', 'idem', 'ille', 'ipse', 'iste', 'meus', 'multus', 'neuter', 'nonnullus', 'noster', 'nullus', 'omnis', 'paucus', 'plerusque', 'qualis', 'quamplures', 'quantus', 'quantuslibet', 'qui', 'quicumque', 'quidam', 'quilibet', 'quispiam', 'quisquam', 'quisque', 'quot', 'quotquot', 'reliquus', 'solus', 'suus', 'talis', 'tantus', 'tot', 'totidem', 'totus', 'tuus', 'uester', 'vester', 'voster', 'ullus', 'uniuersus', 'unusquisque', 'uterque']


# Iterate over all nodes in the document (in all trees)
for node in doc.nodes:
	
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

	
	# nescio quid
	if node.prev_node.lemma == 'nescio' and node.prev_node.upos == 'AUX' and node.prev_node.deprel == 'aux':
		node.prev_node.upos = 'VERB'
		nescio = node.prev_node
		if node.deprel in ['det', 'nmod']:
			nescio.deprel = 'det'
		else:
			nescio.deprel = node.deprel
		node.deprel = 'fixed'
		nescio.parent = node.parent
		node.parent = nescio	
		

	if node.lemma == 'C.':
		node.lemma = 'Caius'
		
	if node.deprel == 'advmod' and node.upos == 'X':
		node.upos = 'ADV'
		
	if node.lemma == 'autem' and node.deprel != 'root':
		node.upos, node.deprel = 'CCONJ', 'cc'
		
	if node.lemma == 'sic' and node.deprel not in ['advmod', 'root', 'conj', 'orphan']:
		node.deprel = 'advmod'
		
	if node.lemma == 'invicem':
		node.upos = 'PRON'
		node.feats = 'Compound=Yes|InflClass=Ind|PronType=Rcp'
		adposition = [k for k in node.children if k.upos == 'ADP']
		cop = [s for s in node.siblings if s.deprel == 'cop']
		obj = [s for s in node.siblings if s.deprel == 'obj']
		if node.deprel != 'nmod':
			if adposition or cop:
				node.deprel = 'obl'
			elif obj:
				node.deprel = 'obl:arg'
			else:
				node.deprel = 'obj'


	# kalendae		
	if node.form.lower().startswith('kal'):
		node.lemma = 'kalendae'
		node.upos = 'NOUN'
		node.feats = 'Gender=Fem|Number=Plur' # cannot assign case
		if node.deprel != 'root':
			node.deprel = 'obl'
		if '.' in node.form and node.form[-1] != '.':
			month = node.create_child()
			month.shift_after_node(node)
			month.form = node.form.split('.')[1]
			node.form = node.form.split('.')[0] + '.'
			month.upos = 'ADJ'
			month.xpos = 'Df'
			month.parent = node
			if node.form[-2:] == 'is' and node.form[-3] != 'i':
				month.deprel = 'nmod'
				month.feats = 'Case=Gen|Gender=Masc|Number=Sing'
			else:
				month.deprel = 'amod'
				month.feats = 'Gender=Fem|Number=Plur'
			node.misc['SpaceAfter'] = 'No'
			if month.form.endswith('as'):
				month.feats['Case'] = 'Acc'
				node.feats['Case'] = 'Acc'
				month.lemma = month.form.replace('as', 'us')
			elif month.form.endswith('ibus') or month.form.endswith('iis'):
				month.feats['Case'] = 'Abl'
				node.feats['Case'] = 'Abl'
	if node.form == 'Maias.':
		node.form, node.lemma = 'Maias', 'Maius'
		node.misc['SpaceAfter'] = 'No'
	if node.prev_node.lemma == 'kalendae' and node.form[0].isupper() and node.upos != 'PROPN':
		node.upos = 'ADJ'
		node.parent = node.prev_node
		if node.form == 'Mai':
			node.deprel, node.lemma = 'nmod', 'Maius'
		elif node.form[-2:] == 'is' and node.form[-3] != 'i':	
			node.deprel = 'nmod'
			if node.feats['Case'] == '':
				node.feats = 'Case=Gen|Gender=Masc|Number=Sing'
		else:
			node.deprel = 'amod'
			
	if node.lemma in ['calendar', 'expression']:
		node.lemma = node.form
			
		
	# atque
	if node.lemma == 'atque' and node.deprel not in ['root', 'cc']:
		node.upos = 'CCONJ'
		if node.parent.lemma in ['aeque', 'alius', 'aliter', 'contra', 'idem', 'par']:
			aeque = node.parent
			kid = [k for k in node.children][0]
			kid.parent = aeque.parent
			kid.deprel = 'advcl:cmpr'
			node.parent = kid
		if node.prev_node.lemma == 'dissimilis':
			dissimilis = node.prev_node
			node.next_node.parent = dissimilis
			node.parent = node.next_node
			node.deprel = 'mark'
			node.next_node.deprel = 'advcl:cmpr'
		elif node.next_node.lemma == 'si':
			node.deprel = 'mark'
			si = node.next_node
			si.parent.parent = node.parent
			node.parent = si.parent
			node.parent.deprel = 'advcl:cmpr'
			si.parent = node
			si.deprel = 'fixed'
		elif node.prev_node.lemma == 'simul':
			node.parent = node.prev_node
			node.deprel = 'fixed'
		else:
			node.deprel == 'cc'			
		
		
	# interjections
	if node.upos == 'INTJ' and node.deprel == 'vocative':
		node.deprel = 'discourse'
			
			
	# discourse particles	
	if node.lemma == 'ergo' and node.deprel != 'discourse': # only 4 cases
		node.deprel = 'discourse'
	if node.lemma == 'etiam' and node.deprel not in ['conj', 'root']:
		node.deprel = 'advmod:emph'
	elif node.lemma in ['en', 'enim', 'equidem', 'etenim', 'igitur', 'itaque', 'nam', 'namque', 'quidem'] and node.deprel not in ['conj', 'root']:
		node.upos, node.deprel = 'PART', 'discourse'
	elif node.lemma == 'ecce' and node.deprel == 'discourse':
		node.upos = 'PART'
		if node.parent.upos != 'VERB':
			node.deprel = 'advmod:emph'
	elif node.lemma in ['num', 'siquidem'] and node.deprel == 'advmod':
		node.upos, node.deprel = 'PART', 'discourse'
		if node.feats['PronType']:
			node.feats['PartType'] = node.feats['PronType']
			node.feats['PronType'] = ''
	elif node.lemma in ['met', 'o'] and node.deprel in ['advmod', 'discourse']:
		node.upos, node.deprel = 'PART', 'advmod:emph'		
		
		
	# ADVerbs
	if node.lemma == 'tamen' and node.deprel == 'discourse':
		node.deprel = 'advmod'
	if node.deprel == 'advmod' and node.upos != 'ADV':
		adp = [k for k in node.children if k.deprel == 'case']
		if adp:
			node.deprel = 'obl'
		elif node.feats['Case'] == 'Dat':
			node.deprel = 'obl:arg'
		elif node.feats['Case'] == 'Abl':
			node.deprel = 'obl'
		elif node.parent.upos == 'NOUN' and node.upos == 'ADJ' and node.feats['Case'] == node.parent.feats['Case'] and node.feats['Number'] == node.parent.feats['Number']:
			node.deprel = 'amod'
		elif node.upos == 'ADJ':
			node.deprel = 'advcl:pred' # mostly accurate, despite some rare exceptions
		elif node.lemma == 'ut':
			node.upos = 'ADV'
		elif node.lemma in ['donec', 'quia', 'quoniam', 'si']:
			node.deprel = 'mark'
		elif node.lemma == 'vel':
			node.deprel = 'advmod:emph'
	if node.lemma in ['et', 'vel'] and node.upos == 'ADV' and node.deprel in ['advmod', 'discourse']:
		node.deprel = 'advmod:emph'
	# locative and temporal adverbs
	if node.form in ['alibi', 'foris', 'hic', 'hinc', 'huc', 'ibi', 'ibidem', 'illuc', 'inde', 'procul', 'qua', 'quo', 'ubi', 'ubicumque', 'ubique', 'unde', 'undique'] and node.form == node.lemma and node.deprel == 'advmod':
		node.deprel = 'advmod:lmod'
		node.feats['AdvType'] = 'Loc'
	if node.form in ['ante', 'cotidie', 'hodie', 'iam', 'interim', 'nonnunquam', 'nunc', 'olim', 'post', 'postea', 'pridem', 'prius', 'quando', 'quandoque', 'saepe', 'semper', 'tum', 'tunc'] and node.form == node.lemma and node.deprel == 'advmod':
		node.deprel = 'advmod:tmod'
		node.feats['AdvType'] = 'Tim'
	# negation	
	if node.lemma in ['haud', 'non'] and node.deprel not in ['conj', 'root']:
		node.upos, node.deprel = 'PART', 'advmod:neg'		
		
	
	# NUMerals
	if node.upos == 'NUM' and node.parent.upos == 'NUM' and node.deprel in ['fixed', 'nummod'] and node.parent.deprel in ['flat', 'nummod']:
		if node.deprel == 'nummod' and node.parent.lemma == 'mille' and node.parent.deprel == 'nummod':
			continue
		else:
			node.deprel = 'flat'
	
		
	# indirect objects
	if node.deprel == 'iobj':
		node.deprel = 'obl:arg'
	
		
	# nmod
	if node.feats['Case'] == 'Gen' and node.parent.upos == 'NOUN' and node.upos in ['ADJ', 'DET', 'PRON'] and node.deprel in ['advmod', 'amod', 'det'] and node.parent.feats['Case'] != 'Gen':
		node.deprel = 'nmod'
	if node.deprel == 'nmod' and node.upos == 'ADJ' and node.feats['Case'] == node.parent.feats['Case'] and node.feats['Number'] == node.parent.feats['Number']:
		node.deprel = 'amod'			
		
		
	# DETerminers
	if node.lemma == 'alteruter':
		node.feats['PronType'] = 'Con'
	if node.lemma in determiners and node.lemma != 'qui' and node.deprel not in ['advmod', 'mark'] and node.upos != 'ADV':
		node.upos = 'DET'
	if node.lemma in determiners and node.deprel == 'amod':
		node.deprel = 'det'
	if node.lemma == 'qui' and node.upos not in ['ADV','PRON']:
		if node.deprel == 'det':
			node.upos = 'DET'
		else:
			node.upos = 'PRON'
	if node.lemma in ['quot', 'tot', 'totidem'] and node.deprel not in ['nsubj', 'obj', 'orphan', 'root']:
		node.deprel = 'det'	
		if node.upos == 'ADV':
			node.upos = 'DET'
	if node.lemma == 'solus':
		if node.deprel in ['amod', 'appos']:
			node.deprel = 'det'	
		elif node.deprel == 'advmod':
			node.deprel ='advcl:pred'
		elif node.deprel == 'dislocated':
			sib = next((s for s in node.siblings if s.upos in ['NOUN', 'PROPN']), False)
			if sib:
				node.deprel = 'det'
				node.parent = sib
	if node.upos == 'DET' and node.feats['Degree'] == 'Sup':
		node.feats['Degree'] = 'Abs'	
	if node.deprel == 'det' and node.feats['Case'] == 'Gen' and node.parent.feats['Case'] != 'Gen' and node.parent.upos != 'VERB': # dominus eius
		node.deprel = 'nmod'

		
	# dep
	if node.deprel == 'dep':
		if node.feats['Case'] == 'Gen' and node.parent.upos == 'NOUN':
			node.deprel = 'nmod'
		elif node.feats['Case'] == 'Abl':
			node.deprel = 'obl'
		elif node.feats['Case'] == 'Acc':
			if len([k for k in node.children if k.deprel == 'case']) > 0:
				node.deprel = 'obl'
		elif node.upos == 'VERB':
			if len([k for k in node.children if k.feats['PronType'] == 'Rel']) > 0:
				node.deprel = 'acl:relcl'
		elif node.upos == 'ADV':
			node.deprel = 'advmod'
		elif node.upos == 'ADJ':
			node.deprel = 'amod'		


	# appos	
	if node.deprel == 'appos' and node.upos == 'ADJ' and node.parent.upos == 'PROPN':
		node.deprel = 'amod'
	if node.deprel == 'appos' and node.parent.upos in ['NOUN', 'PROPN']:
		pron = [k for k in node.children if k.feats['PronType'] == 'Rel']
		if pron:
			node.deprel = 'acl:relcl'
			
				
	# xcomp:pred
	if node.deprel == 'xcomp' and node.upos != 'VERB':
		node.deprel = 'xcomp:pred'		


	if node.lemma in ['quoniam', 'tamquam'] and node.deprel not in ['conj', 'root']:
		node.upos, node.deprel = 'SCONJ', 'mark'

	
	# new PROPNs dependencies
	if node.upos == 'NOUN' and node.parent.upos == 'PROPN' and (node.parent.feats['Case'] == '' or (node.feats['Case'] == node.parent.feats['Case'] and node.feats['Number'] == node.parent.feats['Number'])) and (node.deprel == 'appos' or node.deprel == 'nmod'):
		if node.parent < node: # PROPN - NOUN (Quintus Titurius legatus)
			node.deprel = 'appos'
		elif node < node.parent: # NOUN - PROPN
			kids = [d for d in node.siblings]	
			upper_parent = node.parent
			node.parent = upper_parent.parent
			node.deprel = upper_parent.deprel
			upper_parent.parent = node
			upper_parent.deprel = 'appos' # mostly already like this
			if kids:
				for k in kids:
					if k.deprel not in ['conj', 'flat:name']:
						k.parent = node
						
	if node.upos == 'PROPN' and node.parent.upos == 'NOUN' and (node.parent.feats['Case'] == '' or (node.feats['Case'] == node.parent.feats['Case'] and node.feats['Number'] == node.parent.feats['Number'])):
		if node.parent < node and node.deprel == 'appos': # NOUN - PROPN
			node.deprel = 'flat'


	# AUXiliaries
	if node.deprel.startswith('aux') and node.upos == 'VERB' and node.lemma == 'eo':
		node.feats['Voice'] = ''
		node.upos = 'AUX'


	# participles
	if node.parent.feats['VerbForm'] == 'Part' and node.parent.feats['Voice'] == 'Act' and node.deprel == 'cop':
		node.deprel = 'aux'
	elif node.parent.feats['VerbForm'] == 'Part' and node.parent.feats['Voice'] == 'Pass' and node.deprel == 'aux':
		node.deprel = 'aux:pass'
	
	
	# gerundives
	if node.deprel == 'nsubj' and node.parent.feats['VerbForm'] == 'Gdv':
		sib = [s for s in node.siblings if s.deprel == 'case']
		if sib:
			sib[0].deprel = 'mark'
			node.deprel = 'nsubj:pass'
			if node.parent.deprel not in ['advcl', 'root', 'conj']:
				if node.parent.upos in ['VERB']: # no ADJ occurrences
					node.parent.deprel = 'advcl'
				elif node.parent.upos == 'NOUN':
					node.parent.deprel = 'acl'	
					
						
	# reattach cc and punct to second conjunct
	conv = udapi.block.ud.convert1to2.Convert1to2()
	conv.reattach_coordinations(node)
	
	
	# COMPLEX CONSTRUCTIONS
	
	# Relative clauses
	if node.upos == 'PRON' and node.lemma == 'qui' and node.parent.deprel == 'appos' and node.parent.upos == 'ADJ':
		node.parent.deprel = 'acl:relcl'
	if node.parent.deprel == 'acl' and node.lemma in ['qui', 'ubi']:
		node.parent.deprel = 'acl:relcl'
	if node.lemma in ['qui', 'ubi']:
		if node.parent.parent:
			if node.parent.parent.deprel == 'acl':
				node.parent.parent.deprel = 'acl:relcl'
	if node.deprel == 'nmod':
		rel = [k for k in node.children if k.feats['PronType'] == 'Rel']
		cop = [b for b in node.children if b.deprel == 'cop']
		if len(rel) > 0 and len(cop) > 0:
			node.deprel = 'acl:relcl'
	# elliptical relative clauses
	if node.deprel == 'nsubj' and node.parent.deprel == 'nsubj' and node.feats['PronType'] == 'Rel':
		rel = node.parent
		node.parent = rel.parent
		rel.parent = node
		node.deprel = rel.deprel
		rel.deprel = 'acl:relcl'
	if node.deprel == 'nsubj' and node.parent.deprel == 'obj' and node.feats['PronType'] == 'Rel':
		rel = node.parent
		node.parent = rel.parent
		rel.parent = node
		node.deprel = rel.deprel
		rel.deprel = 'acl:relcl'
	# two subjects in relative structure
	if node.deprel == 'nsubj':
		sib = [s for s in node.siblings]
		bis = [b for b in node.siblings if b.deprel == 'nsubj']
		if bis:
			bis.append(node)
			pron = [b for b in bis if b.feats['PronType'] == 'Rel' and b.upos == 'PRON']
			if pron:
				pron = pron[0]
				bis.remove(pron)
				other = bis[0]
			else:
				continue
			upper = pron.parent
			pron.deprel = upper.deprel
			pron.parent = upper.parent
			upper.deprel = 'acl:relcl'
			upper.parent = pron
			other.parent = pron
			for s in sib:
				if s != pron:
					s.parent = pron

	# fixed in advclauses
	if node.deprel == 'fixed':
		if node.parent.lemma in ['diu', 'minus', 'quam']:
			quam = node.parent
			sib = [s for s in node.siblings]
			node.parent = quam.parent
			quam.parent = node
			node.deprel = 'advcl'
			if sib:
				for s in sib:
					s.parent = node
			if node.parent.lemma == 'quam':
				quam.deprel = 'mark'
			elif node.parent.lemma in ['diu', 'minus']:
				quam.deprel = 'advmod'
		elif node.parent.lemma in ['manu', 'satis']:
			pass


	# comparative clauses
	# quam
	if node.lemma == 'quam' and node.parent.feats['Degree'] == 'Cmp' and node.deprel != 'mark':
		node.upos, node.deprel = 'SCONJ', 'mark'
		node.feats['ConjType'], node.feats['PronType'] = 'Cmpr', 'Rel'
		cmp = node.parent
		advcl = [d for d in node.children if d.deprel != 'conj']
		if len(advcl) == 1:
			advcl[0].deprel = 'advcl:cmpr'
			advcl[0].parent = cmp
			node.parent = advcl[0]	
		elif len(advcl) > 1:
			verb = next((a for a in advcl if a.feats['VerbForm'] == 'Fin'), False)
			if verb:
				verb.parent = cmp
				verb.deprel = 'advcl:cmpr'
				node.parent = verb
			else:
				nom = next((a for a in advcl if a.feats['Case'] == 'Nom'), False)
				if nom:
					nom.parent = cmp
					nom.deprel = 'advcl:cmpr'
					node.parent = nom
				else:
					acc = next((a for a in advcl if a.feats['Case'] == 'Acc'), False)
					if acc:
						acc.parent = cmp
						acc.deprel = 'advcl:cmpr'
						node.parent = acc
	elif node.lemma == 'quam' and node.parent.form in ['amplius', 'celerius', 'citius', 'diutius', 'durius', 'facilius', 'gloriosus', 'gravius', 'honestius', 'latius', 'longius', 'magis', 'melius', 'minus', 'neglegentius', 'paratius', 'plus', 'potius', 'prius', 'rarius', 'tardius', 'tutius']:
		node.upos, node.deprel = 'SCONJ', 'mark'
		node.feats['ConjType'], node.feats['PronType'] = 'Cmpr', 'Rel'
		magis = node.parent
		advcl = [d for d in node.children if d.deprel != 'conj']
		if len(advcl) == 1:
			advcl[0].deprel = 'advcl:cmpr'
			advcl[0].parent = magis.parent
			node.parent = advcl[0]
	elif node.lemma == 'quam' and node.prev_node.form.lower() in ['ante', 'prius', 'post', 'postea']:
		node.upos, node.deprel = 'SCONJ', 'mark'
		node.feats['ConjType'], node.feats['PronType'] = 'Cmpr', 'Rel'
		ante = node.prev_node
		ante.lemma, ante.upos, ante.deprel = ante.form.lower(), 'ADV', 'advmod'
		if node.parent.parent == ante:
			node.parent.parent = ante.parent
		elif ante.parent == node:
			ante.parent = node.parent
		else:
			ante.parent = node.parent.parent
		# node.parent è giusto
		if node.deprel == 'advcl':
			node.deprel = 'advcl:cmpr' # era già advcl
	
	# ut
	if node.lemma == 'ut' and node.upos == 'ADV' and node.parent.deprel in ['advcl', 'dislocated']: # ADV upos was assigned to comparative ut
		node.upos, node.deprel = 'SCONJ', 'mark'
		if node.parent.feats['Mood'] == 'Ind': # ut dixi
			node.parent.deprel = 'advcl:cmpr'
			node.feats['ConjType'] = 'Cmpr'
		elif node.parent.feats['VerbForm'] == 'Part': # ut imperatum est
			aux = [s for s in node.siblings if s.deprel == 'aux:pass' and s.form in ['est', 'sunt']] # mood is not annotated wrt to sum
			if aux:
				node.parent.deprel = 'advcl:cmpr'
				node.feats['ConjType'] = 'Cmpr'
		elif node.parent.upos not in ['AUX', 'VERB']:
			copula = [s for s in node.siblings if s.deprel == 'cop' and s.form in ['est', 'sunt']] # mood is not annotated wrt to sum
			tobe = [s for s in node.siblings if s.deprel == 'cop']
			if copula:
				node.parent.deprel = 'advcl:cmpr'
				node.feats['ConjType'] = 'Cmpr'
			elif not tobe:
				node.parent.deprel = 'advcl:cmpr'
				node.feats['ConjType'] = 'Cmpr'	
	if node.lemma == 'ut' and node.deprel == 'appos':
		if node.parent.deprel == 'advmod':
			adv = node.parent
			kids = [k for k in node.children]
			node.deprel, node.upos = 'mark', 'SCONJ'
			if len(kids) == 1:
				kids[0].parent = adv.parent
				kids[0].deprel = 'advcl:cmpr'
				node.feats['ConjType'] = 'Cmpr'
				node.parent = kids[0]
			elif len(kids) > 1:
				verb = next((k for k in kids if k.feats['VerbForm'] == 'Fin'), False)
				if verb:
					verb.parent = adv.parent
					verb.deprel = 'advcl:cmpr'
					node.feats['ConjType'] = 'Cmpr'
					node.parent = verb
				else:
					nom = next((k for k in kids if k.feats['Case'] == 'Nom'), False)
					if nom:
						nom.parent = adv.parent
						nom.deprel = 'advcl:cmpr'
						node.feats['ConjType'] = 'Cmpr'
						node.parent = nom
					else:
						acc = next((k for k in kids if k.feats['Case'] == 'Acc'), False)
						if acc:
							acc.parent = adv.parent
							acc.deprel = 'advcl:cmpr'
							node.feats['ConjType'] = 'Cmpr'
							node.parent = acc
	if node.lemma == 'ut' and node.parent.deprel == 'appos' and node.deprel == 'orphan':
		node.upos, node.deprel, node.feats['ConjType'] = 'SCONJ', 'mark', 'Cmpr'
		node.parent.deprel = 'advcl:cmpr'
	# tam...quam
	if node.lemma == 'tam':
		node.upos = 'ADV'
	if node.parent.lemma == 'tam' and node.parent.lemma != 'tamquam' and node.lemma == 'quam':
		kid = [k for k in node.children][0]
		kid.parent = node.parent.parent
		kid.deprel = 'advcl:cmpr'
		node.parent.deprel = 'advmod:emph'
		node.parent = kid
		node.deprel = 'mark'
		node.upos = 'SCONJ'
		node.feats['ConjType'], node.feats['PronType'] = 'Cmpr', 'Rel' 
	# tamquam
	if node.form == 'tamquam' and node.deprel not in ['conj', 'root'] and '28124' not in str(node.address): # problematic sentence
		node.upos, node.deprel = 'SCONJ', 'mark'
		kids = [k for k in node.children if k.deprel != 'conj' and k.parent.deprel != 'conj']
		if len(kids) == 1:
			kids[0].parent = node.parent
			kids[0].deprel = 'advcl:cmpr'
			node.parent = kids[0]
		elif len(kids) > 1:
			nom = next((k for k in kids if k.feats['Case'] == 'Nom'), False)
			if nom:
				nom.parent = node.parent
				nom.deprel = 'advcl:cmpr'
				node.parent = nom
			else:
				acc = next((k for k in kids if k.feats['Case'] == 'Acc'), False)
				if acc:
					acc.parent = node.parent
					acc.deprel = 'advcl:cmpr'
					node.parent = acc
				else:
					obl = next((k for k in kids if k.feats['Case'] == 'Abl'), False)
					if obl:
						obl.parent = node.parent
						obl.deprel = 'advcl:cmpr'
						node.parent = obl
	if node.parent.deprel == 'advcl' and node.lemma in ['quam', 'quemadmodum', 'sicut', 'velut']:
		node.upos, node.deprel = 'SCONJ', 'mark'
		node.feats['ConjType'] = 'Cmpr' 
		if not 'quam' in node.prev_node.lemma: # magari cambia quando risolvi antequam priusquam etc.
			node.parent.deprel = 'advcl:cmpr'
	if node.parent.lemma == 'sicut' and node.deprel == 'advcl':
		sicut = node.parent
		cop = [k for k in sicut.children if k.deprel == 'cop' and k < sicut]
		if not cop:
			sicut.upos, sicut.deprel = 'SCONJ', 'mark'
			sicut.feats['ConjType'], sicut.feats['Compound'] = 'Cmpr', 'Yes' 
			node.deprel = 'advcl:cmpr'
			node.parent = sicut.parent
			sicut.parent = node
	if node.lemma == 'sicut' and node.deprel in ['advcl', 'advmod']:
		kids = [k for k in node.children]
		cop = [k for k in node.children if k.deprel == 'cop']
		if not cop:
			node.deprel, node.upos = 'mark', 'SCONJ'
			node.feats['ConjType'], node.feats['Compound'] = 'Cmpr', 'Yes' 
			if len(kids) == 1:
				kids[0].parent = node.parent
				kids[0].deprel = 'advcl:cmpr'
				node.parent = kids[0]
			elif len(kids) > 1:
				verb = next((k for k in kids if k.feats['VerbForm'] == 'Fin'), False)
				if verb:
						verb.parent = node.parent
						verb.deprel = 'advcl:cmpr'
						node.parent = verb
				else:
					nom = next((k for k in kids if k.feats['Case'] == 'Nom'), False)
					if nom:
						nom.parent = node.parent
						nom.deprel = 'advcl:cmpr'
						node.parent = nom
					else:
						acc = next((k for k in kids if k.feats['Case'] == 'Acc'), False)
						if acc:
							acc.parent = node.parent
							acc.deprel = 'advcl:cmpr'
							node.parent = acc

	
	# propterea quod
	if node.lemma == 'propterea' and node.next_node.form == 'quod' and node.deprel != 'mark' and node.next_node.deprel != 'fixed':
		quod = node.next_node
		head = quod.parent
		head.parent = node.parent
		node.deprel = 'mark'
		quod.deprel = 'fixed'
		node.parent = quod.parent
		quod.parent = node

	
	if node.deprel == 'fixed' and node.parent.lemma == 'quam' and 'quam' in node.parent.prev_node.lemma:
		quam = node.parent
		node.parent = quam.parent
		node.deprel = 'advcl'
		quam.parent = node 
	
	# ablative absolute		
	if node.parent.deprel == 'advcl' and node.parent.feats['Case'] == 'Abl' and node.feats['Case'] == 'Abl' and node.deprel.startswith('nsubj'):
		case = [s for s in node.siblings if s.deprel == 'case']
		if len(case) == 0:
			node.parent.deprel = 'advcl:abs'
			
			
	# passive periphrastic
	if node.lemma == 'sum' and node.parent.feats['VerbForm'] == 'Gdv' and node.deprel in ['aux', 'cop']:
		node.deprel = 'aux:pass'
		nsubj = [d for d in node.siblings if d.deprel == 'nsubj']
		if nsubj:
			nsubj[0].deprel = 'nsubj:pass'
		
		
	# ccomp
	if node.lemma == 'quia' and node.deprel in ['ccomp']  and node.next_node:
		subseq = [d for d in node.root.descendants if node < d]
		verb = next((s for s in subseq if s.upos == 'VERB'), False)
		if verb:
			if verb.deprel == 'root':
				verbum = node.parent
				verbum.parent = verb.parent
				verbum.deprel = verb.deprel
				node.deprel = 'mark'
				verb.parent = verbum
			else:
				verb.parent = node.parent
			node.parent = verb
			node.deprel = 'mark'
			verb.deprel = 'ccomp'		
			
			
	# opus est
	if node.deprel == 'nmod' and node.feats['Case'] == 'Abl' and node.parent.form == 'opus':
		node.deprel = 'obl:arg'
		opus = node.parent
		if opus.deprel == 'nsubj' and opus.parent.lemma == 'sum':
			kids = [k for k in opus.siblings]
			upper = opus.parent
			opus.parent = upper.parent
			opus.deprel = upper.deprel
			upper.parent = opus
			upper.deprel = 'cop'
			for k in kids:
				k.parent = opus



# second round of corrections, after the first ones are in place
for node in doc.nodes:

	# numerus est sicut harena maris, non eritis sicut hypocrytae
	if node.parent.lemma in ['sicut', 'tamquam'] and node.parent.deprel in ['acl', 'acl:relcl', 'advcl', 'ccomp', 'conj', 'dislocated', 'root'] and node < node.parent and node.deprel in ['cop', 'nsubj']:
		sicut = node.parent
		sib = [s for s in node.siblings if s > sicut]
		if len(sib) == 1: # mostly only one dependent
			head = sib[0]
		elif len(sib) > 1:
			subj = next((s for s in sib if s.deprel.startswith('nsubj')), False)
			if subj:
				head = subj
			else:
				noun = next((s for s in sib if s.upos == 'NOUN'), False)
				if noun:
					head = noun
		depen = [s for s in head.siblings]
		head.deprel, head.parent = sicut.deprel, sicut.parent
		sicut.deprel, sicut.parent = 'mark', head
		sicut.upos, sicut.feats['ConjType'] = 'SCONJ', 'Cmpr' 
		for d in depen:
				d.parent = head

	# subordinate conjunctions
	if node.lemma in ['nisi', 'quatenus']:
		node.upos, node.deprel = 'SCONJ', 'mark'	
		if node.lemma == 'nisi' and node.parent.deprel != 'advcl':
			kids = [k for k in node.children]
			if len(kids) == 1:
				kids[0].parent = node.parent
				kids[0].deprel = 'advcl'
				node.parent = kids[0]
			elif len(kids) > 1:
				head = next((k for k in kids if k.feats['VerbForm'] == 'Fin'), False)
				if head:
					head.parent = node.parent
					node.parent = head
					head.deprel = 'advcl'
				else:
					head = next((k for k in kids if k.upos in ['NOUN', 'PROPN']), False)
					if head:
						head.parent = node.parent
						node.parent = head
						head.deprel = 'advcl'
	if node.form == 'etiam' and node.parent.form == 'si':
		si = node.parent
		node.lemma, node.upos, node.deprel = 'etiam', 'ADV', 'advmod:emph'
		head = [k for k in si.children if k.deprel == 'fixed'][0]
		head.deprel, head.parent = 'advcl', si.parent
		node.parent = head
		si.parent, si.deprel = head, 'mark'
		for k in si.children:
			k.parent = head
	if node.lemma == 'si' and node.deprel == 'fixed' and node.prev_node.lemma != 'atque': # quod si
		node.deprel = 'mark'
		node.parent = node.parent.parent
	if node.form.lower() == 'quod' and node.deprel == 'mark': # quod	
		node.lemma = node.form.lower()
		node.upos = 'SCONJ'
		node.feats = ''
		node.feats['PronType'] = 'Rel'
	if node.lemma == 'quamvis' and node.upos != 'SCONJ' and node.deprel == 'advmod': # quamvis
		node.upos, node.deprel = 'SCONJ', 'mark'
		node.parent.deprel = 'advcl'
		
		
	
	# fix non-projectivity of punctuation	
	pun = udapi.block.ud.fixpunct.FixPunct()
	pun.process_node(node)	
		
		
		
with open(f'{output_folder}/HM-la_proiel-ud-{split}.conllu', 'w') as output:
	output.write(doc.to_conllu_string())
