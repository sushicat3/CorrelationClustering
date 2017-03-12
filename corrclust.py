from random import randint
from random import shuffle

d = 1500
w = 12419
k = 4
l = 80
delta = 0.20

filename = 'docword.nips.txt'

# create documents
documents = []
# list of words for each document with count >=5
for x in range(d):
	documents.append([])

# open nips.txt
f = open(filename, 'r')

# initialize documents
x = 0
for line in f:
	# skip first 3 lines
	if x < 3:
		x = x + 1
		continue
	# extract docID, wordID and count
	temp = line.split()
	docID = int(temp[0])
	wordID = int(temp[1])
	count = int(temp[2])
	# only if the count is 5 or more, process line into documents
	if count >= 5:
		documents[docID-1].append(wordID)
	x = x + 1
# step
print "document processed."

totalwords = 0
for x in range(d):
	for y in documents[x]:
		totalwords = totalwords + 1
print totalwords

# x = 0
# for d in documents:
# 	x = x+1
# 	print "doc",x,":",d

# print "empty sets:"
# x = 0
# for d in documents:
# 	x = x+1
# 	if len(d) == 0:
# 		print x

# the random permutation of from W! permutations of [1...W]

print "creating permutations..."

myset = []
for i in range(w):
    myset.append(i+1)

permutations = []
for i in range(k*l):
    permutations.append([])

# print len(permutations)

for j in myset:
    for i in range(len(permutations)):
        permutations[i].append(j)

for i in range(len(permutations)):
    shuffle(permutations[i])

def minhash(i, doc):
	# minhash of document doc (list of wordIDs) using permutation i
	for x in permutations[i-1]:
		if x in doc:
			return x
	return -1

# def hash_g(j, d):
# 	# composite minhash of d
# 	ret = []
# 	for i in range(k):
# 		ret.append( minhash( ( (j-1)*k + (i+1) ) , d) )
# 	return ret

def hash_g(j, d):
	# composite minhash of d
	ret = []
	for i in range(k):
		ret.append( minhash( ( (j-1)*k + (i+1) ) , d) )
	ret2 = []
	for i in ret:
		ret2.append(str(i))
	ret3 = ', '.join(ret2)
	return ret3

# preprocessing

print "preprocessing..."

buckets = {}

for x in range(d):
	for j in range(l):
		bucketID = hash_g((j+1), documents[x])
		if bucketID in buckets:
			buckets[bucketID].append(x+1)
			# print "collide!"
		else:
			buckets[bucketID] = [(x+1)]	

# step
print "preprocessing structure created."
for b in buckets:
	print b,":",buckets[b]
print "number of buckets",len(buckets)

# edge marking

# plus edges stored here
plus_edges = []
for x in range(d):
	plus_edges.append([])
# print "length of +e's",len(plus_edges)

def jacqsim(qdoc, doc):
	# jacquard similarity of documents qdoc and doc
	if len(qdoc) == 0 or len(doc) == 0:
		return -1
	union = []
	intersection = []
	for x in qdoc:
		union.append(x)
	for x in doc:
		if x in qdoc:
			intersection.append(x)
		else:
			union.append(x)
	ret = len(intersection) / ((1.0)*(len(union)))
	return ret

# print len(documents[953])
# print "s(16, 164) = ", jacqsim(documents[953], documents[1089])
# print "s(16, 175) = ", jacqsim(documents[953], documents[1104])
# print "s(175, 164) = ", jacqsim(documents[1104], documents[1089])

# edge marking
pecount = 0
for b in buckets:
	if b > 0:
		for r in buckets[b]: # is doc d, because buckets hold real docIDs
			for s in buckets[b]:
				# print 'r',r,'s',s
				if r < s and jacqsim(documents[r-1], documents[s-1]) >= 0.25: 
					if r not in plus_edges[s-1]:
						plus_edges[s-1].append(r)
					if s not in plus_edges[r-1]:
						plus_edges[r-1].append(s)
					pecount = pecount + 1
print "number od pos edges", pecount
# x = 0
# for e in plus_edges:
# 	x = x+1
# 	print "point",x,"has + edge to",e


# correlation clustering

# step
print "positive edges marked."

working_set = []
for x in range(d):
	working_set.append(x+1)

centers = []
clusters = []

shuffle(working_set)

def set_diff(a, b):
	ret = []
	for x in a:
		ret.append(x)
	for x in b:
		if x in ret:
			ret.remove(x)
	return ret

def delta_good(delta, v, clust, graph):
	# v should be a docID
	# clust should be a list of docIDs
	# graph should be a list of docIDS
	# clust should be within graph
	plus_inside = 0
	plus_outside = 0
	for x in plus_edges[v-1]:
		if x in clust:
			plus_inside = plus_inside + 1
	for x in plus_edges[v-1]:
		if x in set_diff(graph, clust):
			plus_outside = plus_outside + 1
	if plus_outside <= delta*len(clust) and plus_inside >= (1-delta)*len(clust):
		return True
	else:
		return False

# correlation clustering algorithm

# step
print "clustering..."

# create graph to represent all docIDs
graph = []
for x in range(d):
	graph.append(x+1)
shuffle(graph)

# holds the chosen centers and clusters
centers = []
clusters = []

while len(graph) > 0:
	v = graph[0]
	centers.append(v)
	cluster_v = [v]
	to_add = []
	to_remove = []
	for x in plus_edges[v-1]:
		if x in graph:
			cluster_v.append(x)
	#modify cluster_v
	for x in cluster_v:
		if delta_good(3*delta, x, cluster_v, graph) == False:
			to_remove.append(x)
	for x in graph:
		if delta_good(7*delta, x, cluster_v, graph) == True:
			to_add.append(x);
	for x in to_remove:
		cluster_v.remove(x)
	for x in to_add:
		if x not in cluster_v:
			cluster_v.append(x)
	#delete cluster_v
	clusters.append(cluster_v)
	for x in cluster_v:
		graph.remove(x)

print "number of centers is:",len(centers)
print "number of clusters is:",len(clusters)

for c in clusters:
	print c

def max_edges(x):
	#returns max edges inside graph of n nodes
	ret = 0
	for i in range(x):
		ret = ret + i
	return ret

pos_within = 0
pos_across = 0

for x in range(len(plus_edges)):
	for y in plus_edges[x]:
		if (x+1) < y:
			for c in clusters:
				if x in c:
					if y in c:
						pos_within = pos_within + 1
					else:
						pos_across = pos_across + 1

c_edges = 0
for c in clusters:
	x = len(c)
	c_edges = c_edges + max_edges(x)

neg_within = c_edges - pos_within

quality = neg_within + pos_across

print "quality is",quality,"disagreeing edges out of",max_edges(1500),"total edges"


