from pymongo import MongoClient

db = MongoClient().viraldb

#Create the new database
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