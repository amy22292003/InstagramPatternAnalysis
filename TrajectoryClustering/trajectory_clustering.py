#!/usr/bin/env python3
"""
    command: 
    output map file to: 
"""
import datetime
import numpy
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
sys.path.append(PACKAGE_PARENT)

import Liu.custommodule.cluster as ccluster
import Liu.custommodule.fuzzycmeans as cfuzzy
import Liu.custommodule.location as clocation
import Liu.custommodule.cpygmaps as cpygmaps
import Liu.custommodule.trajectory as ctrajectory
import Liu.custommodule.user as cuser

"""parameters"""
LC_CLUSTER_NUM = 30
LC_ERROR = 0.0001
LC_MAX_KTH = 30
SC_CLUSTER_NUM = 200
SC_ERROR = 0.0001
SC_MAX_KTH = 100

#CATEGORY_MIN_AMOUNT = 5
#INTERSECT_THRESHOLD = 0.1 # the min intersection tags count% between the category locations and the candidate location

"""file path"""
CLUSTER_FILE = "./data/LocationCluster/LocationClusterCoor_klf_30k30e0.0001.txt"
USER_POSTS_FILE = "./data/TravelerPosts"

OUTPUT_LC_MAP = "./data/Summary/SequenceClusterLocationsMap_c" + str(LC_CLUSTER_NUM) +\
    "k" + str(LC_MAX_KTH) + "e" + str(LC_ERROR) + ".html"
OUTPUT_MAP = "./data/Summary/SequenceClusterMap_c" + str(SC_CLUSTER_NUM) +\
    "k" + str(SC_MAX_KTH) + "e" + str(SC_ERROR) + ".html"
OUTPUT_CLUSTER = "./data/Summary/SequenceCluster_c" + str(SC_CLUSTER_NUM) +\
    "k" + str(SC_MAX_KTH) + "e" + str(SC_ERROR) + ".txt"

def set_location_user_count(locations):
    for key in locations.keys():
        users = set(a_post.uid for a_post in locations[key].posts)
        setattr(locations[key], "usercount", len(users))

def output_sequence_cluster(sequences, cluster_key, file_path):
    sorted_sequences = sorted(sequences, key=lambda x:getattr(x, cluster_key))
    groups = {x:list(y) for x, y in itertools.groupby(sorted_sequences, lambda x:getattr(x, cluster_key))}

    f = open(file_path, "w")
    # for each cluster
    for c, a_group in groups.items():
        f.write("Cluster:" + str(c) + "\t#:" + str(len(a_group)) + "\n")
        for a_sequence in a_group:
            output = [x.lid + x.lname for x in a_sequence]
            output_str = output.join(" ->\t")
            output_str = " " + len(output) + "> " + output_str + "\n"
            f.write(output_str)
    f.close()

def main():
    """end for intersection clustering"""

    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    """Low Layer"""
    # Getting locations membership vectors
    locations = clocation.open_locations()
    print("type:", type(locations), len(locations))
    del_key = [x for x in locations.keys() if locations[x].usercount < 200]
    for key in del_key:
        del locations[key]
    print("type:", type(locations), len(locations))
    users = cuser.open_users_posts_afile(USER_POSTS_FILE)
    for key, a_user in users.items():
        posts = [x for x in a_user.posts if x.lid in set(locations.keys())]
        users[key].posts = posts
    locations = clocation.fit_users_to_location(locations, users, "uid")
    print("type:", type(locations), len(locations))

    set_location_user_count(locations)
    coordinate = numpy.array([(float(x.lat), float(x.lng)) for x in locations.values()])
    location_frequency = numpy.array([x.usercount for x in locations.values()])
    
    # intersect clustering with the kth locations in each cluster & location frequency as weight
    cntr, u, u0, d, jm, p, fpc, membership = cfuzzy.cmeans_coordinate(coordinate.T, LC_CLUSTER_NUM, LC_MAX_KTH, location_frequency, e=LC_ERROR, algorithm="kthCluster_LocationFrequency")
    for i, key in enumerate(locations.keys()):
        setattr(locations[key], "cluster", membership[i])
        setattr(locations[key], "membership", numpy.atleast_2d(u[:,i]))

    cpygmaps.output_clusters(\
        [(float(x.lat), float(x.lng), str(x.cluster) + " >> " + x.lname + " >>u:" + str(u[x.cluster, i])) for i, x in enumerate(locations.values())], \
        membership, LC_CLUSTER_NUM, OUTPUT_LC_MAP)
    print("u.type:", type(u[:,0]), u[:,0].shape)

    # Getting sequences cluster
    print("users.type:", type(users))
    sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users.values()])
    vector_sequences = ctrajectory.get_vector_sequence(sequences, locations)

    u, u0, d, jm, p, fpc, membership = cfuzzy.sequences_clustering_location(vector_sequences, SC_CLUSTER_NUM, SC_MAX_KTH, e = SC_ERROR, algorithm="Original")
    for i in range(0, len(sequences)):
        setattr(sequences[i], "cluster", membership[i])

    cpygmaps.output_patterns_l(sequences, membership, SC_CLUSTER_NUM, OUTPUT_MAP)
    output_sequence_cluster(sequences, "cluster", OUTPUT_CLUSTER)

    """High Layer"""
    """
    cluster_list = ccluster.open_cluster_list(CLUSTER_FILE)
    locations = ccluster.get_locations_from_cluster(cluster_list)
    users = cuser.open_users_posts_afile(USER_POSTS_FILE)

    # split users trajectories to sequences
    sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users])
    

    sequences_clustering_location(sequences, cluster_num, *para, e = 0.01, algorithm="Original")

    coordinate = numpy.array([(float(x.lat), float(x.lng)) for x in locations.values()])
    location_frequency = numpy.array([x.usercount for x in locations.values()])
    
    # intersect clustering with the kth locations in each cluster & location frequency as weight
    cntr, u, u0, d, jm, p, fpc, membership = cfuzzy.cmeans_coordinate(coordinate.T, CLUSTER_NUM, MAX_KTH, location_frequency, e=ERROR, algorithm="kthCluster_LocationFrequency")
    for i, key in enumerate(locations.keys()):
        setattr(locations[key], "cluster", membership[i])

    cpygmaps.output_clusters(\
        [(float(x.lat), float(x.lng), str(x.cluster) + " >> " + x.lname + " >>u:" + str(u[x.cluster, i])) for i, x in enumerate(locations.values())], \
        membership, CLUSTER_NUM, OUTPUT_MAP)

    cfuzzy.output_location_cluster(locations.values(), "cluster", OUTPUT_CLUSTER)
    """

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

if __name__ == '__main__':
    main()
