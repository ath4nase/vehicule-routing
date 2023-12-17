#!/bin/bash

for i in {1..100}; do
  python3 elementaryshortestpathwithsingleslot.py -i ../data/elementaryshortestpathwithslots/instance_$i.json -c c 
done
