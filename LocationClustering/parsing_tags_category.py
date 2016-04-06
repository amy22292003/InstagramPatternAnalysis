import datetime
import numpy
import operator
import random
import time
import custommodule.location as clocation
import custommodule.tag as ctag

"""parameters"""
MAX_FREQ_THRESHOLD = 500
MIN_FREQ_THRESHOLD = 5
INTERSECT_THRESHOLD = 0.1#25 # the min intersection tags count between the category locations and the candidate location
CATEGORY_MIN_AMOUNT = 10

"""file path"""
OUTPUT_CATEGORY_FILE = "./data/LocationCategories_i" + str(INTERSECT_THRESHOLD) + "c" + str(CATEGORY_MIN_AMOUNT) + ".txt"

"""
def count_tag_in_location(location_list):
    tag_dict = dict()
    for a_location in location_list:
        for a_tag in a_location.tags:
            if a_tag not in tag_dict:
                tag_dict[a_tag] =  ctag.Tag()
                tag_dict[a_tag].name = a_tag
            tag_dict[a_tag].count += 1
    return list(tag_dict.values())
"""

def filter_freq_tag(location_list, max_thres=None, min_thres=None):
    tag_list = count_tag_in_location(location_list)
    if not max_thres:
        max_thres = MAX_FREQ_THRESHOLD
    if not min_thres:
        min_thres = MIN_FREQ_THRESHOLD

    filtered_tag_list = [x for x in tag_list if x.count < max_thres and x.count > min_thres]
    filtered_locations = []
    for idx, a_location in enumerate(location_list):
        a_location.tags = a_location.tags & set(x.name for x in filtered_tag_list)
        if idx % 100 == 0:
            print("Filtering locations' set:" + str(idx))
    return filtered_tag_list, location_list

class InterLocation():
    def __init__(self):
        self.clocation = clocation.Location()
        self.interavg = 0 # the average intersection tags count between locations

class ListDict(dict):
    def __init__(self, *args, **kwargs):
        for x in args:
            self.setdefault(x, [])

    def add_count(self, counts):
        for item in counts:
            self[item[0]].append(item[1])
    #def __setitem__(self, key, value):
     #   self.setdefault(key, []).append(value)

def set_location_dict(location_list):
    print("Setting location dictionary...")
    locations = dict()
    for idx, a_location in enumerate(location_list):
        locations[a_location.lid] = InterLocation()
        locations[a_location.lid].clocation = a_location

        # get the average intersection tags count between locations
        remain_locations = location_list[:idx] + location_list[(idx + 1):]
        intersect_count = [len(x.tags & a_location.tags) for x in remain_locations]
        locations[a_location.lid].interavg = sum(intersect_count) / len(intersect_count)
    return locations

def add_location_into_cate(cate_locations, free_locations):
    "Adding a location into the category..."
    candidates = ListDict(*free_locations.keys())
    for a_location in cate_locations:
        # count the intersection tags of the initial location & candidate locations. (key of the location, count)
        intersect_count = [(key, len(free_locations[key].clocation.tags & a_location.clocation.tags) / len(free_locations[key].clocation.tags)) for key in candidates.keys()]

        intersect_count = set(x for x in intersect_count if x[1] > INTERSECT_THRESHOLD) # the locations which intersect num > threshold num
        remove = set(candidates.keys()) - set(x[0] for x in intersect_count)
        #print("fit len for cate location:" + a_location.clocation.lname + " -- " + str(len(intersect_count)) + " -- " + str(len(remove)))
        for key in remove:
            candidates.pop(key) # remove unqualified locations
        candidates.add_count(intersect_count)
    #print("remaining candidates amount:" + str(len(candidates)))

    if len(candidates) is not 0:
        # for the remaining candidate locations
        intersect_ratio = {x:0 for x in candidates.keys()}
        for key in candidates.keys():
            # the average intersect tags count between the category locations & the candidate
            in_avg = sum(candidates[key]) / len(candidates[key])
            intersect_ratio[key] = in_avg / free_locations[key].interavg 
        
        new_add_key = max(intersect_ratio, key=intersect_ratio.get)
        #print("The new added location-" + free_locations[new_add_key].clocation.lname + " intersection ratio:" + str(intersect_ratio[new_add_key]))
        return new_add_key
    else:
        return None
        

def get_a_cate(locations):
    failed_init = set()
    while len(failed_init) < len(locations):
        # the initial location
        init_key = random.choice(list(set(locations.keys()) - failed_init))
        a_category = [locations[init_key]]

        free_locations = {i:locations[i] for i in locations if i != init_key}

        while True:
            new_add_key = add_location_into_cate(a_category, free_locations)
            if new_add_key is None:
                break
            a_category.append(locations[new_add_key])
            free_locations.pop(new_add_key)

        if len(a_category) > CATEGORY_MIN_AMOUNT:
            print("category initial: " + locations[init_key].clocation.lname)
            return a_category, free_locations
        else:
            #print("initial: " + locations[init_key].clocation.lname + " --failed")
            failed_init.add(init_key)
    return None


def get_categories(locations):
    print("Splitting categories...")
    categories = []
    while locations is not None:
        try:
            print("Category number: " + str(len(categories) + 1) + " >>>")
            new_category, free_locations = get_a_cate(locations)
            categories.append(new_category)
            locations = free_locations
            print("  adding locations amount:" + str(len(categories[len(categories)-1])) + " ,remaining locations amount:" + str(len(locations)))
        except Exception:
            print(">>>\nRemaining locations number: " + str(len(locations)))
            break
    return categories, len(locations)

def output_categories(categories, remaining):
    f = open(OUTPUT_CATEGORY_FILE, "w")
    f.write("category number:" + str(len(categories)) + " , remaining locations:" + str(remaining) + "\n")
    for idx, a_category in enumerate(categories):
        f.write("Category:" + str(idx + 1) + " , #= " + str(len(a_category)) + ">>>\n")
        clocation.output_location_part_list([x.clocation for x in a_category], f)
    f.close()

#transform location tags to filtered location tags in a file
"""
print("STARTTIME:" + str(datetime.datetime.now()))
location_list = ctag.get_location_tags()
filtered_tag_list, location_list = filter_freq_tag(location_list)
tag.output_location_tags_afile(location_list)

"""
# 
print("STARTTIME:" + str(datetime.datetime.now()))
#location_list = ctag.get_location_tags_afile("./data/LocationTags_test.txt")
location_list = ctag.get_location_tags_afile()
locations = set_location_dict(location_list)
del location_list
categories, remaining = get_categories(locations)
del locations
print(">>>>>>>>>>>")
output_categories(categories, remaining)
print("ENDTIME:" + str(datetime.datetime.now()))
