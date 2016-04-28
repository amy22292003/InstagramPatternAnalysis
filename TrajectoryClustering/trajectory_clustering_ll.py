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

"""file path"""
CLUSTER_FILE = "./data/LocationCluster/LocationClusterCoor_klf_30k30e0.0001.txt"
USER_POSTS_FOLDER = "./data/TravelerPosts"
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
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    # Getting locations membership vectors
    locations = clocation.open_locations()
    users = cuser.open_users_posts_afile(USER_POSTS_FOLDER)

    # sample users
    print("Sampling users posts...")
    for key, a_user in users.items():
        posts = [x for x in a_user.posts if x.time > 1448928000] # 2015/12/01 00:00:00 GMT
        users[key].posts = posts
    locations = clocation.fit_users_to_location(locations, users, "uid")

    set_location_user_count(locations)

    coordinate = numpy.array([(float(x.lat), float(x.lng)) for x in locations.values()])
    location_frequency = numpy.array([x.usercount for x in locations.values()])
    
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
    sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users.values() if len(a_user.posts) != 0], 3)
    vector_sequences = ctrajectory.get_vector_sequence(sequences, locations)

    u, u0, d, jm, p, fpc, membership = cfuzzy.sequences_clustering_location(vector_sequences, SC_CLUSTER_NUM, SC_MAX_KTH, e = SC_ERROR, algorithm="Original")
    for i in range(0, len(sequences)):
        setattr(sequences[i], "cluster", membership[i])

    cpygmaps.output_patterns_l(sequences, membership, SC_CLUSTER_NUM, OUTPUT_MAP)
    output_sequence_cluster(sequences, "cluster", OUTPUT_CLUSTER)

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

if __name__ == '__main__':
    main()
