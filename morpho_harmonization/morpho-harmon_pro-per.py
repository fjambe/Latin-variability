#!/usr/bin/env python3

"""
Script for morphological harmonisation of Perseus and PROIEL Latin treebanks.
Usage: python3 morpho-harmon_pro-per.py Treebank train/(dev)/test
"""

import sys
import udapi

treebank = sys.argv[1]
split = sys.argv[2]  # train/dev/test
morpho_folder = f'/lnet/work/people/gamba/GitHub/morpho_harmonization/morpho-harmonized-treebanks/UD_Latin-{treebank}'
if treebank == 'Perseus':
    filename = f'/lnet/work/people/gamba/UNIDEPS/UD_Latin-Perseus/la_perseus-ud-{split}.conllu'
elif treebank == 'PROIEL':
    filename = f'/lnet/work/people/gamba/GitHub/harmonization/harmonized-treebanks/UD_Latin-PROIEL/HM-la_proiel-ud-{split}.conllu'

doc = udapi.Document(filename)

if split == 'train':
    from PROIEL_manual_corrections import train as store_dict
elif split == 'dev':
    from PROIEL_manual_corrections import dev as store_dict
elif split == 'test':
    from PROIEL_manual_corrections import test as store_dict

if treebank == 'PROIEL':

    for node in doc.nodes:

        # replicating manual corrections
        # first, features
        # searching for a match; if match is found, apply changes
        if any(match for match in store_dict['feats_info'] if match[0] == node.address()):
            match = [match for match in store_dict['feats_info'] if match[0] == node.address()]
            match = match[0]
            if match[1] == node.lemma:  # compare lemma; right now, always the case
                old_annotation = match[2]
                new_annotation = match[3]
                if old_annotation and old_annotation[0] != '_':
                    temp_dict = {item.split('=')[0]: item.split('=')[1] for item in
                                 old_annotation}  # old feats to be changed
                    for k in temp_dict:
                        for new_feat in new_annotation:
                            if new_feat.split('=')[0] == k:
                                node.feats[k] = new_feat.split('=')[1]
                            elif not any(item.startswith(k) for item in new_annotation):
                                node.feats[k] = ''
                    if new_annotation and new_annotation[0] != '_':
                        for new_feat in new_annotation:
                            f, v = new_feat.split('=')[0], new_feat.split('=')[1]
                            if f not in temp_dict:
                                node.feats[f] = v
                    elif new_annotation and new_annotation[0] == '_':
                        node.feats = ''
                else:
                    for new_feat in new_annotation:
                        f, v = new_feat.split('=')[0], new_feat.split('=')[1]
                        node.feats[f] = v

        # then, UPOS tags
        # searching for a match; if match is found, apply changes
        if any(match for match in store_dict['upos_info'] if match[0] == node.address()):
            match = [match for match in store_dict['upos_info'] if match[0] == node.address()][0]  # only one match
            if match[1] == node.lemma:  # compare lemma; right now, always the case
                node.upos = match[3]  # new UPOS tag

        # correction of previous bugs (in syntax harmonisation)
        if node.lemma == 'nonae':
            if node.form == 'nondum':
                node.lemma, node.upos = 'nondum', 'ADV'
                node.feats['AdvType'] = 'Tim'
                node.feats['Gender'], node.feats['Number'] = '', ''
                node.deprel = 'advmod:tmod'
                node.misc['DeletedPunct'] = ''
            if node.form == 'nonaginta':
                node.lemma, node.upos = 'nonaginta', 'NUM'
                node.feats['NumType'], node.feats['NumForm'] = 'Card', 'Word'
                node.feats['Gender'], node.feats['Number'] = '', ''
                node.misc['DeletedPunct'] = ''
            if node.form in ['nona', 'nonam']:
                node.lemma, node.upos = 'nonus', 'ADJ'
                node.feats = node.parent.feats
                node.feats['NumType'] = 'Ord'
                node.deprel = 'amod'
                node.misc['DeletedPunct'] = ''
            if node.form == 'non' and node.next_node.form == 'nulli':
                node.lemma, node.upos = 'nonnullus', 'DET'
                node.feats = node.next_node.feats
                node.feats['PronType'] = 'Ind'
                node.misc['DeletedPunct'] = ''
            if node.form.lower() in ['nonnulli', 'nonnullos']:
                node.lemma, node.upos = 'nonnullus', 'DET'
                node.feats['PronType'], node.feats['Number'] = 'Ind', 'Plur'
                node.feats['Case'] = 'Acc' if node.lemma.endswith('os') else 'Nom'
                if node.parent.upos == 'VERB':
                    node.deprel = 'obj' if node.form.endswith('os') else 'nsubj'
                elif node.parent.upos in ['NOUN', 'ADJ']:
                    node.deprel = 'det'
                node.misc['DeletedPunct'] = ''
            if node.form.lower() in ['idus', 'idibus']:
                node.lemma = 'idus'
                node.misc['DeletedPunct'] = ''
        if (node.form.lower() in ['non', 'kal', 'dec', 'febr', 'novembr', 'sextil', 'sept', 'pr'] and node.upos in ['NOUN', 'ADJ']) or (node.form.lower() in ['a', 'd'] and node.lemma in ['ante', 'dies']):
            node.feats['Abbr'] = 'Yes'

        if node.form == 'nescio' and node.upos != 'VERB':
            node.upos, node.lemma = 'VERB', 'nescio'
            node.feats = 'Aspect=Imp|Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin|Voice=Act'

        if node.lemma == 'sescentorum':
            node.lemma = 'sescenti'
        elif node.lemma == 'millium':
            node.lemma = 'mille'
        elif node.lemma in ['tria', 'trium']:
            node.lemma = 'tres'
        elif node.lemma == 'quintum' and node.upos == 'ADJ':
            node.lemma = 'quintus'

        # other
        if node.lemma == 'se' and node.upos == 'PRON':
            node.lemma = 'sui'

