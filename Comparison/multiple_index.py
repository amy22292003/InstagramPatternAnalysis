#!/usr/bin/env python3
import datetime
import inspect
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
sys.path.append(PACKAGE_PARENT)

import Liu.custommodule.index as cindex
import Liu.TrajectoryClustering.tc_highlevel_tag_weight as trajectoryclustering

"""file path"""
CLUSTER_RESULT = "./data/Index_cluster#"


"""parameters"""
CLUSTER_NUM = 30
MAX_KTH = 3
GPS_WEIGHT = 0.9
FILTER_TIME_S = 1447545600 
FILTER_TIME_E = 1448928000

def main(*argv):
    start_time = datetime.datetime.now()
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")
    
    global CLUSTER_RESULT
    if len(argv) > 0:
        CLUSTER_RESULT = CLUSTER_RESULT + "_T" + argv[0]
    CLUSTER_RESULT = CLUSTER_RESULT + ".txt"

    cluster = list(range(15, 65, 5))

    cluster.extend([100, 150])
    #cluster = [100,200]
    
    for cluster_num in cluster:
        location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclustering.main(cluster_num, MAX_KTH, GPS_WEIGHT, FILTER_TIME_S, FILTER_TIME_E)
        
        if cluster_num == 15:
            f = open(CLUSTER_RESULT, "w")
            f.write("#\tNPE\tNPC\tXB\n")
        else:
            f = open(CLUSTER_RESULT, "a")
        print("#- ", cluster_num, "------------")
        f.write("#- " + str(cluster_num) + "\t")

        npe = cindex.npe(u)
        print("NPE--\t\t", npe)
        f.write(str(npe) + "\t")

        npc = cindex.npc(u)
        print("NPC--\t\t", npc)
        f.write(str(npc) + "\t")

        xb, up, down = cindex.xb("Cluster", u, MAX_KTH, GPS_WEIGHT, cluster_trajectories, semantic_trajectories)
        print("XB--\t\t", xb, "\t(", up, ",", down, ")")
        f.write(str(xb) + "(" + str(up) + "," + str(down) + ")" + "\t")

        bsc = cindex.bsc("Cluster", u, MAX_KTH, GPS_WEIGHT, cluster_trajectories, semantic_trajectories)
        print("BSC--\t\t", bsc)
        f.write(str(bsc) + "\t")

        rsc, comp, sep = cindex.rsc("Cluster", u, MAX_KTH, GPS_WEIGHT, cluster_trajectories, semantic_trajectories)
        print("RSC--\t\t", rsc, "\t(", comp, ",", sep, ")")
        f.write(str(xb) + "(" + str(comp) + "," + str(sep) + ")" + "\t")

        f.write("\n")
        f.close()


    print("Test ", argv[0], " ---output--->", CLUSTER_RESULT)
    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()), ", SPEND:", datetime.datetime.now() - start_time)
    print("--------------------------------------")

if __name__ == '__main__':
    main(*sys.argv[1:])