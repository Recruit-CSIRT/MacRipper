#! /bin/bash


pythonenv="PYTHONPATH=<>/MFT/mac_ripper"
prefix_cmd="sudo ${pythonenv} python "
cmds=(
app_usage.py
downloaded.py
last_used.py
spotlight_all_files.py
)
#cmds=(
#'sleep 1'
#'sleep 3'
#'sleep 2'
#)
postfix_cmd=" -r / -b -t -10 -o output"

pids=()

for i in `seq 0 3`
do
    ${prefix_cmd}${cmds[${i}]}${postfix_cmd} &
		#${cmds[${i}]} &
    pids[${i}]=$!
    echo ${pids[${i}]}
done

for pid in ${pids[*]}; do
    wait $pid
done
