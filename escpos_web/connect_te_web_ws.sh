#!/usr/bin/zsh

while [[ 1 ]]; do
	echo "sh"
	echo "$1"
	echo "$2"
	./connect_te_web_ws.py $1 $2 
	sleep 1.7
done
