#!/bin/bash

# usage: bash udp-for-hm-accuracy.sh model treebank-to-test
# e.g.: bash udp-for-hm-accuracy.sh udante LLCT

# Input arguments
model="$1"                # lowercase
utreebank="$2"            # normal-case
ltreebank=${utreebank,,}  # lowercase version
FILE=./udp-hm-parsed-testdata/THESIS-udp-$ltreebank-by-$model.conllu

# Base paths
BASE_UDP_MODEL_DIR="/lnet/work/people/gamba/UDPipe"
BASE_HARMONIZED_DIR="/lnet/work/people/gamba/GitHub/syntactic-harmonization/harmonized-treebanks"
BASE_PARSED_OUTPUT_DIR="./udp-hm-parsed-testdata"
BASE_MODEL_DIR="./HM-udp-models"
EVAL_SCRIPT="/lnet/work/people/gamba/conll18_ud_eval.py"

# Specific file paths
MODEL_FILE="$BASE_MODEL_DIR/hm-$model.udpipe"
GOLD_FILE="$BASE_HARMONIZED_DIR/UD_Latin-$utreebank/HM-la_${ltreebank}-ud-test.conllu"
PARSED_FILE="$BASE_PARSED_OUTPUT_DIR/THESIS-udp-${ltreebank}-by-${model}.conllu"

# Create parsed file if it doesn't exist
if ! test -f "$PARSED_FILE"; then
    "$BASE_UDP_MODEL_DIR/udpipe" --tag --parse "$MODEL_FILE" "$GOLD_FILE" > "$PARSED_FILE"
fi

# Measure accuracy
python3 "$EVAL_SCRIPT" -v "$GOLD_FILE" "$PARSED_FILE"