# not treebank-specific
for node in doc.nodes:

    if node.deprel == 'xcomp:pred':
        node.deprel = 'xcomp'

    if node.lemma == 'nihil' and node.upos in ['ADJ', 'NOUN']:  # respectively in Perseus and PROIEL
        node.upos = 'PRON'

    if node.upos in ['VERB', 'AUX']:
        if node.feats['VerbForm'] == 'Part':
            if node.feats['Tense'] == 'Pres':
                node.feats['Aspect'], node.feats['Tense'] = 'Imp', ''
                node.misc['TraditionalMood'], node.misc['TraditionalTense'] = 'Participium', 'Praesens'
                node.feats['Voice'] = 'Act' if not node.feats['Voice'] else node.feats['Voice']
            elif node.feats['Tense'] == 'Fut':
                node.feats['Aspect'], node.feats['Tense'] = 'Prosp', ''
                node.misc['TraditionalMood'], node.misc['TraditionalTense'] = 'Participium', 'Futurum'
            elif node.feats['Tense'] == 'Past':
                node.feats['Aspect'], node.feats['Tense'] = 'Perf', ''
                node.misc['TraditionalMood'], node.misc['TraditionalTense'] = 'Participium', 'Perfectum'

        if not node.feats['Aspect']:
            if node.feats['Tense'] in ['Pres', 'Fut'] and node.feats['VerbForm'] != 'Part':  # Aspect is already specified (Perf) for forms like voluerit, monstraro
                node.feats['Aspect'] = 'Imp'
            elif node.feats['Tense'] == 'Pqp':
                node.feats['Aspect'] = 'Perf'
        if node.feats['VerbForm'] == 'Ger':
            node.feats['Aspect'], node.feats['VerbForm'], node.feats['Voice'] = 'Prosp', 'Part', 'Pass'
            node.feats['Gender'], node.feats['Number'], node.feats['Tense'] = 'Neut', 'Sing', ''
            node.misc['TraditionalMood'] = 'Gerundium'
        elif node.feats['VerbForm'] == 'Gdv':
            node.feats['Aspect'], node.feats['VerbForm'] = 'Prosp', 'Part'
            node.feats['Tense'], node.feats['Voice'] = '', 'Pass'
            node.misc['TraditionalMood'] = 'Gerundivum'
        elif node.feats['VerbForm'] == 'Sup':
            node.feats['VerbForm'], node.feats['Tense'], node.feats['Voice'], node.feats['Aspect'] = 'Conv', '', 'Act', 'Prosp'
            node.feats['Gender'], node.feats['Number'] = 'Masc', 'Sing'
            node.misc['TraditionalMood'] = 'Sup'
        elif node.feats['VerbForm'] == 'Inf':
            aspect_mapping = {'Imp': 'Praesens', 'Inch': 'Praesens', 'Perf': 'Perfectum', 'Prosp': 'Futurum'}
            node.feats['Tense'] = ''
            node.misc['TraditionalMood'] = 'Infinitivus'
            if node.feats['InflClass[nominal]']:
                node.feats['InflClass[nominal]'] = ''
            if node.feats['Aspect'] in aspect_mapping:
                node.misc['TraditionalTense'] = aspect_mapping[node.feats['Aspect']]
        if node.feats['Mood'] in ['Imp', 'Ind', 'Sub']:
            mood_mapping = {'Ind': 'Indicativus', 'Sub': 'Subiunctivus', 'Imp': 'Imperativus'}
            node.misc['TraditionalMood'] = mood_mapping[node.feats['Mood']]
            tense_mapping = {'Pres': 'Praesens', 'Pqp': 'Plusquamperfectum', 'Fut': 'Futurum'}
            if node.feats['Tense'] in tense_mapping:
                node.misc['TraditionalTense'] = tense_mapping[node.feats['Tense']]
            elif node.feats['Tense'] == 'Past' and node.feats['Aspect'] == 'Perf':
                node.misc['TraditionalTense'] = 'Perfectum'
            elif node.feats['Tense'] == 'Past' and node.feats['Aspect'] == 'Imp':
                node.misc['TraditionalTense'] = 'Imperfectum'
    if node.upos == 'AUX':
        node.feats['Voice'] = ''

    # determiners and pronouns
    if node.lemma in ['nihil', 'aliquis', 'nemo', 'ecquis', 'quisquis'] and node.upos == 'DET':
        node.upos = 'PRON'
    if node.lemma in ['aliquot', 'quotus', 'quispiam', 'uter'] and node.upos in ['NUM', 'PRON']:
        node.upos = 'DET'
        if node.deprel == 'nummod':
            node.deprel = 'det'
    if node.lemma == 'multus' and node.upos == 'ADJ':
        node.upos = 'DET'
    if node.lemma == 'aliquis' and node.upos == 'ADJ':
        node.upos = 'PRON'
    if node.lemma == 'quotquot' and node.upos == 'ADV' and node.parent.upos == 'NOUN':
        node.upos, node.feats['PronType'] = 'DET', 'Rel'
    if node.lemma == 'is' and node.upos == 'ADJ':
        node.upos, node.feats['PronType'] = 'PRON', 'Prs'
    if node.lemma in ['aliquis', 'quis'] and node.upos == 'DET':
        if node.parent.upos == 'NOUN':
            node.lemma = node.lemma[:-1]
        else:
            node.upos = 'PRON'
    if node.form.lower() == 'amplius' and node.lemma == 'amplus' and node.upos in ['ADV', 'PRON']:
        node.lemma, node.upos, node.feats = 'ample', 'ADV', 'Degree=Cmp'

    # other
    if node.lemma == 'autem' and node.upos == 'CCONJ':
        node.upos, node.deprel, node.misc['ToDo'] = 'PART', 'discourse', ''

