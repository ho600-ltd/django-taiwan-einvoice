#!/usr/bin/zsh

BASEDIR=$(dirname "$0")

while [[ 1 ]]; do
	echo "$1"
	echo "$2"
	echo "$3"
	echo "$4"
	$1 ${BASEDIR}/connect_tea_web_ws.py $2 $3 $4
	sleep 1.7
done
