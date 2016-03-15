#!/bin/bash

#Arguments:
# $1 = target computer/slave
#Assumed that SSH is setup.

#Copy nupack.
if [ $# -lt 1 ] ; then
echo "Need argument for destination!"
exit
fi

# cd $VIRALDB_HOME
cd ~/vdb-nupack
for slave in $@
do
	rsync -re ssh vdb-nupack $slave:.
	scp src/parallel-cmd.sh $slave:vdb-nupack
done