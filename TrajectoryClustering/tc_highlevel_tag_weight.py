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
FILTER_TIME_S = 1448928000 
FILTER_TIME_E = 1451606400
CLUSTER_NUM = 30
ERROR = 0.000001
MAX_KTH = 3
GPS_WEIGHT = 0.5

"""file path"""

#"./data/LocationTopic/LocationTopic_c30.txt"

def main(*argv):
    start_time = datetime.datetime.now()
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    # set parameters
    global CLUSTER_NUM
    global MAX_KTH
    global GPS_WEIGHT
    global FILTER_TIME_S
    global FILTER_TIME_E
    if len(argv) > 0:
        CLUSTER_NUM = argv[0]
        MAX_KTH = argv[1]
        GPS_WEIGHT = argv[2]
        FILTER_TIME_S = argv[3]
        FILTER_TIME_E = argv[4]
        LOCATION_TOPIC = "./data/LocationTopic/LocationTopic_NOV2w_c35.txt"
    else:
        LOCATION_TOPIC = "./data/LocationTopic/LocationTopic_DEC_c35.txt"

    OUTPUT_MAP = "./data/Result/TC_hl&tag&w_1w_c" + str(CLUSTER_NUM) + "k" + str(MAX_KTH) + "w" + str(GPS_WEIGHT)

    # Getting data
    users, locations = locationclustering.main(FILTER_TIME_S, FILTER_TIME_E)
    location_id, doc_topic = ccluster.open_doc_topic(LOCATION_TOPIC)
    semantic_cluster = numpy.argmax(doc_topic, axis = 1)
    locations = ccluster.fit_locations_cluster(locations, semantic_cluster, location_id, "semantic_cluster")

    # Getting sequences cluster
    #sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users.values() if len(a_user.posts) != 0], SPLIT_DAY)
    sequences = ctrajectory.split_trajectory_byday([a_user.posts for a_user in users.values() if len(a_user.posts) != 0])
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

    cluster_trajectories = ctrajectory.get_cluster_sequence(location_sequences)
    semantic_trajectories = ctrajectory.get_cluster_sequence(location_sequences, "semantic_cluster")

    u, u0, d, jm, p, fpc, center, membership = cfuzzy.sequences_clustering_i("Cluster", cluster_trajectories, CLUSTER_NUM, MAX_KTH, semantic_trajectories, GPS_WEIGHT, e = ERROR, algorithm="2WeightedDistance")
    
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
    """
    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()), ", SPEND:", datetime.datetime.now() - start_time)
    print("--------------------------------------")
    return location_sequences, cluster_trajectories, semantic_trajectories, u

if __name__ == '__main__':
    main(*sys.argv[1:])
