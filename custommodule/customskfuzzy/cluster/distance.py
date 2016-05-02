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
        return _dynamic_programming(s1, s2, len(s1) - 1, len(s2) - 1) / len(s2)
    else:
        return _dynamic_programming(s2, s1, len(s2) - 1, len(s1) - 1) / len(s1)

"""
def lcs(s1, s2):
    md = numpy.empty([len(s2), len(s1)])
 
    """Following steps build L[m+1][n+1] in bottom up fashion
    Note: L[i][j] contains length of LCS of X[0..i-1]
    and Y[0..j-1]"""
    for j in range(len())
    for i in range(m+1):
        for j in range(n+1):
            if i == 0 or j == 0 :
                L[i][j] = 0
            elif X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1]+1
            else:
                L[i][j] = max(L[i-1][j] , L[i][j-1])
 
    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1]
    return L[m][n]
#end of function lcs
"""