#!/usr/bin/env python3

'''
Harmonization script for LLCT Latin treebank.
Usage: python3 harmon-llct.py train/dev/test
'''

import sys, re
import udapi
import udapi.block.ud.la.addmwt
import udapi.block.ud.convert1to2
import udapi.block.ud.fixpunct

split = sys.argv[1] # train/dev/test
UD_folder = '/home/federica/Desktop/latin/UD_devbranch' # path to the folder containing all UD Latin treebanks
filename = f'{UD_folder}/UD_Latin-LLCT-dev/la_llct-ud-{split}.conllu'
output_folder = '/home/federica/Desktop/latin/GITHUB/Latin-variability/harmonization/harmonized-treebanks'
doc = udapi.Document(filename)


determiners = ['aliqualis', 'aliqui', 'alius', 'alter', 'alteruter', 'ambo', 'ceterus', 'complura', 'complures', 'cunctus', 'eiusmodi', 'hic', 'huiusmodi', 'idem', 'ille', 'ipse', 'iste', 'meus', 'multus', 'neuter', 'nonnullus', 'noster', 'nullus', 'omnis', 'paucus', 'plerusque', 'qualis', 'quamplures', 'quantus', 'quantuslibet', 'qui', 'quicumque', 'quidam', 'quilibet', 'quispiam', 'quisquam', 'quisque', 'quot', 'reliquus', 'solus', 'suus', 'talis', 'tantus', 'tot', 'totidem', 'totus', 'tuus', 'uester', 'vester', 'voster', 'ullus', 'uniuersus', 'unusquisque', 'uterque']

company = udapi.block.ud.la.addmwt.AddMwt()
conv = udapi.block.ud.convert1to2.Convert1to2()
pun = udapi.block.ud.fixpunct.FixPunct()


