#!/usr/bin/env python3

"""
Script for morphological harmonisation of ITTB and LLCT Latin treebanks.
Usage: python3 morpho-harmon_ittb-llct.py Treebank train/dev/test
"""

import sys
import udapi
import udapi.block.ud.fixpunct

treebank = sys.argv[1]
split = sys.argv[2]  # train/dev/test
morpho_folder = f'/lnet/work/people/gamba/GitHub/morpho_harmonization/morpho-harmonized-treebanks/UD_Latin-{treebank}'
if treebank == 'ITTB':
    filename = f'/lnet/work/people/gamba/GitHub/harmonization/harmonized-treebanks/UD_Latin-ITTB/HM-la_ittb-ud-{split}.conllu'
elif treebank == 'LLCT':
    filename = f'/lnet/work/people/gamba/GitHub/harmonization/harmonized-treebanks/UD_Latin-LLCT/HM-la_llct-ud-{split}.conllu'
doc = udapi.Document(filename)


# function to compose the whole address of a node for a given split
def ad(address, split=split):
    complete_address = split + '-s' + address  # as `sent_id#node_id`
    return complete_address


# preliminary corrections
for node in doc.nodes:
    if treebank == 'ITTB':
        if node.lemma == 'nemo' and node.upos != 'PRON':
            node.upos = 'PRON'
        elif node.deprel == 'acl' and node.feats['VerbForm'] == 'Part' and not node.feats['Gender'] and node.feats['Case'] == node.parent.feats['Case']:
            node.feats['Gender'] = node.parent.feats['Gender']
        elif node.udeprel == 'nsubj' and node.parent.deprel == 'advcl:abs' and node.parent.feats[
            'VerbForm'] == 'Part' and not node.parent.feats['Gender'] and node.feats['Case'] == node.parent.feats['Case']:
            node.parent.feats['Gender'] = node.feats['Gender']
        elif node.lemma == 'quindex' and node.upos == 'NUM':
            node.lemma = 'quindecim'
    elif treebank == 'LLCT':
        if node.lemma == 'sum' and node.upos == 'VERB':
            node.upos = 'AUX'

