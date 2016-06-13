import datetime
import math
import numpy
from scipy.spatial.distance import cdist

def _dynamic_programming(s1, s2):
    ml = numpy.ones([len(s1), len(s2)])
    for i in range(len(s1)):
        for j in range(len(s2)):
            if i < j:
                ml[i, j] = float('inf')
            elif i == 0 and j == 0:
                ml[i, j] = cdist(s1[i], s2[j])
            elif i > 0 and j == 0:
                ml[i, j] = min(ml[i - 1, j], cdist(s1[i], s2[j]))
            else:
                ml[i, j] = min(ml[i - 1, j - 1] + cdist(s1[i], s2[j]), ml[i - 1, j])
    return ml[len(s1) - 1, len(s2) - 1]

def _sequence_distance(s1, s2):
    if len(s1) >= len(s2):
        return _dynamic_programming(s1, s2) / len(s2)
    else:
        return _dynamic_programming(s2, s1) / len(s1)

def _lcs_length(s1, s2):
    ml = numpy.zeros([len(s1) + 1, len(s2) + 1])
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                ml[i, j] = ml[i - 1, j - 1] + 1
            else:
                ml[i, j] = max(ml[i - 1, j], ml[i, j - 1])
    return ml[len(s1), len(s2)]

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

def _longest_common_sequence(s1, s2):
    #ml = _lcs_length(s1, s2)
    #lcs_set = _lcs(ml, s1, s2, len(s1), len(s2))
    return _lcs_length(s1, s2) / min(len(s1), len(s2)) #, lcs_set 

def get_distance(level, sequences, targets = None):
    # Set distance function of the clustering level (location or cluster)
    start_t = datetime.datetime.now()
    if level is "Location":
        distance_func = _sequence_distance
    elif level is "Cluster":
        distance_func = lambda s1, s2:1 - _longest_common_sequence(s1, s2)
    else:
        print("Error, nonexistent clustering level:", type)
        sys.exit()
    print("sequence id:", id(sequences))
    print("targets id:", id(targets))

    # get sequence distances
    if targets is not None:
        distance = numpy.zeros((len(targets), len(sequences)))
        print("distance id:", id(distance))
        for i, s_t in enumerate(targets):
            for j, s in enumerate(sequences):
                distance[i, j] = distance_func(s_t, s)
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
    #print("-- distance:", distance.shape, distance[0:4, 0:6])
    print("-- [distance] max/min/mean/std:", distance.shape, numpy.amax(distance), numpy.amin(distance), numpy.mean(distance), numpy.std(distance))
    print("distance id b4re:", id(distance))
    print("-- [distance] ", datetime.datetime.now(), ">> spend:", datetime.datetime.now() - start_t)
    return distance