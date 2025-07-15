#!/usr/bin/env python3

'''
Harmonization script for ITTB Latin treebank.
Usage: python3 harmon-ittb.py train/dev/test
'''

import sys, re
import udapi
import udapi.block.ud.la.addmwt
import udapi.block.ud.convert1to2
import udapi.block.ud.setspaceafterfromtext
import udapi.block.ud.fixpunct

split = sys.argv[1] # train/dev/test
UD_folder = '/home/federica/Desktop/latin/UD_devbranch' # path to the folder containing all UD Latin treebanks
filename = f'{UD_folder}/UD_Latin-ITTB-dev/la_ittb-ud-{split}.conllu'
output_folder = '/home/federica/Desktop/latin/GITHUB/Latin-variability/harmonization/harmonized-treebanks'
doc = udapi.Document(filename)


determiners = ['aliqualis', 'aliqui', 'alius', 'alter', 'alteruter', 'ambo', 'ceterus', 'complura', 'complures', 'cunctus', 'eiusmodi', 'hic', 'huiusmodi', 'idem', 'ille', 'ipse', 'iste', 'meus', 'multus', 'neuter', 'nonnullus', 'noster', 'nullus', 'omnis', 'paucus', 'plerusque', 'qualis', 'quamplures', 'quantus', 'quantuslibet', 'qui', 'quicumque', 'quidam', 'quilibet', 'quispiam', 'quisquam', 'quisque', 'quot', 'reliquus', 'solus', 'suus', 'talis', 'tantus', 'tot', 'totidem', 'totus', 'tuus', 'uester', 'vester', 'voster', 'ullus', 'uniuersus', 'unusquisque', 'uterque']

company = udapi.block.ud.la.addmwt.AddMwt()
space = udapi.block.ud.setspaceafterfromtext.SetSpaceAfterFromText()
pun = udapi.block.ud.fixpunct.FixPunct()

