"""
    command: python3 parsing_location_category.py [Cluster number]
        e.g. python3 parsing_location_category.py 30
    output map file to: ./data/Summary/map_cluster#[cluster number].html
"""
import datetime
import itertools
import numpy
import operator
import random 
import sys
import custommodule.fuzzycmeans as cfuzzy
import custommodule.lda as clda
import custommodule.location as clocation
import custommodule.cpygmaps as cpygmaps
import custommodule.user as cuser


"""parameters"""
CLUSTER_NUM_1 = 30
CLUSTER_NUM_2 = 5
CATEGORY_MIN_AMOUNT = 5
INTERSECT_THRESHOLD = 0.1 # the min intersection tags count% between the category locations and the candidate location

"""file path"""
USER_POSTS_FILE = "./data/TravelerPosts"
OUTPUT_MAP = "./data/Summary/LocationMap2Layer_c1|" + str(CLUSTER_NUM_1) +\
    "c2|" + str(CLUSTER_NUM_2) + "cma" + str(CATEGORY_MIN_AMOUNT) + "it" + str(INTERSECT_THRESHOLD)

"""
class CusLocation(clocation.Location()):
    def __init__(self):
        super()
        self.cluster1 = None
        self.cluster2 = None
        self.intersect_avg = 0
        self.tags = set()
"""

def output_on_map(point_all, cluster_membership, c, output_file):
    print("Outputing points on the map...")
    mymap = cpygmaps.googlemap(40.758899, -73.9873197, 13)
    """for a_point in point_cntr:
        mymap.addpoint(a_point[0], a_point[1], "#AE0000")
    """
    rd = lambda: random.randint(0,255)
    color = ["#000000"] + ["#%02X%02X%02X" % (rd(), rd(), rd()) for i in range(0, c)]
    for i, a_point in enumerate(point_all):
        mymap.addpoint(a_point[0], a_point[1], color[cluster_membership[i]], a_point[2])
    mymap.draw(output_file) 

def fit_users_to_location(locations, users):
    print("Fitting users to locations..., locations #=", len(locations))
    all_posts = [y for x in users.values() for y in x.posts]
    locations.fit_posts(all_posts)
    # remove locations which no traveler had post there
    remove = [key for key in locations.keys() if len(locations[key].posts) == 0]
    for key in remove:
        locations.pop(key)
    print("after removing locations had no post, #=", len(locations))

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
        tfidf, tags_name = clda.get_tfidf(corpus)
        cntr, u, u0, d, jm, p, fpc, membership = cfuzzy.cmeans(tfidf.T, CLUSTER_NUM_2)
        #set_location_cluster(a_group, membership, "cluster2")

        output_on_map([(float(x.lat), float(x.lng), x.lname) for x in a_group], membership, CLUSTER_NUM_2, "./data/Summary/map_cluster3_" + str(c) + ".html")

"""for intersection clustering"""
class ListDict(dict):
    def __init__(self, *args, **kwargs):
        for x in args:
            self.setdefault(x, [])

    def add_count(self, counts):
        for item in counts:
            self[item[0]].append(item[1])

def set_location_tags(locations):
    for key in locations.keys():
        tags = set(x for a_post in locations[key].posts for x in a_post.tags)
        setattr(locations[key], "tags", tags)

def set_average_intersection(location_list):
    # set location average intersection #
    for i, a_location in enumerate(location_list):
        remain_locations = location_list[:i] + location_list[(i + 1):]
        intersect_count = []
        for x in remain_locations:
            try:
                intersect_count.append(len(x.tags & a_location.tags) / len(a_location.tags))
            except: # if a_location has no tags
                intersect_count.append(0)
        setattr(location_list[i], "interavg", sum(intersect_count) / len(intersect_count))
    print("-interavg:", sum(x.interavg for x in location_list) / len(location_list))

