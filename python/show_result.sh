#!/bin/bash

for i in {1..100}; do
  echo "-----------"
  echo "Instance $i"
  echo "-----------"
  python3 elementaryshortestpathwithsingleslot.py -i ../data/elementaryshortestpathwithslots/instance_$i.json -c c 
done
