import numpy
import math
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
        return _dynamic_programming(s1, s2, len(s1) - 1, len(s2) - 1)
    else:
        return _dynamic_programming(s2, s1, len(s2) - 1, len(s1) - 1)