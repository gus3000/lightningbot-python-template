#!/usr/bin/env bash

COMMAND="python3 -m mybot"
#COMMAND='echo coucou; sleep 2; echo bisous'

N=$1 # number of processes

if [ "$N" = "" ]; then
    N=1
fi

for i in $(seq ${N})
do
    eval "$COMMAND" &
    pids[${i}]=$! # we store the process id
done

for pid in ${pids[*]}; do
    wait $pid # we wait for every process to finish
done