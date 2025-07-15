#!/bin/bash

arg1_values=(ittb llct perseus proiel udante)
arg2_values=(ITTB LLCT Perseus PROIEL UDante)

MAX_JOBS=4
RESULTS_FILE="THESIS-MM-all-results.csv"
TMP_DIR="./tmp-results"
mkdir -p "$TMP_DIR"

# Write header
echo "ARG1,ARG2,LAS_F1,UAS_F1,UFeats_F1,MLAS_F1" > "$RESULTS_FILE"

run_and_extract() {
  local a1=$1
  local a2=$2
  local tmpfile="$TMP_DIR/${a1}_${a2}.csv"

  output=$(bash THESIS-udp-for-mm-accuracy-feb24.sh "$a1" "$a2")

  # Extract F1 scores using grep + cut
  LAS=$(echo "$output"    | grep '^LAS'     | cut -d '|' -f 4 | tr -d ' ')
  UAS=$(echo "$output"    | grep '^UAS'     | cut -d '|' -f 4 | tr -d ' ')
  UFEATS=$(echo "$output" | grep '^UFeats'  | cut -d '|' -f 4 | tr -d ' ')
  MLAS=$(echo "$output"   | grep '^MLAS'    | cut -d '|' -f 4 | tr -d ' ')

  # Fallbacks
  LAS=${LAS:-NA}
  UAS=${UAS:-NA}
  UFEATS=${UFEATS:-NA}
  MLAS=${MLAS:-NA}

  # Print to screen
  echo "[$a1 → $a2] LAS: $LAS, UAS: $UAS, UFeats: $UFEATS, MLAS: $MLAS"

  # Save this line to a tmp file
  echo "$a1,$a2,$LAS,$UAS,$UFEATS,$MLAS" > "$tmpfile"
}

wait_for_jobs() {
  while [ "$(jobs -rp | wc -l)" -ge "$MAX_JOBS" ]; do
    sleep 1
  done
}

# Run jobs
for arg1 in "${arg1_values[@]}"; do
  for arg2 in "${arg2_values[@]}"; do
    wait_for_jobs
    run_and_extract "$arg1" "$arg2" &
  done
done

wait

# Merge all temporary outputs into the CSV file
cat "$TMP_DIR"/*.csv >> "$RESULTS_FILE"

# Cleanup
rm -r "$TMP_DIR"

