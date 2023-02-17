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
UD_folder = '/home/federica/Desktop/latin/UD_devbranch' # path to the folder containing all UD Latin treebanks
filename = f'{UD_folder}/UD_Latin-PROIEL-dev/la_proiel-ud-{split}.conllu'
output_folder = '/home/federica/Desktop/latin/GITHUB/Latin-variability/harmonization/harmonized-treebanks'
doc = udapi.Document(filename)


determiners = ['aliqualis', 'aliqui', 'alius', 'alter', 'alteruter', 'ambo', 'ceterus', 'complura', 'complures', 'cunctus', 'eiusmodi', 'hic', 'huiusmodi', 'idem', 'ille', 'ipse', 'iste', 'meus', 'multus', 'neuter', 'nonnullus', 'noster', 'nullus', 'omnis', 'paucus', 'plerusque', 'qualis', 'quamplures', 'quantus', 'quantuslibet', 'qui', 'quicumque', 'quidam', 'quilibet', 'quispiam', 'quisquam', 'quisque', 'quot', 'quotquot', 'reliquus', 'solus', 'suus', 'talis', 'tantus', 'tot', 'totidem', 'totus', 'tuus', 'uester', 'vester', 'voster', 'ullus', 'uniuersus', 'unusquisque', 'uterque']

nums = ['i', 'ii', 'iii', 'iiii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii'] # numerals occurring in dates

company = udapi.block.ud.la.addmwt.AddMwt()
conv = udapi.block.ud.convert1to2.Convert1to2()
pun = udapi.block.ud.fixpunct.FixPunct()
space = udapi.block.ud.setspaceafterfromtext.SetSpaceAfterFromText()


