#!/usr/bin/env python3
import datetime
import numpy
import os
from pytz import timezone
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
sys.path.append(PACKAGE_PARENT)

import Liu.custommodule.locationcluster as ccluster
import Liu.custommodule.cpygmaps as cpygmaps
import Liu.custommodule.fuzzycmeans as cfuzzy
import Liu.custommodule.location as clocation
import Liu.custommodule.trajectory as ctrajectory
import Liu.custommodule.user as cuser
import Liu.LocationClustering.gps_locationfreq as locationclustering

"""parameters"""
SPLIT_DAY = 1
FILTER_TIME_S = 1446350400 #2015/11/01 #1448942400 #2015/12/01 @ UTC-4
FILTER_TIME_E = 1451620800 #1451620800 #2016/01/01 @ UTC-4
CLUSTER_NUM = 50
ERROR = 0.000001
MAX_KTH = 1
GPS_WEIGHT = float('nan')


"""file path"""
OUTPUT_MAP = "./data/Result/Highlevelmap_c"
OUTPUT_PATTERN = "./data/Result/Highlevel_"
#"./data/LocationTopic/LocationTopic_c30.txt"

def output_each_pattern(sequences, location_sequences, u, membership, k = None):
    #u_threshold = 0.15
    time_zone = timezone('America/New_York')
    for c in range(u.shape[0]):
    #for c in [40]:
        indices = [i for i, x in enumerate(membership) if x == c]
        if len(indices) is not 0:
            sorted_u = sorted(u[c, indices], reverse = True)
            sorted_indices = sorted(indices, key = lambda x:u[c, x])
            sorted_indices = sorted_indices[::-1]
            if k is not None and len(sorted_indices) > k:
                top_k = sorted_u[k - 1]
                sorted_indices = [i for i in sorted_indices if u[c, i] >= top_k]
            output = []
            number = 0
            for ti, i in enumerate(sorted_indices):
                a_trajectory = [(location_sequences[i][li].lat, location_sequences[i][li].lng, 
                    str(number) + "(" + str(li) + "/" + str(len(sequences[i]) - 1) +  ")>>" +
                    datetime.datetime.fromtimestamp(int(x.time), tz=time_zone).strftime('%Y-%m-%d %H:%M') + 
                    " " + x.lname) for li, x in enumerate(sequences[i]) ]#\
                    #if (float(location_sequences[i][li].lng) > -74.021868 and float(location_sequences[i][li].lng) < -73.984895 and float(location_sequences[i][li].lat) > 40.691014 and float(location_sequences[i][li].lat) < 40.717370) or "Liberty" in location_sequences[i][li].lname]
                if len(a_trajectory) > 0:
                    output.append(a_trajectory)
                    number += 1
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

def get_specific(sequences):
    print("before filter:", len(sequences))
    filter_sequences = []
    for trajectory in sequences:
        #if "3001373" in set([x.lid for x in trajectory]):
        if len(trajectory) >= 3 and len(trajectory) <= 6:
            filter_sequences.append(trajectory)
    print("after filter:", len(filter_sequences))
    return filter_sequences

def count(sequences, location_sequences, u, membership, c):
    this_indices = [i for i in range(len(membership)) if membership[i] == c]
    this_sequences = numpy.array(location_sequences)[this_indices]
    unique_locations = list(set([y for x in this_sequences for y in x]))
    counts = []
    for a_location in unique_locations:
        location_count = [any(y.lid == a_location.lid for y in x) for x in this_sequences]
        counts.append(sum(location_count))
    f = open("./data/Result/Ana_40.txt", "w")
    f.write("# or sequences:" + str(len(this_indices)) + "\tlocation #:" + str(len(unique_locations)) + "\n")
    sorted_indices = sorted(range(len(counts)), key=lambda x:counts[x])
    for i in reversed(sorted_indices):
        f.write(unique_locations[i].lid + "\t" + unique_locations[i].lname + "\t" + str(counts[i]) + "\n")
    f.write("\n\n--\n\n")
    #ll = [set(["Liberty"]), set(["World Trade", "Worldtrade", "World Financial Center", "September"]), set(["Battery Park"]), 
    #    set(["Wall Street", "Stock Exchange"]), set(["Trinity"]), set(["Brooklyn"])]
    ll = [set(["Liberty"]),
        set(["World Trade", "9\/11", "World Financial Center", "September","Battery Park","Wall Street", "Stock Exchange", "Trinity", "Fulton Center", "South Street Seaport", "City Hall", "Conrad New York Hotel", " Stone Street Tavern"]), 
        set(["Brooklyn Bridge", "Jane's Carousel", "Brooklyn Heights", "Jacques Torres Chocolate", "AlMar Dumbo", " Manhattan Bridge"])]
    for l in ll:
        this_lid = [x.lid for x in unique_locations if any([y in x.lname for y in l])]
        uni = [any(y.lid in set(this_lid) for y in x) for x in this_sequences]
        print(l, "(", this_lid, ") --", sum(uni))
        for x in l:
            f.write(x + ", ")
        f.write(" (" + str(len(this_lid)) + ")\t" + str(sum(uni)) + "\n")
    f.close()
    ll = [set(["Liberty"]),
        set(["World Trade", "9\/11", "World Financial Center", "September","Battery Park","Wall Street", "Stock Exchange", "Trinity", "Fulton Center", "South Street Seaport", "City Hall", "Conrad New York Hotel", " Stone Street Tavern"]), 
        set(["Brooklyn Bridge", "Jane's Carousel", "Brooklyn Heights", "Jacques Torres Chocolate", "AlMar Dumbo", " Manhattan Bridge"])]
    return ll

