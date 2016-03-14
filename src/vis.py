import matplotlib.pyplot as plt
import numpy as np
from pymongo import MongoClient
from matplotlib.backends.backend_pdf import PdfPages
db = MongoClient().viraldb


#
# Builds a summary of charts. Outputs to dos/charts.pdf.
#
# Included charts:
# Baltimore class - Pie Chart
# Molecule type - PieChart
# Lengths - Histogram
# Lengths above 500 000, below 500 000, below 50 000 - Histogram
# Linear, circular counts for +/-ssRNA viruses - Bar Chart
#

pp = PdfPages('docs/charts.pdf')

def baltimoreToName(n):
	if n == 1:
		return 'dsDNA'
	elif n == 2:
		return 'ssDNA'
	elif n == 3:
		return 'dsRNA'
	elif n == 4:
		return '+ssRNA'
	elif n == 5:
		return '-ssRNA'
	elif n == 6:
		return 'ssRNA-RT'
	elif n == 7:
		return 'dsDNA-RT'
	else:
		return 'UNKNOWN(%s)' % n

#Baltimore type
plt.title('baltimore class', y = 1)
labels = range(8)[1:]
counts = list(map(lambda x: db.clean_data.count({'baltimore':x}), labels))
plt.pie(counts, labels = list(map(baltimoreToName, labels)), autopct='%1.1f%%', pctdistance=1.1, labeldistance=1.21,startangle=0)
plt.savefig(pp, format='pdf')

plt.clf()

#Mol. type
plt.title('molecule type')
labels = db.clean_data.distinct('molecule_type', {'baltimore':{'$gt':0}})
counts = list(map(lambda x: db.clean_data.count({'molecule_type':x,'baltimore':{'$gt':0}}), labels))
plt.pie(counts, labels = labels, autopct='%1.2f%%', pctdistance=1.1, labeldistance=1.21,startangle=0)
plt.savefig(pp, format='pdf')
plt.clf()

#Lengths, all
data = list(map(lambda x: x['length'], db.clean_data.find({'baltimore':{'$gt':0}}, {'length':1})))
n, bins, patches = plt.hist(data, 50)

plt.xlabel('length')
plt.ylabel('count')
plt.title('length counts')
plt.savefig(pp, format='pdf')

plt.clf()

#Lengths above 500000
data = list(map(lambda x: x['length'], db.clean_data.find({'baltimore':{'$gt':0}}, {'length':1})))
data = list(filter(lambda x: x > 500000, data))
n, bins, patches = plt.hist(data, 50)

plt.xlabel('length')
plt.ylabel('count')
plt.title('length counts above 500 000')
plt.savefig(pp, format='pdf')

plt.clf()

#Lengths below 500000
data = list(map(lambda x: x['length'], db.clean_data.find({'baltimore':{'$gt':0}}, {'length':1})))
data = list(filter(lambda x: x < 500000, data))
n, bins, patches = plt.hist(data, 50)

plt.xlabel('length')
plt.ylabel('count')
plt.title('length counts below 500 000')
plt.savefig(pp, format='pdf')

plt.clf()

#Lengths below 50000
data = list(map(lambda x: x['length'], db.clean_data.find({'baltimore':{'$gt':0}}, {'length':1})))
data = list(filter(lambda x: x < 20000, data))
n, bins, patches = plt.hist(data, 50)

plt.xlabel('length')
plt.ylabel('count')
plt.title('length counts below 50 000')
plt.savefig(pp, format='pdf')

plt.clf()

#Linear vs circular
fig, ax = plt.subplots()

linear = (db.clean_data.count({'baltimore':4, 'morphology':'linear'}),
	db.clean_data.count({'baltimore':5, 'morphology':'linear'}))

circular = (db.clean_data.count({'baltimore':4, 'morphology':'circular'}),
	db.clean_data.count({'baltimore':5, 'morphology':'circular'}))

width = 0.3
lin = ax.bar(np.arange(2), linear, width, color='r')
circ = ax.bar(np.arange(2) + width, circular, width)

ax.legend((lin, circ), ("linear", "circular"))

ax.set_ylabel('counts')
ax.set_title('+/-ssRNA counts, linear and circular')
ax.set_xticks(np.arange(2) + width)
ax.set_xticklabels(('+ssRNA', '-ssRNA'))
plt.savefig(pp, format='pdf')

pp.close()






