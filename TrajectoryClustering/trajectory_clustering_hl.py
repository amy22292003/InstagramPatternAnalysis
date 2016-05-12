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
FILTER_TIME = 1443657600 # 2015/10/01 1448928000 # 2015/12/01
SPLIT_DAY = 1
#LC_CLUSTER_NUM = 30
#LC_ERROR = 0.0001
#LC_MAX_KTH = 30
SC_CLUSTER_NUM = 10
SC_ERROR = 0.0001
SC_MAX_KTH = 20

"""file path"""
#OUTPUT_LC_MAP = "./data/Summary/HermesL_3m_c" + str(LC_CLUSTER_NUM) +\
#    "k" + str(LC_MAX_KTH) + "e" + str(LC_ERROR) + "d" + str(SPLIT_DAY) + ".html"
OUTPUT_MAP = "./data/Summary/SequenceClusterLocationsMap_hl_3m_c" + str(SC_CLUSTER_NUM) +\
    "k" + str(SC_MAX_KTH) + "e" + str(SC_ERROR) + "d" + str(SPLIT_DAY)

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
        if len(s) < 10:
            fail_indices.append(i)
    print("  will delete #:", len(fail_indices))
    sequences = numpy.delete(numpy.array(sequences), fail_indices)
    cluster_sequences = numpy.delete(numpy.array(cluster_sequences), fail_indices)
    location_sequences = numpy.delete(numpy.array(location_sequences), fail_indices)
    print("  remain sequences #:", len(sequences))

    u, u0, d, jm, p, fpc, membership = cfuzzy.sequences_clustering_cluster(cluster_sequences, SC_CLUSTER_NUM, SC_MAX_KTH, e = SC_ERROR, algorithm="Original")

    print("Start Outputting...")
    for c in range(0, SC_CLUSTER_NUM):
        this_cluster_indices = [i for i, x in enumerate(membership) if x == c]
        print(c, " >> this cluster #:", len(this_cluster_indices))
        if len(this_cluster_indices) is not 0:
            print(c, ">>", u[c, this_cluster_indices].shape)
            top_10_u = sorted(u[c, this_cluster_indices], reverse=True)
            print("  top_10_u len:", len(top_10_u))
            if len(top_10_u) >= SC_MAX_KTH:
                top_10_u = top_10_u[SC_MAX_KTH - 1]
            else:
                top_10_u = top_10_u[-1]
            top_10_indices = [i for i, x in enumerate(u[c, this_cluster_indices]) if x >= top_10_u]
            #top_10_indices = sorted(range(len(u[c, this_cluster_indices])), key=lambda x: u[c, this_cluster_indices][x], reverse=True)[0:10]
            print(top_10_indices)
            print(u[c, this_cluster_indices][top_10_indices])
            points_sequences = numpy.array(location_sequences)[this_cluster_indices][top_10_indices]
            color = sorted(range(len(points_sequences)), key=lambda x: top_10_indices[x])
            cpygmaps.output_patterns_l(points_sequences, color, len(points_sequences), OUTPUT_MAP + "_" + str(c) + ".html")

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

if __name__ == '__main__':
    main()