from bs4 import BeautifulSoup
import io
import os
import requests
import re
import sys
from . import post as cpost

"""file path"""
USER_LIST = "./data/Travelers.txt"
USER_POSTS_FOLDER = "./data/UserPosts"

class AUser:
    def __init__(self):
        self.uid = ""
        self.uname = ""
        self.posts = []

    def __init__(self, *args):
        attrs = ["uid", "uname"]
        for i, arg in enumerate(args):
            setattr(self, attrs[i], arg)
        self.posts = []

    def add_post_attr(self, a_post, *args):
        # if only add part of arributes
        if args:
            new_post = cpost.APost()
            for arg in args:
                setattr(new_post, arg, getattr(a_post, arg))
            self.posts.append(new_post)
        else:
            self.posts.append(a_post)

    def get_posts(self, sorted_key):
        if sorted_key:
            self.posts = sorted(self.posts, key = lambda x:getattr(x, sorted_key))
            return self.posts
        else:
            return self.posts
            
class UserDict(dict):
    # UserDict(posts)
    def __init__(self, *args, **kwargs):
        for arg in args:
            self.setdefault(arg.uid, AUser(arg.uid, arg.uname))

    def update(self, news):
        for new in news:
            self[new.uid] = AUser(new.uid, new.uname)

    def fit_posts(self, posts, *args):
        if not args:
            for a_post in posts:
                self[a_post.uid].posts.append(a_post)
        else:
            for a_post in posts:
                self[a_post.uid].add_post_attr(a_post, *args)

    def sort_posts(self, sorted_key):
        print("Sorting posts of users...")
        for key in self.keys():
            self[key].get_posts(sorted_key)

"""Users list related"""
def get_users_list(file_path = None):
    print("Getting users list...")
    users = UserDict()
    if not file_path:
        file_path = USER_LIST
    f = open(file_path, "r")
    f.readline()
    for line in f:
        res = re.match(r"(?P<uid>\w+),(?P<uname>.*?),.*?\n", line)
        a_user = AUser()
        a_user.uid = res.group("uid")
        a_user.uname = res.group("uname")
        users[a_user.uid] = a_user
    f.close()
    print("End Getting users #", len(users))
    return users

"""posts"""
def get_users_posts_afile(file_path = None):
    print("Getting users posts...")
    if not file_path:
        file_path = USER_POSTS_FOLDER
    users = UserDict()
    for root, dirs, files in os.walk(file_path):
        for filename in files:
            print("  file: ", filename)
            f = open(os.path.join(root, filename), "r")
            f.readline()
            # split to each user's part: [uid, uname, content, uid, uname, content...]
            iterator = filter(None, re.split(r"User ID:(\w+)\tUser Name:(.*?)\n", f.read()))
            for uid in iterator:
                a_user = AUser()
                a_user.uid = uid
                a_user.uname = next(iterator)
                posts = cpost.get_part_posts(next(iterator))
                a_user.posts = posts
                users[uid] = a_user
            f.close()
    print("End Getting users posts.")
    return users


"""Output"""
def output_user_posts(users, file_path = None):
    print("Outputing users posts...")
    if not file_path:
        file_path = USER_POSTS_FOLDER
    for a_user in users:
        output_file = file_path + "/UserPosts_" + a_user.uid + ".txt"
        cpost.output_posts(a_user.posts, output_file, "w")

def output_user_posts_afile(users, file_path = None, afile_num = 10000):
    print("Outputing users posts...")
    if not file_path:
        file_path = USER_POSTS_FOLDER
    output_file = ""
    for i, a_user in enumerate(users):
        seperate_str = "User ID:" + a_user.uid + "\tUser Name:" + a_user.uname + "\n"
        if i % afile_num == 0:
            output_file = file_path + "/UserPosts_#" + str(i) + ".txt"
            print("Outputing file: ", output_file)
            cpost.output_posts(a_user.posts, output_file, "w", seperate_str)
        else:
            cpost.output_posts(a_user.posts, output_file, "a", seperate_str)
    print("End outputing users #:", len(users))
