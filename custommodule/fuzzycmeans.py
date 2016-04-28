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
    print("-fuzzy c means - gps + relation")
    cntr1, cntr2, u, u0, d1, d2, d, jm, p, fpc = cskfuzzy.cluster.cmeans(coordinate, tag_feature, cluster_num, w, 2, error=e, maxiter=100000)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr1, cntr2, u, u0, d1, d2, d, jm, p, fpc, cluster_membership

def cmeans_intersect(coordinate, similarity, cluster_num, *para, w = 0.4, e = 0.01, algorithm="Original"):
    print("-fuzzy c means - gps + relation")
    cntr1, u, u0, d1, d2, d, jm, p, fpc = cskfuzzy.cluster.cmeans_intersect(coordinate, similarity, cluster_num, w, 2, e, 10000, algorithm, *para)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr1, u, u0, d1, d2, d, jm, p, fpc, cluster_membership

def cmeans_coordinate(coordinate, cluster_num, *para, e = 0.01, algorithm="Original"):
    print("-fuzzy c means - gps")
    cntr, u, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_coordinate(coordinate, cluster_num, 2, e, 5000, algorithm, *para)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr, u, u0, d, jm, p, fpc, cluster_membership

"""Sequence Clustering"""
def sequences_clustering_location(sequences, cluster_num, *para, e = 0.01, algorithm="Original"):
    print("[fuzzy c means] - no center.")
    distance = numpy.zeros((len(sequences), len(sequences)))
    for i, s1 in enumerate(sequences):
        if i % 10 == 0:
            print("  getting sequence distance, sequence#", i)
        for j, s2 in enumerate(sequences):
            if i < j:
                distance[i, j] = cskfuzzy.cluster.sequence_distance(s1, s2)
            else:
                # for i >= j
                distance[i, j] = distance[j, i]
    print("--distance:", distance[0:4, 0:4])

    u, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_nocenter(distance, cluster_num, 2, e, 5000, algorithm, *para)
    print("--looping time:", p)
    cluster_membership = numpy.argmax(u, axis=0)
    return u, u0, d, jm, p, fpc, cluster_membership

""" output """
def output_location_cluster(location_list, cluster_key, output_file):
    sorted_locations = sorted(location_list, key=lambda x:getattr(x, cluster_key))
    groups = {x:list(y) for x, y in itertools.groupby(sorted_locations, lambda x:getattr(x, cluster_key))}

    clocation.output_location_list([], "w", output_file)
    # for each cluster
    for c, a_group in groups.items():
        phase_ste = "Cluster:" + str(c) + "\t#:" + str(len(a_group)) + "\n"
        clocation.output_location_list(a_group, "a", output_file, phase_ste)
