"""
Fuzzy clustering subpackage, containing fuzzy c-means clustering algorithm.
This can be either supervised or unsupervised, depending if U_init kwarg is
used (if guesses are provided, it is supervised).

"""
__all__ = ['cmeans',
           'cmeans_predict',
           'cmeans_intersect',
           'cmeans_location',
           'cmeans_nocenter',
           'cmeans_sequence'
           ]

from ._cmeans import cmeans, cmeans_predict

from ._cmeans_intersect import cmeans as cmeans_intersect

from ._cmeans_location import cmeans as cmeans_location

from ._cmeans_nocenter import cmeans as cmeans_nocenter

from ._cmeans_sequence import cmeans as cmeans_sequence

from .distance import *