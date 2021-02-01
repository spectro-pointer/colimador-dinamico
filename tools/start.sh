#!/usr/bin/env bash

# Parse arguments
while getopts "i:p:" opt;
do
    case $opt in
        i) IP="$OPTARG"
        ;;
        p) PORT="$OPTARG"
        ;;
    esac
done

# Default arguments
if [ -z  $IP ]; then
    IP=0.0.0.0
fi
if [ -z  $PORT ]; then
    PORT=8081
fi
python3 star_detector.py --ip $IP --port $PORT
