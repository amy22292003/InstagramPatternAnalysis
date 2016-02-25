import datetime
import os
import sys
import time
import custommodule.location as clocation
#import custommodule.tag as ctag
import custommodule.post as cpost
import custommodule.user as cuser

"""parameters"""
FILTER_USERS_THRES = 5
SHORT_TIME_RANGE = 30

"""file path"""
TEST = "./data/test"
LOCATION_POSTS_FOLDER = "./data/LocationPosts"
TRAVELERS_POSTS_FOLDER = "./data/TravelerPosts"
OUTPUT_TRAVELER = "./data/Travelers.txt"

def filter_users(users):
    print("Filtering users...")
    filtered_users = []
    #res_locations = set()
    for a_user in users:
        locations = set(x.lid for x in a_user.posts)
        if len(locations) >= FILTER_USERS_THRES:
            filtered_users.append(a_user)
            #res_locations = res_locations | locations
    #print("res locations #:", len(res_locations))
    return filtered_users

def get_traveler(users):
    print("Getting travelers...")
    in_short_time = lambda x: True if x[len(x) - 1].time - x[0].time <= (SHORT_TIME_RANGE * 86400) else False
    travelers = []
    for a_user in users:
        if in_short_time(a_user.get_posts("time")):
            travelers.append(a_user)
    return travelers

def fit_posts_to_users(posts, users):
    for a_post in posts:
        # check if the user in users dict(i.e. is traveler)
        if a_post.uid in users.keys():
            users.fit_posts([a_post])

def output_traveler(travelers):
    print("Outputing travelers...")
    f = open(OUTPUT_TRAVELER, "w")
    f.write("uid,uname,post count,cross time\n")
    for a_user in travelers:
        cross_time = round((a_user.posts[len(a_user.posts) - 1].time - a_user.posts[0].time) / 86400)
        f.write(a_user.uid + "," + str(a_user.uname) + "," + str(len(a_user.posts)) + "," + str(cross_time) + "\n")
    f.close()


print("STARTTIME:" + str(datetime.datetime.now()))

# Get users, filter, get travelers, output
"""
users = cuser.UserDict()
for root, dirs, files in os.walk(LOCATION_POSTS_FOLDER):
    for i, filename in enumerate(files):
        posts = cpost.get_file_posts(os.path.join(root, filename))
        new_users = [x for x in posts if x.uid not in users.keys()]
        users.update(new_users) # add group of users to dictionary
        users.fit_posts(posts, "lid", "time") # add location id & time of each post into the users's post list
        if i % 100 == 0:
            print("At locations #: ", i, " /users len: ", len(users))

filtered_users = filter_users(users.values())
del users
print("filtered_users #:", len(filtered_users))
travelers = get_traveler(filtered_users)
print("travelers #:", len(travelers))
output_traveler(travelers)
"""

# Get travelers' posts
users = cuser.get_users_list()
print("Getting locations posts...")
for root, dirs, files in os.walk(LOCATION_POSTS_FOLDER):
    for i, filename in enumerate(files):
        posts = cpost.get_file_posts(os.path.join(root, filename))
        fit_posts_to_users(posts, users)
        if i % 100 == 0:
            print("At locations #: ", i)
    print("locations #:", len(files) - 1)

cuser.output_user_posts_afile(users.values(), TRAVELERS_POSTS_FOLDER)

print("ENDTIME:" + str(datetime.datetime.now()))