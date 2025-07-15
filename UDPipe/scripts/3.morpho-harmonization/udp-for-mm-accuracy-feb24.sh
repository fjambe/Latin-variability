#!/bin/bash

# usage: bash udp-for-mm-accuracysh model treebank-to-test
# e.g.: bash udp-for-mm-accuracy.sh udante LLCT

# Input arguments
model="$1"                # lowercase
utreebank="$2"            # normal-case
ltreebank=${utreebank,,}  # lowercase version

# Base paths
BASE_UDP_MODEL_DIR="/lnet/work/people/gamba/UDPipe"
BASE_MODEL_SUBDIR="$BASE_UDP_MODEL_DIR/udp-harmonisation/morphoharmo/MM-udp-models"
BASE_HARMONIZED_DIR="/lnet/work/people/gamba/GitHub/morpho-harmonization/morpho-harmonized-treebanks"
BASE_PARSED_OUTPUT_DIR="./udp-mm-parsed-testdata"
EVAL_SCRIPT="/lnet/work/people/gamba/conll18_ud_eval.py"

# Specific file paths
MODEL_FILE="$BASE_MODEL_SUBDIR/mm-${model}-feb24.udpipe"
GOLD_FILE="$BASE_HARMONIZED_DIR/UD_Latin-$utreebank/MM-la_${ltreebank}-ud-test.conllu"
PARSED_FILE="$BASE_PARSED_OUTPUT_DIR/THESIS-udp-${ltreebank}-by-${model}-feb24.conllu"

# Create parsed file if it doesn't exist
if ! test -f "$PARSED_FILE"; then
    "$BASE_UDP_MODEL_DIR/udpipe" --tag --parse "$MODEL_FILE" "$GOLD_FILE" > "$PARSED_FILE"
fi

# Measure accuracy
python3 "$EVAL_SCRIPT" -v "$GOLD_FILE" "$PARSED_FILE"

