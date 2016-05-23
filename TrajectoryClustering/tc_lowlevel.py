#!/usr/bin/env python3
import datetime
import numpy
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
sys.path.append(PACKAGE_PARENT)

import Liu.custommodule.cluster as ccluster
import Liu.custommodule.cpygmaps as cpygmaps
import Liu.custommodule.fuzzycmeans as cfuzzy
import Liu.custommodule.location as clocation
import Liu.custommodule.trajectory as ctrajectory
import Liu.custommodule.user as cuser
import Liu.LocationClustering.gps_locationfreq as locationclustering

"""parameters"""
SPLIT_DAY = 1
CLUSTER_NUM = 20
ERROR = 0.01
MAX_KTH = 10

"""file path"""
USER_POSTS_FOLDER = "./data/TravelerPosts"
OUTPUT_MAP = "./data/Summary/SequenceClusterLL_1w_c" + str(CLUSTER_NUM) +\
    "k" + str(MAX_KTH) + "e" + str(ERROR) + "d" + str(SPLIT_DAY)

def main():
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    users, locations = locationclustering.main()

    # Getting sequences cluster
    sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users.values() if len(a_user.posts) != 0], SPLIT_DAY)
    vector_sequences = ctrajectory.get_vector_sequence(sequences, locations)
    location_sequences = ctrajectory.convertto_location_sequences(sequences, locations)

    u, u0, d, jm, p, fpc, membership, distance = cfuzzy.sequences_clustering("Location", vector_sequences, CLUSTER_NUM, MAX_KTH, e = ERROR, algorithm="Original")

    print("Start Outputting...")
    for c in range(0, SC_CLUSTER_NUM):
        this_cluster_indices = [i for i, x in enumerate(membership) if x == c]
        if len(this_cluster_indices) is not 0:
            print(c, ">>", u[c, this_cluster_indices].shape)
            top_10_u = sorted(u[c, this_cluster_indices], reverse=True)[9]
            top_10_indices = [i for i, x in enumerate(u[c, this_cluster_indices]) if x >= top_10_u]
            #top_10_indices = sorted(range(len(u[c, this_cluster_indices])), key=lambda x: u[c, this_cluster_indices][x], reverse=True)[0:10]
            print(top_10_indices)
            print(u[c, this_cluster_indices][top_10_indices])
            points_sequences = numpy.array(location_sequences)[this_cluster_indices][top_10_indices]
            color = sorted(range(len(points_sequences)), key=lambda x: top_10_indices[x])
            print("  color:", color)
            cpygmaps.output_patterns_l(points_sequences, color, len(points_sequences), OUTPUT_MAP + "_" + str(c) + ".html")

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

if __name__ == '__main__':
    main()
