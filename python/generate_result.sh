#!/bin/bash

for i in {81..100}; do
  python3 elementaryshortestpathwithsingleslot.py -i ../data/elementaryshortestpathwithslots/instance_$i.json -c ../data/resultsV02/result_V02_instance_$i.json
done
