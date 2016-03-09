"""
    command: python3 parsing_location_category.py [Cluster number]
        e.g. python3 parsing_location_category.py 30
    output map file to: ./data/Summary/map_cluster#[cluster number].html
"""
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
CLUSTER_NUM_1 = 30
CLUSTER_NUM_2 = 5

"""file path"""
USER_POSTS_FILE = "./data/TravelerPosts"

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

def fit_users_to_location(locations, users):
    print("Fitting users to locations...")
    all_posts = [y for x in users.values() for y in x.posts]
    locations.fit_posts(all_posts)

def set_location_cluster(locations, membership, attr):
    for c, x in enumerate(locations.keys()):
        setattr(locations[x], attr, membership[c])
   
            
def each_cluster(locations, users):
    sorted_locations = sorted(locations.values(), key=lambda x:x.cluster1)
    groups = {x:list(y) for x, y in itertools.groupby(sorted_locations, lambda x:x.cluster1)}
    
    # for each cluster
    for c, a_group in groups.items():
        print("In layer 2 - cluster:", c, ", #:", len(a_group))
        corpus = []
        for a_location in a_group:
            doc = " ".join([" ".join(x.tags) for x in a_location.posts])
            corpus.append(doc)
        tfidf, tags_name = cfuzzy.get_tfidf(corpus)
        cntr, u, u0, d, jm, p, fpc, membership = cfuzzy.cmeans(tfidf.T, CLUSTER_NUM_2)
        #set_location_cluster(a_group, membership, "cluster2")

        output_on_map([(float(x.lat), float(x.lng), x.lname) for x in a_group], membership, CLUSTER_NUM_2, "./data/Summary/map_cluster3_" + str(c) + ".html")



print("STARTTIME:" + str(datetime.datetime.now()))
# setting cluster number
if len(sys.argv) > 1:
    CLUSTER_NUM = int(sys.argv[1])

""" Layer 1 """
print("> Getting layer 1 clusters...")
locations = clocation.get_locations_list()
coordinate = numpy.array([(float(x.lat), float(x.lng)) for x in locations.values()])

cntr, u, u0, d, jm, p, fpc, membership = cfuzzy.cmeans(coordinate.T, CLUSTER_NUM_1)
set_location_cluster(locations, membership, "cluster1")

""" Layer 2"""
print("> Getting layer 2 clusters...")
users = cuser.get_users_posts_afile(USER_POSTS_FILE)
fit_users_to_location(locations, users)
each_cluster(locations, users)

print("ENDTIME:" + str(datetime.datetime.now()))


