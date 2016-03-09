import scipy
import datetime
import itertools
import numpy
import random 
import sys
import custommodule.fuzzycmeans as cfuzzy
import custommodule.location as clocation
import custommodule.cpygmaps as cpygmaps
import custommodule.user as cuser


"""parameters"""
CLUSTER_NUM = 50
#CLUSTER_NUM_2 = 5
TFIDF_THRESHOLD = 0.005
ERROR = 0.0001
WEIGHT = 0.4

"""file path"""
USER_POSTS_FILE = "./data/TravelerPosts"
OUTPUT_MAP = "./data/Summary/LocationMapComb_c" + str(CLUSTER_NUM) +\
    "stt" + str(TFIDF_THRESHOLD) + "w" + str(WEIGHT) + "e" + str(ERROR) + ".html"
OUTPUT_LOCATION_CLUSTER = "./data/Summary/LocationMapComb_c" + str(CLUSTER_NUM) +\
    "stt" + str(TFIDF_THRESHOLD) + "w" + str(WEIGHT) + "e" + str(ERROR) + ".txt"

class CusLocation(clocation.Location()):
    def __init__(self):
        super()
        self.cluster1 = None
        self.cluster2 = None

def output_on_map(point_all, cluster_membership, c, output_file):
    print("Outputing points on the map...")
    mymap = cpygmaps.googlemap(40.758899, -73.9873197, 13)
    """for a_point in point_cntr:
        mymap.addpoint(a_point[0], a_point[1], "#AE0000")
    """
    rd = lambda: random.randint(0,255)
    color = ["#%02X%02X%02X" % (rd(), rd(), rd()) for i in range(0, c)]
    for i, a_point in enumerate(point_all):
        mymap.addpoint(a_point[0], a_point[1], color[cluster_membership[i]], a_point[2])
    mymap.draw(output_file) 

def output_location_cluster(locations, output_file):
    sorted_locations = sorted(locations.values(), key=lambda x:x.cluster1)
    groups = {x:list(y) for x, y in itertools.groupby(sorted_locations, lambda x:x.cluster1)}

    clocation.output_location_list([], output_file)
    f = open(output_file, "a")
    # for each cluster
    for c, a_group in groups.items():
        f.write("Cluster:" + str(c) + "\t#:" + str(len(a_group)) + "\n")
        clocation.output_location_part_list(a_group, f)
    f.close()


def fit_users_to_location(locations, users):
    print("Fitting users to locations...")
    all_posts = [y for x in users.values() for y in x.posts]
    locations.fit_posts(all_posts)

def get_corpus(locations_list):
    print("getting tags corpus...")
    corpus = []
    for a_location in locations_list:
        doc = " ".join([" ".join(x.tags) for x in a_location.posts])
        corpus.append(doc)
    tfidf, tags_name = cfuzzy.get_tfidf(corpus)
    return tfidf, tags_name

def filter_tag(tfidf, tags_name):
    print("filtering tags...")
    print("tfidf.shape=", tfidf.shape)
    removes = set()
    new_tfidf = []
    for tag_i in range(0, tfidf.shape[0]):
        #max_i = numpy.amax(tfidf[tag_i][:])
        max_i = tfidf[tag_i][:].argmax()
        second_tfidf = numpy.amax(scipy.delete(tfidf[tag_i][:], max_i, 0))
        if second_tfidf > TFIDF_THRESHOLD:
            new_tfidf.append(tfidf[tag_i][:])
        else:
            #print("  rm: ", tags_name[tag_i], " (", second_tfidf, ")")
            removes.add(tag_i)
        if tag_i % 50000 == 0:
            print("  tag # ", tag_i)
    new_tfidf = numpy.array(new_tfidf)
    tags_name = [x for i, x in enumerate(tags_name) if i not in removes]
    print("new tfidf.shape=", new_tfidf.shape)
    return new_tfidf, tags_name

"""
def set_location_cluster(locations, membership, attr):
    for c, x in enumerate(locations.keys()):
        setattr(locations[x], attr, membership[c])
"""

"""
def each_cluster(locations, users):
    sorted_locations = sorted(locations.values(), key=lambda x:x.cluster1)
    groups = {x:list(y) for x, y in itertools.groupby(sorted_locations, lambda x:x.cluster1)}
    
    # for each cluster
    for c, a_group in groups.items():
        print("In layer 2 - cluster:", c, ", #:", len(a_group))
        tfidf, tags_name = get_corpus(a_group)
        
        cntr, u, u0, d, jm, p, fpc, membership = cfuzzy.cmeans(coordinate.T, tfidf.T, CLUSTER_NUM_2)
        #set_location_cluster(a_group, membership, "cluster2")

        #output_on_map([(float(x.lat), float(x.lng), x.lname) for x in a_group], membership, CLUSTER_NUM_2, "./data/Summary/map_cluster3_" + str(c) + ".html")
"""

print("--------------------------------------")
print("STARTTIME:", (datetime.datetime.now()))
print("--------------------------------------")
# setting cluster number
if len(sys.argv) > 1:
    CLUSTER_NUM = int(sys.argv[1])

locations = clocation.get_locations_list()
users = cuser.get_users_posts_afile(USER_POSTS_FILE)
fit_users_to_location(locations, users)

coordinate = numpy.array([(float(x.lat), float(x.lng)) for x in locations.values()])
tfidf, tags_name = get_corpus(locations.values())
print("END getting data:", datetime.datetime.now())
tfidf, tags_name = filter_tag(tfidf.T, tags_name)

cntr1, cntr2, u, u0, d1, d2, d, jm, p, fpc, cluster_membership = cfuzzy.cmeans_comb(coordinate.T, tfidf, CLUSTER_NUM, WEIGHT, ERROR)
output_on_map([(float(x.lat), float(x.lng), x.lname) for x in locations.values()] \
    , cluster_membership, CLUSTER_NUM, OUTPUT_MAP)

for i, key in enumerate(locations.keys()):
    setattr(locations[key], "cluster1", cluster_membership[i])
output_location_cluster(locations, OUTPUT_LOCATION_CLUSTER)

#set_location_cluster(locations, membership, "cluster1")

#each_cluster(locations, users)

print("--------------------------------------")
print("ENDTIME:", (datetime.datetime.now()))
print("--------------------------------------")

