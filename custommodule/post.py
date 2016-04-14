#from sets import Set
import re
import os

"""file path"""
USER_POSTS_FILE = "./data/UserPosts"
#BRIEFSUMMARY_FILE = "./data/BriefSummary.txt"
#USER_POSTS_SUMMARY_FILE = "./data/UserPosts_selLocaInRegion/"
#SUMMARY_FILE = "./data/Summary_selLocaInRegion.txt"

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

def get_file_posts(filePath):
    f = open(filePath, "r")
    posts = []
    f.readline()
    for line in f:
        aPost = APost()
        aPost.fit_post(line)
        posts.append(aPost)
    return posts

def get_part_posts(lines):
    posts = []
    # split lines into single line with \n
    for line in lines.splitlines(True):
        aPost = APost()
        aPost.fit_post(line)
        posts.append(aPost)
    return posts


"""
def GetUserList():
    userList = []
    for dir_entry in os.listdir(USER_POSTS_FILE):
        res = re.match(r"UserPosts_(\w+)\.txt", dir_entry)
        uid = res.group(1)
        userList.append(uid)
    return userList

def GetAUserPosts(uid):
    posts = Set()
    user = AUser()
    try:
        f = open(USER_POSTS_FILE + "UserPosts_" + str(uid) + ".txt", "r")
        line = f.readline()
        #res = re.match(r"uid\t(\w+)\tallpostcount=(\w+)\tlocationPoastCount=(\w+).*?\n", line)
        res = re.match(r"uid\t(\w+)\tfilterPostCount=(\w+)\tallPostCount=(\w+)\tlocationPostCount=(\w+).*?\n", line)
        user.uid = res.group(1)
        user.allPostCount = int(res.group(2))
        user.locationPostCount = int(res.group(3))
        f.readline()
        for line in f:
            aPost = APost(uid)
            aPost.FitPost(line)
            posts.add(aPost)
            del aPost
            del line
        user.posts = posts
        f.close()
        return user
    except:
        print "EXCEPT: No such a user"
        return None

def GetAllPosts():
    allPosts = Set()

    for dir_entry in os.listdir(USER_POSTS_FILE):
        dir_entry_path = os.path.join(USER_POSTS_FILE, dir_entry)
        if os.path.isfile(dir_entry_path):
            with open(dir_entry_path, "r") as f:
                line = f.readline()
                #res = re.match(r"uid\t(\w+)\tallpostcount=(\w+)\tlocationPoastCount=(\w+).*?\n", line)
                res = re.match(r"uid\t(\w+)\tfilterPostCount=(\w+)\tallPostCount=(\w+)\tlocationPostCount=(\w+).*?\n", line)
                uid = res.group(1)
                del res
                f.readline()
                for line in f:
                    aPost = APost(uid)
                    aPost.FitPost(line)
                    allPosts.add(aPost)
                    del aPost
                    del line
                f.close()
    return allPosts

def GetSummary():
    threshold = 5
    allCount = []
    zeroCount = 0
    thresholdCount = 0
    maxCount = 0
    for dir_entry in os.listdir(USER_POSTS_SUMMARY_FILE):
        dir_entry_path = os.path.join(USER_POSTS_SUMMARY_FILE, dir_entry)
        if os.path.isfile(dir_entry_path):
            with open(dir_entry_path, "r") as f:
                line = f.readline()
                res = re.match(r"uid\t(\w+)\tfilterPostCount=(\w+)\tallPostCount=(\w+)\tlocationPostCount=(\w+).*?\n", line)
                if not res.group(3) == "0":
                    allCount.append(int(res.group(2)))
                    if int(res.group(2)) <= threshold:
                        thresholdCount += 1
                    if int(res.group(2)) > maxCount:
                        maxCount = res.group(2)
                else:
                    zeroCount += 1
    allCountAvg = float(sum(allCount)) / float(len(allCount))

    f = open(SUMMARY_FILE, "w")
    f.write("filtered post num=" + str(sum(allCount)) + "\n")
    f.write("average post num= " + str(allCountAvg) + "\n")
    f.write("Less than " + str(threshold) + " post num= " + str(thresholdCount) + "\n")
    f.write("Zero post num= " + str(zeroCount) + "\n")
    f.write("Max post num= " + str(maxCount) + "\n")
    f.close()


def GetUserBrief():
    allUsers = []
    securityAccount = 0
    for dir_entry in os.listdir(USER_POSTS_FILE):
        dir_entry_path = os.path.join(USER_POSTS_FILE, dir_entry)
        if os.path.isfile(dir_entry_path):
            with open(dir_entry_path, "r") as f:
                line = f.readline()
                res = re.match(r"uid\t(\w+)\tallpostcount=(\w+)\tlocationPoastCount=(\w+)\n", line)
                try:
                    propotion = float(res.group(3))/float(res.group(2))
                    allUsers.append(propotion)
                except:
                    securityAccount += 1
    locationPropotion = sum(allUsers) / float(len(allUsers))
    del allUsers

    f = open(BRIEFSUMMARY_FILE, "w")
    f.write("location propotion: " + str(locationPropotion) + "\n")
    f.write("security account: " + str(securityAccount) + "\n")
    f.close

"""