# second round, not treebank-specific
for node in doc.nodes:

    if node.upos == 'PRON':
        if node.lemma in ['is', 'ego', 'tu', 'sui', 'nos', 'uos', 'vos', 'tumetipse', 'nosmetipse']:
            node.feats['PronType'] = 'Prs'
            if node.lemma in ['ego', 'nos']:
                node.feats['Gender'] = ''
                node.feats['Person'] = '1'
            elif node.lemma in ['tu', 'uos', 'vos']:
                node.feats['Gender'] = ''
                node.feats['Person'] = '2'
            elif node.lemma == 'sui':
                node.feats['Gender'] = ''
                node.feats['Reflex'] = 'Yes'
                node.feats['Person'] = '3'
            elif node.lemma == 'is':
                node.feats['Person'] = '3'
        elif node.lemma in ['aliquis', 'nihil', 'nemo', 'quivis']:
            node.feats['PronType'] = 'Ind'
            if node.lemma == 'nihil':
                node.feats['Polarity'] = 'Neg'
        elif node.lemma in ['inuicem', 'invicem']:
            node.feats['PronType'] = 'Rcp'
            node.feats['InflClass'] = ''
            node.feats['Gender'] = ''
        elif node.lemma in ['quicumque', 'quisquis']:
            node.feats['PronType'] = 'Rel'
        elif node.lemma == 'qui' and (node.parent.deprel == 'acl:relcl' or node.misc['LId'] == 'quis2'):
            node.feats['PronType'] = 'Rel'
        elif node.lemma == 'quis':
            # if node.misc['LId'] == 'quis2' or (node.misc['LId'] == 'quis1' and node.parent.deprel == 'acl'):
            # LId is specific of Perseus
            if node.parent.deprel == 'acl':
                node.lemma = 'qui'
                node.feats['PronType'] = 'Rel'
                node.parent.deprel = 'acl:relcl'
            elif node.parent.parent and node.parent.parent.deprel == 'acl':
                node.lemma = 'qui'
                node.feats['PronType'] = 'Rel'
                node.parent.deprel = 'acl:relcl'
            else:
                node.feats['PronType'] = 'Int'
            if node.parent.deprel in ['csubj', 'csubj:pass', 'ccomp']:
                node.feats['PronType'] = 'Int'
        if node.lemma in ['quisnam', 'ecquis']:
            node.feats['PronType'] = 'Int'
        question = [d for d in node.root.descendants if d.lemma == '?']
        if question and node.lemma == 'quis' and node < question[0]:
            node.feats['PronType'] = 'Int'
        si = [d for d in node.root.descendants if d.lemma == 'si']
        if si and node.lemma == 'quis' and si[0] < node:
            node.feats['PronType'] = 'Ind'

    if node.upos == 'DET':
        if node.lemma in ['suus', 'meus', 'noster', 'tuus', 'uester', 'vester', 'voster']:
            node.feats['PronType'] = 'Prs'
            node.feats['Person'] = ''
            node.feats['Poss'] = 'Yes'
            if node.lemma == 'meus':
                node.feats['Person[psor]'], node.feats['Number[psor]'] = '1', 'Sing'
            if node.lemma == 'tuus':
                node.feats['Person[psor]'], node.feats['Number[psor]'] = '2', 'Sing'
            if node.lemma == 'noster':
                node.feats['Person[psor]'], node.feats['Number[psor]'] = '1', 'Plur'
            if node.lemma in ['voster', 'vester', 'uester', 'uoster']:
                node.feats['Person[psor]'], node.feats['Number[psor]'] = '2', 'Plur'
            if node.lemma == 'suus':
                node.feats['Person[psor]'] = '3'
        elif node.lemma in ['aliquot', 'quidam', 'quivis', 'nullus', 'nonnullus', 'aliqui', 'qui', 'quilibet', 'unus',
                            'ullus', 'multus', 'plures', 'complura', 'complures', 'quamplures', 'quisque', 'paucus',
                            'reliquus', 'plerusque', 'aliqualis', 'quisquam', 'quispiam', 'qualiscumque']:
            node.feats['PronType'] = 'Ind'
            if node.lemma == 'complura':
                node.lemma = 'complures'
            if node.lemma in ['aliquot', 'multus', 'plures', 'complures', 'quamplures', 'paucus']:
                node.feats['NumType'] = 'Card'
                if node.form.lower() == 'plus' and not node.feats['Gender']:
                    node.feats['Gender'] = 'Neut'
        elif node.lemma in ['omnis', 'totus', 'ambo', 'cunctus', 'unusquisque', 'uniuersus']:
            node.feats['PronType'] = 'Tot'
        elif node.lemma in ['qualis', 'quantus', 'quicumque', 'quot']:
            node.feats['PronType'] = 'Rel'
        elif node.lemma in ['qui', 'quot']:
            node.feats['PronType'] = 'Int'
        elif node.lemma in ['hic', 'ipse', 'ille', 'tantus', 'talis', 'is', 'iste', 'eiusmodi', 'huiusmodi', 'idem',
                            'totidem', 'tot']:
            node.feats['PronType'] = 'Dem'
            if node.lemma == 'ipse':
                node.feats['Person'] = ''
        elif node.lemma in ['alius', 'alter', 'solus', 'ceterus', 'alteruter', 'neuter', 'uter', 'uterque']:
            node.feats['PronType'] = 'Con'
        if node.parent.lemma == 'dies' and ',' in node.parent.feats['Gender']:
            node.parent.feats['Gender'] = 'Masc'
            node.feats['Gender'] = node.parent.feats['Gender']

    if node.upos == 'NUM':
        if node.lemma in ['unus', 'duo', 'tres', 'quattuor', 'quinque', 'sex', 'septem', 'octo', 'novem', 'decem',
                          'undecim', 'duodecim', 'quattuordecim', 'quindecim', 'sedecim', 'septendecim', 'duodeviginti',
                          'undeviginti', 'uiginti', 'viginti', 'duodetreginta', 'triginta', 'quadraginta',
                          'quinquaginta', 'sexaginta', 'septuaginta', 'octoginta', 'centum', 'ducenti', 'trecenti',
                          'quadringenti', 'quingenti', 'sescenti', 'octingenti', 'octogenti', 'mille', 'milia']:
            node.feats['NumType'] = 'Card'
            node.feats['NumForm'] = 'Word'
        if node.lemma.lower() in ['ii', 'iii', 'iiii', 'iv', 'v', 'vi', 'vii', 'viii', 'x', 'xi', 'xii', 'xiii',
                                  'xiiii', 'xv', 'xvi', 'xvii', 'xxviii', 'dc']:
            node.feats['NumType'] = 'Card'
            node.feats['NumForm'] = 'Roman'
            if node.feats['Number'] or node.feats['Gender'] or node.feats['Case']:
                node.feats['Number'], node.feats['Gender'], node.feats['Case'] = '', '', ''
        if node.lemma in ['primus', 'secundus', 'tertius', 'quartus', 'quintus', 'sextus', 'decimus', 'undecimus',
                          'duodecimus', 'vicesimus', 'vigesimus', 'septuagensumus', 'millesimus']:
            node.upos = 'ADJ'
            if node.deprel == 'nummod':
                node.deprel = 'amod'
        if node.lemma in ['singulus', 'singuli', 'bini', 'quaterni']:
            node.upos, node.feats['NumType'] = 'ADJ', 'Dist'
            if node.deprel == 'nummod':
                node.deprel = 'amod'
            if node.lemma == 'singulus':
                node.lemma = 'singuli'
        if node.parent.lemma == 'dies' and ',' in node.parent.feats['Gender']:
            node.parent.feats['Gender'] = 'Masc'
            node.feats['Gender'] = node.parent.feats['Gender']

    if node.upos == 'ADJ':
        if node.lemma in ['primus', 'secundus', 'tertius', 'quartus', 'quintus', 'sextus', 'septimus', 'octavus',
                          'nonus', 'decimus', 'undecimus', 'duodecimus', 'vicesimus', 'vigesimus', 'septuagensumus',
                          'millesimus']:
            node.feats['NumType'] = 'Ord'
        if node.lemma == 'nemo':
            node.upos = 'PRON'
            node.feats['PronType'], node.feats['Polarity'] = 'Ind', 'Neg'
            node.feats['Gender'], node.feats['Number'] = '', ''

    if node.feats['Degree'] == 'Pos':
        node.feats['Degree'] = ''

    if node.upos == 'SCONJ':
        node.feats['ConjType'] = ''

    if node.feats['Clitic']:
        node.feats['Clitic'] = ''

    if treebank == 'PROIEL':
        if (node.upos in ['ADJ', 'DET', 'PRON', 'NUM'] and node.deprel in ['amod', 'det', 'nummod']) or (node.feats['VerbForm'] == 'Part' and node.deprel in ['acl', 'orphan']):
            if node.feats['Case'] and not (node.feats['PronType'] in ['Prs', 'Rcp'] and node.upos == 'PRON'):
                if ',' in node.feats['Gender'] or not node.feats['Gender']:
                    node.feats['Gender'] = node.parent.feats['Gender']

    # fixing ToDos (coordination)
    if node.misc['ToDo']:
        if node.misc['ToDo'] in ['cc-without-conj', 'cc-in-coord'] and node.lemma in ['autem', 'que']:
            if node.lemma == 'que' and node.prev_node.lemma != 'ne':
                if node.prev_node.upos == node.prev_node.prev_node.upos:
                    node.parent = node.prev_node
                elif node.prev_node.upos == 'VERB':
                    node.parent = node.prev_node
                elif node.prev_node.parent.upos == 'VERB':
                    node.parent = node.prev_node.parent
        if node.misc['ToDo'] == 'cc-after-conj':
            if node.prev_node.deprel == 'conj':
                node.parent = node.prev_node
            elif node.next_node.deprel == 'conj':
                node.parent = node.next_node
        if node.misc['ToDo'] == 'cc-without-conj':
            if node.next_node and node.next_node.deprel == 'conj':
                node.parent = node.next_node
            if node.next_node and not node.next_node.is_leaf():
                conj = [n for n in node.next_node.children if n.deprel == 'conj']
                if conj:
                    node.parent = node.next_node
        if node.misc['ToDo'] == 'cc-in-coord':
            conj = next((c for c in node.root.descendants if c > node and c.deprel == 'conj'), False)
            if conj:
                node.parent = conj
                if node.lemma == 'et' and node.next_node.lemma == 'ecce':
                    node.next_node.parent = conj
        node.misc['ToDo'] = ''

