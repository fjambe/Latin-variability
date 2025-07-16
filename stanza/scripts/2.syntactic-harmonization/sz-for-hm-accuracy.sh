#!/bin/bash

# usage: bash sz-for-hm-accuracy.sh model treebank-to-test
# e.g.: bash sz-for-hm-accuracy.sh udante_hm LLCT

# Input arguments
model="$1"                 # lowercase
utreebank="$2"             # normal-case
ltreebank="${utreebank,,}" # lowercase version

# Base paths
BASE_SZ_MODEL_DIR="/lnet/work/people/gamba/sz-training/stanza"
EVAL_SCRIPT="/lnet/work/people/gamba/conll18_ud_eval.py"

# Specific file paths
BASE_HARMONIZED_DIR="/lnet/work/people/gamba/GitHub/syntactic-harmonization/harmonized-treebanks"
GOLD_FILE="$BASE_HARMONIZED_DIR/UD_Latin-$utreebank/HM-la_${ltreebank}-ud-test.conllu"
PARSED_FILE="$BASE_SZ_MODEL_DIR/THESIS-output_HM_conllus/THESIS-sz_${ltreebank}-by-${model}_hm-model.conllu"

# Measure accuracy
python3 "$EVAL_SCRIPT" -v "$GOLD_FILE" "$PARSED_FILE"
