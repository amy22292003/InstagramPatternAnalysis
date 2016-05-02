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
FILTER_TIME = 1451001600 # 2015/12/25 1448928000 # 2015/12/01
SPLIT_DAY = 1
LC_CLUSTER_NUM = 30
LC_ERROR = 0.0001
LC_MAX_KTH = 30
SC_CLUSTER_NUM = 10
SC_ERROR = 0.0001
SC_MAX_KTH = 50

"""file path"""
USER_POSTS_FOLDER = "./data/TravelerPosts"
OUTPUT_LC_MAP = "./data/Summary/SequenceClusterLocationsMap_c" + str(LC_CLUSTER_NUM) +\
    "k" + str(LC_MAX_KTH) + "e" + str(LC_ERROR) + "d" + str(SPLIT_DAY) + ".html"
OUTPUT_MAP = "./data/Summary/SequenceClusterMap_top10_c" + str(SC_CLUSTER_NUM) +\
    "k" + str(SC_MAX_KTH) + "e" + str(SC_ERROR) + "d" + str(SPLIT_DAY)

def set_location_user_count(locations):
    for key in locations.keys():
        users = set(a_post.uid for a_post in locations[key].posts)
        setattr(locations[key], "usercount", len(users))

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
        posts = [x for x in a_user.posts if (x.time > FILTER_TIME) and (x.time < 1451606400)]
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

    # Getting sequences cluster
    sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users.values() if len(a_user.posts) != 0], SPLIT_DAY)
    vector_sequences = ctrajectory.get_vector_sequence(sequences, locations)
    location_sequences = ctrajectory.convertto_location_sequences(sequences, locations)

    u, u0, d, jm, p, fpc, membership = cfuzzy.sequences_clustering_location(vector_sequences, SC_CLUSTER_NUM, SC_MAX_KTH, e = SC_ERROR, algorithm="Original")

    print("Start Outputting...")
    for c in range(0, SC_CLUSTER_NUM):
        this_cluster_indices = [i for i, x in enumerate(membership) if x == c]
        if len(this_cluster_indices) is not 0:
            print(c, ">>", u[c, this_cluster_indices].shape)
            top_10_indices = sorted(range(len(u[c, this_cluster_indices])), key=lambda x: u[c, this_cluster_indices][x])[0:10]
            print(type(top_10_indices), top_10_indices.shape)
            print(u[c, this_cluster_indices][top_10_indices])
            points_sequences = location_sequences[this_cluster_indices][top_10_indices]
            color = sorted(range(len(points_sequences)), key=lambda x: top_10_indices[x])
            print("  color:", color)
            cpygmaps.output_patterns_l(points_sequences, color, len(points_sequences), OUTPUT_MAP + "_" + str(c) + ".html")

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

if __name__ == '__main__':
    main()
