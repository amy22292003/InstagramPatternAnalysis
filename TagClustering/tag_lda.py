#!/usr/bin/env python3
import datetime
import numpy
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
sys.path.append(PACKAGE_PARENT)

import Liu.custommodule.cluster as ccluster
import Liu.custommodule.fuzzycmeans as cfuzzy
import Liu.custommodule.tag as ctag

"""parameters"""
TOPIC_NUM = 10


"""file path"""
USER_POSTS_FILE = "./data/LocationTags"
OUTPUT_TAG_TOPIC = "./data/LocationCluster/TagTopic_c" + str(TOPIC_NUM) + ".txt"
OUTPUT_LOCATION_TOPIC = "./data/LocationCluster/LocationTopic_c" + str(TOPIC_NUM) + ".txt"

def main():
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")
    
    # getting data
    locations = ctag.open_location_tags(USER_POSTS_FILE)

    corpus = ctag.get_corpus([x.tags for x in locations.values()])
    vector, tag_name = cfuzzy.get_tag_vector(corpus)
    topic_word, doc_topic = cfuzzy.fit_lda(vector, tag_name, TOPIC_NUM)
    ccluster.output_topics(topic_word, doc_topic, tag_name, [x.lid for x in locations.values()], OUTPUT_TAG_TOPIC, OUTPUT_LOCATION_TOPIC)

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

if __name__ == '__main__':
    main()
