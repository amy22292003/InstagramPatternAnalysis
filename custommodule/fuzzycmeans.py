from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer
import numpy
import skfuzzy
import custommodule.customskfuzzy as cskfuzzy

"""parameters"""
#ERROR = 0.0001 #0.01

def get_tfidf(corpus):
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    vector = vectorizer.fit_transform(corpus) # location # x tags #
    feature_name =vectorizer.get_feature_names() # tags #
    tfidf = transformer.fit_transform(vector)
    return tfidf.toarray(), feature_name

def cmeans_ori(array, cluster_num):
    cntr, u, u0, d, jm, p, fpc = skfuzzy.cluster.cmeans(array, cluster_num, 2, error=0.01, maxiter=100000, init=None)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr, u, u0, d, jm, p, fpc, cluster_membership

# w = the weight of gps side
def cmeans_comb(coordinate, tag_relation, cluster_num, w = 0.4, e = 0.01):
    print("-fuzzy c means - gps + relation")
    cntr1, cntr2, u, u0, d1, d2, d, jm, p, fpc = cskfuzzy.cluster.cmeans(coordinate, tag_relation, cluster_num, w, 2, error=e, maxiter=100000)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr1, cntr2, u, u0, d1, d2, d, jm, p, fpc, cluster_membership
