#! /bin/bash

set -e

for pl in "./scripts"/*
do
	if [ -d "$pl" ]; then
		if [ -s "$pl/install.sh" ]; then
			/bin/bash $pl/install.sh
			echo ""
			echo ""
			echo ""
			echo -e "\e[92m$(basename $pl)\e[39m installed successfully!"
			echo ""
			echo ""	
			echo ""
		else
			echo ""
			echo ""
			echo -e "\e[93m\e[1mWARNNING!!! \e[21m\e[33m$(basename $pl) \e[39minstall.sh file does not exist!!!"
			echo " "
			echo ""
			echo ""
		fi
	fi
done

rm -rf ./scripts

