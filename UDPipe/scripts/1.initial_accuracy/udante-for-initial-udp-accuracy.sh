#!/bin/bash

# usage: bash udp-for-accuracy.sh
# Runs UDPipe parsing + evaluation for all 5 treebanks using the UDante model

# Treebanks to process
treebanks=("ITTB" "LLCT" "Perseus" "PROIEL" "UDante")

# Base paths
BASE_MODEL_DIR="./udp-models_and_training"
BASE_UDPIPE_BIN="/lnet/work/people/gamba/UDPipe/udpipe"
BASE_GOLD_DIR="/lnet/work/people/gamba/UD-devbranch"
BASE_OUTPUT_DIR="/lnet/work/people/gamba/UDPipe/initial_parsed_udp_outputs"
EVAL_SCRIPT="/lnet/work/people/gamba/conll18_ud_eval.py"
RESULTS_CSV="THESIS-initial-results.csv"

# Model
MODEL_NAME="udante"
MODEL_FILE="$BASE_MODEL_DIR/UDante-devbr-3param-emb-v210.udpipe"

# Initialize CSV if it doesn't exist
if [ ! -f "$RESULTS_CSV" ]; then
    echo "Model,Treebank,LAS,UAS" > "$RESULTS_CSV"
fi

# Process each treebank
for utreebank in "${treebanks[@]}"; do
    ltreebank=${utreebank,,}

    GOLD_FILE="$BASE_GOLD_DIR/UD_Latin-$utreebank-dev/la_${ltreebank}-ud-test.conllu"
    PARSED_FILE="$BASE_OUTPUT_DIR/THESIS-udp-initial-${ltreebank}-by-udante.conllu"

    # Parse if output doesn't already exist
    if [ ! -f "$PARSED_FILE" ]; then
        echo "Parsing $utreebank..."
        "$BASE_UDPIPE_BIN" --tag --parse "$MODEL_FILE" "$GOLD_FILE" > "$PARSED_FILE"
    else
        echo "Parsed file for $utreebank already exists. Skipping parsing."
    fi

    # Run evaluation and extract LAS + UAS
    echo "Evaluating $utreebank..."
    eval_output=$(python3 "$EVAL_SCRIPT" -v "$GOLD_FILE" "$PARSED_FILE")

    las=$(echo "$eval_output" | grep -E "^LAS" | awk '{print $5}')
    uas=$(echo "$eval_output" | grep -E "^UAS" | awk '{print $5}')

    # Append to CSV
    echo "$MODEL_NAME,$utreebank,$las,$uas" >> "$RESULTS_CSV"
    echo "Done with $utreebank — LAS: $las | UAS: $uas"
    echo "----------------------------------------"
done

