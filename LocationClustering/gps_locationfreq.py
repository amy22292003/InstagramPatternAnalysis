#!/usr/bin/env python3
"""
    command: 
    output map file to: 
"""
import datetime
import numpy
import os
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

"""parameters"""
FILTER_TIME_S = 1446350400 #2015/11/01 @ UTC-4
FILTER_TIME_E = 1451620800 #2016/01/01 @ UTC-4
CLUSTER_NUM = 30
ERROR = 0.000001
MAX_KTH = 60

"""file path"""
USER_POSTS_FILE = "./data/TravelerPosts"
OUTPUT_MAP = "./data/Result/LocationMap_" + str(CLUSTER_NUM) +\
    "k" + str(MAX_KTH) + "e" + str(ERROR) + ".html"
OUTPUT_REPRESENTATIVES = "./data/Result/LocationRepre_" + str(CLUSTER_NUM) +\
    "k" + str(MAX_KTH) + "e" + str(ERROR) + ".html"
OUTPUT_CLUSTER = "./data/Result/LocationCluster_" + str(CLUSTER_NUM) +\
    "k" + str(MAX_KTH) + "e" + str(ERROR) + ".txt"


def filter_users_timeperiod(users, starttime, endtime):
    removes = []
    for key, a_user in users.items():
        posts = [x for x in a_user.posts if (x.time >= starttime) and (x.time <= endtime)]
        users[key].posts = posts
        if len(posts) == 0:
            removes.append(key)
    return removes

def set_location_user_count(locations):
    for key in locations.keys():
        users = set(a_post.uid for a_post in locations[key].posts)
        setattr(locations[key], "usercount", len(users))

def output_representatives(data, u, k):
    """
    cpygmaps.output_clusters(\
        [(float(x[0]), float(x[1]), "") \
            for x in cntr], range(30), 30, "./data/Result/center" + str(R) + ".html")
    """
    representatives = []
    membership = []
    for i in range(u.shape[0]):
        indices = numpy.where(u[i, :] >= sorted(u[i, :], reverse=True)[k - 1])[0]
        representatives.extend(data[indices, :])
        membership.extend([i] * len(indices))
    cpygmaps.output_clusters([(float(x[0]), float(x[1]), str(mem)) \
        for x, mem in zip(representatives, membership)], membership, u.shape[0], OUTPUT_REPRESENTATIVES)

def main(*argv):
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    # set UNIXTIME
    global FILTER_TIME_S
    global FILTER_TIME_E
    if len(argv) > 0:
        FILTER_TIME_S = argv[0]
        FILTER_TIME_E = argv[1]

    # getting data
    locations = clocation.open_locations()
    users = cuser.open_users_posts_afile(USER_POSTS_FILE)

    # preporcessing. remove unqualified users
    removes = filter_users_timeperiod(users, FILTER_TIME_S, FILTER_TIME_E)
    sequences = ctrajectory.split_trajectory_byday([a_user.posts for a_user in users.values() if len(a_user.posts) != 0])
    sequences = ctrajectory.remove_adjacent_location(sequences)
    sequences = ctrajectory.remove_short(sequences)
    removes = list(set(removes) | (set(users.keys()) - set([x[0].uid for x in sequences])))

    for key in removes:
        del users[key]
    print("  remain users #:", len(users.keys()))

    locations = clocation.fit_users_to_location(locations, users, "uid")
    set_location_user_count(locations)

    coordinate = numpy.array([(float(x.lat), float(x.lng)) for x in locations.values()])
    location_frequency = numpy.array([x.usercount for x in locations.values()])
    
    # clustering locations
    cntr, u, u0, d, jm, p, fpc, membership = cfuzzy.cmeans_location(coordinate.T, CLUSTER_NUM, MAX_KTH, location_frequency, e=ERROR, algorithm="Original")#"kthCluster_LocationFrequency")
    locations = ccluster.fit_locations_membership(locations, u, locations.keys())
    locations = ccluster.fit_locations_cluster(locations, membership, locations.keys())
    
    """
    # output result
    cpygmaps.output_clusters(\
        [(float(x.lat), float(x.lng), str(x.cluster) + " >> " + x.lname + "(" + x.lid + ")>>u:" + str(u[x.cluster, i])) \
            for i, x in enumerate(locations.values())], membership, CLUSTER_NUM, OUTPUT_MAP)
    output_representatives(coordinate, u, MAX_KTH)
    ccluster.output_location_cluster(locations.values(), "cluster", OUTPUT_CLUSTER)
    """

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    return users, locations

if __name__ == '__main__':
    main(*sys.argv[1:])
