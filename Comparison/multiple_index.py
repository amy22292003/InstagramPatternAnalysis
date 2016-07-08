#!/usr/bin/env python3
import datetime
import inspect
import numpy
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
sys.path.append(PACKAGE_PARENT)

import Liu.custommodule.index as cindex
import Liu.TrajectoryClustering.tc_highlevel_tag_weight as trajectoryclusteringh
import Liu.TrajectoryClustering.tc_lowlevel_tag_weight as trajectoryclusteringl

"""file path"""
CLUSTER_RESULT = "./data/Evaluate/Index_cluster#"
K_RESULT = "./data/Evaluate/Index_k"
W_RESULT = "./data/Evaluate/Index_w"
RESULT = "./data/Evaluate/Index"

"""parameters"""
CLUSTER_NUM = 40
MAX_KTH = 3
GPS_WEIGHT = float('nan')
FILTER_TIME_S = 1448337600 #2015/11/24 @ UTC-4 
FILTER_TIME_E = 1448942400 #2015/12/01 @ UTC-4

def output(level, c, k, w, cluster_trajectories, semantic_trajectories, u, f):
    print("[Index] - (c,k,w)= ", c, ",", k, ",", w)
    if level == 'H':
        f.write(str(c) + "," + str(k))
    else:
        f.write(str(c) + "," + str(k) + "," + str(w))

    npe = cindex.npe(u)
    print("NPE--\t\t", npe)
    f.write("\t" + str(npe))

    npc = cindex.npc(u)
    print("NPC--\t\t", npc)
    f.write("\t" + str(npc))

    xb, up, down = cindex.xb(level, u, MAX_KTH, GPS_WEIGHT, cluster_trajectories, semantic_trajectories)
    print("XB--\t\t", xb, "\t(", up, ",", down, ")")
    f.write("\t" + str(xb) + "(" + str(up) + "," + str(down) + ")")

    f.write("\n")

def output_index_it(level, i, para, cluster_trajectories, semantic_trajectories, u, k, w, file):
    if i == 0:
        f = open(file, "w")
        f.write("#\tNPE\tNPC\tXB\tBSC\tRSC\n")
    else:
        f = open(file, "a")
    print("#- ", para, "------------ u.shpae:", u.shape)
    f.write("#- " + str(para) + "\t")

    npe = cindex.npe(u)
    print("NPE--\t\t", npe)
    f.write(str(npe) + "\t")

    npc = cindex.npc(u)
    print("NPC--\t\t", npc)
    f.write(str(npc) + "\t")

    xb, up, down = cindex.xb(level, u, k, w, cluster_trajectories, semantic_trajectories)
    print("XB--\t\t", xb, "\t(", up, ",", down, ")")
    f.write(str(xb) + "(" + str(up) + "," + str(down) + ")" + "\t")

    f.write("\n")
    f.close()

    """
    bsc = cindex.bsc("Cluster", u, MAX_KTH, GPS_WEIGHT, cluster_trajectories, semantic_trajectories)
    print("BSC--\t\t", bsc)
    f.write(str(bsc) + "\t")

    sep, comp = cindex.rsc_c(level, u, MAX_KTH, GPS_WEIGHT, cluster_trajectories, semantic_trajectories)

    return sep, comp
    """

def output_rsc(rsc_n, para_range, file):
    rsc = cindex.rsc(rsc_n[:,0], rsc_n[:,1])
    f = open(file, "a")
    f.write("----RSC--------->\n")
    for i, para in enumerate(para_range):
        f.write("#- " + str(para) + "\t" + str(rsc[i]) + "\n")
    f.close()

def decide_cluster(level, cluster):
    for i, cluster_num in enumerate(cluster):
        location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclusteringh.main(cluster_num, MAX_KTH, GPS_WEIGHT, FILTER_TIME_S, FILTER_TIME_E)
        output_index_it(level, i, cluster_num, cluster_trajectories, semantic_trajectories, u, MAX_KTH, GPS_WEIGHT, CLUSTER_RESULT)

def decide_k(level, k_range):
    for i, k in enumerate(k_range):
        location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclusteringh.main(CLUSTER_NUM, k, GPS_WEIGHT, FILTER_TIME_S, FILTER_TIME_E)
        output_index_it(level, i, k, cluster_trajectories, semantic_trajectories, u, k, GPS_WEIGHT, K_RESULT)

def decide_w(level, w_range):
    for i, w in enumerate(w_range):
        location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclusteringh.main(CLUSTER_NUM, MAX_KTH, w, FILTER_TIME_S, FILTER_TIME_E)
        output_index_it(level, i, w, cluster_trajectories, semantic_trajectories, u, MAX_KTH, w, W_RESULT)

def main(*argv):
    start_time = datetime.datetime.now()
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    # the test set
    cluster = list(range(15, 65, 5))
    k_range = list(range(1, 6))
    k_range.extend(list(range(7, 12, 2)))
    #k_range.extend(list(range(10, 25, 5)))
    w_range = [x / 10 for x in range(10, 0, -1)]

    """
    file = RESULT + "_seed" + argv[1] + ".txt"
    f = open(file, "w")
    f.write("#\tNPE\tNPC\tXB\n")
    f.close()

    if argv[0] == 'L':
        for c in cluster:
            for k in k_range:
                f = open(file, "a")
                for w in w_range:
                    location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclusteringh.main(c, k, w, FILTER_TIME_S, FILTER_TIME_E)
                    output("Location", c, k, w, cluster_trajectories, semantic_trajectories, u, f)
                f.close()

    if argv[0] == 'H':
        for c in cluster:
            for k in k_range:
                w = float('nan')
                ocation_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclusteringh.main(c, k, float('nan'), FILTER_TIME_S, FILTER_TIME_E)
                f = open(file, "a")
                output("Cluster", c, k, w, cluster_trajectories, semantic_trajectories, u, f)
                f.close()

    """

    if argv[0] == 'L':
        level = "Location"
    elif argv[0] == 'H':
        level = "Cluster"

    if argv[1] == 'c':
        global CLUSTER_RESULT
        CLUSTER_RESULT = CLUSTER_RESULT + "-" + argv[0] + "k"+ str(MAX_KTH) + "w" + str(GPS_WEIGHT) + "_T" + argv[2] + ".txt"
        decide_cluster(level, cluster)

    elif argv[1] == 'k':
        global K_RESULT
        K_RESULT = K_RESULT + "-" + argv[0] + "c"+ str(CLUSTER_NUM) + "w" + str(GPS_WEIGHT) + "_T" + argv[2] + ".txt"
        decide_k(level, k_range)

    elif argv[1] == 'w':
        global W_RESULT
        W_RESULT = W_RESULT + "-" + argv[0] + "c"+ str(CLUSTER_NUM) + "k" + str(MAX_KTH) + "_T" + argv[2] + ".txt"
        decide_w(level, w_range)



    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()), ", SPEND:", datetime.datetime.now() - start_time)
    print("--------------------------------------")

if __name__ == '__main__':
    main(*sys.argv[1:])