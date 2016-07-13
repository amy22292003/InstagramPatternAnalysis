import datetime
import itertools
import numpy as np
import random
import skfuzzy
import sys
import custommodule.customskfuzzy as cskfuzzy
import custommodule.location as clocation

"""parameters"""
RAND_SEED_K = 0
RAND_SEED_INIT = 0
CLUSTER_DIST_THRESHOLD = 0.95 #H 0.8 #L

"""Location Clustering"""
def cmeans_location(coordinate, cluster_num, *para, e = 0.01, algorithm="Original"):
    print("[fuzzy c means] - gps")
    cntr, u, u0, d, jm, p, fpc = cskfuzzy.cmeans_location(coordinate, cluster_num, 2, e, 200, algorithm, *para)
    cluster_membership = np.argmax(u, axis=0)
    return cntr, u, u0, d, jm, p, fpc, cluster_membership

"""Sequence Clustering"""
def _get_init_u(level, cluster_num, sequences1, sequences2, k, w):
    distance = np.ones((cluster_num, len(sequences1)))

    np.random.seed(RAND_SEED_INIT)
    init = np.random.randint(0, len(sequences1) - 1, 1)
    distance[0,:] = cskfuzzy.get_distance(level, w, sequences1, sequences2, np.array(sequences1)[init], np.array(sequences2)[init])   
    
    random.seed(RAND_SEED_INIT)
    # get far away cluster initial
    for c in range(1, cluster_num):
        far_cluster = list(np.where((distance[0:c, :] >= CLUSTER_DIST_THRESHOLD).all(axis=0))[0])
        far_cluster = list(set(far_cluster) - set(init))
        if len(far_cluster) == 0:
            not_init = list(set(range(len(sequences1))) - set(init))
            far_cluster = sorted(not_init, key = lambda x:distance[0:c, x].sum(axis=0))
            far_cluster = [far_cluster[-1]]
        add_init = random.sample(far_cluster, 1)
        distance[c,:] = cskfuzzy.get_distance(level, w, sequences1, sequences2, np.array(sequences1)[add_init], np.array(sequences2)[add_init])   
        init = np.append(init, add_init)
    print("[fuzzy c means]- get_init_u> \n-- init:", init)

    # get enough k sequences for each cluster
    #u = np.zeros((cluster_num, len(sequences1)))
    filter_k = lambda row:row <= sorted(row)[k - 1]
    large_k_indices = np.apply_along_axis(filter_k, axis=1, arr=distance)
    u = large_k_indices.astype(int)

    random.seed(RAND_SEED_K)
    print("--each cluster initial # before random choose:", u.sum(axis=1))
    for i in range(cluster_num):
        if sum(u[i, :]) > k:
            indices = [i for i, x in enumerate(u[i, :]) if x == 1]
            rand_k = random.sample(indices, k)
            u[i, :] = 0
            u[i, :][rand_k] = 1
    print("--each cluster initial #:", u.sum(axis=1))
    return u

def sequences_clustering_i(level, sequences, cluster_num, *para, e = 0.001, algorithm = "2WeightedDistance"):
    print("[fuzzy c means] Sequence Clustering - level:", level)
    k = para[0]
    sequences2 = para[1]
    w = para[2]

    u = _get_init_u(level, cluster_num, sequences, sequences2, k, w)
    u, u0, d, jm, p, fpc, center = cskfuzzy.cmeans_sequence(sequences, cluster_num, 2, e, 30, algorithm, level, k, sequences2, w, init = u)

    print("-- looping time:", p)
    cluster_membership = np.argmax(u, axis=0)
    return u, u0, d, jm, p, fpc, center, cluster_membership