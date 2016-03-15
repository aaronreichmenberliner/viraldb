import os
from pymongo import MongoClient
from subprocess import Popen
import glob

db = MongoClient().viraldb

path = os.environ['VIRALDB_HOME']

if not os.path.exists('vdb-nupack/tmp/res'):
    os.makedirs('vdb-nupack/tmp/res')

#Retrieve files from master.
transfer_res = "rsync -re ssh $MASTER:vdb-nupack/res %s/tmp/" % path
transfer_logfile = "scp $MASTER:vdb-nupack/logfile.log %s/tmp" % path
p_res = Popen(transfer_res, shell=True)
p_log = Popen(transfer_logfile, shell=True)
p_res.communicate()
p_log.communicate()


data = []
log = []

#Parses the logfile for runtimes.
log_file = open('%s/tmp/logfile.log' % path, 'r')
next(log_file)
for line in log_file:
	entry = line.rstrip().split(' ')
	entry[-2] = entry[-2].replace('gen', 'res')
	entry[0] = entry[0].split('\t')
	log.append(entry)

for mfe_res_path in glob.glob('%s/tmp/res/*.mfe' % path):
	res_file_name = mfe_res_path[:-4]


	pfunc_file_path = res_file_name + '.pfunc'
	if (not os.path.isfile(pfunc_file_path)):
		print ("%s is missing it's corresponding pfunc file! Skipping entry." % res_file)
		continue

	locus = res_file_name.split('/')[-1]
	#Match to mongo now.
	#Make new table for now? Yeah.

	mfe_file = open(mfe_res_path, "r")
	ctr = 0
	for line in mfe_file:
		ctr+=1
		if (ctr == 15):
			mfe_energy = float(line)
		if (ctr == 16):
			mfe_structure = line
			break;

	pfunc_file = open(pfunc_file_path, "r")
	ctr = 0
	for line in pfunc_file:
		ctr +=1
		if (ctr == 14):
			pfunc_energy = float(line)
		if (ctr == 15):
			pfunc_partition_number = float(line)
			break;

	mfe_time = list(filter(lambda entry: (entry[-2] == locus) and (entry[-1] == 'mfe'), log))[0][0][3]
	pfunc_time = list(filter(lambda entry: (entry[-2] == locus) and (entry[-1] == 'pfunc'), log))[0][0][3]

	data_entry = {
		'locus':locus,
		'temperature':37,
		'mfe_energy':mfe_energy,
		'mfe_structure': mfe_structure.rstrip(),
		'mfe_time': float(mfe_time),
		'pfunc_energy': pfunc_energy,
		'pfunc_partition_number': pfunc_partition_number,
		'pfunc_time': float(pfunc_time)
	}

	db.nupack.insert_one(data_entry)

start_time = float(log[0][0][2])
end_time = max(map(lambda x:float(x[0][2]) + float(x[0][3]), log))
total_time = end_time - start_time

res_file = open('%s/tmp/runtime.txt' % path, 'w')
res_file.write(str(total_time))
res_file.close()