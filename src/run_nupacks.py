import subprocess
import os
import glob
import sys

#
# This is meant to be run on a separate computer! 
# Just so a local computer doesn't have to be on for 10 days.
#

#For each slave, copy all possible files.
#Puts the files in vdb-nupack/runs/.
#Expects sequences in vdb-nupack/tmp/seqs, args in tmp/cmd_file.txt.
os.chdir(os.path.expanduser('~/vdb-nupack'))
slave_file = open('params/IP_list.txt', 'r')
for slave in slave_file:
	slave = slave.split('/')[-1].rstrip()
	transfer_seqs = "rsync -re ssh %s %s:vdb-nupack/runs" % ('runs/seqs/', slave)
	p = subprocess.Popen(transfer_seqs, shell=True)
	p.communicate()
slave_file.close()

cmd_file = open('runs/cmd_file.txt', 'r')
args = cmd_file.next()

cmd = "parallel --slf params/IP_list.txt --progress -k --joblog logfile.log vdb-nupack/parallel-cmd.sh ::: %s ::: mfe pfunc" % args
progress_file = open('resume-cmd.sh', 'w')
progress_file.write('#!/bin/bash\n')
progress_file.write(cmd)
progress_file.close()
cmd_process = subprocess.Popen(cmd, shell=True)
cmd_process.communicate()

print "Collecting files back to master"
#Return files to master.
if not os.path.exists('res'):
    os.makedirs('res')

slave_file = open('params/IP_list.txt', 'r')
for slave in slave_file:
	slave = slave.split('/')[-1].rstrip()
	cmd = "scp -r %s:vdb-nupack/res ." % slave
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.communicate()
slave_file.close()