# Iterate over all nodes in the document (in all trees)
for node in doc.nodes:

	if node.lemma in ['affectualis', 'afflictiuus', 'atheniensis', 'chalcedonensis', 'ecclesiasticus', 'exclusiuus', 'graecus', 'inconueniens', 'potentialis'] and node.upos == 'NOUN':
		node.upos = 'ADJ'
		if node.deprel == 'appos':
			node.deprel = 'amod'
	if node.lemma.lower() in ['isaias', 'matthaeus'] and node.upos != 'PROPN':
		node.upos = 'PROPN'
	if node.lemma == 'deus' and node.upos == 'PROPN':
		node.upos = 'NOUN'
	if node.upos == 'NOUN' and node.parent.upos == 'PROPN' and node.lemma in ['apostolus', 'propheta', 'uirgo'] and node.deprel != 'conj':	# ioannes apostolus, ionas prophetas, maria uirgo (only in train)
		if node.parent < node: # PROPN - NOUN	
			node.deprel = 'appos'
		else: # NOUN - PROPN
			node.deprel = 'flat'		

	# MWT
	company.process_node(node)
	# postprocessing of abbreviation+dot combinations, which in the previous step were provisionally treated like MWTs
	# MWT line is removed, so that in the end they have been simply tokenised
	if node.multiword_token:
		mwt = node.multiword_token
		if mwt.form.endswith('.') and len(mwt.form) > 1 and mwt.form != '...':
			mwt.remove()
			
	# setting SpaceAfter=No when relevant
	space.process_tree(node.root)
	
	
	# discourse particles	
	if node.lemma in ['ergo', 'uero'] and node.deprel == 'advmod':
		node.upos, node.deprel = 'ADV', 'discourse'
	elif node.lemma in ['enim', 'equidem', 'igitur', 'itaque', 'nam', 'namque', 'quidem', 'siquidem'] and node.deprel == 'advmod':
		node.upos, node.deprel = 'PART', 'discourse'
	elif node.lemma == 'ecce' and node.deprel != 'root':
		node.upos = 'PART'
		if node.parent.upos == 'VERB':
			node.deprel = 'discourse'
		else:
			node.deprel = 'advmod:emph'
	elif node.lemma in ['met', 'o'] and node.deprel not in ['root', 'conj']:
		node.upos = 'PART'
	elif node.lemma == 'an': # an as interrogative particle, not conjunction 
		sib = [s for s in node.siblings if s.lemma == '?']
		if sib:
			node.upos, node.deprel = 'PART', 'discourse'
			
			
	#  ADVerbs
	if node.deprel == 'advmod' and node.upos != 'ADV': # all instances of biblical references (e.g. 'dicitur enim hebr. 3-1', train-s19672)
		if node.parent.deprel != 'obl':
			node.deprel = 'obl'
		else:
			if node.parent.upos == 'NUM':
				node.deprel = 'nmod'
			elif node.parent.upos == 'PROPN':
				lucae = node.parent
				node.deprel = lucae.deprel
				lucae.deprel = 'nmod'
				node.parent = lucae.parent
				lucae.parent = node
	# locative and temporal adverbs
	if node.form in ['alibi', 'foris', 'hic', 'hinc', 'huc', 'ibi', 'ibidem', 'illuc', 'inde', 'procul', 'qua', 'quo', 'ubi', 'ubicumque', 'ubique', 'unde', 'undique'] and node.form == node.lemma and node.deprel == 'advmod':
		node.deprel = 'advmod:lmod'
		node.feats['AdvType'] = 'Loc'
	if node.form in ['ante', 'cotidie', 'hodie', 'iam', 'interim', 'nonnunquam', 'nunc', 'olim', 'post', 'postea', 'pridem', 'prius', 'quando', 'quandoque', 'saepe', 'semper', 'tum', 'tunc'] and node.deprel == 'advmod':
		node.deprel = 'advmod:tmod'
		node.feats['AdvType'] = 'Tim'
			
				
	# NUMerals
	if node.upos == 'NUM' and node.deprel == 'amod':
		node.deprel = 'nummod'
	if node.upos == 'NUM' and node.parent.upos == 'NUM' and node.deprel not in ['conj', 'advcl']:
		if node.parent.form == 'octoginta': # no other instances of numbers
			node.deprel = 'flat'
		
		
	# case
	if node.deprel == 'case' and node.feats['AdpType'] == 'Prep' and node > node.parent: # prepositions depending on wrong head and following correct head
		sib = [s for s in node.siblings]
		non = node.parent
		if len(sib) == 1:
			node.parent = sib[0]
			if non.lemma == 'non': # in this case there is always a mismatch of dependencies
				sib[0].parent = non.parent
		elif sib == []: # only 2 occurrences
			continue
		elif len(sib) > 1:
			sib2 = [s for s in sib if s.deprel not in ['cc', 'punct', 'mark', 'advmod', 'conj']]
			if len(sib2) == 1:
				node.parent = sib2[0]
				if non.lemma == 'non':
					sib[0].parent = non.parent
			else:
				noun = [s for s in sib if s.upos == 'NOUN']
				if len(noun) == 1 or len(noun) > 1:
					node.parent = noun[0]
					if non.lemma == 'non':
						sib[0].parent = non.parent
				else: # only 1 occurrence
					continue
	
	
	# DETerminers
	if node.upos == 'DET' and node.deprel == 'amod':
		node.deprel = 'det'
	if node.lemma == 'huiusmodi' and node.upos != 'DET' and node.parent.upos in ['ADJ', 'DET', 'NOUN']:
		node.upos = 'DET'
		if node.deprel == 'advmod':
			node.deprel = 'det'
	if node.lemma in determiners and node.deprel == 'amod':
		node.deprel = 'det'
	if node.lemma in determiners and node.upos == 'ADJ':
		node.upos = 'DET'
	if node.lemma in ['quot', 'quotquot', 'tot'] and node.deprel == 'nmod':
		node.deprel = 'det'
	
	
	# participles
	if node.parent.feats['VerbForm'] == 'Part' and node.deprel == 'cop':
		if node.parent.lemma in ['doceo', 'nosco']:
			no_ending = node.parent.form.rpartition('t')[0] # reconstructing lemma
			node.parent.lemma = no_ending + 'tus'
			node.parent.upos = 'ADJ'
			node.parent.feats['InflClass'] = node.parent.feats['InflClass[nominal]']
			node.parent.feats['InflClass[nominal]'] = ''
			node.parent.feats['Voice'] = ''
			node.parent.feats['Aspect'] = ''
		elif node.parent.feats['Voice'] == 'Pass':
			node.deprel = 'aux:pass'
		elif node.parent.feats['Voice'] == 'Act':
			node.deprel = 'aux'		
		
	# Degree
	if node.feats['Degree'] == 'Sup':
		node.feats['Degree'] = 'Abs'
		
			
	# expl:pass
	if node.deprel == 'expl:pass':
		if node.parent.feats['Voice'] == 'Act' or node.parent.feats['VerbForm'] == 'Ger':
			if node.feats['Case'] == 'Acc':
				node.deprel = 'obj'
			elif node.feats['Case'] == 'Dat':
				node.deprel = 'obl:arg'
			
		
	# COMPLEX CONSTRUCTIONS
		
	# Relative clauses
	if node.feats['PronType'] == 'Rel' and node.parent.deprel == 'acl':
		node.parent.deprel = 'acl:relcl'
	if node.lemma == 'qualis' and node.deprel == 'acl':
		node.deprel = 'acl:relcl'
	# inverting head-dep in 'sum' dependencies in relative clauses
	if node.lemma == 'qui' and node.deprel == 'obl' and node.parent.lemma == 'sum':
		dependents = [s for s in node.siblings]
		est = node.parent
		kids = [k for k in node.children if k.deprel == 'case']
		if kids:
			node.parent = est.parent
			node.deprel = est.deprel
			est.parent = node
			est.deprel = 'cop'
			for d in dependents:
				d.parent = node
		
		
	# comparative clauses
	if node.deprel == 'advcl:cmpr':
		node.deprel = 'advcl:cmp'
	compar = ['quam', 'quasi', 'quemadmodum', 'sicut', 'tamquam', 'uelut']
	if node.parent.deprel == 'advcl:cmp' and node.lemma in compar and node.upos == 'ADV':
		node.upos, node.deprel = 'SCONJ', 'mark'
	if node.parent.deprel == 'advcl' and node.lemma in compar and node.upos == 'SCONJ':
		sib = [s for s in node.siblings if s.deprel == 'mark' and s.upos == 'SCONJ']
		if sib:
			if node < sib[0]:
				node.parent.deprel = 'advcl:cmp'
				node.deprel = 'mark'
	# ut
	if node.lemma == 'ut' and node.parent.deprel == 'advcl' and node < node.parent:
		if node.parent.feats['Mood'] == 'Ind': # ut dicitur
			node.parent.deprel = 'advcl:cmp'
			node.upos, node.deprel = 'SCONJ', 'mark'
		elif node.parent.feats['VerbForm'] == 'Part': # ut dictum/ostensum est
			aux = [s for s in node.siblings if s.deprel == 'aux:pass' and s.form in ['est', 'sunt']] # mood is not annotated wrt to sum
			if aux:
				node.parent.deprel = 'advcl:cmp'
				node.upos, node.deprel = 'SCONJ', 'mark'
		elif node.parent.upos not in ['AUX', 'VERB']:
			copula = [s for s in node.siblings if s.deprel == 'cop' and s.form in ['est', 'sunt']] # mood is not annotated wrt to sum
			tobe = [s for s in node.siblings if s.deprel == 'cop']
			if copula:
				node.parent.deprel = 'advcl:cmp'
				node.upos, node.deprel = 'SCONJ', 'mark'
			elif not tobe:
				node.parent.deprel = 'advcl:cmp'
				node.upos, node.deprel = 'SCONJ', 'mark'
	# quasi
	if node.lemma == 'quasi' and node.deprel == 'mark' and node.parent.deprel == 'advcl':
		node.parent.deprel = 'advcl:cmp'
	# magis quam, alius quam, comparative + quam
	if node.lemma == 'quam' and node.parent.deprel == 'advcl':
		node.upos, node.deprel = 'SCONJ', 'mark' # already like this, just managing errors
		node.parent.deprel = 'advcl:cmp'
		node.feats['PronType'] = 'Rel'
	if node.lemma == 'quam' and node.parent.deprel == 'conj': # tam...quam
		kids = [k for k in node.parent.siblings if k.lemma == 'tam']
		if kids:
			node.deprel, node.upos = 'mark', 'SCONJ'
			node.feats['PronType'] = 'Rel'
			father = node.parent
			father.deprel = 'advcl:cmp'
			kids[0].deprel = 'advmod:emph'
	
	
	# absolute ablative
	if node.parent.deprel == 'advcl' and node.parent.feats['Case'] == 'Abl' and node.feats['Case'] == 'Abl' and node.udeprel == 'nsubj':
		case = [s for s in node.siblings if s.deprel == 'case']
		if len(case) == 0:
			node.parent.deprel = 'advcl:abs'
			
	
	# etiam si was annotates as fixed		
	if node.deprel == 'fixed' and node.parent.lemma == 'etiam' and node.lemma == 'si':
		etiam = node.parent
		node.deprel = 'mark'
		etiam.deprel = 'advmod:emph'
		node.parent = etiam.parent
		
	
	# propterea quod
	if node.lemma == 'propterea' and node.next_node.form == 'quod' and node.next_node.deprel != 'fixed':
		node.next_node.deprel = 'fixed'
		node.next_node.parent = node
		
		
	# mark-advcl with nominalised participles
	if node.upos == 'ADP' and node.deprel == 'mark' and node.parent.feats['VerbForm'] == 'Part' and node.next_node.lemma != 'quod': # e.g. not secundum quod
		if node.parent.deprel in ['advcl', 'ccomp']:
			node.deprel = 'case'
			node.parent.deprel = 'obl'
		elif node.parent.deprel == 'conj':
			node.deprel = 'case'
		elif node.parent.deprel == 'acl':
			node.deprel = 'case'
			node.parent.deprel = 'nmod'
		elif node.form == 'per' and node.parent.form == 'consequens':
			node.deprel = 'case'		
		
		
	# opus est
	if node.feats['Case'] == 'Abl' and node.parent.form == 'opus' and node.parent.parent.lemma == 'sum':
		sib = [s for s in node.parent.siblings]
		est = node.parent.parent
		opus = node.parent
		opus.parent = est.parent
		opus.deprel = est.deprel
		est.parent = opus
		est.deprel = 'cop'
		node.deprel = 'obl:arg'
		node.parent = opus
		for s in sib:
			s.parent = opus

	if node.deprel == 'csubj' and node.parent.lemma in ['dico', 'pono', 'probo', 'requiro'] and node.parent.feats['Voice'] == 'Act':
		node.deprel = 'ccomp'
		
	if node.udeprel == 'nsubj':
		s = [s for s in node.siblings if s.udeprel == 'csubj']
		if s:
			if s[0].feats['VerbForm'] == 'Inf':
				if node.parent.lemma == 'possum':
					s[0].deprel = 'xcomp'
				else:
					if node.feats['Case'] == 'Acc' or node.feats['Gender'] == 'Neut':
						node.parent = s[0]
						if s[0].feats['Voice'] == 'Pass':
							node.deprel = 'nsubj:pass'
							
