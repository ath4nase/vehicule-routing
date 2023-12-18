#! /bin/bash
# This script generates results for dynamic programming

for (( i = 0; i <= 100; i++ )); do
    ./generate_result.sh dp $i 
done