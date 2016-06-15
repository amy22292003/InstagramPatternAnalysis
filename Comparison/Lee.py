#!/usr/bin/env python3
from collections import deque
import inspect
import numpy
import os
import sys

PACKAGE_PARENT = '..'
FILE_DIR = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
sys.path.insert(0, os.path.normpath(os.path.join(FILE_DIR, PACKAGE_PARENT)))
sys.path.insert(0, PACKAGE_PARENT)

import Liu.custommodule.customskfuzzy as cskfuzzy

"""parameters"""
EPSILON = 0.01
MINLNS = 50

def _get_neighborhood_2(dist_type, level, lines1, lines2, w, ep):
    print("[Lee] get neighborhood, 2 data.")
    if dist_type is "Mine":
        distance_func = cskfuzzy.cluster.get_distance
    else:
        distance_func = None

    d1 = distance_func(level, lines1)
    d1 = d1 / numpy.amax(d1)
    d2 = distance_func(level, lines2)
    d2 = d2 / numpy.amax(d2)

    d = w * d1 + (1 - w) * d2

    neighborhood = []
    for i in range(len(lines1)):
        i_neighbor = numpy.where(d[i, :] <= ep)
        neighborhood.append(i_neighbor)
    print("--neighborhood:", len(neighborhood), neighborhood[0:5])
    return neighborhood

def _get_neighborhood(dist_type, level, lines, ep):
    print("[Lee] get neighborhood, 1 data only.")
    if dist_type is "Mine":
        distance_func = cskfuzzy.cluster.get_distance
    else:
        distance_func = None

    d = distance_func(level, lines)
    d = d / numpy.amax(d)

    neighborhood = []
    for i in range(len(lines)):
        i_neighbor = numpy.where(d[i, :] <= ep)[0]
        neighborhood.append(i_neighbor)
    print("--neighborhood:", len(neighborhood), neighborhood[0:5])
    print("  n id:", id(neighborhood))
    return neighborhood

# Step 2
def _expand_cluster(q, cluster_id, minlns, neighborhood, noise, cluster_membership):
    print("[Lee] extend q:", len(q), q)
    while len(q) != 0:
        target = q[0]
        neighbors = deque(neighborhood[target])
        if len(neighbors) >= minlns:
            print("  ", target, "-expand cluster:", len(neighbors))
            for index in neighbors:
                if cluster_membership[index] is None:
                    q.append(index)
                if cluster_membership[index] is None or index in noise:
                    cluster_membership[index] = cluster_id
        q.popleft()
    return cluster_membership

def line_segment_clustering(lines, dist_type, level, ep = EPSILON, minlns = MINLNS):
    cluster_id = 0
    cluster_membership = numpy.array([None] * len(lines))
    noise = set()

    #neighborhood = _get_neighborhood_2(dist_type, level, lines1, lines2, w, ep)
    neighborhood = _get_neighborhood(dist_type, level, lines, ep)

    # Step 1
    for i in range(len(lines)):
        if cluster_membership[i] is None:
            neighbors = deque(neighborhood[i])
            if len(neighbors) >= minlns:
                print("----", cluster_id, " - neighbors:", len(neighbors))
                cluster_membership[neighbors] = cluster_id
                neighbors.remove(i)
                cluster_membership = _expand_cluster(neighbors, cluster_id, minlns, neighborhood, noise, cluster_membership)
                cluster_id += 1
            else:
                noise.add(i)

    print("[Lee] cluster #:", cluster_id)
    print("  noise:", len(noise), noise)
    return cluster_id, cluster_membership, noise