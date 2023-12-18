#! /bin/bash
# This script generates results for dynamic programming + column generation

ALGO_TYPE=$1

for (( i = 0; i <= 100; i++ )); do
    ./generate_result.sh cgdp $i -a "$ALGO_TYPE"
done