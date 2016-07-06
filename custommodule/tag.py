import os
import re
import custommodule.location as location

"""default file path"""
LOCATION_TAGS_FOLDER = "./data/LocationTags/"
LOCATION_TAGS_AFILE = "./data/LocationTags.txt"

class Tag():
    def __init__(self):
        self.tag = ""
        self.count = 0

def add_attr_tag(a_object):
    setattr(a_object, "tags", [])
    return a_object

"""Tag files"""
def open_location_tags(file_path = LOCATION_TAGS_FOLDER):
    print("[Tag] Getting locations tags..., folder:", file_path)
    locations = location.LocationDict()
    for root, dirs, files in os.walk(file_path):
        for filename in files:
            print("  file: ", filename)
            f = open(os.path.join(root, filename), "r")
            paragraphs = f.read().split("Location ID:")
            # for each location
            for it in paragraphs[1:]:
                res = re.search(r"(?P<lid>\w+)\tLocation Name:(?P<lname>.*?)\n", it)
                a_location = location.Location()
                a_location.lid = res.group("lid")
                a_location.lname = res.group("lname")
                a_location = add_attr_tag(a_location)

                # for each tag
                lines = it[res.end():]
                for line in lines.splitlines(True):
                    res = re.match(r"\t(?P<tag>.*?)\t(?P<count>\w+)\n", line)
                    a_tag = Tag()
                    a_tag.tag = res.group("tag")
                    a_tag.count = int(res.group("count"))
                    a_location.tags.append(a_tag)
                locations[a_location.lid] = a_location
            f.close()
    print("-- End Getting users posts. locations #:", len(locations))
    return locations

"""Operations"""
def get_corpus(tags_list):
    print("[tag] getting corpus...")
    corpus = []
    for tags in tags_list:
        doc_str = " ".join((x.tag + " ") * x.count for x in tags)
        corpus.append(doc_str)
    print("-- corpus doc #:", len(corpus))
    return corpus

def get_location_posts_corpus(locations):
    print("[tag] getting corpus from posts of locations")
    corpus = []
    for key in locations.keys():
        doc_str = " ".join(x for a_post in locations[key].posts for x in a_post.tags)
        corpus.append(doc_str)
    print("-- corpus doc #:", len(corpus))
    return corpus


"""
def open_location_tags_afile(file_path = None):
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
"""
