import sys

#
# Helper functions used throughout the other scripts.
#

# Tries to classify a given entry is sigle stranded or double stranded.
# Required to separate the ambiguity of 'RNA' or 'DNA' as the molecule type.
# Based off of the baltimore type if not explicit in the molecule type.
def classifyStrandedness(mol_type, baltimore, taxonomy):
	taxonomy = list(map(lambda x:x.lower().replace('-', ' '), taxonomy))
	if 'ss' in mol_type:
		return 1
	elif 'ds' in mol_type:
		return 2
	elif baltimore in [1,3,7]:
		return 2
	elif baltimore in [2,4,5,6]:
		return 1
	elif any(map(lambda x: "single stranded" in x or "ss" in x, taxonomy)):
		return 1
	elif any(map(lambda x: "double stranded" in x or "ds" in x, taxonomy)):
		return 2
	else:
		print ("Could not find number of strands.")
		print (taxonomy)
		return 'error'



# Tries to classify the baltimore class based on the taxonomy description.
# 
# Error codes:
#-1: Could not read molecule type, critical error.
#-2: Is a RNA type but could not infer type, critical error.
#-10: Satellite virus.
#-11: Unassigned.
#
def getBaltimoreClass(mol_type, taxonomy, locus, err=sys.stderr, warn=sys.stderr, critical=sys.stderr):

	mol_type = mol_type.lower()
	taxonomy = list(map(lambda x:x.lower(), taxonomy))

	#Retro transcribing viruses.
	if any(map(lambda x: "retro" in x, taxonomy)):
		if 'rna' in mol_type:
			return 6
		elif 'dna' in mol_type:
			return 7
		else:
			print ("Error in inferring baltimore class.")
			err.write("Error in inferring baltimore class. Is retroviral.\n")
			err.write("Molecule type: %s, taxonomy: %s\n" % (mol_type, taxonomy))
			err.write("Locus: %s\n" % locus)
			critical.write("%s\n" % locus)

	elif any(map(lambda x: "dsdna" in x, taxonomy)):
		return 1
	elif any(map(lambda x: "ssdna" in x, taxonomy)):
		return 2
	elif any(map(lambda x: "dsrna" in x, taxonomy)):
		return 3
	elif any(map(lambda x: "positive-strand" in x, taxonomy)):
		return 4
	elif any(map(lambda x: "negative-strand" in x, taxonomy)):
		return 5
	elif any(map(lambda x: "deltavirus" in x, taxonomy)): #Cleaning up.
		return 5

	#Errors here.
	elif any(map(lambda x: "satellite" in x, taxonomy)):
		err.write("Satellite virus.\n")
		err.write("Locus %s\n" % locus)
		warn.write("%s\n" % locus)
		return -10
	elif any(map(lambda x: "unassigned" in x or "unclassified" in x or "not assigned" in x, taxonomy)):
		err.write("Unassigned virus.\n")
		err.write("Locus %s\n" % locus)
		warn.write("%s\n" % locus)
		return -11
	else:
		print ("Error in inferring baltimore class. Could not find keywords.")
		err.write("Error in inferring baltimore class. Could not find keywords.\n")
		err.write("Molecule type: %s, taxonomy: %s\n" % (mol_type, taxonomy))
		err.write("Locus: %s\n" % locus)
		critical.write("%s\n" % locus)
		return -1