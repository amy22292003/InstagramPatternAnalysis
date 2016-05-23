import itertools
import numpy
import os
import re
import custommodule.location as clocation
import custommodule.tag as ctag

"""file path"""
CLUSTERS = "./data/LocationCluster/LocationCluster.txt"
TAG_TOPICS = "./data/LocationCluster/TagTopic.txt"
LOCATION_TOPICS = "./data/LocationCluster/LocationTopic.txt"

class Cluster():
    def __init__(self, index, items = None):
        self.index = index
        try:
            self.items = set(items)
        except:
            self.items = set()

"""Open files"""
def open_cluster_list(file_path = CLUSTERS):
    print("Getting clusters...")
    cluster_list = []
    f = open(file_path, "r")
    f.readline()
    iterator = filter(None, re.split(r"Cluster:(\w+)\t#:\w+\n", f.read()))
    for cluster_index in iterator:
        locations = location.txt_to_locations(next(iterator))
        a_cluster = Cluster(int(cluster_index), set(locations.values()))
        cluster_list.append(a_cluster)
    return cluster_list

def open_tag_topic(file_path = TAG_TOPICS):
    print("[cluster] Opening tag topic, file path:", file_path)
    f = open(file_path, "r")
    tag_name = f.readline().split()
    topic_word = []
    for line in f:
        words = line.split()[1:]
        topic_word.append([float(x) for x in words])
    return tag_name, numpy.array(topic_word)

def open_doc_topic(file_path = LOCATION_TOPICS):
    print("[cluster] Opening location topic, file path:", file_path)
    location_id = []
    doc_topic = []
    f = open(file_path, "r")
    f.readline()
    for line in f:
        words = line.split()
        location_id.append(words[0]) # the first word is the location id
        doc_topic.append([float(x) for x in words[1:]])
    return location_id, numpy.array(doc_topic)

""" output """
def output_location_cluster(location_list, cluster_key, output_file):
    sorted_locations = sorted(location_list, key=lambda x:getattr(x, cluster_key))
    groups = {x:list(y) for x, y in itertools.groupby(sorted_locations, lambda x:getattr(x, cluster_key))}

    clocation.output_location_list([], "w", output_file)
    # for each cluster
    for c, a_group in groups.items():
        phase_ste = "Cluster:" + str(c) + "\t#:" + str(len(a_group)) + "\n"
        clocation.output_location_list(a_group, "a", output_file, phase_ste)

def output_topics(topic_word, doc_topic, tag_name, doc_name, file_path_tag = TAG_TOPICS, file_path_doc = LOCATION_TOPICS):
    print("[cluster] Outputting topic...")
    # output topic_word
    print("-- outputing tag topics...")
    f = open(file_path_tag, "w")
    f.write("topics\\tags")
    for a_tag in tag_name:
        f.write("\t" + a_tag)
    f.write("\n")
    for i, topic_dist in enumerate(topic_word):
        f.write(str(i) + ">")
        for x in topic_dist:
            f.write("\t" + str(x))
        f.write("\n")
    f.close()
    # output doc_topic
    print("-- outputing doc topics...")
    f = open(file_path_doc, "w")
    f.write("docs\\topics")
    for i in range(doc_topic.shape[1]):
        f.write("\t" + str(i))
    f.write("\n")
    for i, topic_dist in enumerate(doc_topic):
        f.write(doc_name[i])
        for x in topic_dist:
            f.write("\t" + str(x))
        f.write("\n")
    f.close()

"""mining"""
def fit_locations_semantic_membership(locations, doc_topic, doc_list, attr = "semantic_mem"):
    print("[cluster] Fitting the semantic membership of locations...")
    print("locations #:", len(locations), "\tdoc x topic shape:", doc_topic.shape)
    for i, doc_id in enumerate(doc_list):
        if doc_id in locations:
            setattr(locations[doc_id], attr, numpy.atleast_2d(doc_topic[i,:]))
    return locations
