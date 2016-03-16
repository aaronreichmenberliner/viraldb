import os
from pymongo import MongoClient
from subprocess import Popen
import glob

#
# Gets nupack files from MASTER, and inserts them into the database.
#

db = MongoClient().viraldb

path = os.environ['VIRALDB_HOME']

if not os.path.exists('vdb-nupack/tmp/res'):
    os.makedirs('vdb-nupack/tmp/res')

#Retrieve results and the logfile from master.
#Logfile is for runtimes.
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
	#Parsing magic that I don't feel like looking up what I'm doing here.
	entry = line.rstrip().split(' ')
	entry[-2] = entry[-2].replace('gen', 'res')
	entry[0] = entry[0].split('\t')
	log.append(entry)

#Iterate through each unique locus.
for mfe_res_path in glob.glob('%s/tmp/res/*.mfe' % path):
	res_file_name = mfe_res_path[:-4]

	#Ensure that the pfunc file is also there
	pfunc_file_path = res_file_name + '.pfunc'
	if (not os.path.isfile(pfunc_file_path)):
		print ("%s is missing it's corresponding pfunc file! Skipping entry." % res_file)
		continue

	#Parsing mfe/pfunc files
	locus = res_file_name.split('/')[-1]

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

	#The datastructure to add.
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

	#Inserts into a unique collection instead of updating.
	db.nupack.insert_one(data_entry)

#Create the new database in which we merge existing data with the nupack data.
db.nupack.aggregate([{'$lookup':
	{'from':'short_clean_data', 
	'localField':'locus', 
	'foreignField':'locus',
	'as':'merged'}},
	{'$out':'tmp_nupack'}])

bulk = db.nupack_short_clean_data.initialize_unordered_bulk_op()

for entry in db.tmp_nupack.find():
	m = entry['merged'][0]
	entry.update(m)
	del entry['merged']
	bulk.insert(m)

bulk.execute()
db.tmp_nupack.drop()

#Getting the overall runtime for all the sequences.
start_time = float(log[0][0][2])
end_time = max(map(lambda x:float(x[0][2]) + float(x[0][3]), log))
total_time = end_time - start_time

res_file = open('%s/tmp/runtime.txt' % path, 'w')
res_file.write(str(total_time))
res_file.close()