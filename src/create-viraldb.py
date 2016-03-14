from Bio import SeqIO
from pymongo import MongoClient
import pprint
import sys
import os
import glob

from viraldbhelpers import getBaltimoreClass, classifyStrandedness

#
# Builds a database of viruses using MongoDB.
# Assumptions:
# A Mongo server is running.
# The environment variable VIRAL_DATA points to a folder containing exclusively GenBank files add.
# 
# Note: The folder for VIRAL_DATA can be built using 'fetch_genbanks.py' or 'parse_genbanks.py'.
# Preferred method is 'parse_genbanks.py', it is more comprehensive and only grabs reference sequences.
#

#Setup the connection to Mongo.
client = MongoClient()
db = client.viraldb
col_data = db.all_data
col_indexes = db.all_indexes

try:
	#Error logs
	err = open("err.log", 'w')
	warn = open("warn.log", 'w')
	critical = open("critical.log", 'w')
	
	#Get the location of thd genbank files.
	path = os.environ["VIRAL_DATA"]
	
	num_processed = 0
	#Iterate thorugh all the files in the directory.
	for file in glob.glob("%s/*" % path):
	
		#Read the first line of the GenBank file.
		#Due to some limitations of biopython, SeqIO doesn't read this.
		handle = open(file, 'r')
		header = handle.readline()
		tokens = header.split()
	
		handle = open(file, 'r') #Reset the file line pointer for Biopython.
		genome = SeqIO.read(handle, 'gb')
	
		#The data structure to be built for the given genbank file.
		data = {'misc':{}}
	
		data['accession'] = genome.id
		data['desc'] = genome.description
	
		taxonomy = genome.annotations['taxonomy']

		baltimore_class = getBaltimoreClass(tokens[4], taxonomy, tokens[1], err, warn, critical)
		if baltimore_class == -10:
			data['misc']['baltimore_details'] = 'Satellite virus'
		elif baltimore_class == -11:
			data['misc']['baltimore_details'] = 'Unassigned'
		data['baltimore'] = baltimore_class
		
		data['taxonomy'] = dict(zip(map(str, range(len(taxonomy))), taxonomy))
	
		data['locus'] = tokens[1]
		data['length'] = int(tokens[2])
		data['original_molecule_type'] = tokens[4]

		data['strands'] = classifyStrandedness(data['original_molecule_type'], data['baltimore'], taxonomy)
		if data['original_molecule_type'].lower() == 'dna':
			data['molecule_type'] = 'ss-DNA' if data['strands'] == 1 else 'ds-DNA' if data['strands'] == 2 else 'Undetermined DNA'
		elif data['original_molecule_type'].lower() == 'rna':
			data['molecule_type'] = 'ss-RNA' if data['strands'] == 1 else 'ds-RNA' if data['strands'] == 2 else 'Undetermined RNA'
		else:
			data['molecule_type'] = data['original_molecule_type']

		data['morphology'] = tokens[5]
		data['gb_division'] = genome.annotations['data_file_division']
		data['sequence'] = str(genome.seq)
	
		#Store structure to Mongo.
		db.all_data.insert_one(data)

		if data['baltimore'] > 0:
			db.clean_data.insert_one(data)

			if data['length'] < 10000:
				db.short_clean_data.insert_one(data)
	
		num_processed += 1
		if (num_processed % 1000 == 0):
			print ("%s files Processed" % num_processed)
except KeyboardInterrupt:
	print ("Saving error file..")
	err.close()
	warn.close()
	critical.close()
	sys.exit()

err.write("End of errors.")
warn.close()
critical.close()
err.close()
