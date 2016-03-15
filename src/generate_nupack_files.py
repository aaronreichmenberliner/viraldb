from pymongo import MongoClient
from subprocess import Popen
import os

db = MongoClient().viraldb

#get viraldb home
path = os.environ['VIRALDB_HOME']
if not os.path.exists('%s/tmp' % path):
    os.makedirs('%s/tmp' % path)
if not os.path.exists('%s/tmp/seqs' % path):
    os.makedirs('%s/tmp/seqs' % path)

args = []
temp = str(37)

#Need to write sequences to file.
for entry in db.short_clean_data.find({}, {'sequence':1, 'locus':1, 'baltimore':1}).sort([('length', 1)]).limit(4):
	if entry['baltimore'] in [1, 2, 7]:
		material = 'dna'
	elif entry['baltimore'] in [3,4,5,6]:
		material = 'rna'
	else:
		print ("Error in baltimore class. skipping locus " + entry['locus'])
		continue

	#Write file
	f = open(path + '/tmp/seqs/' + entry['locus'] + '.in', 'w')
	f.write(entry['sequence'] + '\n')
	f.close()

	#Add to args str.
	args.append('"' + temp + ' ' + material + ' ' + entry['locus'] + '"')

cmd_file = open(path + '/tmp/cmd_file.txt', 'w')
cmd_file.write(' '.join(args))
cmd_file.close()

#Push files to Master.
transfer_seqs = "rsync -re ssh %s/tmp/ $MASTER:vdb-nupack/runs" % path
p = Popen(transfer_seqs, shell=True)
p.communicate()
