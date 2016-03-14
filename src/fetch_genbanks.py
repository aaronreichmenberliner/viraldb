from Bio import Entrez
import os
import math
import sys

#
# This is for parsing and fetching files from GenBank.
# 
# Assumption: The environment variable VIRAL_DATA should be set to a place to store the data.
#
# Default method is to search GenBank for acession numbers.
# Set get_accession_from_file to 0 for the default method.
# Set get_accession_from_file to 1 to use the provided file downlaoded from genbank.
# Set get_accession_from_file to 2 if you also want strains.
#

get_accession_from_file = 0

#Place to store the data.
path = os.environ["VIRAL_DATA"]
if path = '':
	print "Please set the env variable VIRAL_DATA!"
	sys.exit()

print("Storing data in %s" % path)

Entrez.email = "justin.ng@autodesk.com"

#Get accession numbers, depending on method chosen.
if get_accession_from_file > 0:
	#Get the file with all the accessions.
	accession_file = open('viral_genbank_list.txt', 'r')

	#The first two lines of that file are garbage/headers.
	accession_file.next()
	accession_file.next()

	#Dictionary with all the accession numbers.
	ac_list = {}
	for line in accession_file:
		tokens = line.split()
		#Get 1st and 2nd columns.
		ac_list[tokens[0]]=True #Reference sequence
		ac_list[tokens[1]]=True #Strain

	#Get the accession numbers.
	items = ac_list.keys()

elif get_accession_from_file == 0:
	#Grab the required sequences.
	handle = Entrez.esearch(db="nucleotide", term="((RefSeq[Keyword]) OR (complete genome[Keyword])) AND (Viruses[Organism])", retmax=15000)

	record = Entrez.read(handle)
	items = record['IdList']
else:
	print ("Bad flag! Error in get_accession_from_file")
	sys.exit()


#Choose how many accession numbers to fetch at a time.
batch = 1000

#For the required number of rounds...
for i in range(int(math.ceil(len(items)/float(batch)))):

	#Grab the required sequences.
	print "Fetching sequences %s:%s" % (batch * i, batch * (i+1))
	handle = Entrez.efetch(db="nucleotide", id=items[batch * i: batch * (i + 1)], rettype="gb")

	#Split the incoming data stream into separate genbank files.
	current_file = None
	for line in handle:
		tokens = line.split()
		#Identify new genbank files by starting with LOCUS (Could also look for the // at the end.)
		if len(tokens) > 0 and tokens[0] == "LOCUS":
			if not current_file is None:
				current_file.close()
			current_file = open("%s/%s.gb" % (path, tokens[1]), 'w')
		current_file.write(line)
	current_file.close()