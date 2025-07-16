#!/bin/bash

# Script to train generate parsed data using Stanza.
# Uses default parameters, pretrained FastText Facebook embeddings, and harmonized training data.
# To be executed from the Stanza main directory.

# Activate virtual environment and load config variables
source ../bin/activate
source ./scripts/config.sh

# Define treebanks and models
TREEBANKS=("ITTB" "LLCT" "Perseus" "PROIEL" "UDante")
TRAIN_DATASETS=("ittb_hm" "llct_hm" "perseus_hm" "proiel_hm" "udante_hm")

# Loop over all treebanks and training datasets
for TB in "${TREEBANKS[@]}"; do
    for TRAIN_DATA in "${TRAIN_DATASETS[@]}"; do
        echo "Processing treebank: $TB with training data: $TRAIN_DATA"
        python3 THESIS-room_newmodels_HM.py "$TB" "$TRAIN_DATA"
    done
done
