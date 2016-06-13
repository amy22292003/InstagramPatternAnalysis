#from sets import Set
import re
import os

"""file path"""
USER_POSTS_FILE = "./data/UserPosts"

class APost:
    def __init__(self):
        self.postid = ""
        self.uname = ""
        self.uid = ""
        self.time = 0
        self.posttype = 0 #1 as photo;2 as video
        self.lname = ""
        self.lid = ""
        self.lat = ""
        self.lng = ""
        self.text = ""
        self.tags = []
        self.likes = 0
        self.comments = 0

    def fit_tags(self, tagStr):
        tags = list(filter(None, re.split(',|\"', tagStr)))
        return tags

    # fit post string into a post
    def fit_post(self, line):
        #res = re.match(r"(?P<uname>.*?)\t(?P<postid>\w+)\t(?P<time>\w+)\t(?P<posttype>\w+)\t(?P<lname>.*?)\t(?P<lid>.*?)\t(?P<likes>\w+)\t(?P<comments>\w+)\t(?P<text>.*?)\t\[u\'\[(?P<tags>.*?)\]\'\].*?\n", line)
        res = re.match(r"(?P<uid>\w+)\t(?P<uname>.*?)\t(?P<postid>\w+)\t(?P<time>\w+)\t(?P<posttype>\w+)\t(?P<lname>.*?)\t(?P<lid>.*?)\t(?P<likes>\w+)\t(?P<comments>\w+)\t(?P<text>.*?)\t(?P<tags>.*?)\n", line)
        self.postid = res.group("postid")
        self.uid = res.group("uid")
        self.uname = res.group("uname")
        self.time = int(res.group("time"))


        self.posttype = res.group("posttype")
        self.lname = res.group("lname")
        self.lid = res.group("lid")
        self.text = res.group("text")
        
        #self.tags = res.group("tags")
        self.tags = self.fit_tags(res.group("tags"))

        self.likes = int(res.group("likes"))
        self.comments = int(res.group("comments"))
        del res

"""Output"""
def output_posts(posts, outputFile, mode, phase_str = None):
    f = open(outputFile, mode)
    if mode is "w":
        f.write("uid\tuname\tpostid\ttime\tposttype\tlocation\tlocation Id\tlikes\tcomments\ttext\ttags\n")
    if phase_str:
        f.write(phase_str)
    for aPost in posts:
        f.write(aPost.uid + "\t" + aPost.uname + "\t" + aPost.postid + "\t" + str(aPost.time) + "\t" + str(aPost.posttype) + "\t" + aPost.lname + "\t" + aPost.lid + "\t" + str(aPost.likes) + "\t" + str(aPost.comments) + "\t" + aPost.text + "\t")
        for aTag in aPost.tags:
            f.write("\"" + aTag + "\"")
        f.write("\n")
    f.close()

"""Open files"""
def open_file_posts(filePath):
    f = open(filePath, "r")
    posts = []
    f.readline()
    for line in f:
        aPost = APost()
        aPost.fit_post(line)
        posts.append(aPost)
    return posts

"""Get posts"""
def txt_to_posts(lines):
    posts = []
    # split lines into single line with \n
    for line in lines.splitlines(True):
        aPost = APost()
        aPost.fit_post(line)
        posts.append(aPost)
    return posts
