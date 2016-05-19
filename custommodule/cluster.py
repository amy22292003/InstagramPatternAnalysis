import itertools
import numpy
import os
import re
import custommodule.location as clocation
import custommodule.tag as ctag

"""file path"""
CLUSTERS = "./data/LocationCluster/LocationCluster.txt"
TAG_TOPICS = "./data/LocationCluster/TagTopic.txt"

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

""" output """
def output_location_cluster(location_list, cluster_key, output_file):
    sorted_locations = sorted(location_list, key=lambda x:getattr(x, cluster_key))
    groups = {x:list(y) for x, y in itertools.groupby(sorted_locations, lambda x:getattr(x, cluster_key))}

    clocation.output_location_list([], "w", output_file)
    # for each cluster
    for c, a_group in groups.items():
        phase_ste = "Cluster:" + str(c) + "\t#:" + str(len(a_group)) + "\n"
        clocation.output_location_list(a_group, "a", output_file, phase_ste)

def output_tag_topic(topic_word, tag_name, file_path = TAG_TOPICS):
    print("[cluster] Outputting tag topic...")
    f = open(file_path, "w")
    for a_tag in tag_name:
        f.write("\t" + a_tag)
    f.write("\n")
    for i, topic_dist in enumerate(topic_word):
        f.write(str(i) + ">")
        for x in topic_dist:
            f.write("\t" + str(x))
        f.write("\n")
    f.close()