# Iterate over all nodes in the document (in all trees)
for node in doc.nodes:

	# MWT
	if node.form != 'tecum':
		company.process_node(node)
	
	
	# discourse particles	
	if node.lemma == 'uero' and node.deprel == 'advmod':
		node.deprel = 'discourse'
	elif node.lemma in ['enim', 'igitur', 'itaque', 'nam', 'namque', 'quidem'] and node.deprel == 'advmod':
		node.upos, node.deprel = 'PART', 'discourse'
	elif node.lemma == 'nam' and node.deprel == 'cc':
		node.upos, node.deprel = 'PART', 'discourse'
	elif node.lemma == 'ecce' and node.deprel == 'advmod:emph':
		node.upos = 'PART'
		if node.parent.upos == 'VERB':
			node.deprel = 'discourse'
			
			
	# ADVerbs
	if node.deprel == 'advmod' and node.upos != 'ADV' and node.lemma != 'non':
		if node.lemma == 'sicut' and node.next_node.form == 'et':
			et = node.next_node
			et.parent.deprel = 'advcl:cmp'
			node.upos, node.deprel = 'SCONJ', 'mark'
			node.parent = et.parent
			et.parent, et.deprel = node, 'fixed'
		elif node.lemma in ['atque', 'aut', 'que', 'seu'] and node.upos == 'CCONJ':
			node.deprel = 'cc'
	# locative and temporal adverbs
	if node.form in ['alibi', 'foris', 'hic', 'hinc', 'huc', 'ibi', 'ibidem', 'illuc', 'inde', 'procul', 'qua', 'quo', 'ubi', 'ubicumque', 'ubique', 'unde', 'undique'] and node.form == node.lemma and node.deprel == 'advmod':
		node.deprel = 'advmod:lmod'
		node.feats['AdvType'] = 'Loc'
	if node.form in ['ante', 'cotidie', 'hodie', 'iam', 'interim', 'nonnunquam', 'nunc', 'olim', 'post', 'postea', 'pridem', 'prius', 'quando', 'quandoque', 'saepe', 'semper', 'tum', 'tunc'] and node.form == node.lemma and node.deprel == 'advmod':
		node.deprel = 'advmod:tmod'
		node.feats['AdvType'] = 'Tim'		
	# negation
	if node.lemma == 'non' and node.deprel == 'advmod':
		node.deprel = 'advmod:neg'
	
		
	# DETerminers
	if node.deprel == 'amod' and (node.upos == 'DET' or node.lemma in determiners):
		node.deprel = 'det'	
	if node.lemma in determiners and node.upos == 'ADJ':
		node.upos = 'DET'
	if node.form == 'quot' and node.lemma != 'quod':
		node.lemma, node.upos = 'quot', 'DET'
		
	
	# NUMerals
	if node.upos == 'NUM' and node.parent.upos == 'NUM' and node.deprel == 'compound':
		if node.parent < node:
			node.deprel = 'flat'
		else: 
			num = node.parent
			node.parent = num.parent
			num.parent = node
			node.deprel = num.deprel
			num.deprel = 'flat'	
			
	# Degree
	if node.feats['Degree'] == 'Sup':
		node.feats['Degree'] = 'Abs'
			
		
	# SCONJ
	if node.lemma == 'nisi' and node.deprel == 'cc':
		node.deprel = 'mark'
		if node.parent.deprel == 'conj':
			node.parent.deprel = 'advcl'
	# aut si
	if node.lemma == 'aut' and node.deprel == 'mark' and node.next_node.lemma == 'si':
		node.deprel = 'cc'
		node.parent = node.next_node.parent
	
	
	# propterea quod
	if node.lemma == 'propterea' and node.next_node.form == 'quod' and node.deprel != 'mark' and node.next_node.deprel != 'fixed':
		quod = node.next_node
		node.deprel = 'mark'
		quod.deprel = 'fixed'
		node.parent = quod.parent
		quod.parent = node
			
	# participles
	if node.parent.feats['VerbForm'] == 'Part' and node.deprel == 'cop' and node.parent.feats['Voice'] == 'Act':
		node.deprel = 'aux'
			
				
	# COMPLEX CONSTRUCTIONS
	
	# absolute ablative
	if node.parent.deprel == 'advcl' and node.parent.feats['Case'] == 'Abl' and node.feats['Case'] == 'Abl' and node.udeprel == 'nsubj':
		case = [s for s in node.siblings if s.deprel == 'case']
		if len(case) == 0:
			node.parent.deprel = 'advcl:abs'

	
	# Relative clauses
	if node.feats['PronType'] == 'Rel' and node.parent.deprel == 'acl':
		node.parent.deprel = 'acl:relcl'
	# qualis
	if node.lemma == 'qualis' and node.deprel == 'acl':
		node.deprel = 'acl:relcl'
	# inverting head-dep in 'sum' dependencies in relative clauses
	if node.lemma == 'qui' and node.deprel == 'obl' and node.parent.lemma == 'sum' and node.parent.deprel == 'acl:relcl':
		dependents = [s for s in node.siblings]
		est = node.parent
		kids = [k for k in node.children if k.deprel == 'case']
		if kids:
			node.parent = est.parent
			node.deprel = est.deprel
			est.parent = node
			est.deprel = 'cop'
			if est.upos == 'VERB':
				est.upos = 'AUX'
			for d in dependents:
				d.parent = node
	
	# csubj -> advcl
	if node.form == 'ego' and node.deprel == 'nsubj' and node.parent.lemma == 'manifestus':
		csubj = [s for s in node.siblings if s.deprel == 'csubj']
		if csubj:
			csubj[0].deprel = 'advcl'		
	
	# xcomp
	if node.lemma in ['capanna', 'casa'] and node.feats['Case'] == 'Acc' and node.deprel == 'xcomp':
		infin = [k for k in node.children if k.deprel == 'conj' and k.feats['VerbForm'] == 'Inf']
		if infin:
			infin[0].parent = node.parent
			infin[0].deprel = node.deprel
			node.parent = infin[0]
			node.deprel = 'obj'
			for i in infin[1:]:
				i.parent = infin[0]
	if node.deprel == 'xcomp' and node.upos != 'VERB':
		esse = [k for k in node.children if k.deprel == 'cop']
		if not esse:
			node.deprel = 'xcomp:pred'


	# comparative clauses
	if node.deprel == 'advcl:cmpr':
		node.deprel = 'advcl:cmp'
	compar = ['quam', 'quasi', 'quemadmodum', 'sicut', 'tamquam', 'uelut']
	if node.parent.deprel == 'advcl' and node.lemma in compar:
		node.parent.deprel = 'advcl:cmp'
		if node.upos != 'SCONJ':
			node.upos = 'SCONJ'
		if node.deprel != 'mark':
			node.deprel = 'mark'
	# ut
	if node.lemma == 'ut' and node.parent.deprel == 'advcl':
		if node.parent.feats['Mood'] == 'Ind' and node.parent.lemma in ['decerno', 'dico', 'lego', 'memoro']: # ut dixi
			node.parent.deprel = 'advcl:cmp'
		elif node.parent.feats['VerbForm'] == 'Part': # ut dictum est
			aux = [s for s in node.siblings if s.deprel == 'aux:pass' and s.form in ['est', 'sunt']]
			if aux:
				node.parent.deprel = 'advcl:cmp'
	# comparative forms + quam
	if node.lemma == 'quam' and node.parent.deprel == 'advcl' and 'ior' in node.parent.parent.form:
		node.upos, node.deprel = 'SCONJ', 'mark' # already like this, just managing errors
		node.parent.deprel = 'advcl:cmp'
		node.feats['PronType'] = 'Rel' 
		
		
	if node.parent.lemma == 'sum' and node.deprel == 'nsubj':
		sib = [s for s in node.siblings if s.deprel == 'obl'] # sib[0] = head of oblique NP 
		dependents = [s for s in node.siblings]
		potestas = [s for s in node.siblings if s.deprel == 'obl' and s.lemma == 'potestas']
		est = node.parent
		if sib:
			kids = [k for k in sib[0].children if k.deprel == 'case'] # kids[0] = adposition in the oblique NP
			if kids and not potestas:
				sib[0].parent = est.parent
				sib[0].deprel = est.deprel
				node.parent = sib[0]
				est.parent = sib[0]
				est.deprel = 'cop'
				if est.upos == 'VERB':
					est.upos = 'AUX'
				for d in dependents:
					if d != sib[0]:
						d.parent = sib[0]				
	
	
    if node.deprel == 'xcomp:pred':
        node.deprel = 'xcomp'
    if node.feats['Clitic']:
        node.feats['Clitic'] = ''
    if node.feats['ConjType']:
        node.feats['ConjType'] = ''
	
						
	# final reattachment of coordinations, since sometimes the previous modifications led to incorrect dependencies				
	conv.reattach_coordinations(node)
	
# correction of 'sum' still occurring as head						
for node in doc.nodes:						
    if node.lemma == 'sum' and node.deprel in ['root', 'conj', 'advcl'] and 'necesse' not in node.form:   
        est_depend = [c for c in node.children] 
        true_dep = [d for d in est_depend if d.udeprel in ['obl', 'advmod', 'ccomp', 'xcomp'] and d.sdeprel not in ['emph', 'neg']]                                    
        if len(true_dep) == 0:
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

	
with open(f'{output_folder}/UD_Latin-LLCT/HM-la_llct-ud-{split}.conllu', 'w') as output:
	output.write(doc.to_conllu_string())
