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
CLUSTER_NUM = 65
ERROR = 0.000001
MAX_KTH = 1
GPS_WEIGHT = 0.7

"""file path"""
OUTPUT_MAP = "./data/Result/Lowlevelmap_NOVDEC_"
OUTPUT_PATTERN = "./data/Result/Lowlevel_NOVDEC_"
OUTPUT_ANALYSIS = "./data/Result/Analysis_low_"
#"./data/LocationTopic/LocationTopic_c30.txt"

def output_each_pattern(sequences, location_sequences, u, membership, k = None):
    #u_threshold = 0.15
    time_zone = timezone('America/New_York')
    for c in range(u.shape[0]):
    #for c in [39]:
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

def output_specify_pattern(sequences, location_sequences, u, membership, c_list, k = None):
    #u_threshold = 0.15
    time_zone = timezone('America/New_York')
    for c in c_list:
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

ll = [set(["Museum", "Jacqueline Kennedy Onassis Reservoir", "Hewitt", "Neue Galerie", "The Frick Collection"]), \
    set(["Central Park", "Belvedere Castle", "Strawberry Fields", "Bethesda Terrace and Fountain"])]

def filter_sequence(sequences, location_sequences, u, membership):
    new_seq = []
    new_l_seq = []
    new_memidx = []
    for index, a_sequence in enumerate(sequences):
        new_indices = [i for i, x in enumerate(a_sequence) if any([lstr in x.lname for lset in ll for lstr in lset])]
        if len(new_indices) > 0:
            new_seq.append(numpy.array(a_sequence)[new_indices])
            new_l_seq.append(numpy.array(location_sequences[index])[new_indices])
            new_memidx.append(index)
    return new_seq, new_l_seq, numpy.array(membership)[new_memidx]

def output_cluster_detail(sequences, location_sequences, u, membership, c, file = OUTPUT_ANALYSIS):
    file = file + str(c) + ".txt"
    # basic information
    this_indices = [i for i in range(len(membership)) if membership[i] == c]
    this_l_sequences = numpy.array(location_sequences)[this_indices]
    unique_locations = list(set([y for x in this_l_sequences for y in x]))
    counts = []
    for a_location in unique_locations:
        location_count = [any(y.lid == a_location.lid for y in x) for x in this_l_sequences]
        counts.append(sum(location_count))
    f = open(file, "w")
    f.write("# or sequences:" + str(len(this_indices)) + "\tlocation #:" + str(len(unique_locations)) + "\n")

    output_counts(counts, unique_locations, this_l_sequences, f)
    idx = area2_count(this_l_sequences, unique_locations, ll[0], ll[1], f)
    f.write("except>>>\n")
    idx2 = (area2_count(this_l_sequences, unique_locations, ll[0], ll[1], f, True))
    f.write("\naboves:" + str(len(idx | idx2)))
    f.close()

def output_counts(counts, unique_locations, this_l_sequences, f):
    #count of locations
    sorted_indices = sorted(range(len(counts)), key=lambda x:counts[x])
    for i in reversed(sorted_indices):
        f.write(unique_locations[i].lid + "\t" + unique_locations[i].lname + "\t" + str(counts[i]) + "\n")
    f.write("\n\n--Cluster counts>>\n")

    #count of cluster
    for lstr in ll:
        this_lid = [x.lid for x in unique_locations if any([y in x.lname for y in lstr])]
        uni = [any(y.lid in set(this_lid) for y in x) for x in this_l_sequences]
        print(lstr, "(", this_lid, ") --", sum(uni))
        for x in lstr:
            f.write(x + ", ")
        f.write(" (" + str(len(this_lid)) + ")\t" + str(sum(uni)) + "\n")

def area2_count(this_l_sequences, unique_locations, area1, area2, f, is_except = False):
    area1_lid = set([x.lid for x in unique_locations if any([y in x.lname for y in area1])])
    area1_lname = [x.lname for x in unique_locations if any([y in x.lname for y in area1])]
    area2_lid = set([x.lid for x in unique_locations if any([y in x.lname for y in area2])])
    area2_lname = [x.lname for x in unique_locations if any([y in x.lname for y in area2])]
    unique_trajectories = []
    count = 0
    unique_idx = []
    for i, seq in enumerate(this_l_sequences):
        this_lid = set([x.lid for x in seq])
        if is_except:
            if any([x in area1_lid for x in this_lid]) and not any(x in area2_lid for x in  this_lid):
                count += 1
                unique_idx.append(i)
        else:
            if any([x in area1_lid for x in this_lid]) and any(x in area2_lid for x in  this_lid):
                count += 1
                unique_idx.append(i)
    print(area1, "<->", area2, count)
    for x in area1_lname:
        f.write(x + ", ")
    f.write("  <--->  ")
    for x in area2_lname:
        f.write(x + ", ")
    f.write(":\t" + str(count) + "\n")
    print(unique_idx)
    return set(unique_idx)

