import datetime
import itertools
import lda
import numpy
import random
import skfuzzy
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer
import custommodule.customskfuzzy as cskfuzzy
import custommodule.location as clocation

"""parameters"""
RAND_SEED_K = 0
RAND_SEED_INIT = 0

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
def _get_init_u(level, cluster_num, k, s_num, *para, distance = None):
    u = numpy.zeros((cluster_num, s_num))
    numpy.random.seed(RAND_SEED_INIT)
    init = numpy.random.randint(0, s_num - 1, cluster_num)
    print("[fuzzy c means]- get_init_u> \n-- init:", init)
    if distance is not None:
        for i, center in enumerate(init):
            top_k = sorted(distance[:, center])[k - 1]
            is_top_k = [True if x <= top_k else False for x in distance[:, center]]
            u[i, numpy.array(is_top_k)] = 1
    else:
        sequences1 = para[0]
        sequences2 = para[1]
        w = para[2]

        init_s1 = numpy.array(sequences1)[init]
        distance1 = cskfuzzy.cluster.get_distance(level, sequences1, init_s1)
        distance1 = numpy.array(distance1) / numpy.amax(distance1)
        
        init_s2 = numpy.array(sequences2)[init]
        distance2 = cskfuzzy.cluster.get_distance(level, sequences2, init_s2)
        distance2 = numpy.array(distance2) / numpy.amax(distance2)
        #print("-- distance1:", distance1.shape, distance1[0:4, 0:5])
        #print("-- distance2:", distance2.shape, distance2[0:4, 0:5])
        
        distance = w * distance1 + (1 - w) * distance2
        filter_k = lambda row:row <= sorted(row)[k - 1]
        large_k_indices = numpy.apply_along_axis(filter_k, axis=1, arr=distance)
        u = large_k_indices.astype(int)

        random.seed(RAND_SEED_K)
        print("--each cluster initial # before random choose:", u.sum(axis=1))
        for i in range(cluster_num):
            if sum(u[i, :]) > k:
                indices = [i for i, x in enumerate(u[i, :]) if x == 1]
                rand_k = random.sample(indices, k)
                u[i, :] = 0
                u[i, :][rand_k] = 1
    print("--each cluster initial #:", u.sum(axis=1))
    return u

def sequences_clustering(level, sequences, cluster_num, *para, e = 0.001, algorithm = "Original"):
    print("[fuzzy c means] Sequence Clustering - level:", level)
    print("--data:")
    distance = cskfuzzy.cluster.get_distance(level, sequences)
    k = para[0]
    if algorithm is "Original":
        # get init
        u = _get_init_u(level, cluster_num, k, distance.shape[0], distance = distance)
        du, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_nocenter(distance, cluster_num, 2, e, 100, algorithm, k, init = u)
    else:
        # get distance of semantic sequences
        print("--data 2:")
        distance2 = cskfuzzy.cluster.get_distance(level, para[1])
        if algorithm is "2Distance":
            # get init
            u = _get_init_u(level, cluster_num, k, distance.shape[0], distance = distance * distance2)
            u, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_nocenter(distance, cluster_num, 2, e, 100, algorithm, k, distance2, init = u) 
        else:
            w = para[2]
            # get init
            u = _get_init_u(level, cluster_num, k, distance.shape[0], distance = w * distance + (1-w) * distance2)
            u, u0, d, jm, p, fpc = cskfuzzy.cluster.cmeans_nocenter(distance, cluster_num, 2, e, 100, algorithm, k, distance2, para[2], init = u)
    
    print("-- looping time:", p)
    cluster_membership = numpy.argmax(u, axis=0)
    return u, u0, d, jm, p, fpc, cluster_membership, distance

def sequences_clustering_i(level, sequences, cluster_num, *para, e = 0.001, algorithm = "2WeightedDistance"):
    print("[fuzzy c means] Sequence Clustering - level:", level)
    k = para[0]
    sequences2 = para[1]
    w = para[2]
    print("!k:", k)

    u = _get_init_u(level, cluster_num, k, len(sequences), sequences, sequences2, w)
    u, u0, d, jm, p, fpc, center = cskfuzzy.cluster.cmeans_nocenter_i(sequences, cluster_num, 2, e, 30, algorithm, level, k, sequences2, w, init = u)

    print("-- looping time:", p)
    cluster_membership = numpy.argmax(u, axis=0)
    return u, u0, d, jm, p, fpc, center, cluster_membership