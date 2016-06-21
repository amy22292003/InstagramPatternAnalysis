#!/usr/bin/env python3
import datetime
import inspect
import numpy
import os
import sys

PACKAGE_PARENT = '..'
FILE_DIR = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
sys.path.insert(0, os.path.normpath(os.path.join(FILE_DIR, PACKAGE_PARENT)))
sys.path.insert(0, PACKAGE_PARENT)

import Liu.custommodule.cluster as ccluster
import Liu.custommodule.cpygmaps as cpygmaps
import Liu.custommodule.fuzzycmeans as cfuzzy
import Liu.custommodule.location as clocation
import Liu.custommodule.trajectory as ctrajectory
import Liu.custommodule.user as cuser
import Liu.LocationClustering.gps_locationfreq as locationclustering

"""parameters"""
SPLIT_DAY = 1
FILTER_TIME = 1448928000 # 2015/12/01
CLUSTER_NUM = 30
ERROR = 0.0000001
MAX_KTH = 3
GPS_WEIGHT = 0.9

"""file path"""
LOCATION_TOPIC = "./data/LocationTopic/LocationTopic_c30.txt"
OUTPUT_MAP = "./data/Result/TC_ll&tag&w_1m_c" + str(CLUSTER_NUM) + "k" + str(MAX_KTH) + "w" + str(GPS_WEIGHT) + "e" + str(ERROR)

def main():
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    # Getting data
    users, locations = locationclustering.main()
    location_id, doc_topic = ccluster.open_doc_topic(LOCATION_TOPIC)
    locations = ccluster.fit_locations_membership(locations, numpy.transpose(doc_topic), location_id, "semantic_mem")

    # Getting sequences of posts & locations
    sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users.values() if len(a_user.posts) != 0], SPLIT_DAY)
    location_sequences, longest_len = ctrajectory.convertto_location_sequences(sequences, locations)
    print("Filtering short trajectories...")
    fail_indices = []
    for i, s in enumerate(sequences):
        if len(s) <= 2:
            fail_indices.append(i)
    print("  will delete #:", len(fail_indices))
    sequences = numpy.delete(numpy.array(sequences), fail_indices)
    location_sequences = numpy.delete(numpy.array(location_sequences), fail_indices)
    print("  remain sequences #:", len(sequences), " ,average length=", sum([len(x) for x in sequences]) / len(sequences))

    vector_trajectories = ctrajectory.get_vector_sequence(location_sequences)
    semantic_trajectories = ctrajectory.get_vector_sequence(location_sequences, "semantic_mem")

    u, u0, d, jm, p, fpc, membership = cfuzzy.sequences_clustering_i("Location", vector_trajectories, CLUSTER_NUM, MAX_KTH, semantic_trajectories, GPS_WEIGHT, e = ERROR, algorithm="2WeightedDistance")
    """
    u, init = cfuzzy.sequences_clustering_i("Location", vector_sequences, CLUSTER_NUM, MAX_KTH, semantic_sequences, GPS_WEIGHT, e = ERROR, algorithm="2WeightedDistance")
    for c_i in range(CLUSTER_NUM):
        indices = [i for i, x in enumerate(u[c_i, :]) if x == 1]
        print("  ", c_i, "-#:", len(indices))
        points_sequences = numpy.array(location_sequences)[indices]
        color = [0 if x == init[c_i] else 1 for x in indices]
        cpygmaps.output_patterns_l(points_sequences, color, 2, "./data/Summary/InitSame_" + str(c_i) + ".html")
    """

    print("Start Outputting...")
    for c in range(CLUSTER_NUM):
        this_cluster_indices = [i for i, x in enumerate(membership) if x == c]
        print(c, " >> this cluster #:", len(this_cluster_indices))
        if len(this_cluster_indices) is not 0:
            top_10_u = sorted(u[c, this_cluster_indices], reverse=True)
            if len(top_10_u) >= MAX_KTH:
                top_10_u = top_10_u[MAX_KTH - 1]
            else:
                top_10_u = top_10_u[-1]
            top_10_indices = [i for i, x in enumerate(u[c, this_cluster_indices]) if x >= top_10_u]
            #top_10_indices = sorted(range(len(u[c, this_cluster_indices])), key=lambda x: u[c, this_cluster_indices][x], reverse=True)[0:10]
            print("  top_10:", top_10_u, ">", top_10_indices)
            print(u[c, this_cluster_indices][top_10_indices])
            points_sequences = numpy.array(location_sequences)[this_cluster_indices][top_10_indices]
            color = sorted(range(len(points_sequences)), key=lambda x: top_10_indices[x])
            cpygmaps.output_patterns_l(points_sequences, color, len(points_sequences), OUTPUT_MAP + "_" + str(c) + ".html")

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

if __name__ == '__main__':
    main()
