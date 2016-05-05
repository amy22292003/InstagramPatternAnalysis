import datetime
import math
import numpy
from scipy.spatial.distance import cdist

# len(s1) > len(s2)
def _dynamic_programming(s1, s2, i, j):
    if i < j:
        return float('inf')
    elif i == 0 & j == 0:
        return cdist(s1[i], s2[j])
    elif i > 0 & j == 0:
        return min(_dynamic_programming(s1, s2, i - 1, j), cdist(s1[i], s2[j]))
    else:
        add_dij = _dynamic_programming(s1, s2, i - 1, j - 1) + cdist(s1[i], s2[j])
        return min(add_dij, _dynamic_programming(s1, s2, i - 1, j))

def sequence_distance(s1, s2):
    if len(s1) >= len(s2):
        return _dynamic_programming(s1, s2, len(s1) - 1, len(s2) - 1) / len(s2)
    else:
        return _dynamic_programming(s2, s1, len(s2) - 1, len(s1) - 1) / len(s1)

def _lcs_length(s1, s2):
    ml = numpy.zeros([len(s1) + 1, len(s2) + 1])
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                ml[i, j] = ml[i - 1, j - 1] + 1
            else:
                ml[i, j] = max(ml[i - 1, j], ml[i, j - 1])
    return ml

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

def longest_common_sequence(s1, s2):
    ml = _lcs_length(s1, s2)
    lcs_set = _lcs(ml, s1, s2, len(s1), len(s2))
    return ml[len(s1), len(s2)], lcs_set # / min(len(s1), len(s2))