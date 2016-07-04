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

"""parameters"""
CLUSTER_NUM = 30
MAX_KTH = 3
GPS_WEIGHT = 0.9
FILTER_TIME_S = 1448323200 #2015/11/24 
FILTER_TIME_E = 1448928000 #2015/12/1

def output_index_it(level, i, para, cluster_trajectories, semantic_trajectories, u, file):
    if i == 0:
        f = open(file, "w")
        f.write("#\tNPE\tNPC\tXB\tBSC\tRSC\n")
    else:
        f = open(file, "a")
    print("#- ", para, "------------")
    f.write("#- " + str(para) + "\t")

    npe = cindex.npe(u)
    print("NPE--\t\t", npe)
    f.write(str(npe) + "\t")

    npc = cindex.npc(u)
    print("NPC--\t\t", npc)
    f.write(str(npc) + "\t")

    xb, up, down = cindex.xb(level, u, MAX_KTH, GPS_WEIGHT, cluster_trajectories, semantic_trajectories)
    print("XB--\t\t", xb, "\t(", up, ",", down, ")")
    f.write(str(xb) + "(" + str(up) + "," + str(down) + ")" + "\t")

    """
    bsc = cindex.bsc("Cluster", u, MAX_KTH, GPS_WEIGHT, cluster_trajectories, semantic_trajectories)
    print("BSC--\t\t", bsc)
    f.write(str(bsc) + "\t")
    """

    sep, comp = cindex.rsc_c(level, u, MAX_KTH, GPS_WEIGHT, cluster_trajectories, semantic_trajectories)
    f.write("\n")
    f.close()

    return sep, comp

def output_rsc(rsc_n, para_range, file):
    rsc = cindex.rsc(rsc_n[:,0], rsc_n[:,1])
    f = open(file, "a")
    f.write("----RSC--------->\n")
    for i, para in enumerate(para_range):
        f.write("#- " + str(para) + "\t" + str(rsc[i]) + "\n")
    f.close()

def decide_cluster(level, cluster):
    rsc_n = numpy.zeros((len(cluster), 2))
    for i, cluster_num in enumerate(cluster):
        if level == 'H':
            location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclusteringh.main(cluster_num, MAX_KTH, GPS_WEIGHT, FILTER_TIME_S, FILTER_TIME_E)
            sep, comp = output_index_it("Cluster", i, cluster_num, cluster_trajectories, semantic_trajectories, u, CLUSTER_RESULT)
        elif level == 'L':
            location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclusteringl.main(cluster_num, MAX_KTH, GPS_WEIGHT, FILTER_TIME_S, FILTER_TIME_E)
            sep, comp = output_index_it("Location", i, cluster_num, cluster_trajectories, semantic_trajectories, u, CLUSTER_RESULT)
        else:
            print("[ERROR] no such level")
            return 1
        rsc_n[i, 0] = sep
        rsc_n[i, 1] = comp
    output_rsc(rsc_n, cluster, CLUSTER_RESULT)
    return 0

def decide_k(level, k_range):
    rsc_n = numpy.zeros((len(k_range), 2))
    for i, k in enumerate(k_range):
        if level == 'H':
            location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclusteringh.main(CLUSTER_NUM, k, GPS_WEIGHT, FILTER_TIME_S, FILTER_TIME_E)
            sep, comp = output_index_it("Cluster", i, k, cluster_trajectories, semantic_trajectories, u, K_RESULT)
        elif level == 'L':
            location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclusteringl.main(CLUSTER_NUM, k, GPS_WEIGHT, FILTER_TIME_S, FILTER_TIME_E)
            sep, comp = output_index_it("Location", i, k, cluster_trajectories, semantic_trajectories, u, K_RESULT)
        else:
            print("[ERROR] no such level")
            return 1
        rsc_n[i, 0] = sep
        rsc_n[i, 1] = comp
    output_rsc(rsc_n, k_range, K_RESULT)
    return 0

def decide_w(level, w_range):
    rsc_n = numpy.zeros((len(w_range), 2))
    for i, w in enumerate(w_range):
        if level == 'H':
            location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclusteringh.main(CLUSTER_NUM, MAX_KTH, w, FILTER_TIME_S, FILTER_TIME_E)
            sep, comp = output_index_it("Cluster", i, w, cluster_trajectories, semantic_trajectories, u, W_RESULT)
        elif level == 'L':
            location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclusteringl.main(CLUSTER_NUM, MAX_KTH, w, FILTER_TIME_S, FILTER_TIME_E)
            sep, comp = output_index_it("Location", i, w, cluster_trajectories, semantic_trajectories, u, W_RESULT)
        else:
            print("[ERROR] no such level")
            return 1
        rsc_n[i, 0] = sep
        rsc_n[i, 1] = comp
    output_rsc(rsc_n, w_range, W_RESULT)
    return 0

def main(*argv):
    start_time = datetime.datetime.now()
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    
    if argv[1] == 'c':
        global CLUSTER_RESULT
        CLUSTER_RESULT = CLUSTER_RESULT + "-" + argv[0] + "_T" + argv[2] + ".txt"
        cluster = list(range(10, 65, 5))
        #cluster.extend([100, 150])
        decide_cluster(argv[0], cluster)

    elif argv[1] == 'k':
        global K_RESULT
        K_RESULT = K_RESULT + "-" + argv[0] + "_T" + argv[2] + ".txt"
        k_range = list(range(1, 10))
        k_range.extend(list(range(10, 20, 5)))
        decide_k(argv[0], k_range)

    elif argv[1] == 'w':
        global W_RESULT
        W_RESULT = W_RESULT + "-" + argv[0] + "_T" + argv[2] + ".txt"
        w_range = [x / 10 for x in range(10, 0, -1)]
        decide_w(argv[0], w_range)

    else:
        print("[ERROR] wrong command!!!! :", argv)

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()), ", SPEND:", datetime.datetime.now() - start_time)
    print("--------------------------------------")

if __name__ == '__main__':
    main(*sys.argv[1:])