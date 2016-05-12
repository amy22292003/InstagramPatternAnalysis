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

import Liu.custommodule.cpygmaps as cpygmaps
import Liu.custommodule.fuzzycmeans as cfuzzy
import Liu.custommodule.location as clocation
import Liu.custommodule.user as cuser

"""parameters"""
CLUSTER_NUM = 30
WEIGHT = 0.4
MAX_KTH = 30
ERROR = 0.0001
#CATEGORY_MIN_AMOUNT = 5
#INTERSECT_THRESHOLD = 0.1 # the min intersection tags count% between the category locations and the candidate location

"""file path"""
USER_POSTS_FILE = "./data/TravelerPosts"
OUTPUT_MAP = "./data/Summary/LocationMapN_lf_" + str(CLUSTER_NUM) +\
    "k" + str(MAX_KTH) + "w" + str(WEIGHT) + "e" + str(ERROR) + ".html"
OUTPUT_CLUSTER = "./data/Summary/LocationClusterN_lf_" + str(CLUSTER_NUM) +\
    "k" + str(MAX_KTH) + "w" + str(WEIGHT) + "e" + str(ERROR) + ".txt"


def set_location_tags(locations):
    for key in locations.keys():
        tags = set(x for a_post in locations[key].posts for x in a_post.tags)
        setattr(locations[key], "tags", tags)

def set_location_user_count(locations):
    for key in locations.keys():
        users = set(a_post.uid for a_post in locations[key].posts)
        setattr(locations[key], "usercount", len(users))

def get_tag_intersection(location_list):
    # output a square array(28xx * 28xx), x[i,j] : for location j, the propotion of the intersection with location i
    # x[i,j] != x[j,i] !!!
    print("Getting tags intersection...")
    intersection = numpy.zeros((len(location_list), len(location_list)))
    for i, i_location in enumerate(location_list):
        if i % 100 == 0:
            print("  lopping, locations#", i)
        for j, j_location in enumerate(location_list):
            try:
                intersection[i,j] = len(i_location.tags & j_location.tags) / len(j_location.tags)
            except:
                intersection[i,j] = 0
    return intersection


def main():
    """end for intersection clustering"""

    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")    
    # getting data
    locations = clocation.get_locations_list()
    users = cuser.get_users_posts_afile(USER_POSTS_FILE)
    locations = clocation.fit_users_to_location(locations, users, "tags", "uid")
    del users
    set_location_tags(locations)
    set_location_user_count(locations)

    coordinate = numpy.array([(float(x.lat), float(x.lng)) for x in locations.values()])
    intersection = get_tag_intersection(locations.values())
    location_frequency = numpy.array([x.usercount for x in locations.values()])
    print("avg location_frequency:", sum(location_frequency) / len(location_frequency), " max:", max(location_frequency), " min:", min(location_frequency))

    print("location 1:", list(locations.values())[0].lname, list(locations.values())[0].lid)
    print("intersection.sum:", intersection.sum(axis=0)[0:6], intersection.sum(axis=1)[0:6])
    print("location_frequency:", location_frequency.shape)
    # original intersect clustering
    #cntr1, u, u0, d1, d2, d, jm, p, fpc, membership = cfuzzy.cmeans_intersect(coordinate.T, intersection, CLUSTER_NUM, w=WEIGHT, e=ERROR)
    
    # intersect clustering with the kth locations in each cluster
    #cntr1, u, u0, d1, d2, d, jm, p, fpc, membership = cfuzzy.cmeans_intersect(coordinate.T, intersection, CLUSTER_NUM,  MAX_KTH, w=WEIGHT, e=ERROR, algorithm="kthCluster")
    
    # intersect clustering with the kth locations in each cluster & location frequency as weight
    cntr1, u, u0, d1, d2, d, jm, p, fpc, membership = cfuzzy.cmeans_intersect(coordinate.T, intersection, CLUSTER_NUM,  MAX_KTH, location_frequency, w=WEIGHT, e=ERROR, algorithm="kthCluster_LocationFrequency")
    
    for i, key in enumerate(locations.keys()):
        setattr(locations[key], "cluster", membership[i])

    cpygmaps.output_clusters([(float(x.lat), float(x.lng), str(x.cluster) + " >> " + x.lname) for x in locations.values()], \
        membership, CLUSTER_NUM, OUTPUT_MAP)

    cfuzzy.output_location_cluster(locations.values(), "cluster", OUTPUT_CLUSTER)


    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

if __name__ == '__main__':
    main()
