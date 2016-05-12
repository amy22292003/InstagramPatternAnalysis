import itertools
import os
import re
import custommodule.location as clocation

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

""" output """
def output_location_cluster(location_list, cluster_key, output_file):
    sorted_locations = sorted(location_list, key=lambda x:getattr(x, cluster_key))
    groups = {x:list(y) for x, y in itertools.groupby(sorted_locations, lambda x:getattr(x, cluster_key))}

    clocation.output_location_list([], "w", output_file)
    # for each cluster
    for c, a_group in groups.items():
        phase_ste = "Cluster:" + str(c) + "\t#:" + str(len(a_group)) + "\n"
        clocation.output_location_list(a_group, "a", output_file, phase_ste)