if node.deprel == 'xcomp:pred':
	node.deprel = 'xcomp'
if node.feats['Clitic']:
	node.feats['Clitic'] = ''
if node.feats['ConjType']:
	node.feats['ConjType'] = ''


# second round of interventions, after the first ones are in place
for node in doc.nodes:

	# inverting head-dep in 'sum' construcions (general)
	if node.parent.lemma == 'sum' and node.deprel == 'nsubj':
		sib = [s for s in node.siblings if s.deprel == 'obl' and s.form != 'etc'] # sib[0] = head of oblique NP 
		csubj = [s for s in node.siblings if s.udeprel == 'csubj']
		dependents = [s for s in node.siblings]
		est = node.parent
		if sib:
			kids = [k for k in sib[0].children if k.deprel == 'case'] # kids[0] = adposition in the oblique NP
			if kids:
				sib[0].parent = est.parent
				sib[0].deprel = est.deprel
				node.parent = sib[0]
				est.parent = sib[0]
				est.deprel = 'cop'
				for d in dependents:
					if d != sib[0] and not re.search(r'test-s1348#41\b', str(d.address)) and not re.search(r'test-s1348#43\b', str(d.address)): # specific intervention needed for validation (otherwise, conj right-to-left)
						d.parent = sib[0]
						
		elif csubj:
			csubj[0].parent = est.parent
			csubj[0].deprel = est.deprel
			node.parent = csubj[0]
			est.parent = csubj[0]
			est.deprel = 'cop'
			for d in dependents:
				if d != csubj[0]:
					d.parent = csubj[0]
				sib = [s for s in node.siblings if s.deprel == 'nsubj']
			chil = [c for c in csubj[0].children if c.deprel == 'nsubj']
			if chil:
				if node in chil:
					node.deprel = 'nsubj:outer'
			
	elif node.form == 'esse' and node.parent.lemma == 'possum':
		subj = [s for s in node.siblings if s.udeprel == 'nsubj']
		obl = [k for k in node.children if k.deprel == 'obl'] # obl[0] = head of oblique NP 
		if subj and obl:
			dependents = [s for s in node.children]
			adp = [k for k in obl[0].children if k.deprel == 'case'] # adp[0] = adposition in the oblique NP
			if adp:
				obl[0].parent = node.parent
				obl[0].deprel = node.deprel
				node.parent = obl[0]
				node.deprel = 'cop'
				for d in dependents:
					if d != obl[0]:
						d.parent = obl[0]

