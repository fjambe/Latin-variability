#!/bin/bash

# usage: bash sz-for-mm-accuracy-feb24.sh model treebank-to-test
# e.g.: bash sz-for-mm-accuracy-feb24.sh udante LLCT

# Input arguments
model="$1"                 # lowercase
utreebank="$2"             # normal-case
ltreebank="${utreebank,,}" # lowercase version

# Base paths
BASE_SZ_MODEL_DIR="/lnet/work/people/gamba/sz-training/stanza"
EVAL_SCRIPT="/lnet/work/people/gamba/conll18_ud_eval.py"

# Specific file paths
BASE_HARMONIZED_DIR="/lnet/work/people/gamba/GitHub/morpho-harmonization/morpho-harmonized-treebanks"
GOLD_FILE="$BASE_HARMONIZED_DIR/UD_Latin-$utreebank/MM-la_${ltreebank}-ud-test.conllu"
PARSED_FILE="$BASE_SZ_MODEL_DIR/morphoharmo/output_MM_conllus-feb24/stanza_${ltreebank}-by-${model}_mm_feb24-model.conllu"

# Measure accuracy
python3 "$EVAL_SCRIPT" -v "$GOLD_FILE" "$PARSED_FILE"
