#! /bin/bash
# This script generates a result for specified arguments
# Usage : generate_result <PROG TYPE> <INSTANCE NUMBER> <OPTIONS ...>

PROG_TYPE=$1
INSTANCE_NUMBER=$2
OPTIONS=

for ((i = 3; i <= $#; i++ )); do
    OPTIONS="$OPTIONS ${!i}"
done

case $PROG_TYPE in 
dp)     PROG_FILE="..\python\elementaryshortestpathwithsingleslot.py"
        RESULT_TYPE=dynamicprogramming ;;

ts)     PROG_FILE="..\python\elementaryshortestpathwithslots.py"
        RESULT_TYPE=treesearch ;;

cgdp)   PROG_FILE="..\python\vehicleroutingwithsingleslot.py"
        RESULT_TYPE=columnsdynamicprogramming ;;

cgts)   PROG_FILE="..\python\vehicleroutingwithslots.py"
        RESULT_TYPE=columnstreesearch ;;
*) echo "Bad usage : Type of file is in {dp, ts, cgdp, cgts}" && exit 1;;
esac

if [[ $PROG_TYPE =~ cg(dp|ts) ]]; then
    DATA_TYPE=vehicleroutingwithslots
else 
    DATA_TYPE=elementaryshortestpathwithslots
fi

INSTANCE="..\data\\$DATA_TYPE\instance_$INSTANCE_NUMBER.json"
RESULT_PATH="..\results\\$RESULT_TYPE\instance_$INSTANCE_NUMBER.json"

CALL="$PROG_FILE -i $INSTANCE -c $RESULT_PATH $OPTIONS"
printf 'python %s\n\n' "$CALL"
python $CALL