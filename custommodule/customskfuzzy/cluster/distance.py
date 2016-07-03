import datetime
import math
import numpy
from numba import jit
#from scipy.spatial.distance import cdist

@jit
def _dist(u, v):
    dist = 0
    for k in range(u.shape[1]):
        dist += (u[0, k] - v[0, k]) ** 2
    return math.sqrt(dist) #math.sqrt(((u - v) * (u - v)).sum())

@jit
def _dynamic_programming(s1, s2):
    ml = numpy.ones((len(s1), len(s2)))
    for i in range(len(s1)):
        for j in range(len(s2)):
            if i > j:
                ml[i, j] = float('inf')
            elif i == 0 and j == 0:
                ml[i, j] = _dist(s1[i], s2[j]) #math.sqrt(((s1[i] - s2[j]) * (s1[i] - s2[j])).sum())
            elif i == 0 and j > 0:
                ml[i, j] = min(ml[i, j - 1], _dist(s1[i], s2[j]))
            else:
                ml[i, j] = min(ml[i - 1, j - 1] + _dist(s1[i], s2[j]), ml[i, j - 1])
    return ml[len(s1) - 1, len(s2) - 1]

@jit
def _sequence_distance(s1, s2):
    if len(s1) > len(s2):
        return _dynamic_programming(s2, s1) / len(s1)
    else:
        return _dynamic_programming(s1, s2) / len(s2)

@jit
def _lcs_length(s1, s2):
    ml = numpy.zeros([len(s1) + 1, len(s2) + 1])
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                ml[i, j] = ml[i - 1, j - 1] + 1
            else:
                ml[i, j] = max(ml[i - 1, j], ml[i, j - 1])
    return ml[len(s1), len(s2)]

@jit
def _longest_common_sequence(s1, s2):
    #ml = _lcs_length(s1, s2)
    #lcs_set = _lcs(ml, s1, s2, len(s1), len(s2))
    return 1 - _lcs_length(s1, s2) / max(len(s1), len(s2)) #, lcs_set

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
@jit
def _sequence_distance_target(targets, sequences):
    distance = numpy.zeros((len(targets), len(sequences)))
    for i in range(len(targets)):
        for j in range(len(sequences)):
            # Get target i & sequence j length
            
            #len_i = numpy.where(targets[i,:,:].sum(axis=1) == 0)[0]
            #len_j = numpy.where(sequences[j,:,:].sum(axis=1) == 0)[0]
            #if len(len_i) == 0:
            #    len_i = targets.shape[1]
            #else:
            #    len_i = len_i[0] + 1
            #if len(len_j) == 0:
            #    len_j = sequences.shape[1]
            #else:
            #    len_j = len_j[0] + 1
            
            len_i = len(targets[i])
            len_j = len(sequences[j])
            ml = numpy.ones((min(len_i, len_j), max(len_i, len_j)))
            for x_s in range(min(len_i, len_j)):
                for x_l in range(max(len_i, len_j)):
                    if x_s > x_l:
                        ml[x_s, x_l] = float('inf')
                    else:
                        if len_i <= len_j:
                            ii = x_s
                            jj = x_l
                        else:
                            ii = x_l
                            jj = x_s
                        dist = 0
                        for k in range(targets[i][ii].shape[1]):
                            dist += (targets[i][ii][0,k] - sequences[j][jj][0,k]) ** 2
                        dist = math.sqrt(dist)

                        if x_s == 0 and x_l == 0:
                            ml[x_s, x_l] = dist
                        elif x_s == 0 and x_l > 0:
                            ml[x_s, x_l] = min(ml[x_s, x_l - 1], dist)
                        else:
                            ml[x_s, x_l] = min(ml[x_s - 1, x_l - 1] + dist, ml[x_s, x_l - 1])
            distance[i, j] = ml[x_s, x_l] / max(len_i, len_j)
    return distance
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

def get_distance(level, sequences, targets = None):
    # Set distance function of the clustering level (location or cluster)
    start_t = datetime.datetime.now()
    if level is "Location":
        distance_func = _sequence_distance
    elif level is "Cluster":
        distance_func = _longest_common_sequence
    else:
        print("Error, nonexistent clustering level:", level)
        sys.exit()

    # get sequence distances
    if targets is not None:
        distance = numpy.zeros((len(targets), len(sequences)))
        for i in range(len(targets)):
            for j in range(len(sequences)):
                distance[i,j] = distance_func(targets[i], sequences[j])
    else:
        distance = numpy.zeros((len(sequences), len(sequences)))
        for i, s1 in enumerate(sequences):
            if i % 100 == 0:
                print("  sequence#", i, "\t", datetime.datetime.now())
            for j, s2 in enumerate(sequences):
                if i < j:
                    distance[i, j] = distance_func(s1, s2)
                else:
                    distance[i, j] = distance[j, i]
    print("   [distance] max/min/mean/std:", distance.shape, numpy.amax(distance), numpy.amin(distance), numpy.mean(distance), numpy.std(distance))
    print("   [distance] ", datetime.datetime.now(), ">> spend:", datetime.datetime.now() - start_t)
    return distance