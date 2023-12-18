#! /bin/bash
# This script generates all results
ALGO_TYPE=$1

./generate_all_dp.sh
./generate_all_ts.sh
./generate_all_cgdp.sh $ALGO_TYPE
./generate_all_cgts.sh $ALGO_TYPE