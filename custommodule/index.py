from collections import deque
import numpy as np
import math
import random
import custommodule.customskfuzzy as cskfuzzy

"""parameters"""
RAND_SEED_K = 0

def _total_compactness(u):
    print("u.shape:", u.shape)
    sqrt_sum = (u ** 2).sum(axis=1)
    print("sq:", sqrt_sum.shape, sqrt_sum)
    um = max(sqrt_sum)
    compactness = sum(sqrt_sum / um)
    print("um:", um)
    print((sqrt_sum / um).shape)
    print(sqrt_sum / um)
    print("com:", compactness)
    return compactness

def _total_separation(d):
    ctr_dist = (d ** 2).sum(axis=1) / d.shape[0] # replace to_center distance with avg distance for each cluster
    beta = ctr_dist.sum() / d.shape[0]
    
    each_cluster = lambda row: math.exp(- sorted(row ** 2)[1] / beta)
    print("sort:", sorted(d[0,:] ** 2))
    print("sort2:", sorted(d[1,:] ** 2))
    separation = np.apply_along_axis(each_cluster, axis=1, arr=d)
    print("separa:", separation)
    return separation.sum()

def _center(level, u, k, seed=RAND_SEED_K):
    # get large k indices for each cluster
    filter_k = lambda row:row >= sorted(row, reverse=True)[k - 1] # get the indices which fit the condition
    large_k = np.apply_along_axis(filter_k, axis=1, arr=u)

    large_k_indices = deque()
    random.seed(seed)
    for i in range(u.shape[0]):
        indices = list(np.nonzero(large_k[i, :])[0])
        if len(indices) > k:
            rand_k = random.sample(indices, k)
            large_k_indices.extend(rand_k)
        else:
            large_k_indices.extend(indices)
    print("-- unique center #:", len(set(large_k_indices)))
    print("-- center:", large_k_indices)
    return large_k_indices

def _cluster_dist(level, c, k, w, data1, data2, center):
    print("[index] Getting cluster distances")
    d1 = _distance(level, c, k, data1, center)
    d2 = _distance(level, c, k, data2, center)
    d = w * d1 + (1 - w) * d2
    print("d:", d.shape, d[0:3, 0:3])
    return d

def _distance(level, c, k, data, center):
    center_data = np.array(data)[center]
    distance = cskfuzzy.cluster.distance.get_distance(level, center_data)
    distance = distance / np.amax(distance)

    each_cluster = np.zeros((c, c))
    np.fill_diagonal(each_cluster, 1)
    each_cluster = np.repeat(each_cluster, k, axis = 1)
    d = each_cluster.dot(distance)
    d = d.dot(each_cluster.transpose()) / (k * k)
    print("d1-2:", d.shape, "\n", d[0:5,0:5])
    np.fill_diagonal(d, 0)
    print(d[0:5,0:5])
    return d

def pcaes(level, u, k, w, data1, data2):
    print("[Index] PCAES -->")
    compactness = _total_compactness(u)
    
    center = _center(level, u, k)
    d = _cluster_dist(level, u.shape[0], k, w, data1, data2, center)
    separation = _total_separation(d)
    result = compactness - separation
    print("-- compactness:", compactness, ", separation:", separation)
    print("-- PCAES:", result)
    return pcaes