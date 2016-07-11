import datetime
from decimal import *
import math
import numpy
from numba import jit
#from scipy.spatial.distance import cdist

"""
@jit
def _dist(u, v):
    dist = 0
    for k in range(u.shape[1]):
        dist += (u[0, k] - v[0, k]) ** 2
    return math.sqrt(dist) #math.sqrt(((u - v) * (u - v)).sum())

@jit
def _similarity(u, v):
    similarity = 0
    u_norm = 0
    v_norm = 0
    for k in range(u.shape[1]):
        similarity += u[0, k] * v[0, k]
        u_norm += u[0, k] ** 2
        v_norm += v[0, k] ** 2
    return similarity / (math.sqrt(u_norm) * math.sqrt(v_norm))
"""

# pay attention to precision errors of float
@jit
def _dynamic_programming(w, u_1, u_2, v_1, v_2, len_u, len_v):
    ml = numpy.zeros((len_u + 1, len_v + 1))
    for i in range(1, len_u + 1):
        for j in range(i, len_v + 1):
            sim_1 = sim_2 = u_norm_1 = u_norm_2 = v_norm_1 = v_norm_2 = 0.0
            for k in range(u_1.shape[1]):
                sim_1 += u_1[i - 1, k] * v_1[j - 1, k]
                sim_2 += u_2[i - 1, k] * v_2[j - 1, k]
                u_norm_1 += u_1[i - 1, k] ** 2
                u_norm_2 += u_2[i - 1, k] ** 2
                v_norm_1 += v_1[j - 1, k] ** 2
                v_norm_2 += v_2[j - 1, k] ** 2
            sim_1 = sim_1 / (math.sqrt(u_norm_1) * math.sqrt(v_norm_1))
            sim_2 = sim_2 / (math.sqrt(u_norm_2) * math.sqrt(v_norm_2))
            sim = w * sim_1 + (1 - w) * sim_2
            ml[i, j] = round(max(ml[i - 1, j - 1] + sim, ml[i, j - 1]), 12)
    return ml[len_u, len_v]

def _sequence_distance(u_1, u_2, v_1, v_2, w):
    len_u = len(u_1) - int(numpy.isnan(u_1[:,0]).sum())
    len_v = len(v_1) - int(numpy.isnan(v_1[:,0]).sum())
    if len_u > len_v:
        d = 1 - _dynamic_programming(w, v_1, v_2, u_1, u_2, len_v, len_u) / float(len_u)
    else:
        d = 1 - _dynamic_programming(w, u_1, u_2, v_1, v_2, len_u, len_v) / float(len_v)
    return d

@jit
def _lcs_length(w, u_1, u_2, v_1, v_2):
    ml = numpy.zeros([len(u_1) + 1, len(v_1) + 1])
    for i in range(1, len(u_1) + 1):
        for j in range(1, len(v_1) + 1):
            if s1[i - 1] == s2[j - 1]:
                ml[i, j] = ml[i - 1, j - 1] + 1
            else:
                ml[i, j] = max(ml[i - 1, j], ml[i, j - 1])
    return ml[len(s1), len(s2)]

@jit
def _edit_distance(u_1, u_2, v_1, v_2, len_u, len_v):
    ml = numpy.zeros((len_u + 1, len_v + 1))
    ml[0, :] = list(numpy.array(range(len_v + 1)) ** 2)
    ml[:, 0] = list(numpy.array(range(len_u + 1)) ** 2)
    for i in range(1, len_u + 1):
        for j in range(1, len_v + 1):
            dij = 2 - ((u_1[i - 1] == v_1[j - 1]) + (u_2[i - 1] == v_2[j - 1]))
            ml[i, j] = min(ml[i - 1, j] + 2, ml[i, j - 1] + 2, ml[i - 1, j - 1] + dij)
    return ml[len_u, len_v]

def _cluster_sequence_distance(u_1, u_2, v_1, v_2, w):
    #len_u = len(u_1) - int(numpy.isnan(u_1).sum())
    #len_v = len(v_1) - int(numpy.isnan(v_1).sum())
    len_u = len(u_1)
    len_v = len(v_1)
    d = _edit_distance(u_1, u_2, v_1, v_2, len_u, len_v) / (2 * max(len_u, len_v))
    return d


"""
def _lcs(ml, s1, s2, i, j):
    if i == 0 or j == 0:
        return set()
    elif s1[i - 1] == s2[j - 1]:
        return set([sub_s + s1[i - 1] for sub_s in _lcs(ml, s1, s2, i - 1, j - 1)])
    else:
        if ml[i, j - 1] > ml[i - 1, j]:
            return _lcs(ml, s1, s2, i, j - 1)
        elif ml[i - 1, j] > ml[i, j - 1]:
            return _lcs(ml, s1, s2, i - 1, j)
        else:
            return _lcs(ml, s1, s2, i, j - 1) | _lcs(ml, s1, s2, i - 1, j)
"""

"""
def get_target_distance(level, targets, sequences):
    # Set distance function of the clustering level (location or cluster)
    start_t = datetime.datetime.now()
    if level is "Location":
        distance_func = _sequence_distance_target
    elif level is "Cluster":
        distance_func = 1 - _longest_common_sequence_target
    else:
        print("Error, nonexistent clustering level:", level)
        sys.exit()
    distance = distance_func(targets, sequences)
    print("   [distance] max/min/mean/std:", distance.shape, numpy.amax(distance), numpy.amin(distance), numpy.mean(distance), numpy.std(distance))
    print("   [distance] ", datetime.datetime.now(), ">> spend:", datetime.datetime.now() - start_t)
    return distance
"""

def get_distance(level, w, sequences_1, sequences_2, targets_1 = None, targets_2 = None):
    # Set distance function of the clustering level (location or cluster)
    start_t = datetime.datetime.now()
    if level is "Location":
        distance_func = _sequence_distance
    elif level is "Cluster":
        #distance_func = _longest_common_sequence
        distance_func = _cluster_sequence_distance
    else:
        print("Error, nonexistent clustering level:", level)
        sys.exit()

    # get sequence distances
    if targets_1 is not None:
        distance = numpy.zeros((len(targets_1), len(sequences_1)))
        for i in range(len(targets_1)):
            for j in range(len(sequences_1)):
                d = distance_func(targets_1[i], targets_2[i], sequences_1[j], sequences_2[j], w)
                distance[i, j] = d
    else:
        distance = numpy.zeros((len(sequences_1), len(sequences_1)))
        for i in range(len(sequences_1)):
            if i % 100 == 0:
                print("  sequence#", i, "\t", datetime.datetime.now())
            for j in range(len(sequences_1)):
                if i < j:
                    d = distance_func(sequences_1[i], sequences_2[i], sequences_1[j], sequences_2[j], w)
                    distance[i, j] = d
                else:
                    distance[i, j] = distance[j, i]
    print("   [distance] max/min/mean/std:", distance.shape, numpy.amax(distance), numpy.amin(distance), numpy.mean(distance), numpy.std(distance))
    print("   [distance] ", datetime.datetime.now(), ">> spend:", datetime.datetime.now() - start_t)
    return distance