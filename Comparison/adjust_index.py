#!/usr/bin/env python3
import datetime
import inspect
import numpy
import os
import re
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
sys.path.append(PACKAGE_PARENT)

import Liu.custommodule.index as cindex
import Liu.TrajectoryClustering.locationlevel as FCM_T
import Liu.TrajectoryClustering.clusterlevel as FCM_C

"""file path"""
CLUSTER_RESULT = "./data/Evaluate/Index_2w_cluster#"
K_RESULT = "./data/Evaluate/Index_2w_k"
W_RESULT = "./data/Evaluate/Index_2w_w"
RESULT = "./data/Evaluate/Index"

"""parameters"""
CLUSTER_NUM = 30
MAX_KTH = 3
GPS_WEIGHT = 0.7
FILTER_TIME_S = 1443672000 #2015/10/01 @ UTC-4 
FILTER_TIME_E = 1446350400 #2015/11/01 @ UTC-4

def output(level, cluster_trajectories, semantic_trajectories, u, k, w, f):
    print("(", u.shape[0], ",", k, ",", w, ")---------------")
    f.write(str(u.shape[0]) + " , " + str(k) + " , " + str(w) + "\t")

    npe = cindex.npe(u)
    print("NPE--\t\t", npe)
    f.write(str(npe) + "\t")

    npc = cindex.npc(u)
    print("NPC--\t\t", npc)
    f.write(str(npc) + "\t")

    xb, up, down = cindex.xb(level, u, k, w, cluster_trajectories, semantic_trajectories)
    print("XB--\t\t", xb, "\t(", up, ",", down, ")")
    f.write(str(xb) + "(" + str(up) + "," + str(down) + ")" + "\n")



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

def decide_cluster(level, tc, cluster):
    for i, cluster_num in enumerate(cluster):
        location_sequences, cluster_trajectories, semantic_trajectories, u = tc(cluster_num, MAX_KTH, GPS_WEIGHT, FILTER_TIME_S, FILTER_TIME_E)
        output_index_it(level, i, cluster_num, cluster_trajectories, semantic_trajectories, u, MAX_KTH, GPS_WEIGHT, CLUSTER_RESULT)

def decide_k(level, tc, k_range):
    for i, k in enumerate(k_range):
        location_sequences, cluster_trajectories, semantic_trajectories, u = tc(CLUSTER_NUM, k, GPS_WEIGHT, FILTER_TIME_S, FILTER_TIME_E)
        output_index_it(level, i, k, cluster_trajectories, semantic_trajectories, u, k, GPS_WEIGHT, K_RESULT)

def decide_w(level, tc, w_range):
    for i, w in enumerate(w_range):
        location_sequences, cluster_trajectories, semantic_trajectories, u = tc(CLUSTER_NUM, MAX_KTH, w, FILTER_TIME_S, FILTER_TIME_E)
        output_index_it(level, i, w, cluster_trajectories, semantic_trajectories, u, MAX_KTH, w, W_RESULT)

def main(*argv):
    start_time = datetime.datetime.now()
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    # the test set
    cluster = list(range(25, 75, 5))
    cluster.extend([80, 100])
    #cluster = [40, 50, 70]
    k_range = list(range(1, 7))
    k_range.extend([8, 10, 20])
    
    #k_range.extend(list(range(10, 25, 5)))
    w_range = [x / 10 for x in range(10, 4, -1)]

    if argv[0] == 'L':
        level = "Location"
        tc = FCM_T.main
    elif argv[0] == 'H':
        level = "Cluster"
        tc = FCM_C.main

    
    file = RESULT + "_" + argv[0] + "_seed" + argv[1] + ".txt"
    f = open(file, "w")
    f.write("#\tNPE\tNPC\tXB\n")
    f.close()
    for c in cluster:
        for k in k_range:
            f = open(file, "a")
            if level == "Location":
                for w in w_range:
                    location_sequences, cluster_trajectories, semantic_trajectories, u = tc(c, k, w, FILTER_TIME_S, FILTER_TIME_E)
                    output(level, cluster_trajectories, semantic_trajectories, u, k, w, f)
            else:
                w = float('nan')
                location_sequences, cluster_trajectories, semantic_trajectories, u = tc(c, k, w, FILTER_TIME_S, FILTER_TIME_E)
                output(level, cluster_trajectories, semantic_trajectories, u, k, w, f)
            f.close()    

    
    """
    if argv[1] == 'c':
        global CLUSTER_RESULT
        CLUSTER_RESULT = CLUSTER_RESULT + "-" + argv[0] + "k"+ str(MAX_KTH) + "w" + str(GPS_WEIGHT) + "_T" + argv[2] + ".txt"
        decide_cluster(level, tc, cluster)

    elif argv[1] == 'k':
        global K_RESULT
        K_RESULT = K_RESULT + "-" + argv[0] + "c"+ str(CLUSTER_NUM) + "w" + str(GPS_WEIGHT) + "_T" + argv[2] + ".txt"
        decide_k(level, tc, k_range)

    elif argv[1] == 'w':
        global W_RESULT
        W_RESULT = W_RESULT + "-" + argv[0] + "c"+ str(CLUSTER_NUM) + "k" + str(MAX_KTH) + "_T" + argv[2] + ".txt"
        decide_w(level, tc, w_range)
    """


    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()), ", SPEND:", datetime.datetime.now() - start_time)
    print("--------------------------------------")

if __name__ == '__main__':
    main(*sys.argv[1:])