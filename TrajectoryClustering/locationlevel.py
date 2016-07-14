#!/usr/bin/env python3
import datetime
import inspect
import numpy
import os
from pytz import timezone
import sys

PACKAGE_PARENT = '..'
FILE_DIR = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
sys.path.insert(0, os.path.normpath(os.path.join(FILE_DIR, PACKAGE_PARENT)))
sys.path.insert(0, PACKAGE_PARENT)

import Liu.custommodule.locationcluster as ccluster
import Liu.custommodule.cpygmaps as cpygmaps
import Liu.custommodule.fuzzycmeans as cfuzzy
import Liu.custommodule.location as clocation
import Liu.custommodule.trajectory as ctrajectory
import Liu.custommodule.user as cuser
import Liu.LocationClustering.gps_locationfreq as locationclustering

"""parameters"""
SPLIT_DAY = 1
FILTER_TIME_S = 1446350400 # 2015/11/01 #1448942400 #2015/12/01 @ UTC-4
FILTER_TIME_E = 1451620800 #1451620800 #2016/01/01 @ UTC-4
CLUSTER_NUM = 60
ERROR = 0.000001
MAX_KTH = 3
GPS_WEIGHT = 0.9

"""file path"""
OUTPUT_MAP = "./data/Result/Lowlevelmap_NOVDEC_c"
OUTPUT_PATTERN = "./data/Result/Lowlevel_NOVDEC_"
#"./data/LocationTopic/LocationTopic_c30.txt"

def output_each_pattern(sequences, location_sequences, u, membership, k = None):
    #u_threshold = 0.15
    time_zone = timezone('America/New_York')
    for c in range(u.shape[0]):
        indices = [i for i, x in enumerate(membership) if x == c]
        if len(indices) is not 0:
            sorted_u = sorted(u[c, indices], reverse = True)
            sorted_indices = sorted(indices, key = lambda x:u[c, x])
            sorted_indices = sorted_indices[::-1]
            if k is not None and len(sorted_indices) > k:
                top_k = sorted_u[k - 1]
                sorted_indices = [i for i in sorted_indices if u[c, i] >= top_k]
            output = []
            for ti, i in enumerate(sorted_indices):
                output.append([(location_sequences[i][li].lat, location_sequences[i][li].lng, 
                    str(ti) + "(" + str(li) + "/" + str(len(sequences[i]) - 1) +  ")>>" +
                    datetime.datetime.fromtimestamp(int(x.time), tz=time_zone).strftime('%Y-%m-%d %H:%M') + 
                    " " + x.lname) for li, x in enumerate(sequences[i])])
            color = range(len(sorted_indices))
            if len(sorted_indices) > 0:
                cpygmaps.output_patterns(output, color, len(output), OUTPUT_MAP + "_" + str(c) + ".html")

def ouput_pattern(sequences, location_sequences, u, membership, k = 3):
    print("Output patterns on map...")
    time_zone = timezone('America/New_York')
    output = []
    for c in range(u.shape[0]):
        indices = [i for i, x in enumerate(membership) if x == c]
        if len(indices) is not 0:
            sorted_u = sorted(u[c, indices], reverse = True)
            sorted_indices = sorted(indices, key = lambda x:u[c, x])
            sorted_indices = sorted_indices[::-1]
            if k is not None and len(sorted_indices) > k:
                top_k = sorted_u[k - 1]
                sorted_indices = [i for i in sorted_indices if u[c, i] >= top_k]
            for ti, i in enumerate(sorted_indices):
                output.append([(location_sequences[i][li].lat, location_sequences[i][li].lng, 
                    "C" + str(membership[i]) + "-" + str(ti) + "(" + str(li) + "/" + str(len(sequences[i]) - 1) +  ")>>" +
                    datetime.datetime.fromtimestamp(int(x.time), tz=time_zone).strftime('%Y-%m-%d %H:%M') + 
                    " " + x.lname) for li, x in enumerate(sequences[i])])
    cpygmaps.output_patterns(output, membership, u.shape[0], OUTPUT_MAP + "_all.html")

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
    global OUTPUT_MAP
    global OUTPUT_PATTERN
    if len(argv) > 0:
        CLUSTER_NUM = argv[0]
        MAX_KTH = argv[1]
        GPS_WEIGHT = argv[2]
        FILTER_TIME_S = argv[3]
        FILTER_TIME_E = argv[4]
        LOCATION_TOPIC = "./data/LocationTopic/LocationTopic_OCT_c35.txt"
    else:
        LOCATION_TOPIC = "./data/LocationTopic/LocationTopic_NOVDEC_c35.txt"

    OUTPUT_MAP = OUTPUT_MAP + str(CLUSTER_NUM) + "k" + str(MAX_KTH) + "w" + str(GPS_WEIGHT)
    OUTPUT_PATTERN = OUTPUT_PATTERN + str(CLUSTER_NUM) + "k" + str(MAX_KTH)
    
    # Getting data
    users, locations = locationclustering.main(FILTER_TIME_S, FILTER_TIME_E)
    location_id, doc_topic = ccluster.open_doc_topic(LOCATION_TOPIC)
    locations = ccluster.fit_locations_membership(locations, numpy.transpose(doc_topic), location_id, "semantic_mem")
    print("  users # :", len(users))

    # Getting sequences of posts & locations
    #sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users.values() if len(a_user.posts) != 0], SPLIT_DAY)
    sequences = ctrajectory.split_trajectory_byday([a_user.posts for a_user in users.values() if len(a_user.posts) != 0])
    sequences = ctrajectory.remove_adjacent_location(sequences)
    sequences = ctrajectory.remove_short(sequences)
    print("  remain users #:", len(set([x[0].uid for x in sequences])))

    location_sequences, longest_len = ctrajectory.convertto_location_sequences(sequences, locations)
    spatial_array = ctrajectory.get_vector_array(location_sequences, longest_len)
    semantic_array = ctrajectory.get_vector_array(location_sequences, longest_len, "semantic_mem")

    u, u0, d, jm, p, fpc, center, membership = cfuzzy.sequences_clustering_i("Location", spatial_array, CLUSTER_NUM, MAX_KTH, semantic_array, GPS_WEIGHT, e = ERROR, algorithm="2WeightedDistance")

    
    ouput_pattern(sequences, location_sequences, u, membership)
    output_each_pattern(sequences, location_sequences, u, membership, 8)
    ctrajectory.output_clusters(sequences, membership, u, OUTPUT_PATTERN)
    
    
    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()), ", SPEND:", datetime.datetime.now() - start_time)
    print("--------------------------------------")
    return location_sequences, spatial_array, semantic_array, u

if __name__ == '__main__':
    main(*sys.argv[1:])