# third round, following correction of pronouns and determiners
for node in doc.nodes:

    # Gender (PROIEL)
    if ',' in node.feats['Gender'] or not node.feats['Gender'] and node.feats['PronType'] not in ['Prs', 'Rcp']:
        if node.udeprel == 'xcomp' and node.feats['Case']:
            sib = [s for s in node.siblings if s.feats['Case'] == node.feats['Case']]
            if node.feats['Case'] == node.prev_node.feats['Case']:
                node.feats['Gender'] = node.prev_node.feats['Gender']
            elif sib:
                node.feats['Gender'] = sib[0].feats['Gender']

        success = None
        if node.deprel == 'conj' and (node.feats['VerbForm'] == 'Part' or node.upos in ['ADJ', 'DET']):
            conjuncts = [c for c in node.siblings if c.deprel == 'conj' and (c.upos == 'ADJ' or c.feats['VerbForm'] == 'Part')]
            if (node.parent.feats['Gender'] and ',' not in node.parent.feats['Gender']) and (node.parent.upos in ['ADJ', 'DET'] or node.parent.feats['VerbForm'] == 'Part' or (node.parent.upos == 'PRON' and node.parent.feats['PronType'] not in ['Prs', 'Rcp'])):
                node.feats['Gender'] = node.parent.feats['Gender']
            elif conjuncts:
                for c in conjuncts:
                    if c.feats['Gender'] and ',' not in c.feats['Gender']:
                        node.feats['Gender'] = c.feats['Gender']
                        success = True
                        break
                for c in conjuncts:
                    if success and c.feats['Gender'] == '' or ',' in c.feats['Gender'] and (c.upos == 'ADJ' or c.feats['VerbForm'] == 'Part'):
                        c.feats['Gender'] = node.feats['Gender']
                if (node.parent.feats['Gender'] == '' or ',' in node.parent.feats['Gender']) and (node.parent.upos == 'ADJ' or node.parent.feats['VerbForm'] == 'Part'):
                    node.parent.feats['Gender'] = node.feats['Gender']

        # e.g., civitates in quibus
        if node.feats['PronType'] == 'Rel' and node.parent.deprel == 'acl:relcl' and node.upos == 'PRON':
            grandparent = node.parent.parent
            if grandparent.feats['Gender'] and ',' not in grandparent.feats['Gender']:
                node.feats['Gender'] = grandparent.feats['Gender']

        # advcl:abs
        if node.deprel == 'advcl:abs':
            nsubj = [c for c in node.children if
                     c.udeprel == 'nsubj' and c.feats['Gender'] and ',' not in c.feats['Gender']]
            if nsubj:
                node.feats['Gender'] = nsubj[0].feats['Gender']
        if node.udeprel == 'nsubj' and node.parent.deprel == 'advcl:abs' and (
                node.upos != 'PRON' and node.feats['PronType'] not in ['Prs', 'Rcp']):
            if node.parent.feats['Gender'] and ',' not in node.parent.feats['Gender']:  # verifica
                node.feats['Gender'] = node.parent.feats['Gender']

        # cum sollicitior esset … profectus
        if (node.upos == 'ADJ' or node.feats['VerbForm'] == 'Part') and node.feats['Case'] == node.parent.feats['Case'] and node.feats['Number'] == node.parent.feats['Number']:
            if node.deprel == 'advcl':
                node.feats['Gender'] = node.parent.feats['Gender']

        # some guessing euristics
        if node.deprel == 'det' and node.parent.lemma in ['ego', 'tu', 'nos', 'uos', 'vos']:
            node.feats['Gender'] = 'Masc'
        second = [c for c in node.children if c.feats['Person'] in ['1', '2']]
        if second and (node.feats['VerbForm'] == 'Part' or node.upos == 'ADJ'):
            node.feats['Gender'] = 'Masc'
        if node.form == 'cui' and node.prev_node.form == 'ne':
            node.feats['Gender'] = 'Masc'
        if node.form.lower() == 'quis' and node.next_node.form in ['es', 'est']:
            node.feats['Gender'] = 'Masc'
        if node.form == 'nullius' and node.deprel == 'nmod' and node.upos == 'DET':
            node.feats['Gender'] = 'Masc'
        if node.form in ['alicui', 'huic'] and node.upos in ['PRON', 'DET'] and node.feats['Case'] == 'Dat':
            node.feats['Gender'] = 'Masc'
        if node.form in ['certior', 'certiorem', 'certiores']:
            node.feats['Gender'] = 'Masc'
        if node.lemma == 'scrobis':
            node.feats['Gender'] = 'Fem'

        # dies
        if node.lemma == 'dies' and node.feats['Gender'] == 'Fem,Masc':
            genitive = [k for k in node.children if k.deprel == 'nmod' and node.feats['Case'] == 'Gen']
            if genitive:
                node.feats['Gender'] = 'Fem'
            else:
                node.feats['Gender'] = 'Masc'
                children = [c for c in node.children if
                            c.feats['Case'] == node.feats['Case'] and c.feats['Number'] == node.feats['Number']]
                if children:
                    for c in children:
                        c.feats['Gender'] = node.feats['Gender']

    if node.upos in ['ADJ', 'DET'] or (
            node.feats['VerbForm'] == 'Part' and node.misc['TraditionalMood'] == 'Participium') or (node.upos == 'PRON' and node.feats['PronType'] not in ['Prs', 'Rcp']):
        nsubj = [n for n in node.children if
                 n.udeprel == 'nsubj' and n.feats['Gender'] and not ',' in n.feats['Gender']]
        if nsubj:
            node.feats['Gender'] = nsubj[0].feats['Gender']

    # specific corrections
    if node.address() in ['26946#4', '33507#14']:
        node.feats['Voice'] = 'Act'

with open(f'{morpho_folder}/MM-la_{treebank.lower()}-ud-{split}.conllu', 'w') as output:
    output.write(doc.to_conllu_string())