def get_specific(sequences):
    print("before filter:", len(sequences))
    filter_sequences = []
    for trajectory in sequences:
        #if "3001373" in set([x.lid for x in trajectory]):
        if len(trajectory) >= 3 and len(trajectory) <= 6:
            filter_sequences.append(trajectory)
    print("after filter:", len(filter_sequences))
    return filter_sequences
"""
#ll = [set(["Liberty"]), set(["World", "September"]), set(["Battery"]), set(["Wall Street", "Stock Exchange"]), set(["Brooklyn"])]
def count(sequences, location_sequences, u, membership, c):
    this_indices = [i for i in range(len(membership)) if membership[i] == c]
    this_sequences = numpy.array(location_sequences)[this_indices]
    unique_locations = list(set([y for x in this_sequences for y in x]))
    counts = []
    for a_location in unique_locations:
        location_count = [any(y.lid == a_location.lid for y in x) for x in this_sequences]
        counts.append(sum(location_count))
    f = open("./data/Result/Ana_39.txt", "w")
    f.write("# or sequences:" + str(len(this_indices)) + "\tlocation #:" + str(len(unique_locations)) + "\n")
    sorted_indices = sorted(range(len(counts)), key=lambda x:counts[x])
    for i in reversed(sorted_indices):
        f.write(unique_locations[i].lid + "\t" + unique_locations[i].lname + "\t" + str(counts[i]) + "\n")
    f.write("\n\n--\n\n")
    ll = [set(["Museum"]), set(["Central Park", "Jacqueline Kennedy Onassis Reservoir"])]
    for l in ll:
        this_lid = [x.lid for x in unique_locations if any([y in x.lname for y in l])]
        uni = [any(y.lid in set(this_lid) for y in x) for x in this_sequences]
        print(l, "(", this_lid, ") --", sum(uni))
        for x in l:
            f.write(x + ", ")
        f.write(" (" + str(len(this_lid)) + ")\t" + str(sum(uni)) + "\n")
    f.close()
    return ll

def from_to(location_sequences, membership, c, ll):
    f = open("./data/Result/Ana_39.txt", "a")
    this_indices = [i for i in range(len(membership)) if membership[i] == c]
    this_sequences = numpy.array(location_sequences)[this_indices]
    unique_locations = list(set([y for x in this_sequences for y in x]))
    from_lid = set([x.lid for x in unique_locations if any([y in x.lname for y in ll[0]])])
    from_lname = [x.lname for x in unique_locations if any([y in x.lname for y in ll[0]])]
    to_lid = set([x.lid for x in unique_locations if any([y in x.lname for y in ll[1]])])
    to_lname = set([x.lname for x in unique_locations if any([y in x.lname for y in ll[1]])])
    cc = 0
    tag = []
    for i, seq in enumerate(this_sequences):
        start_i = [i for i, x in enumerate(seq) if x.lid in from_lid]
        if len(start_i) > 0 and len(seq) > 1:
            if any([x.lid in to_lid for x in seq[start_i[0]+1:]]):
                #print(start_i[0], seq[start_i[0]].lname, "-->")
                cc += 1
                tag.append(i)
    print(ll, cc)
    for x in from_lname:
        f.write(x + ", ")
    f.write("  --->  ")
    for x in to_lname:
        f.write(x + ", ")
    f.write(":\t" + str(cc) + "\n")
    f.close()
    return tag
"""
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

    #sequences = get_specific(sequences) 

    sequences = ctrajectory.remove_short(sequences)
    print("  remain users #:", len(set([x[0].uid for x in sequences])))

    location_sequences, longest_len = ctrajectory.convertto_location_sequences(sequences, locations)
    spatial_array = ctrajectory.get_vector_array(location_sequences, longest_len)
    semantic_array = ctrajectory.get_vector_array(location_sequences, longest_len, "semantic_mem")

    u, u0, d, jm, p, fpc, center, membership = cfuzzy.sequences_clustering_i("Location", spatial_array, CLUSTER_NUM, MAX_KTH, semantic_array, GPS_WEIGHT, e = ERROR, algorithm="2WeightedDistance")

    #sequences, location_sequences, membership = filter_sequence(sequences, location_sequences, u, membership)
    #ouput_pattern(sequences, location_sequences, u, membership)
    #output_each_pattern(sequences, location_sequences, u, membership, 30)
    #ctrajectory.output_clusters(sequences, membership, u, OUTPUT_PATTERN)
    
    #output_cluster_detail(sequences, location_sequences, u, membership, 39, file = OUTPUT_ANALYSIS)

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()), ", SPEND:", datetime.datetime.now() - start_time)
    print("--------------------------------------")
    return location_sequences, spatial_array, semantic_array, u

if __name__ == '__main__':
    main(*sys.argv[1:])
