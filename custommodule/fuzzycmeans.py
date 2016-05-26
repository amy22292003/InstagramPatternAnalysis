import datetime
import itertools
import lda
import numpy
import skfuzzy
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer
import custommodule.customskfuzzy as cskfuzzy
import custommodule.location as clocation

def get_tag_vector(corpus):
    print("[fuzzy c means] getting tag vector...")
    vectorizer = CountVectorizer()
    vector = vectorizer.fit_transform(corpus) # location # x tags #
    feature_name =vectorizer.get_feature_names() # tags #
    print("-- vector shape:", vector.shape)
    return vector.toarray(), feature_name

def get_tfidf(corpus):
    transformer = TfidfTransformer()
    vector, feature_name = get_tag_vector(corpus)
    print("vector:", vector.shape)
    tfidf = transformer.fit_transform(vector)
    return tfidf.toarray(), feature_name

"""LDA"""
def fit_lda(corpus, tag_name, topic_num):
    print("[fuzzy c means] LDA")
    model = lda.LDA(n_topics = topic_num, n_iter = 1000)
    model.fit(corpus)
    topic_word = model.topic_word_
    doc_topic = model.doc_topic_
    print("--loglikelihood:", model.loglikelihood())
    print("--")
    for i, topic_dist in enumerate(topic_word):
        topic_words = numpy.array(tag_name)[numpy.argsort(topic_dist)][:-(10+1):-1] # show the top 10 words in each topic
        print('  Topic {}: {}'.format(i, ' '.join(topic_words)))
    return topic_word, doc_topic

"""Location Clustering"""
def cmeans_ori(array, cluster_num):
    cntr, u, u0, d, jm, p, fpc = skfuzzy.cluster.cmeans(array, cluster_num, 2, error=0.01, maxiter=100, init=None)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr, u, u0, d, jm, p, fpc, cluster_membership

# w = the weight of gps side
def cmeans_comb(coordinate, tag_feature, cluster_num, w = 0.4, e = 0.01):
    print("[fuzzy c means] - gps + relation")
    cntr1, cntr2, u, u0, d1, d2, d, jm, p, fpc = cskfuzzy.cluster.cmeans(coordinate, tag_feature, cluster_num, w, 2, error=e, maxiter=100)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr1, cntr2, u, u0, d1, d2, d, jm, p, fpc, cluster_membership

def cmeans_intersect(coordinate, similarity, cluster_num, *para, w = 0.4, e = 0.01, algorithm="Original"):
    print("[fuzzy c means] - gps + relation")
    cntr1, u, u0, d1, d2, d, jm, p, fpc = cskfuzzy.cluster.cmeans_intersect(coordinate, similarity, cluster_num, w, 2, e, 100, algorithm, *para)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr1, u, u0, d1, d2, d, jm, p, fpc, cluster_membership

def cmeans_coordinate(coordinate, cluster_num, *para, e = 0.01, algorithm="Original"):
    print("[fuzzy c means] - gps")
    cntr, u, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_coordinate(coordinate, cluster_num, 2, e, 100, algorithm, *para)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr, u, u0, d, jm, p, fpc, cluster_membership

"""Sequence Clustering"""
def _get_init_u(distance, cluster_num, k, *para):
    if para:
        distance2 = para[0]
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

def _get_distance(level, sequences):
    print("-- Get sequences distance >>")
    # Set distance function of the clustering level (location or cluster)
    distance_func = None
    if level is "Location":
        distance_func = cskfuzzy.cluster.sequence_distance
    elif level is "Cluster":
        distance_func = lambda s1, s2:1 - cskfuzzy.cluster.longest_common_sequence(s1, s2)
    else:
        print("Error, nonexistent clustering level:", type)
        sys.exit()

    # get sequence distances
    distance = numpy.zeros((len(sequences), len(sequences)))
    for i, s1 in enumerate(sequences):
        if i % 100 == 0:
            print("  sequence#", i, "\t", datetime.datetime.now())
        for j, s2 in enumerate(sequences):
            if i < j:
                distance[i, j] = distance_func(s1, s2)
            else:
                distance[i, j] = distance[j, i]
    print("-- distance:", distance[0:4, 0:4])
    print("-- distance max:", numpy.amax(distance), numpy.mean(distance), numpy.std(distance))
    return distance

def sequences_clustering(level, sequences, cluster_num, *para, e = 0.001, algorithm = "Original"):
    print("[fuzzy c means] Sequence Clustering - level:", level)
    print("--data:")
    distance = _get_distance(level, sequences)
    k = para[0]
    if algorithm is "Original":
        # get init
        u = _get_init_u(distance, cluster_num, para[0])
        du, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_nocenter(distance, cluster_num, 2, e, 100, algorithm, k, init = u)
    else:
        # get distance of semantic sequences
        print("--data 2:")
        distance2 = _get_distance(level, para[1])
        # get init
        u = _get_init_u(distance * distance2, cluster_num, para[0])
        if algorithm is "2Distance":
            u, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_nocenter(distance, cluster_num, 2, e, 100, algorithm, k, distance2, init = u) 
        else:   
            u, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_nocenter(distance, cluster_num, 2, e, 100, algorithm, k, distance2, para[2], init = u)
    
    print("-- looping time:", p)
    cluster_membership = numpy.argmax(u, axis=0)
    return u, u0, d, jm, p, fpc, cluster_membership, distance