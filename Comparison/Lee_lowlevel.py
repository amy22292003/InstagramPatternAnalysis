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
import Liu.custommodule.trajectory as ctrajectory
import Liu.LocationClustering.gps_locationfreq as locationclustering
import Comparison.Lee as lee

"""parameters"""
SPLIT_DAY = 1
EPSILON = 0.01
MINLNS = 20
#GPS_WEIGHT = 0.9

"""file path"""
LOCATION_TOPIC = "./data/LocationTopic/LocationTopic_c30.txt"
OUTPUT_MAP = "./data/Result/Lee_&mydist_1w_ep" + str(EPSILON) + "m" + str(MINLNS)# + "w" + str(GPS_WEIGHT)

def main():
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")
    # Getting data
    users, locations = locationclustering.main()
    #location_id, doc_topic = ccluster.open_doc_topic(LOCATION_TOPIC)
    #locations = ccluster.fit_locations_membership(locations, numpy.transpose(doc_topic), location_id, "semantic_mem")

    # Getting sequences cluster
    sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users.values() if len(a_user.posts) != 0], SPLIT_DAY)
    vector_sequences = ctrajectory.get_vector_sequence(sequences, locations)
    #semantic_sequences = ctrajectory.get_vector_sequence(sequences, locations, "semantic_mem")
    location_sequences = ctrajectory.convertto_location_sequences(sequences, locations)

    print("Filtering short trajectories...")
    fail_indices = []
    for i, s in enumerate(sequences):
        if len(s) <= 2:
            fail_indices.append(i)
    print("  will delete #:", len(fail_indices))
    sequences = numpy.delete(numpy.array(sequences), fail_indices)
    vector_sequences = numpy.delete(numpy.array(vector_sequences), fail_indices)
    #semantic_sequences = numpy.delete(numpy.array(semantic_sequences), fail_indices)
    location_sequences = numpy.delete(numpy.array(location_sequences), fail_indices)
    print("  remain sequences #:", len(sequences), " ,average length=", sum([len(x) for x in sequences]) / len(sequences))

    #cluster_num, cluster_membership, noise = lee.line_segment_clustering(vector_sequences, semantic_sequences, "Mine", "Location", GPS_WEIGHT, ep = EPSILON, minlns = MINLNS)
    cluster_num, cluster_membership, noise = lee.line_segment_clustering(vector_sequences, "Mine", "Location", ep = EPSILON, minlns = MINLNS)
    print(cluster_membership)

    print("Start Outputting...")
    for c in range(cluster_num):
        this_cluster_indices = numpy.where(cluster_membership == c)[0]
        print(c, " >> this cluster #:", len(this_cluster_indices))
        points_sequences = numpy.array(location_sequences)[this_cluster_indices]
        color = range(len(points_sequences))
        cpygmaps.output_patterns_l(points_sequences, color, len(points_sequences), OUTPUT_MAP + "_" + str(c) + ".html")

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

if __name__ == '__main__':
    main()