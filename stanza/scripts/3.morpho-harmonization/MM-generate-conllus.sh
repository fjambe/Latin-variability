#!/bin/bash

# Script to train generate parsed data using Stanza.
# Uses default parameters, pretrained FastText Facebook embeddings, and harmonized training data.
# To be executed from the Stanza main directory.

# Activate virtual environment and load config variables
source /lnet/work/people/gamba/sz-training/bin/activate
source /lnet/work/people/gamba/sz-training/stanza/scripts/config.sh

# Define treebanks and models
TREEBANKS=("ITTB" "LLCT" "Perseus" "PROIEL" "UDante")
TRAIN_DATASETS=("ittb_mm_feb24" "llct_mm_feb24" "perseus_mm_feb24" "proiel_mm_feb24" "udante_mm_feb24")

# Loop over all treebanks and training datasets
for TB in "${TREEBANKS[@]}"; do
    for TRAIN_DATA in "${TRAIN_DATASETS[@]}"; do
        echo "Processing treebank: $TB with training data: $TRAIN_DATA"
        python3 /lnet/work/people/gamba/sz-training/stanza/morphoharmo/room_newmodels_MM-feb24.py "$TB" "$TRAIN_DATA"
    done
done
