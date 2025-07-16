#!/bin/bash

# usage: bash sz-for-initial-accuracy.sh model treebank-to-test
# e.g.: bash sz-for-initial-accuracy.sh udante LLCT

# Input arguments
model="$1"                 # lowercase
utreebank="$2"             # normal-case
ltreebank="${utreebank,,}" # lowercase version

# File paths
EVAL_SCRIPT="/lnet/work/people/gamba/conll18_ud_eval.py"
GOLD_FILE="/lnet/work/people/gamba/UD-devbranch/UD_Latin-$utreebank-dev/la_${ltreebank}-ud-test.conllu"
PARSED_FILE="/home/gamba/personal_work_ms/stanza_initial/outputs_by_stanza/stanza_pretrained/stanza_${ltreebank}-by-${model}-model.conllu"

# Determine parsed file path based on model type
if [[ "$model" == "llct" || "$model" == "udante" ]]; then
    PARSED_FILE="/home/gamba/personal_work_ms/stanza_initial/outputs_by_stanza/stanza_long-models/stanza_${ltreebank}-by-${model}-model.conllu"
else
    PARSED_FILE="/home/gamba/personal_work_ms/stanza_initial/outputs_by_stanza/stanza_pretrained/stanza_${ltreebank}-by-${model}-model.conllu"
fi

# Output info
# echo "Evaluating model: $model"
# echo "Testing on treebank: $utreebank"
# echo "Using parsed file: $PARSED_FILE"
# echo "Gold file: $GOLD_FILE"

# Measure accuracy
python3 "$EVAL_SCRIPT" -v "$GOLD_FILE" "$PARSED_FILE"
