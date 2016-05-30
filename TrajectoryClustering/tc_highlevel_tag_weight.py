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
ERROR = 0.0001
MAX_KTH = 5
GPS_WEIGHT = 0.3

"""file path"""
LOCATION_TOPIC = "./data/LocationCluster/LocationTopic_c30.txt"
OUTPUT_MAP = "./data/Summary/TC_hl&tag&w_c" + str(CLUSTER_NUM) + "k" + str(MAX_KTH) + "w" + str(GPS_WEIGHT) + "e" + str(ERROR)

def main():
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    # Getting data
    users, locations = locationclustering.main()
    location_id, doc_topic = ccluster.open_doc_topic(LOCATION_TOPIC)
    locations = ccluster.fit_locations_membership(locations, numpy.transpose(doc_topic), location_id, "semantic_mem")
    semantic_cluster = numpy.argmax(doc_topic, axis = 1)
    locations = ccluster.fit_locations_cluster(locations, semantic_cluster, location_id, "semantic_cluster")

    # Getting sequences cluster
    sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users.values() if len(a_user.posts) != 0], SPLIT_DAY)
    cluster_sequences = ctrajectory.get_cluster_sequence(sequences, locations)
    semantic_sequences = ctrajectory.get_cluster_sequence(sequences, locations, "semantic_cluster")
    location_sequences = ctrajectory.convertto_location_sequences(sequences, locations)

    print("Filtering short trajectories...")
    fail_indices = []
    for i, s in enumerate(sequences):
        if len(s) <= 2:
            fail_indices.append(i)
    print("  will delete #:", len(fail_indices))
    sequences = numpy.delete(numpy.array(sequences), fail_indices)
    cluster_sequences = numpy.delete(numpy.array(cluster_sequences), fail_indices)
    semantic_sequences = numpy.delete(numpy.array(semantic_sequences), fail_indices)
    location_sequences = numpy.delete(numpy.array(location_sequences), fail_indices)
    print("  remain sequences #:", len(sequences))

    u, u0, d, jm, p, fpc, membership, distance = cfuzzy.sequences_clustering_i("Cluster", cluster_sequences, CLUSTER_NUM, MAX_KTH, semantic_sequences, GPS_WEIGHT, e = ERROR, algorithm="2WeightedDistance")

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