for node in doc.nodes:

    if node.deprel == 'xcomp:pred':
        node.deprel = 'xcomp'
    if node.feats['Clitic']:
        node.feats['Clitic'] = ''
    if node.feats['ConjType']:
        node.feats['ConjType'] = ''

    if node.upos == 'AUX':
        if treebank == 'ITTB':
            if 'modA' in node.xpos or 'modJ' in node.xpos:  # indicative (resp. active and passive)
                node.feats['VerbForm'], node.feats['Mood'] = 'Fin', 'Ind'
            elif 'modB' in node.xpos or 'modK' in node.xpos:  # subjunctive (resp. active and passive)
                node.feats['VerbForm'], node.feats['Mood'] = 'Fin', 'Sub'
            elif 'modC' in node.xpos:  # imperative
                node.feats['VerbForm'], node.feats['Mood'] = 'Fin', 'Imp'
            if 'gen4' in node.xpos:  # gender-number pairs
                node.feats['Person'], node.feats['Number'] = '1', 'Sing'
            elif 'gen5' in node.xpos:
                node.feats['Person'], node.feats['Number'] = '2', 'Sing'
            elif 'gen6' in node.xpos:
                node.feats['Person'], node.feats['Number'] = '3', 'Sing'
            elif 'gen7' in node.xpos:
                node.feats['Person'], node.feats['Number'] = '1', 'Plur'
            elif 'gen8' in node.xpos:
                node.feats['Person'], node.feats['Number'] = '2', 'Plur'
            elif 'gen9' in node.xpos:
                node.feats['Person'], node.feats['Number'] = '3', 'Plur'
            elif node.form == 'esse' and not node.feats['Aspect']:
                node.feats['VerbForm'], node.feats['Aspect'], node.feats['Tense'] = 'Inf', 'Imp', ''
                node.misc['TraditionalTense'] = 'Praesens'

        elif treebank == 'LLCT':
            if node.lemma == 'sum':
                node.feats['Voice'] = ''
            if node.form in ['sum', 'es', 'is', 'his', 'et', 'est', 'sumus', 'summus', 'estis', 'sunt', 'sit', 'siit',
                             'sia', 'simus', 'sint', 'essem', 'esset', 'essed', 'esse', 'essere', 'habemus', 'abemus',
                             'abetis']:
                node.feats['Aspect'] = 'Imp'
            elif node.form in ['phore', 'abuerimus']:
                node.feats['Aspect'] = 'Prosp'

    if node.upos in ['VERB', 'AUX']:
        # non-finite forms
        if node.feats['VerbForm'] == 'Part':
            if node.feats['Tense'] == 'Pres':
                node.feats['Tense'] = ''
                node.misc['TraditionalMood'], node.misc['TraditionalTense'] = 'Participium', 'Praesens'
            elif node.feats['Tense'] == 'Fut':
                node.feats['Aspect'], node.feats['Tense'] = 'Prosp', ''
                node.misc['TraditionalMood'], node.misc['TraditionalTense'] = 'Participium', 'Futurum'
            elif node.feats['Aspect'] == 'Perf':
                node.feats['Tense'] = ''
                node.misc['TraditionalMood'], node.misc['TraditionalTense'] = 'Participium', 'Perfectum'
        elif node.feats['VerbForm'] == 'Ger':
            node.feats['Aspect'], node.feats['VerbForm'] = 'Prosp', 'Part'
            node.feats['Gender'], node.feats['Number'], node.feats['Tense'] = 'Neut', 'Sing', ''
            node.feats['Voice'] = 'Pass' if node.upos == 'VERB' else ''
            node.misc['TraditionalMood'] = 'Gerundium'
        elif node.feats['VerbForm'] == 'Gdv':
            node.feats['Aspect'], node.feats['VerbForm'] = 'Prosp', 'Part'
            node.feats['Tense'], node.feats['Voice'] = '', 'Pass'
            node.misc['TraditionalMood'] = 'Gerundivum'
        elif node.feats['VerbForm'] == 'Sup':
            node.feats['VerbForm'], node.feats['Tense'], node.feats['Voice'], node.feats[
                'Aspect'] = 'Conv', '', 'Act', 'Prosp'
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
        # finite forms
        if node.feats['Mood'] in ['Imp', 'Ind', 'Sub']:
            if not node.feats['Tense'] and node.xpos:
                if 'tem1' in node.xpos:
                    node.feats['Tense'], node.feats['Aspect'] = 'Pres', 'Imp'
                elif 'tem2' in node.xpos:
                    node.feats['Tense'], node.feats['Aspect'] = 'Past', 'Imp'
                elif 'tem3' in node.xpos:
                    node.feats['Tense'], node.feats['Aspect'] = 'Fut', 'Imp'
                elif 'tem4' in node.xpos:
                    node.feats['Tense'], node.feats['Aspect'] = 'Past', 'Perf'
                elif 'tem5' in node.xpos:
                    node.feats['Tense'], node.feats['Aspect'] = 'Pqp', 'Perf'
                elif 'tem6' in node.xpos:
                    node.feats['Tense'], node.feats['Aspect'] = 'Fut', 'Perf'
            tense_mapping = {'Pres': 'Praesens', 'Pqp': 'Plusquamperfectum', 'Fut': 'Futurum'}  # finite forms
            if node.feats['Tense'] in tense_mapping:
                node.misc['TraditionalTense'] = tense_mapping[node.feats['Tense']]
            elif node.feats['Tense'] == 'Past' and node.feats['Aspect'] == 'Perf':
                node.misc['TraditionalTense'] = 'Perfectum'
            elif node.feats['Tense'] == 'Past' and node.feats['Aspect'] == 'Imp':
                node.misc['TraditionalTense'] = 'Imperfectum'
            mood_mapping = {'Ind': 'Indicativus', 'Sub': 'Subiunctivus', 'Imp': 'Imperativus'}  # finite forms
            if node.feats['Mood'] in mood_mapping:
                node.misc['TraditionalMood'] = mood_mapping[node.feats['Mood']]

    elif node.upos == 'DET':
        if node.lemma in ['qualis', 'quantus', 'quicumque', 'quot'] and (
                not node.feats['PronType'] or ',' in node.feats['PronType']):
            node.feats['PronType'] = 'Rel'
            if node.lemma in ['quantus', 'quot']:
                node.feats['NumType'] = 'Card'
        elif node.lemma in ['aliqualis', 'aliqui', 'nullus', 'qualiscumque', 'quidam', 'quisque', 'quilibet',
                            'quotlibet'] and (
                not node.feats['PronType'] or ',' in node.feats['PronType'] or node.feats['PronType'] == 'Tot'):
            node.feats['PronType'] = 'Ind'
            if node.lemma == 'nullus':
                node.feats['Polarity'] = 'Neg'
        elif node.lemma in ['ambo', 'omnis', 'cunctus', 'totus', 'uniuersus', 'unusquisque']:
            node.feats['PronType'] = 'Tot'
            if node.lemma == 'ambo':
                node.feats['NumType'], node.feats['NumValue'] = 'Card', '2'
        elif node.lemma in ['eiusmodi', 'ille', 'iste', 'hic', 'huiusmodi', 'talis', 'tantus', 'tot']:
            node.feats['PronType'] = 'Dem'
            if node.lemma in ['tantus', 'tot']:
                node.feats['NumType'] = 'Card'

        if treebank == 'ITTB':
            if not node.feats['Poss'] and node.lemma in ['meus', 'tuus', 'suus', 'noster', 'uester']:
                node.feats['Poss'] = 'Yes'
            if not node.feats['PronType'] and node.feats['Person[psor]']:
                node.feats['PronType'], node.feats['Poss'] = 'Prs', 'Yes'
            elif node.lemma in ['multus', 'paucus'] and not node.feats['PronType']:
                node.feats['PronType'], node.feats['NumType'] = 'Ind', 'Card'
            elif node.lemma == 'uterlibet':
                node.feats['PronType'] = 'Con'
            elif node.lemma == 'qui' and node.feats['PronType'] == 'Dem':
                node.upos, node.feats['PronType'] = 'PRON', 'Rel'
            elif node.lemma == 'seipsum':
                node.upos, node.feats['Person'] = 'PRON', '3'
            elif node.lemma == 'qui' and node.feats['PronType'] == 'Rel' and node.deprel == 'det':
                node.upos = 'PRON'
            elif node.lemma == 'is':
                node.upos = 'PRON'
                node.feats['PronType'], node.feats['Person'] = 'Prs', '3'
            elif node.lemma in ['aliquis', 'quisquis', 'quiuis']:
                node.upos = 'PRON'
                if node.lemma == 'quisquis' and ',' in node.feats['PronType']:
                    node.feats['PronType'] = 'Ind'  # due to how it is employed in ITTB
            elif node.form.lower() == 'aliquatenus':
                node.upos, node.deprel = 'ADV', 'advmod'
                node.feats['Case'], node.feats['Gender'], node.feats['InflClass'], node.feats['Number'] = '', '', '', ''
                node.feats['Compound'] = 'Yes'

        elif treebank == 'LLCT':
            if node.lemma in ['alius', 'alter', 'ceterus']:
                node.feats['PronType'] = 'Con'

    if treebank == 'ITTB':
        if node.deprel == 'nmod' and not node.feats['Gender'] and node.feats['Case'] == node.parent.feats['Case'] and \
                node.feats['Number'] == node.parent.feats['Number'] and not node.feats['Abbr'] and node.feats['InflClass'] != 'Ind':
            node.feats['Gender'] = node.parent.feats['Gender']

    if node.upos == 'NUM':
        if node.lemma in ['unus', 'duo', 'tres', 'quattuor', 'quatuor', 'quator', 'quinque', 'sex', 'septem', 'octo',
                          'novem', 'nouem', 'decem', 'undecim', 'duodecim', 'tredecim', 'quattuordecim', 'quindecim',
                          'sedecim', 'septendecim', 'duodeviginti', 'undeviginti', 'uiginti', 'viginti',
                          'duodetreginta', 'triginta', 'quadraginta', 'quinquaginta', 'sexaginta', 'septuaginta',
                          'octoginta', 'nonaginta', 'centum', 'ducenti', 'trecenti', 'quadringenti', 'quingenti',
                          'sescenti', 'octingenti', 'octogenti', 'mille', 'milia']:
            node.feats['NumForm'] = 'Word'
            if not node.feats['NumType']:
                node.feats['NumType'] = 'Card'
            if node.lemma in ['quatuor', 'quator']:
                node.lemma = 'quattuor'

        if treebank == 'ITTB':
            if node.feats['NumForm'] == 'Digit':
                node.feats['NumForm'], node.feats['NumType'] = 'Roman', 'Card'
            elif node.feats['NumForm'] == 'Roman':
                node.feats['NumType'] = 'Card'
            elif node.feats['NumForm'] == 'Reference' and not node.feats['NumType']:
                node.feats['NumType'] = 'Card'

        elif treebank == 'LLCT':
            if node.form in ['XX', 'XIIII']:
                node.feats['NumForm'] = 'Roman'

    elif node.upos == 'PRON':
        if node.lemma == 'se':
            node.lemma, node.feats['Person'] = 'sui', '3'
            node.feats['Reflex'], node.feats['PronType'] = 'Yes', 'Prs'
        elif node.lemma == 'quisquis' and ',' in node.feats['PronType']:
            node.feats['PronType'] = 'Rel'
        elif node.lemma in ['nemo', 'nihil', 'nihilum']:
            node.feats['PronType'], node.feats['Polarity'] = 'Ind', 'Neg'
            node.feats['Gender'], node.feats['Number'] = '', ''
        if node.lemma == 'sui':
            node.feats['Gender'], node.feats['PronType'], node.feats['Person'], node.feats[
                'Reflex'] = '', 'Prs', '3', 'Yes'
        elif node.lemma in ['seipsum', 'semetipse']:
            node.feats['PronType'], node.feats['Person'] = 'Prs', '3'
        elif node.lemma in ['egoipse', 'egometipse']:
            node.feats['Person'] = '1'
        elif node.lemma in ['ego', 'nos', 'nosmetipse']:
            node.feats['Person'] = '1'
            if node.feats['Gender']:
                node.feats['Gender'] = ''
            node.feats['PronType'] = 'Prs'
        elif node.lemma in ['tu', 'tumetipse', 'uos', 'vos']:
            node.feats['Person'] = '2'
            node.feats['PronType'] = 'Prs'
            if node.lemma == 'vos':
                node.lemma = 'uos'

        if treebank == 'ITTB':
            if node.lemma == 'numquis' and ',' in node.feats['PronType']:
                node.feats['PronType'] = 'Int'
            elif node.lemma == 'qui' and node.feats['PronType'] == 'Dem':
                node.feats['PronType'] = 'Rel'
            elif node.lemma in ['quisquam', 'reliquus']:
                node.upos = 'DET'
            elif node.lemma == 'is':
                node.feats['PronType'], node.feats['Person'] = 'Prs', '3'
            elif node.lemma == 'quis' and (',' in node.feats['PronType'] or not node.feats['PronType']):
                question = [d for d in node.root.descendants if d.lemma == '?']
                si = [d for d in node.root.descendants if d.lemma == 'si']
                if question and node < question[0]:
                    node.feats['PronType'] = 'Int'
                elif si and si[0] < node:
                    node.feats['PronType'] = 'Ind'
                else:
                    node.feats['PronType'] = 'Ind'
            elif node.lemma == 'aliquis' and not node.feats['PronType']:
                node.feats['PronType'] = 'Ind'
            elif node.form.lower() == 'quatenus':  # always corresponds to aliquatenus, but nisi precedes
                node.upos, node.deprel = 'ADV', 'advmod'
                node.feats['Case'], node.feats['Gender'], node.feats['InflClass'], node.feats['Number'] = '', '', '', ''
                node.feats['Compound'] = 'Yes'

        elif treebank == 'LLCT':
            if node.lemma == 'is' and node.feats['PronType'] == 'Dem,Prs':
                node.feats['PronType'] = 'Prs'
            elif node.lemma == 'ceterus':
                node.upos, node.feats['PronType'] = 'DET', 'Con'

    # adverbs
    if treebank == 'ITTB':
        if node.upos in ['ADJ', 'DET', 'NOUN', 'VERB'] and node.xpos and 'casG' in node.xpos:
            node.upos = 'ADV'
            node.feats['Case'], node.feats['Number'] = '', ''
            node.feats['Aspect'], node.feats['InflClass[nominal]'], node.feats['VerbForm'], node.feats[
                'Voice'] = '', '', '', ''
            if node.form[-3:] == 'ius':
                node.feats['Degree'] = 'Cmp'
        if node.upos == 'ADV':
            if node.lemma == 'inuicem':
                node.upos, node.feats = 'PRON', 'Compound=Yes|PronType=Rcp'
                node.deprel = 'obl' if node.deprel == 'advmod' else node.deprel
            elif node.lemma == 'numquis' and ',' in node.feats['PronType']:
                node.feats['PronType'] = 'Int'
        if node.form == 'puta':
            node.lemma = node.form

    elif treebank == 'LLCT':
        if node.lemma == 'nihil':
            node.feats['PronType'], node.feats['Polarity'] = 'Ind', 'Neg'

    # other - only in ITTB
    if treebank == 'ITTB':
        if node.upos == 'PROPN':
            if node.feats['Proper']:
                node.feats['Proper'] = ''

        if node.lemma == 'autem' and node.upos in ['ADV', 'CCONJ'] and node.deprel != 'root':
            node.upos, node.deprel = 'PART', 'discourse'

        if node.lemma == 'ambo' and node.upos != 'DET':
            node.upos, node.feats['PronType'] = 'DET', 'Tot'

    # correct specific errors
    if treebank == 'ITTB':
        if not node.feats['Number'] and node.form == 'hoc':
            node.feats['Number'] = 'Sing'
        if node.address() == ad('2056#13') and node.form == 'una':
            node.lemma, node.feats['NumForm'] = 'unus', 'Word'
        if node.address() == ad('5044#9') and node.lemma == 'qui':
            node.feats['Gender'] = 'Neut'
        if node.address() == ad('1957#13'):
            node.feats['Gender'] = ''
        elif node.address() in [ad('1957#13'), ad('7839#15')]:
            node.feats['Gender'] = 'Fem'
        elif node.address() == ad('1847#9') and node.lemma == 'careo':
            node.feats['Gender'] = node.parent.feats['Gender']
        elif (node.address() in [ad('2362#13'), ad('7790#14'), ad('1337#31'), ad('8480#36'),
                                 ad('10582#9')]) and node.lemma == 'quod':
            node.lemma, node.feats['PronType'] = 'qui', 'Rel'
        elif node.address() in [ad('8141#15'), ad('11941#30'), ad('17905#4'), ad('19460#50')] and node.upos == 'PRON':
            node.feats['Case'] = 'Acc'
        elif node.address() == ad('16756#42') and node.lemma == 'aliquid':
            node.lemma, node.feats['PronType'] = 'aliquis', 'Ind'
        elif node.address() == ad('19507#13') and node.upos == 'ADV':
            node.feats['Gender'] = ''
        elif node.address() in [ad('13523#3'), ad('13547#30')] and node.upos == 'PRON':
            node.feats['Case'], node.feats['Number'] = 'Nom', 'Plur'
        elif node.address() == ad('13526#11') and node.lemma == 'plurimus':
            node.lemma = 'multus'

    if treebank == 'LLCT':
        if node.lemma == 'nos' and node.upos == 'PRON' and not node.feats['PronType']:
            node.feats['PronType'], node.feats['Gender'], node.feats['Person'] = 'Prs', '', '1'
        elif node.lemma == 'aliqui' and node.upos == 'PRON':
            node.upos = 'DET'
        elif node.address() == ad('2159#20') and node.lemma == 'fio':
            node.feats['Aspect'] = 'Imp'
        elif node.address() == ad('3479#4') and node.form == 'Toti':
            node.lemma, node.upos, node.feats['PronType'] = 'Totus', 'PROPN', ''
        if node.misc['ToDo']:
            if node.misc['ToDo'] == 'cc-without-conj':
                if node.next_node.form == 'posteros' and node.prev_node.form == 'subcessores':
                    node.parent = node.next_node
                elif node.prev_node.form == 'noctu':
                    node.parent = node.prev_node
                elif node.next_node.form == 'subcessoribus':
                    node.parent = node.next_node
                elif node.prev_node.deprel == 'conj':
                    node.parent = node.prev_node
            elif node.address() == ad('186#33'):
                node.parent = [p for p in node.root.descendants if p.deprel == 'root'][0]
            node.misc['ToDo'] = ''

# fix non-projectivity of punctuation
pun = udapi.block.ud.fixpunct.FixPunct()
pun.process_document(doc)

with open(f'{morpho_folder}/MM-la_{treebank.lower()}-ud-{split}.conllu', 'w') as output:
    output.write(doc.to_conllu_string())