# Iterate over all nodes in the document (in all trees)
for node in doc.nodes:

    # MWT
    if node.form.lower() not in ['a.', 'a.d.', 'd.', 'kal.', 'kalend.', 'non.', 'non.iun.', 'decembr.', 'febr.', 'novembr.', 'quint.', 'sext.']: # dates are dealt with specifically, because they show more complexity and inconsistencies
        company.process_node(node)
    # postprocessing of abbreviation+dot combinations, that in the previous step were provisionally treated like MWTs
    # MWT line is removed, so that in the end they have been simply tokenised
    if node.multiword_token:
        mwt = node.multiword_token
        if mwt.form.endswith('.') and len(mwt.form) > 1 and mwt.form != '...':
            mwt.remove()

    # setting SpaceAfter=No when relevant
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
    # ADVerbs
    if node.lemma == 'tamen' and node.deprel == 'discourse':
        node.deprel = 'advmod'
    if node.deprel == 'advmod' and node.upos != 'ADV':
        adp = [k for k in node.children if k.deprel == 'case']
        if adp:
            node.deprel = 'obl'
        elif node.parent.upos == 'NOUN' and node.upos == 'ADJ' and node.feats['Case'] == node.parent.feats['Case'] and node.feats['Number'] == node.parent.feats['Number']:
            node.deprel = 'amod'
        elif node.upos == 'ADJ':
            node.deprel = 'advcl:pred' # mostly accurate, despite some rare exceptions
        elif node.feats['Case'] == 'Dat':
            node.deprel = 'obl:arg'
        elif node.feats['Case'] == 'Abl':
            node.deprel = 'obl'
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


    # dates
    if node.form.lower().startswith('a.d'):
        d = node.create_child()
        d.shift_after_node(node)
        d.form, d.lemma, d.feats = 'd', 'dies', 'Case=Acc|Gender=Masc|Number=Sing'
        d.upos, d.deprel, d.parent = 'NOUN', 'obl:tmod', node.parent
        d.misc['DeletedPunct'] = '.' if node.form.startswith('a.d.') else ''
        kids = [k for k in node.children if k.deprel != 'fixed']
        for k in kids:
            k.parent = d
        ad = re.match('a\.d\..+', node.form.lower()) # a.d. numeral
        if node.form.lower() in ['a.d', 'a.d.']:
            num = [k for k in node.children if k.deprel == 'fixed' and k > d and k.form.lower() in nums]
            if num:
                num[0].upos, num[0].feats['NumForm'] = 'NUM', 'Roman'
                num[0].lemma = num[0].form
                num[0].deprel, num[0].parent = 'nummod', d
        elif ad:
            num = node.create_child()
            num.shift_after_node(d)
            num.form = node.form.split('.')[-1]
            num.lemma, num.parent = num.form, d
            if num.form in nums:
                num.feats['NumForm'], num.upos, num.deprel = 'Roman', 'NUM', 'nummod'
            else:
                num.feats, num.upos, num.deprel = num.parent.feats, 'ADJ', 'amod'
        node.form, node.lemma, node.upos, node.feats = 'a', 'ante', 'ADP', 'AdpType=Prep'
        node.misc['DeletedPunct'] = '.'
        if node.deprel != 'root':
            node.deprel = 'case'
            node.parent = d
        node.root.text = None
        node.root.text = node.root.get_sentence()
    
    if node.form == 'd.' and node.prev_node.form.lower() in ['a.', 'a']:
        ante = node.prev_node
        node.form, node.lemma, node.feats = 'd', 'dies', 'Case=Acc|Gender=Masc|Number=Sing'
        node.upos, node.deprel, node.parent = 'NOUN', 'obl:tmod', ante.parent
        node.misc['DeletedPunct'] = '.'
        ante.upos, ante.deprel, ante.parent = 'ADP', 'case', node
        ante.lemma, ante.feats = 'ante', 'AdpType=Prep'
        ante.form = ante.form[:-1] if ante.form[-1] == '.' else ante.form
        ante.misc['DeletedPunct'] = '.' if ante.form.lower() == 'a.' else ''
        kids = [k for k in ante.children if k.deprel != 'fixed']
        for k in kids:
            k.parent = node
        if node.next_node.form.lower() in nums:
            num = node.next_node
            num.upos, num.lemma, num.feats['NumForm'], num.deprel, num.parent = 'NUM', num.form, 'Roman', 'nummod', node
        node.root.text = None
        node.root.text = node.root.get_sentence()
    
    if node.form == 'diem' and node.prev_node.form.lower() == 'ante' and node.upos == 'ADV':
        ante = node.prev_node
        node.upos, node.lemma, node.feats = 'NOUN', 'dies', 'Case=Acc|Gender=Masc|Number=Sing'
        node.deprel, node.parent = 'obl:tmod', ante.parent
        ante.upos, ante.lemma, ante.feats = 'ADP', 'ante', 'AdpType=Prep'
        ante.deprel, ante.parent = 'case', node
        kids = [k for k in ante.children if k.deprel != 'fixed']
        for k in kids:
            k.parent = node
        if node.next_node.form.lower() in nums:
            node.next_node.upos, node.next_node.deprel, node.next_node.parent = 'NUM', 'nummod', node
        node.root.text = None
        node.root.text = node.root.get_sentence()
            
    if node.form.lower() in ['decembr.', 'febr.', 'iun', 'novembr.', 'quint.', 'sext.']:
        node.misc['DeletedPunct'] = '.'
        node.form = node.form[:-1]
        node.lemma = 'december' if node.form.lower() == 'decembr' else 'februarius' if node.form.lower() == 'febr' else 'iunius' if node.form.lower() == 'iun' else 'november' if node.form.lower() == 'novembr' else 'quintilis' if node.form.lower() == 'quint' else 'sextilis'
        node.root.text = None
        node.root.text = node.root.get_sentence()
        
    if node.form.lower().startswith(('idus', 'kal', 'non')) and node.feats['Polarity'] != 'Neg': # no abbreviations of Idus found
        node.upos = 'NOUN'
        node.feats = 'Gender=Fem|Number=Plur' # cannot assign case
        if node.form.lower() == 'idus':
            node.lemma = 'Idus'
            if node.next_node and node.next_node.deprel == 'fixed':
                d = node.parent.parent
                node.next_node.parent = d
        if node.deprel != 'root':
            node.deprel = 'nmod'
            if node.parent.form.lower() in ['a', 'ante']:
                d = node.parent.parent
                node.parent = d
        calend = re.match( r'(kal|non)\..+', node.form.lower()) # any string that starts with kal or non, includes a dot, and other characters
        if calend:
            month = node.create_child()
            month.shift_after_node(node)
            month.form = node.form.split('.')[1]
            node.form = node.form.split('.')[0]
            node.misc['DeletedPunct'] = '.'
            month.upos = 'ADJ'
            if node.prev_node.prev_node.lemma == 'dies':
                node.parent = node.prev_node.prev_node
            month.parent = node
            node.lemma = 'kalendae' if node.form.lower().startswith('kal') else 'nonae'
            month.lemma = month.form # approximation
            if (month.form[-2:] == 'is' and month.form[-3] != 'i') or month.form[-1] == 'i': # genitive
                month.deprel = 'nmod'
                month.feats = 'Case=Gen|Gender=Masc|Number=Sing'
            else:
                month.deprel = 'amod'
                month.feats = 'Gender=Fem|Number=Plur'
            if month.form.endswith('as'):
                month.upos = 'ADJ'
                month.feats['Case'] = 'Acc'
                node.feats['Case'] = 'Acc'
                month.lemma = month.form.replace('as', 'us')
            elif month.form.endswith('ibus') or month.form.endswith('iis'):
                month.feats['Case'] = 'Abl'
                node.feats['Case'] = 'Abl'
        elif not calend and node.lemma.lower() not in ['nonne', 'nondum', 'nonaginta', 'nonus', 'nonnumquam', 'nonnullus', 'nonnihil', 'Nonius']:
            if node.form[-1] == '.': # else remains the same
                node.form = node.form[:-1]
                node.misc['DeletedPunct'] = '.'
            if node.form.lower().startswith('kal'):        
                node.lemma = 'kalendae'
            elif node.form.lower() in ['idus', 'idibus']:
                node.lemma = 'idus'
            elif node.form in ['Nonas', 'Nonis', 'Nonarum']:
                node.lemma = 'nonae'
                node.feats['Case'] = 'Acc' if node.form == 'Nonas' else ''
                node.feats['Case'] = 'Abl' if node.form == 'Nonis' else 'Gen'


        node.root.text = None
        node.root.text = node.root.get_sentence()
    
    if node.form in ['Maias', 'Maias.', 'Maiis']:
        node.lemma, node.feats = 'Maius', 'Gender=Fem|Number=Plur'
        if node.form == 'Maiis':
            node.feats['Case'] = 'Abl'
        else:
            node.feats['Case'] = 'Acc'
        if node.form == 'Maias.':
            node.form = 'Maias'
            node.misc['DeletedPunct'] = '.'
            node.root.text = None
            node.root.text = node.root.get_sentence()
            
    # reamining forms lemmatised as 'expression'
    if node.form == 'Decembribus':
        node.lemma = 'December'
    elif node.form == 'Iuniis':
        node.lemma, node.feats['Case'] = 'Iunius', 'Abl'
    elif node.form in ['Sext', 'Sextil', 'Sextilibus', 'Sextilis']:
        node.lemma = 'Sextilis'
    elif node.form == 'Septembr':
        node.lemma = 'September'
    elif node.form in ['Octobr', 'Octobribus']:
        node.lemma = 'October'
    elif node.form == 'Quintilis':
        node.lemma = node.form
    elif node.form == 'Martiis':
        node.lemma = 'Martius'
    elif node.form == 'K':
        node.lemma = 'kalendae'
    
    if node.deprel == 'fixed' and node.upos == 'ADV' and node.form[0].isupper(): 
        node.upos = 'ADJ'
        if node.prev_node.form.lower().startswith(('idus', 'kal', 'non')):
            node.parent = node.prev_node
        if node.form == 'Mai':
            node.deprel, node.lemma = 'nmod', 'Maius'
        elif node.form[-2:] == 'is' and node.form[-3] != 'i':    
            node.deprel = 'nmod'
            if node.feats['Case'] == '':
                node.feats = 'Case=Gen|Gender=Masc|Number=Sing'
        else:
            node.deprel = 'amod'
            node.feats = node.parent.feats
            
    if node.lemma in ['calendar', 'expression', 'calendar.expression']: # correcting less systematic inconsistencies
        if node.form.lower() in ['pr', 'prid', 'pridie', 'postridie']:
            node.lemma = 'pridie' if node.form.startswith('pr') else 'postridie'
        elif node.form.lower().startswith('ian'):
            node.lemma = 'ianuarius'
        elif node.form.lower() == 'ante':
            node.lemma, node.upos, node.feats = 'ante', 'ADP', 'AdpType=Prep'
        elif node.form.lower() == 'a' and node.next_node.form.lower() == 'd':
            d = node.next_node
            node.lemma, node.upos, node.feats = 'ante', 'ADP', 'AdpType=Prep'
            d.lemma, d.upos, d.feats = 'dies', 'NOUN', 'Case=Acc|Gender=Masc|Number=Sing'
            d.parent, d.deprel = node.parent, 'obl:tmod' # not trivial deprel, see train 75863 (just one occurrence)
            node.parent, node.deprel = d, 'case'
            num = d.next_node
            num.lemma, num.feats['NumForm'] = num.form, 'Roman'
            num.upos, num.deprel, num.parent = 'NUM', 'nummod', d
        elif node.form.lower() in ['idibus', 'idus']: 
            node.lemma, node.upos = 'idus', 'NOUN'
            node.feats = 'Case=Abl|Gender=Fem|Number=Plur' if node.form.lower() == 'idibus' else 'Case=Acc|Gender=Fem|Number=Plur'
            node.deprel = 'obl:tmod' if node.deprel == 'advmod' else node.deprel
            if node.next_node and node.next_node.lemma == 'expression':
                month = node.next_node
                month.upos = 'ADJ'
                if month.form[-3:] == 'iis':
                    month.lemma = month.form.replace('iis', 'ius')
                elif month.form[-4:] == 'ibus':
                    month.lemma = month.form.replace('ibus', 'is')
                else:
                    month.lemma = month.form
                month.feats = 'Case=Acc|Gender=Fem|Number=Plur' if node.feats['Case'] == 'Acc' else 'Case=Abl|Gender=Fem|Number=Plur'
                month.deprel, month.parent = 'amod' , node    
        elif node.form == 'Terminalia': # just one occurrence
            node.lemma, node.upos, node.feats, node.deprel, node.parent = node.form, 'NOUN', 'Case=Acc|Gender=Neut|Number=Plur', 'nmod', node.prev_node.prev_node
        elif node.form.lower() in nums and node.next_node.lemma.lower().startswith(('expression', 'ian', 'febr', 'mar', 'april', 'mai', 'iun', 'quint', 'sext', 'sept', 'octob', 'novem', 'dec', 'kal', 'non', 'id')):
            if node.upos == 'ADV':
                node.lemma, node.upos = node.form, 'NUM'
            if node.deprel == 'advmod' and node.parent.upos == 'VERB':
                node.deprel = 'obl:tmod'
        
                    
    # atque
    if node.lemma == 'atque' and node.deprel not in ['root', 'cc']:
        node.upos = 'CCONJ'
        if node.parent.lemma in ['aeque', 'alius', 'aliter', 'contra', 'idem', 'par']:
            aeque = node.parent
            kid = [k for k in node.children][0]
            kid.parent = aeque.parent
            kid.deprel = 'advcl:cmp'
            node.parent = kid
        if node.prev_node.lemma == 'dissimilis':
            dissimilis = node.prev_node
            node.next_node.parent = dissimilis
            node.parent = node.next_node
            node.deprel = 'mark'
            node.next_node.deprel = 'advcl:cmp'
        elif node.next_node.lemma == 'si':
            node.deprel = 'mark'
            si = node.next_node
            si.parent.parent = node.parent
            node.parent = si.parent
            node.parent.deprel = 'advcl:cmp'
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
        
        
    
    # NUMerals
    if node.upos == 'NUM' and node.parent.upos == 'NUM' and node.deprel in ['fixed', 'nummod'] and node.parent.deprel in ['flat', 'nummod']:
        if node.deprel == 'nummod' and node.parent.lemma == 'mille' and node.parent.deprel == 'nummod':
            continue
        else:
            node.deprel = 'flat'
    
    # ADPositions
    if node.upos == 'ADP' and node.precedes(node.parent):
        node.feats['AdpType'] = 'Prep'
        
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
    if node.deprel == 'det' and node.feats['Case'] == 'Gen' and node.parent.feats['Case'] != 'Gen' and node.parent.upos != 'VERB': # dominus eius
        node.deprel = 'nmod'


    # Degree
    if node.feats['Degree'] == 'Sup':
        node.feats['Degree'] = 'Abs'
    
        
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
    if node.udeprel == 'aux' and node.upos == 'VERB' and node.lemma == 'eo':
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
        rel.deprel = 'csubj'
    if node.deprel == 'nsubj' and node.parent.deprel == 'obj' and node.feats['PronType'] == 'Rel':
        rel = node.parent
        rel.deprel = 'ccomp'
    # two subjects in relative structure
    if node.deprel == 'nsubj':
        bis = [b for b in node.siblings if b.deprel == 'nsubj']
        if bis:
            if (node.parent.ord - node.ord) < (node.parent.ord - bis[0].ord): # distance between node's parent and node
                bis[0].deprel = 'nsubj:outer'
            else:
                node.deprel = 'nsubj:outer'


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
        # elif node.parent.lemma in ['manu', 'satis']:
        #     continue


    # comparative clauses
    if node.deprel == 'advcl:cmpr':
        node.deprel = 'advcl:cmp'    
    # quam
    if node.lemma == 'quam' and node.parent.feats['Degree'] == 'Cmp' and node.deprel != 'mark':
        node.upos, node.deprel = 'SCONJ', 'mark'
        node.feats['PronType'] = 'Rel'
        cmp = node.parent
        advcl = [d for d in node.children if d.deprel != 'conj']
        if len(advcl) == 1:
            advcl[0].deprel = 'advcl:cmp'
            advcl[0].parent = cmp
            node.parent = advcl[0]    
        elif len(advcl) > 1:
            verb = next((a for a in advcl if a.feats['VerbForm'] == 'Fin'), False)
            if verb:
                verb.parent = cmp
                verb.deprel = 'advcl:cmp'
                node.parent = verb
            else:
                nom = next((a for a in advcl if a.feats['Case'] == 'Nom'), False)
                if nom:
                    nom.parent = cmp
                    nom.deprel = 'advcl:cmp'
                    node.parent = nom
                else:
                    acc = next((a for a in advcl if a.feats['Case'] == 'Acc'), False)
                    if acc:
                        acc.parent = cmp
                        acc.deprel = 'advcl:cmp'
                        node.parent = acc
    elif node.lemma == 'quam' and node.parent.form in ['amplius', 'celerius', 'citius', 'diutius', 'durius', 'facilius', 'gloriosus', 'gravius', 'honestius', 'latius', 'longius', 'magis', 'melius', 'minus', 'neglegentius', 'paratius', 'plus', 'potius', 'prius', 'rarius', 'tardius', 'tutius']:
        node.upos, node.deprel = 'SCONJ', 'mark'
        node.feats['PronType'] = 'Rel'
        magis = node.parent
        advcl = [d for d in node.children if d.deprel != 'conj']
        if len(advcl) == 1:
            advcl[0].deprel = 'advcl:cmp'
            advcl[0].parent = magis.parent
            node.parent = advcl[0]
    elif node.lemma == 'quam' and node.prev_node.form.lower() in ['ante', 'prius', 'post', 'postea']:
        node.upos, node.deprel = 'SCONJ', 'mark'
        node.feats['PronType'] = 'Rel'
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
            node.deprel = 'advcl:cmp' # era già advcl
    
    # ut
    if node.lemma == 'ut' and node.upos == 'ADV' and node.parent.deprel in ['advcl', 'dislocated']: # ADV upos was assigned to comparative ut
        node.upos, node.deprel = 'SCONJ', 'mark'
        if node.parent.feats['Mood'] == 'Ind': # ut dixi
            node.parent.deprel = 'advcl:cmp'
        elif node.parent.feats['VerbForm'] == 'Part': # ut imperatum est
            aux = [s for s in node.siblings if s.deprel == 'aux:pass' and s.form in ['est', 'sunt']] # mood is not annotated wrt to sum
            if aux:
                node.parent.deprel = 'advcl:cmp'
        elif node.parent.upos not in ['AUX', 'VERB']:
            copula = [s for s in node.siblings if s.deprel == 'cop' and s.form in ['est', 'sunt']] # mood is not annotated wrt to sum
            tobe = [s for s in node.siblings if s.deprel == 'cop']
            if copula:
                node.parent.deprel = 'advcl:cmp'
            elif not tobe:
                node.parent.deprel = 'advcl:cmp'   
    if node.lemma == 'ut' and node.deprel == 'appos':
        if node.parent.deprel == 'advmod':
            adv = node.parent
            kids = [k for k in node.children]
            node.deprel, node.upos = 'mark', 'SCONJ'
            if len(kids) == 1:
                kids[0].parent = adv.parent
                kids[0].deprel = 'advcl:cmp'
                node.parent = kids[0]
            elif len(kids) > 1:
                verb = next((k for k in kids if k.feats['VerbForm'] == 'Fin'), False)
                if verb:
                    verb.parent = adv.parent
                    verb.deprel = 'advcl:cmp'
                    node.parent = verb
                else:
                    nom = next((k for k in kids if k.feats['Case'] == 'Nom'), False)
                    if nom:
                        nom.parent = adv.parent
                        nom.deprel = 'advcl:cmp'
                        node.parent = nom
                    else:
                        acc = next((k for k in kids if k.feats['Case'] == 'Acc'), False)
                        if acc:
                            acc.parent = adv.parent
                            acc.deprel = 'advcl:cmp'
                            node.parent = acc
    if node.lemma == 'ut' and node.parent.deprel == 'appos' and node.deprel == 'orphan':
        node.upos, node.deprel = 'SCONJ', 'mark'
        node.parent.deprel = 'advcl:cmp'
    # tam...quam
    if node.lemma == 'tam':
        node.upos = 'ADV'
    if node.parent.lemma == 'tam' and node.parent.lemma != 'tamquam' and node.lemma == 'quam':
        kid = [k for k in node.children][0]
        kid.parent = node.parent.parent
        kid.deprel = 'advcl:cmp'
        node.parent.deprel = 'advmod:emph'
        node.parent = kid
        node.deprel = 'mark'
        node.upos = 'SCONJ'
        node.feats['PronType'] = 'Rel' 
    # tamquam
    if node.form == 'tamquam' and node.deprel not in ['conj', 'root'] and '28124' not in str(node.address): # problematic sentence
        node.upos, node.deprel = 'SCONJ', 'mark'
        kids = [k for k in node.children if k.deprel != 'conj' and k.parent.deprel != 'conj']
        if len(kids) == 1:
            kids[0].parent = node.parent
            kids[0].deprel = 'advcl:cmp'
            node.parent = kids[0]
        elif len(kids) > 1:
            nom = next((k for k in kids if k.feats['Case'] == 'Nom'), False)
            if nom:
                nom.parent = node.parent
                nom.deprel = 'advcl:cmp'
                node.parent = nom
            else:
                acc = next((k for k in kids if k.feats['Case'] == 'Acc'), False)
                if acc:
                    acc.parent = node.parent
                    acc.deprel = 'advcl:cmp'
                    node.parent = acc
                else:
                    obl = next((k for k in kids if k.feats['Case'] == 'Abl'), False)
                    if obl:
                        obl.parent = node.parent
                        obl.deprel = 'advcl:cmp'
                        node.parent = obl
    if node.parent.deprel == 'advcl' and node.lemma in ['quam', 'quemadmodum', 'sicut', 'velut']:
        node.upos, node.deprel = 'SCONJ', 'mark'
        if not 'quam' in node.prev_node.lemma: # priusquam
            node.parent.deprel = 'advcl:cmp'
    if node.parent.lemma == 'sicut' and node.deprel == 'advcl':
        sicut = node.parent
        cop = [k for k in sicut.children if k.deprel == 'cop' and k < sicut]
        if not cop:
            sicut.upos, sicut.deprel = 'SCONJ', 'mark'
            sicut.feats['Compound'] = 'Yes' 
            node.deprel = 'advcl:cmp'
            node.parent = sicut.parent
            sicut.parent = node
    if node.lemma == 'sicut' and node.deprel in ['advcl', 'advmod']:
        kids = [k for k in node.children]
        cop = [k for k in node.children if k.deprel == 'cop']
        if not cop:
            node.deprel, node.upos = 'mark', 'SCONJ'
            node.feats['Compound'] = 'Yes' 
            if len(kids) == 1:
                kids[0].parent = node.parent
                kids[0].deprel = 'advcl:cmp'
                node.parent = kids[0]
            elif len(kids) > 1:
                verb = next((k for k in kids if k.feats['VerbForm'] == 'Fin'), False)
                if verb:
                        verb.parent = node.parent
                        verb.deprel = 'advcl:cmp'
                        node.parent = verb
                else:
                    nom = next((k for k in kids if k.feats['Case'] == 'Nom'), False)
                    if nom:
                        nom.parent = node.parent
                        nom.deprel = 'advcl:cmp'
                        node.parent = nom
                    else:
                        acc = next((k for k in kids if k.feats['Case'] == 'Acc'), False)
                        if acc:
                            acc.parent = node.parent
                            acc.deprel = 'advcl:cmp'
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
    
    # absolute ablative        
    if node.parent.deprel == 'advcl' and node.parent.feats['Case'] == 'Abl' and node.feats['Case'] == 'Abl' and node.udeprel == 'nsubj':
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
    if node.parent.lemma in ['sicut', 'tamquam'] and node.parent.udeprel in ['acl', 'advcl', 'ccomp', 'conj', 'dislocated', 'root'] and node < node.parent and node.deprel in ['cop', 'nsubj']:
        sicut = node.parent
        sib = [s for s in node.siblings if s > sicut]
        if len(sib) == 1: # mostly only one dependent
            head = sib[0]
        elif len(sib) > 1:
            subj = next((s for s in sib if s.udeprel == 'nsubj'), False)
            if subj:
                head = subj
            else:
                noun = next((s for s in sib if s.upos == 'NOUN'), False)
                if noun:
                    head = noun
        depen = [s for s in head.siblings]
        head.deprel, head.parent = sicut.deprel, sicut.parent
        sicut.deprel, sicut.parent = 'mark', head
        sicut.upos = 'SCONJ'
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
        
        
with open(f'{output_folder}/UD_Latin-PROIEL/HM-la_proiel-ud-{split}.conllu', 'w') as output:
    output.write(doc.to_conllu_string())