# correction of 'sum' still occurring as head						
for node in doc.nodes:						
    if node.lemma == 'sum' and node.deprel in ['root', 'conj', 'advcl'] and 'necesse' not in node.form:   
        est_depend = [c for c in node.children] 
        true_dep = [d for d in est_depend if d.udeprel in ['obl', 'advmod', 'ccomp', 'xcomp'] and d.sdeprel not in ['emph', 'neg']]
        if node.prev_node.form.lower() == 'hoc' and node.next_node.form == 'quod' and node.next_node.next_node.lemma == 'dico': # hoc est quod dicitur/dicit			
            dico = node.next_node.next_node
            node.prev_node.deprel = 'nsubj:outer'
            dico.deprel, dico.parent = node.deprel, node.parent
            node.parent, node.deprel = dico, 'cop'
            for other_dep in est_depend:
                if other_dep != dico:
                    other_dep.parent = dico
        
        elif any(c.udeprel == 'ccomp' for c in est_depend):
            c = [c for c in est_depend if c.udeprel == 'ccomp'][0]
            c.parent, c.deprel = node.parent, node.deprel
            node.parent, node.deprel = c, 'cop'
            for other_c in est_depend:
                if other_c != c:
                    other_c.parent = c
            # explicit vs implicit ccomp clauses
            subjects = [sub for sub in c.children if sub.udeprel == 'nsubj']
            if c.feats['VerbForm'] == 'Fin' and len(subjects) > 1:
                subjects[0].deprel = 'nsubj:outer'
                                        
        elif len(true_dep) == 0:
            continue # 'sum' remains root
        elif len(true_dep) == 1:
            true_dep[0].parent, true_dep[0].deprel = node.parent, node.deprel
            node.parent, node.deprel = true_dep[0], 'cop'
            for other_dep in est_depend:
                if other_dep != true_dep[0]:
                    other_dep.parent = true_dep[0]
        elif len(true_dep) > 1:
            obl = [n for n in true_dep if n.udeprel == 'obl']
            if obl:
                obl[0].parent, obl[0].deprel = node.parent, node.deprel
                node.parent, node.deprel = obl[0], 'cop'
                for other_dep in est_depend:
                    if other_dep != obl[0]:
                        other_dep.parent = obl[0]
            else:
                true_dep[0].parent, true_dep[0].deprel = node.parent, node.deprel # pick the first non-subject dependent, since it is not possible to automatically decide which one should be the head  
                node.parent, node.deprel = true_dep[0], 'cop'
                for other_dep in est_depend:
                    if other_dep != true_dep[0]:
                        other_dep.parent = true_dep[0]
                        

# fix non-projectivity of punctuation
pun.process_document(doc)

with open(f'{output_folder}/UD_Latin-ITTB/HM-la_ittb-ud-{split}.conllu', 'w') as output:
	output.write(doc.to_conllu_string())