def from_to(location_sequences, membership, c, ll):
    f = open("./data/Result/Ana_40.txt", "a")
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
                cc += 1
                tag.append(i)
    print(ll, cc)
    #for x in from_lname:
    one_to_two(ll[0], ll[1], f)
    f.write(":\t" + str(cc) + "\n")
    """
    other_lid = set([x.lid for x in unique_locations if any([y in x.lname for y in ll[2]])])
    from_ = [all([x.lid in from_lid and x.lid not in (to_lid|other_lid) for x in seq]) for seq in this_sequences]
    to = [all([x.lid in to_lid and x.lid not in (from_lid|other_lid) for x in seq]) for seq in this_sequences]
    other = [all([x.lid in other_lid and x.lid not in (from_lid|to_lid) for x in seq]) for seq in this_sequences]
    one_to_two(ll[0], ll[0], f)
    f.write(":\t" + str(sum(from_)) + "\n")
    one_to_two(ll[1], ll[1], f)
    f.write(":\t" + str(sum(to)) + "\n")
    one_to_two(ll[2], ll[2], f)
    f.write(":\t" + str(sum(other)) + "\n")
    """
    f.close()
    return tag

def one_to_two(a, b, f):
    for x in a:
        f.write(x + ", ")
    f.write("  --->  ")
    for x in b:
        f.write(x + ", ")


def main(*argv):
    start_time = datetime.datetime.now()
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    # set parameters
    global CLUSTER_NUM
    global MAX_KTH
    global FILTER_TIME_S
    global FILTER_TIME_E
    global OUTPUT_MAP
    global OUTPUT_PATTERN
    if len(argv) > 0:
        CLUSTER_NUM = argv[0]
        MAX_KTH = argv[1]
        FILTER_TIME_S = argv[3]
        FILTER_TIME_E = argv[4]
        LOCATION_TOPIC = "./data/LocationTopic/LocationTopic_OCT_c35.txt"
    else:
        LOCATION_TOPIC = "./data/LocationTopic/LocationTopic_NOVDEC_c35.txt"

    OUTPUT_MAP = OUTPUT_MAP + str(CLUSTER_NUM) + "k" + str(MAX_KTH)
    OUTPUT_PATTERN = OUTPUT_PATTERN + str(CLUSTER_NUM) + "k" + str(MAX_KTH)

    # Getting data
    users, locations = locationclustering.main(FILTER_TIME_S, FILTER_TIME_E)
    location_id, doc_topic = ccluster.open_doc_topic(LOCATION_TOPIC)
    semantic_cluster = numpy.argmax(doc_topic, axis = 1)
    locations = ccluster.fit_locations_cluster(locations, semantic_cluster, location_id, "semantic_cluster")
    print("  users # :", len(users))

    # Getting sequences cluster
    #sequences = ctrajectory.split_trajectory([a_user.posts for a_user in users.values() if len(a_user.posts) != 0], SPLIT_DAY)
    sequences = ctrajectory.split_trajectory_byday([a_user.posts for a_user in users.values() if len(a_user.posts) != 0])
    sequences = ctrajectory.remove_adjacent_location(sequences)

    #sequences = get_specific(sequences) 

    sequences = ctrajectory.remove_short(sequences)
    print("  remain users #:", len(set([x[0].uid for x in sequences])))

    location_sequences, longest_len = ctrajectory.convertto_location_sequences(sequences, locations)
    spatial_sequences, semantic_sequences = ctrajectory.get_cluster_array(location_sequences, longest_len, "cluster", "semantic_cluster")

    u, u0, d, jm, p, fpc, center, membership = cfuzzy.sequences_clustering_i("Cluster", spatial_sequences, CLUSTER_NUM, MAX_KTH, semantic_sequences, GPS_WEIGHT, e = ERROR, algorithm="2WeightedDistance")

    
    #ouput_pattern(sequences, location_sequences, u, membership)
    output_each_pattern(sequences, location_sequences, u, membership, 20)
    #ctrajectory.output_clusters(sequences, membership, u, OUTPUT_PATTERN)
    
    """
    ll = count(sequences, location_sequences, u, membership, 40)
    tag = from_to(location_sequences, membership, 40, [ll[0], ll[1], ll[2]])
    tag.extend(from_to(location_sequences, membership, 40, [ll[1], ll[0], ll[2]]))
    tag.extend(from_to(location_sequences, membership, 40, [ll[0], ll[0]]))
    tag.extend(from_to(location_sequences, membership, 40, [ll[1], ll[1]]))
    tag.extend(from_to(location_sequences, membership, 40, [ll[1], ll[2], ll[0]]))
    tag.extend(from_to(location_sequences, membership, 40, [ll[2], ll[1]]))
    f = open("./data/Result/Ana_40.txt", "a")
    f.write("\naboves:" + str(len(set(tag))))
    f.close()
    """

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()), ", SPEND:", datetime.datetime.now() - start_time)
    print("--------------------------------------")
    return location_sequences, spatial_sequences, semantic_sequences, u

if __name__ == '__main__':
    main(*sys.argv[1:])
