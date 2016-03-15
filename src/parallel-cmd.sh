#!/bin/bash

#To be run by parallel!

if [ $# -ne 2 ] ; then
	echo "Needs exactly 2 params; (temperature, material, file), function."
	exit
fi

temp=`echo $1 | cut -d " " -f 1`
material=`echo $1 | cut -d " " -f 2`
locus=`echo $1 | cut -d " " -f 3`

export NUPACKHOME=~/vdb-nupack
cd ~/vdb-nupack
mkdir -p res

if [ $2 == "mfe" ] ; then
	./bin/mfe -T $temp -material $material runs/$locus
	mv runs/$locus.mfe res/$locus.mfe
elif [ $2 == "pfunc" ] ; then
	./bin/pfunc -T $temp -material $material runs/$locus > res/$locus.pfunc
else 
	echo "What why no should be mfe/pfunc"
fi

