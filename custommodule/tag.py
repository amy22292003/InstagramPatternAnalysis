import os
import re
from . import location

"""default file path"""
LOCATION_TAGS_FILE = "./data/LocationTags/"
LOCATION_TAGS_AFILE = "./data/LocationTags.txt"
OUTPUT_TAG_COUNT_FILE = "./data/Summary/TagCount.txt"
OUTPUT_LOCATION_TAGS_AFILE = "./data/LocationTags.txt"

class Tag():
    def __init__(self):
        self.name = ""
        self.count = 0

def get_file_tags(file_path, is_set = True):
    f = open(file_path, "r")
    line = f.readline()
    res = re.match(r"location ID=(?P<lid>\w+)\tlocation Name=(?P<lname>.*?)\n", line)
    lid = res.group("lid")
    lname = res.group("lname")
    post_tags = []
    for line in f:
        tags = set(filter(None, re.split(",", line.rstrip())))
        post_tags.append(tags)
    if is_set:
        return lid, lname, set.union(*post_tags)
    else:
        return lid, lname, post_tags

def get_location_tags(file_path = None):
    location_list = []
    if not file_path:
        file_path = LOCATION_TAGS_FILE
    for root, dirs, files in os.walk(file_path):
        for filename in files:
            lid, lname, tag_set = get_file_tags(os.path.join(root, filename))
            a_location = location.Location()
            a_location.lid = lid
            a_location.lname = lname
            a_location.tags = tag_set
            location_list.append(a_location)
    return location_list

def get_location_tags_afile(file_path = None):
    location_list = []
    if not file_path:
        file_path = LOCATION_TAGS_AFILE
    f = open(file_path, "r")
    for line in f:
        res = re.match(r"location ID=(?P<lid>\w+)\tlocation Name=(?P<lname>.*?)\n", line)
        a_location = location.Location()
        a_location.lid = res.group("lid")
        a_location.lname = res.group("lname")
        line = f.readline()
        a_location.tags = set(filter(None, re.split(",", line.rstrip())))
        location_list.append(a_location)
    return location_list

def output_tag_count(tag_list, output_file = None):
    if not output_file:
        output_file = OUTPUT_TAG_COUNT_FILE
    f = open(output_file, "w")
    for a_tag in tag_list:
        f.write(a_tag.name + "\t" + str(a_tag.count) + "\n")
    f.close()

def output_location_tags_afile(location_list, output_file = None):
    if not output_file:
        output_file = OUTPUT_LOCATION_TAGS_AFILE
    f = open(output_file, "w")
    for a_location in location_list:
        f.write("location ID=" + a_location.lid + "\tlocation Name=" + a_location.lname + "\n")
        for a_tag in a_location.tags:
            f.write("," + a_tag)
        f.write("\n")
    f.close()