def add_location_into_cate(cate_locations, free_locations):
    "Adding a location into the category..."
    candidates = ListDict(*range(0, len(free_locations)))
    #print("cate tags # avg:", sum(len(x.tags) for x in cate_locations) / len(cate_locations))
    #print("free tags #:", [len(x.tags) for x in free_locations])
    for a_location in cate_locations:
        # count the intersection tags of the initial location & candidate locations. (key of the location, count)
        intersect_count = [(i, len(free_locations[i].tags & a_location.tags) / len(free_locations[i].tags)) for i in candidates.keys()]
        intersect_count = set(x for x in intersect_count if x[1] > INTERSECT_THRESHOLD) # the locations which intersect num > threshold num
        remove = set(candidates.keys()) - set(x[0] for x in intersect_count)
        for i in remove:
            candidates.pop(i) # remove unqualified locations
        candidates.add_count(intersect_count)

    if len(candidates) is not 0:
        # for the remaining candidate locations
        intersect_ratio = {x:0 for x in candidates.keys()}
        for i in candidates.keys():
            # the average intersect tags count between the category locations & the candidate
            in_avg = sum(candidates[i]) / len(candidates[i])
            intersect_ratio[i] = in_avg / free_locations[i].interavg 
        
        new_add = max(intersect_ratio, key=intersect_ratio.get)
        return new_add
    else:
        return None
        

def get_a_cate(location_list):
    failed_init = set()
    while len(failed_init) < len(location_list):
        # the initial location
        #init_lid = random.choice(list(set(x.lid for x in location_list) - failed_init))
        init = random.choice(list(set(range(0, len(location_list))) - failed_init))
        a_category = [location_list[init]]

        free_locations = location_list[0:init] + location_list[(init + 1):]
        #free_locations = [location_list[i] for i in locations if i != init_key}

        while True:
            new_add = add_location_into_cate(a_category, free_locations)
            if new_add is None:
                break
            a_category.append(free_locations[new_add])
            free_locations = free_locations[0:new_add] + free_locations[(new_add + 1):]

        if len(a_category) > CATEGORY_MIN_AMOUNT:
            print("  L2|category initial: " + location_list[init].lname)
            return a_category, free_locations
        else:
            #print("initial: " + locations[init_key].clocation.lname + " --failed")
            failed_init.add(init)
    return None


def get_categories(location_list):
    print("  L2|Splitting categories...")
    category_num = 1
    new_location_list = []
    free_locations = location_list
    while free_locations is not None:
        try:
            print("  L2|Category number: ", category_num, " >>>")
            new_category, free_locations = get_a_cate(free_locations)
            for a_location in new_category:
                setattr(a_location, "cluster2", category_num)
                new_location_list.append(a_location)
            category_num += 1
            print("  L2|adding locations amount:" + str(len(new_category)) + " ,remaining locations amount:" + str(len(free_locations)))
        except Exception:
            print("  >>>\n  L2|Remaining locations number: " + str(len(free_locations)))
            for a_location in free_locations:
                setattr(a_location, "cluster2", 0)
                new_location_list.append(a_location)
            break
    return new_location_list, category_num

def each_cluster_by_intersect(locations):
    sorted_locations = sorted(locations.values(), key=lambda x:x.cluster1)
    groups = {x:list(y) for x, y in itertools.groupby(sorted_locations, lambda x:x.cluster1)}
    
    # for each cluster
    for c, a_group in groups.items():
        print("- In layer 2, cluster1 no.", c, ", #:", len(a_group))
        set_average_intersection(a_group)
        new_a_group, cluster_num_2 = get_categories(a_group)
        output_on_map([(float(x.lat), float(x.lng), x.lname) for x in new_a_group], [x.cluster2 for x in new_a_group], cluster_num_2, OUTPUT_MAP + "_c" + str(c) + ".html")

"""end for intersection clustering"""

print("--------------------------------------")
print("STARTTIME:", (datetime.datetime.now()))
print("--------------------------------------")
# setting cluster number
if len(sys.argv) > 1:
    CLUSTER_NUM = int(sys.argv[1])

""" Layer 1 """
print("> Getting layer 1 clusters...")
locations = clocation.get_locations_list()
coordinate = numpy.array([(float(x.lat), float(x.lng)) for x in locations.values()])
#print(locations["1420070"].__dict__)

cntr, u, u0, d, jm, p, fpc, membership = cfuzzy.cmeans_ori(coordinate.T, CLUSTER_NUM_1)
for i, key in enumerate(locations.keys()):
    setattr(locations[key], "cluster1", membership[i])

""" Layer 2"""
print("> Getting layer 2 clusters...")
users = cuser.get_users_posts_afile(USER_POSTS_FILE)
fit_users_to_location(locations, users)

# tfidf distance
"""
each_cluster(locations, users)
"""

# intersection clustering
set_location_tags(locations)
each_cluster_by_intersect(locations)

print("--------------------------------------")
print("ENDTIME:", (datetime.datetime.now()))
print("--------------------------------------")


