import lda
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer

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
        topic_words = np.array(tag_name)[np.argsort(topic_dist)][:-(10+1):-1] # show the top 10 words in each topic
        print('  Topic {}: {}'.format(i, ' '.join(topic_words)))
    return topic_word, doc_topic