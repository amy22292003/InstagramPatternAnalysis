import datetime
import itertools
import numpy
import skfuzzy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer
import custommodule.customskfuzzy as cskfuzzy
import custommodule.location as clocation

"""parameters"""
#ERROR = 0.0001 #0.01

def get_tag_vector(corpus):
    vectorizer = CountVectorizer()
    vector = vectorizer.fit_transform(corpus) # location # x tags #
    feature_name =vectorizer.get_feature_names() # tags #
    return vector.toarray(), feature_name

def get_tfidf(corpus):
    transformer = TfidfTransformer()
    vector, feature_name = get_tag_vector(corpus)
    print("vector:", vector.shape)
    tfidf = transformer.fit_transform(vector)
    return tfidf.toarray(), feature_name

"""Location Clustering"""
def cmeans_ori(array, cluster_num):
    cntr, u, u0, d, jm, p, fpc = skfuzzy.cluster.cmeans(array, cluster_num, 2, error=0.01, maxiter=100000, init=None)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr, u, u0, d, jm, p, fpc, cluster_membership

# w = the weight of gps side
def cmeans_comb(coordinate, tag_feature, cluster_num, w = 0.4, e = 0.01):
    print("[fuzzy c means] - gps + relation")
    cntr1, cntr2, u, u0, d1, d2, d, jm, p, fpc = cskfuzzy.cluster.cmeans(coordinate, tag_feature, cluster_num, w, 2, error=e, maxiter=100000)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr1, cntr2, u, u0, d1, d2, d, jm, p, fpc, cluster_membership

def cmeans_intersect(coordinate, similarity, cluster_num, *para, w = 0.4, e = 0.01, algorithm="Original"):
    print("[fuzzy c means] - gps + relation")
    cntr1, u, u0, d1, d2, d, jm, p, fpc = cskfuzzy.cluster.cmeans_intersect(coordinate, similarity, cluster_num, w, 2, e, 10000, algorithm, *para)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr1, u, u0, d1, d2, d, jm, p, fpc, cluster_membership

def cmeans_coordinate(coordinate, cluster_num, *para, e = 0.01, algorithm="Original"):
    print("[fuzzy c means] - gps")
    cntr, u, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_coordinate(coordinate, cluster_num, 2, e, 5000, algorithm, *para)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr, u, u0, d, jm, p, fpc, cluster_membership

"""Sequence Clustering"""
def _get_init_u(distance, cluster_num, *para):
    k = para[0]
    u = numpy.zeros((cluster_num, distance.shape[0]))
    init = numpy.random.randint(0, distance.shape[0] - 1, cluster_num)
    print("[fuzzy c means]- get_init_u> init:", init)
    for i, center in enumerate(init):
        top_k = sorted(distance[:, center])[k - 1]
        is_top_k = [True if x <= top_k else False for x in distance[:, center]]
        u[i, numpy.array(is_top_k)] = 1
    #u /= numpy.ones((cluster_num, 1)).dot(numpy.atleast_2d(u.sum(axis=0))).astype(numpy.float64)
    print("--each cluster initial #:", u.sum(axis=1))
    return u

def sequences_clustering_location(sequences, cluster_num, *para, e = 0.01, algorithm="Original"):
    print("[fuzzy c means] - no center.")
    distance = numpy.zeros((len(sequences), len(sequences)))
    for i, s1 in enumerate(sequences):
        if i % 100 == 0:
            print("  getting sequence distance, sequence#", i, "\t", datetime.datetime.now())
        for j, s2 in enumerate(sequences):
            if i < j:
                distance[i, j] = cskfuzzy.cluster.sequence_distance(s1, s2)
            else:
                # for i >= j
                distance[i, j] = distance[j, i]
    print("-- distance:", distance[0:4, 0:4], numpy.amax(distance))

    u, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_nocenter(distance, cluster_num, 2, e, 5000, algorithm, *para)
    print("-- looping time:", p)
    cluster_membership = numpy.argmax(u, axis=0)
    return u, u0, d, jm, p, fpc, cluster_membership

def sequences_clustering_cluster(sequences, cluster_num, *para, e = 0.01, algorithm="Original"):
    print("[fuzzy c means] - no center")
    distance = numpy.zeros((len(sequences), len(sequences)))
    for i, s1 in enumerate(sequences):
        if i % 100 == 0:
            print("  getting sequence distance, sequence#", i, "\t", datetime.datetime.now())
        for j, s2 in enumerate(sequences):
            if i < j:
                #distance[i, j] = 1 - cskfuzzy.cluster.longest_common_sequence(s1, s2)
                length = cskfuzzy.cluster.longest_common_sequence(s1, s2)
                distance[i, j] = length 
            else:
                distance[i, j] = distance[j, i]
    distance = numpy.amax(distance) - distance
    print("-- distance:", distance[0:4, 0:4])
    print("-- distance max:", numpy.amax(distance), numpy.mean(distance), numpy.std(distance))
    u = _get_init_u(distance, cluster_num, *para)

    u, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_nocenter(distance, cluster_num, 2, e, 5000, algorithm, *para, init = u)
    print("-- looping time:", p)
    cluster_membership = numpy.argmax(u, axis=0)
    return u, u0, d, jm, p, fpc, cluster_membership