#!/usr/bin/env python3

"""
Script for morphological harmonisation of UDante Latin treebank.
Usage: python3 morpho-harmon_udante.py train/dev/test
"""

import sys
import udapi
import udapi.block.ud.fixpunct


split = sys.argv[1]  # train/dev/test
treebank = 'UDante'
morpho_folder = f'/lnet/work/people/gamba/GitHub/morpho_harmonization/morpho-harmonized-treebanks/UD_Latin-{treebank}'
filename = f'/lnet/work/people/gamba/GitHub/harmonization/harmonized-treebanks/UD_Latin-UDante/HM-la_udante-ud-{split}.conllu'
doc = udapi.Document(filename)

for node in doc.nodes:

    if node.upos in ['AUX', 'VERB']:
        if node.feats['VerbForm'] == 'Vnoun':
            node.feats['VerbForm'] = 'Inf'
        # TraditionalTense and TraditionalMood
        mood_mapping = {'Ind': 'Indicativus', 'Sub': 'Subiunctivus', 'Imp': 'Imperativus'}  # finite forms
        tense_mapping = {'Pres': 'Praesens', 'Fut': 'Futurum'}  # finite
        aspect_mapping = {'Imp': 'Praesens', 'Inch': 'Praesens', 'Perf': 'Perfectum', 'Prosp': 'Futurum'}  # non-finite

        if node.feats['Mood'] in mood_mapping:
            node.misc['TraditionalMood'] = mood_mapping[node.feats['Mood']]
        if node.feats['Tense'] in tense_mapping:
            node.misc['TraditionalTense'] = tense_mapping[node.feats['Tense']]
        elif node.feats['Tense'] == 'Pres' and node.feats['Aspect'] == 'Perf':
            node.misc['TraditionalTense'] = 'Perfectum'
        elif node.feats['Tense'] == 'Past' and node.feats['Aspect'] == 'Perf':
            node.misc['TraditionalTense'] = 'Plusquamperfectum'
        if node.feats['VerbForm'] == 'Part':
            if node.xpos[-3:-1] == 'fg':
                node.misc['TraditionalMood'] = 'Gerundium'
            elif node.xpos[-5:-3] == 'gv':
                node.misc['TraditionalMood'] = 'Gerundivum'
            else:
                node.misc['TraditionalMood'] = 'Participium'
                if node.feats['Aspect'] in aspect_mapping:
                    node.misc['TraditionalTense'] = aspect_mapping[node.feats['Aspect']]
        elif node.feats['VerbForm'] == 'Inf':
            node.misc['TraditionalMood'] = 'Infinitivus'
            if node.feats['Aspect'] in aspect_mapping:
                node.misc['TraditionalTense'] = aspect_mapping[node.feats['Aspect']]
            if node.feats['InflClass[nominal]']:
                node.feats['InflClass[nominal]'] = ''

    elif node.upos == 'PROPN' and node.feats['Proper']:
        node.feats['Proper'] = ''

    elif node.upos == 'NUM':
        if node.lemma in ['unus', 'duo', 'tres', 'quattuor', 'quatuor', 'quator', 'quinque', 'sex', 'septem', 'octo',
                          'novem', 'nouem', 'decem', 'undecim', 'duodecim', 'tredecim', 'quattuordecim', 'quindecim',
                          'sedecim', 'septendecim', 'duodeviginti', 'undeviginti', 'uiginti', 'viginti',
                          'duodetreginta', 'triginta', 'quadraginta', 'quinquaginta', 'sexaginta', 'septuaginta',
                          'octoginta', 'nonaginta', 'centum', 'ducenti', 'trecenti', 'quadringenti', 'quingenti',
                          'sescenti', 'octingenti', 'octogenti', 'mille', 'milia']:
            node.feats['NumForm'] = 'Word'
        elif node.feats['NumForm'] == 'Roman' and not node.feats['NumType']:
            node.feats['NumType'] = 'Card'

    elif node.upos == 'ADV':
        if node.feats['Case']:
            node.feats['Case'] = ''

    elif node.upos == 'DET':
        if node.lemma in ['multus', 'quamplures'] and not node.feats['PronType']:
            node.feats['PronType'] = 'Ind'
        elif node.lemma == 'qualis' and node.feats['PronType'] == 'Int':
            node.feats['PronType'] = 'Rel'
        elif node.form == 'prius':
            node.upos = 'ADJ'

    elif node.upos == 'PRON':
        if node.lemma == 'quis' and node.feats['PronType'] == 'Rel':
            node.feats['PronType'] = 'Int'
        elif node.lemma == 'quod' and node.feats['PronType'] == 'Rel':
            node.lemma = 'qui'

    # specific corrections
    # verbal features
    if not node.feats['Voice'] and node.form.lower() in ['abstinebam', 'ades', 'adesset', 'adest', 'adirem', 'adsolet',
                                                         'advolaverit', 'afferunt', 'affuerit', 'cadat', 'caderet',
                                                         'cadet', 'competebat', 'displicet', 'distribuit', 'exarserat',
                                                         'exivit', 'exueras', 'infit', 'innuit', 'noluerunt',
                                                         'preponderet', 'regnat', 'retulit', 'sufficiunt', 'tendit',
                                                         'vacet', 'venerat']:
        node.feats['Voice'] = 'Act'
    if node.address() in ['Epi-125#15', 'Epi-209#5'] and not node.feats['Person']:
        node.feats['Person'], node.feats['Number'] = '3', 'Sing'
    elif node.address() == 'Mon-674#14':
        node.feats['Aspect'] = 'Imp'
    elif node.address() == 'Epi-93#10':
        node.feats['VerbForm'], node.feats['Mood'] = 'Inf', ''

    # nominal features
    # case 
    if not node.feats['Case']:
        if node.address() in ['DVE-265#49', 'Egl-26#13', 'Egl-26#34', 'Egl-86#20', 'Epi-60#5', 'Epi-296#16',
                              'Epi-300#3', 'Mon-286#50', 'Mon-465#9', 'Que-91#7'] or node.form.lower() == 'ego':
            node.feats['Case'] = 'Nom'
        elif node.address() in ['Egl-87#22', 'Epi-86#4', 'Mon-512#12', 'Que-106#44']:
            node.feats['Case'] = 'Acc'
        elif node.address() in ['Mon-216#1', 'Mon-425#36']:
            node.feats['Case'] = 'Abl'
    # number
    if not node.feats['Number']:
        if node.form in ['illustri', 'sensibilis', 'redeundum', 'tollerando'] or node.address() == 'Egl-87#22':
            node.feats['Number'] = 'Sing'
        elif node.address() in ['Egl-26#34', 'Egl-42#26', 'Egl-86#20', 'Epi-10#27'] and not node.feats['Number']:
            node.feats['Number'] = 'Plur'
    # gender
    if not node.feats['Gender']:
        if node.form in ['destructa', 'peritura', 'alienate', 'edite', 'solite', 'sortite',
                         'subiecte'] or node.address() in ['Egl-87#22', 'Epi-200#10', 'Mon-216#1', 'Mon-425#36']:
            node.feats['Gender'] = 'Fem'
        elif node.address() in ['DVE-265#49', 'Egl-26#34']:
            node.feats['Gender'] = 'Masc'
        elif node.address() in ['Epi-86#4', 'Mon-293#16', 'Mon-512#12']:
            node.feats['Gender'] = 'Neut'

# fix non-projectivity of punctuation
pun = udapi.block.ud.fixpunct.FixPunct()
pun.process_document(doc)

with open(f'{morpho_folder}/MM-la_{treebank.lower()}-ud-{split}.conllu', 'w') as output:
    output.write(doc.to_conllu_string())
