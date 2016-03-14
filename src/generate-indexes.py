from pymongo import MongoClient
import sys

#
# Generates a data summary for a given table that follows the schema in schemas.txt.
#
# Arguments: A list of table classes to build indexes for.
# Ex: To build a table for clean_data and all_data, the command should be:
# python generate-indexes.py all clean
#

if len(sys.argv) <= 1:
	print ("Error: Please enter a collection to index!")
	print ("Aborting.")
	sys.exit()

db = MongoClient().viraldb
collections = db.collection_names()

for collection in sys.argv[1:]:
	collection_data = collection + '_data'
	collection_indexes = collection + '_indexes'

	if 'data' in collection:
		print ("Please do not include 'data' in the collection...")
		print ("Skipping.")
		continue
	elif 'index' in collection:
		print ("Please do not include 'index' in the collection...")
		print ("Skipping.")
		continue
	elif not collection_data in collections:
		print ("Collection specified not found!")
		print ("Skipping.")
		continue

	print("Constructing index for %s" % collection_data)


	new_indexes = {}
	for field in ['baltimore', 'molecule_type', 'morphology', 'gb_division', 'strands', 'original_molecule_type']:
		new_indexes[field] = {}
		keys = db[collection_data].distinct(field) #Builds a entry for each distinct key.

		for key in keys:
			if field == 'baltimore':
				new_indexes[field][str(key)] = db[collection_data].count({field:key})
			else:
				new_indexes[field][str(key)] = db[collection_data].count({field:key})

	db[collection_indexes].remove()
	db[collection_indexes].insert_one(new_indexes)