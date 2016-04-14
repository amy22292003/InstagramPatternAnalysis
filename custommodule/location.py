import os
import re
from . import post

"""file path"""
LOCATIONDETAIL_FILE = "./data/LocationDetail_NY.txt"
LOCATION_POSTS_FILE = "./data/LocationPosts"
OUTPUT_LOCATION_DETAIL = "./data/LocationDetail_.txt"

# NYC REGION
MINLAT = 40.49
MAXLAT = 40.92
MINLNG = -74.26
MAXLNG = -73.7

class Location:
    def __init__(self):
        self.lid = ""
        self.lname = ""
        #self.usercount = 0
        self.lat = ""
        self.lng = ""
        self.posts = []
        #self.tags = set()

    def __init__(self, *args):
        attrs = ["lid", "lname", "lat", "lng"]
        for i, arg in enumerate(args):
            setattr(self, attrs[i], arg)
        self.posts = []

    def add_post_attr(self, a_post, *args):
        # if only add part of arributes
        if args:
            new_post = post.APost()
            for arg in args:
                setattr(new_post, arg, getattr(a_post, arg))
            self.posts.append(new_post)
        else:
            self.posts.append(a_post)

class LocationDict(dict):
    # UserDict(posts)
    def __init__(self, *args, **kwargs):
        for arg in args:
            self.setdefault(arg.lid, Location(arg.lid, arg.lname))

    def update(self, news):
        for new in news:
            self[new.lid] = Location(new.lid, new.lname)

    def fit_posts(self, posts, *args):
        if not args:
            for a_post in posts:
                self[a_post.lid].posts.append(a_post)
                #self[a_post.lid].add_post_attr(a_post)
        else:
            for a_post in posts:
                self[a_post.lid].add_post_attr(a_post, *args)

""" Location list related """
# Get location Details Dict
def get_locations_list(locationListFile = None):
    #sortedLocations = []
    locations = LocationDict()
    if not locationListFile:
        locationListFile = LOCATIONDETAIL_FILE
    f = open(locationListFile, "r")
    print("open filename:", f.name)
    line = f.readline()
    for line in f:
        res = re.match(r"(?P<lid>\w+)\t(?P<location>.*?)\t(?P<usercount>\w+)\t(?P<lat>.*?)\t(?P<lng>.*?)\n", line)
        item = Location()
        item.lid = res.group("lid")
        item.lname = res.group("location")
        item.usercount = int(res.group("usercount"))
        item.lat = res.group("lat")
        item.lng = res.group("lng")
        locations[item.lid] = item
    return locations

def get_in_region_locations_list():
    locations = get_locations_list()
    newLocations = filter(lambda x: MAXLAT >= float(x.lat) >= MINLAT and MAXLNG >= float(x.lng) >= MINLNG, locations.values())
    return newLocations

"""
def output_location_part_list(locations, f):
    for item in locations:
        f.write(item.lid + "\t" + item.lname + "\t" + str(item.usercount) + "\t" + item.lat + "\t" + item.lng + "\n")
"""

def output_location_list(location_list, mode, locationListFile = OUTPUT_LOCATION_DETAIL, phase_str = None):
    print("Outputing location list...")
    f = open(locationListFile, mode)
    if mode is "w":
        f.write("lid\tlocation\tlatitude\tlongitude\tuser count\n")
    if phase_str:
        f.write(phase_str)
    for item in location_list:
        f.write(item.lid + "\t" + item.lname + "\t" + item.lat + "\t" + item.lng)
        if hasattr(item, 'usercount'):
            f.write("\t" + str(item.usercount))
        f.write("\n")
    f.close()

""" Location posts related """
# get locations posts
def get_location_posts(file_path = None):
    print("Getting locations posts...")
    locations = []
    if not file_path:
        file_path = LOCATION_POSTS_FILE
    for root, dirs, files in os.walk(file_path):
        for filename in files:
            posts = post.get_file_posts(os.path.join(root, filename))
            a_location = Location()
            a_location.posts = posts
            a_location.lid = posts[0].lid
            locations.append(a_location)
            del posts
            if len(locations) % 100 == 0:
                print("locations #:", len(locations))
    print("End getting locations.")
    return locations

""" mining """
def fit_users_to_location(locations, users, *attr):
    print("Fitting users to locations..., locations #=", len(locations))
    all_posts = [y for x in users.values() for y in x.posts]
    locations.fit_posts(all_posts, *attr)

    # remove locations which no traveler had post there
    remove = [key for key in locations.keys() if len(locations[key].posts) == 0]
    for key in remove:
        locations.pop(key)
    print("after removing locations had no post, #=", len(locations))
    return locations


