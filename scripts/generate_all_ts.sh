#! /bin/bash
# This script generates results for tree search

for (( i = 0; i <= 100; i++ )); do
    ./generate_result.sh ts $i 
done