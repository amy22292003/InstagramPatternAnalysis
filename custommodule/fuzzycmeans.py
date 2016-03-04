from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer
import numpy
import skfuzzy

def get_tfidf(corpus):
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    vector = vectorizer.fit_transform(corpus) # location # x tags #
    feature_name =vectorizer.get_feature_names() # tags #
    tfidf = transformer.fit_transform(vector)
    return tfidf.toarray(), feature_name

def cmeans(array, cluster_num):
    cntr, u, u0, d, jm, p, fpc = skfuzzy.cluster.cmeans(array, cluster_num, 2, error=0.01, maxiter=100000, init=None)
    cluster_membership = numpy.argmax(u, axis=0)
    return cntr, u, u0, d, jm, p, fpc, cluster_membership
