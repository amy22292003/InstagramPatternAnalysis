import os
import re
from . import location

"""file path"""
CLUSTERS = "./data/LocationCluster/LocationCluster.txt"

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