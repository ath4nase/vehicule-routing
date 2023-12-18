#! /bin/bash
# This script generates results for tree search + column generation

ALGO_TYPE=$1

for (( i = 0; i <= 100; i++ )); do
    ./generate_result.sh cgts $i -a "$ALGO_TYPE"
done