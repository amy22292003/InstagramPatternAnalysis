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

"""parameters"""
CLUSTER_NUM = 30
MAX_KTH = 3
GPS_WEIGHT = 0.9



def main():
    start_time = datetime.datetime.now()
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")
    

    # Set c#
    f = open("./data/t.txt", "w")
    for cluster_num in range(20,60,10):
        location_sequences, cluster_trajectories, semantic_trajectories, u = trajectoryclustering.main(cluster_num, MAX_KTH, GPS_WEIGHT)
        pcaes = cindex.pcaes("Cluster", u, MAX_KTH, GPS_WEIGHT, cluster_trajectories, semantic_trajectories)
        f.write("PCAES\t" + str(pcaes) + "\n")






    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()), ", SPEND:", datetime.datetime.now() - start_time)
    print("--------------------------------------")

if __name__ == '__main__':
    main()