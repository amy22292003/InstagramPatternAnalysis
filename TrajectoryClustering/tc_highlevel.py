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
import Liu.custommodule.fuzzycmeans as cfuzzy
import Liu.custommodule.location as clocation
import Liu.custommodule.cpygmaps as cpygmaps
import Liu.custommodule.trajectory as ctrajectory
import Liu.custommodule.user as cuser
import Liu.LocationClustering.gps_locationfreq as locationclustering

"""parameters"""
SPLIT_DAY = 1
CLUSTER_NUM = 10
ERROR = 0.01
MAX_KTH = 10

"""file path"""
OUTPUT_MAP = "./data/Summary/SequenceClusterHL_3m_c" + str(CLUSTER_NUM) +\
    "k" + str(MAX_KTH) + "e" + str(ERROR) + "d" + str(SPLIT_DAY)

def main():
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    users, locations = locationclustering.main()

    # Getting sequences cluster
    sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users.values() if len(a_user.posts) != 0], SPLIT_DAY)
    cluster_sequences = ctrajectory.get_cluster_sequence(sequences, locations)
    location_sequences = ctrajectory.convertto_location_sequences(sequences, locations)

    print("Filtering short trajectories...")
    fail_indices = []
    for i, s in enumerate(cluster_sequences):
        if len(s) <= 2:
            fail_indices.append(i)
    print("  will delete #:", len(fail_indices))
    sequences = numpy.delete(numpy.array(sequences), fail_indices)
    cluster_sequences = numpy.delete(numpy.array(cluster_sequences), fail_indices)
    location_sequences = numpy.delete(numpy.array(location_sequences), fail_indices)
    print("  remain sequences #:", len(sequences))

    u, u0, d, jm, p, fpc, membership, distance = cfuzzy.sequences_clustering("Cluster", vector_sequences, CLUSTER_NUM, MAX_KTH, e = ERROR, algorithm="Original")

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

            #print("  center:", this_cluster_indices[top_10_indices[0]], " ;distance:", distance[:, this_cluster_indices[top_10_indices[0]]])
            #closest_indices = [i for i, x in enumerate(distance[:, this_cluster_indices[top_10_indices[0]]]) if x <= 0.25]
            #print("  closest_indices:", closest_indices)
            #dist_points_sequences = numpy.array(location_sequences)[closest_indices]
            #dist_color = range(len(dist_points_sequences))
            #cpygmaps.output_patterns_l(dist_points_sequences, dist_color, len(dist_points_sequences), "./data/Summary/distance_" + str(c) + ".html")

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

if __name__ == '__main__':
    main()