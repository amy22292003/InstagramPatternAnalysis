#from sets import Set
from bs4 import BeautifulSoup
import requests
import re
import datetime
import time
from random import randint
from . import PostParsing as PostPars

# the time line
TIMELINE = 1388534400
#TIMELINE = 1450336849

CURRENTTOKEN = 0

def ig_accesstoken(change = False):
    tokens = []
    tokens.append(str("418194919.5592c2e.fbbaad3f95d64d45990b5f104a6cbe82"))
    tokens.append(str("418194919.1b5dda4.3e2b630ad92a46e7b8d6060885a9f434"))
    if change:
        global CURRENTTOKEN
        CURRENTTOKEN = 1 - CURRENTTOKEN
    return tokens[CURRENTTOKEN]

def fit_a_post(aPostStr):
    aPost = PostPars.APost()

    try:
        #--Tags
        res = re.search(r"\"tags\":\[(.*?)\]",aPostStr)
        aPost.tags = filter(None, re.split(',|\"', str(res.group(1))))

        #--Image or Video
        res = re.search(r"\"type\":\"(\w+)\"", aPostStr)
        if str(res.group(1)) == "image":
            aPost.postType = 1
        else:
            aPost.postType = 2
    except:
        print("Error Exception(Tags, type):" + aPostStr)

    #-- Location
    try:
        res = re.search(r"\"location\":\{\"latitude\":(.*?),\"name\":\"(.*?)\",\"longitude\":(.*?),\"id\":(.*?)\}",aPostStr)
        aPost.lat = res.group(1)
        aPost.lName = res.group(2)
        aPost.lng = res.group(3)
        aPost.lId = res.group(4)
        aPostStr = aPostStr[res.end():]#cut the post
    except Exception as e:# when it's the post without location
        aPost.lat = ""
        aPost.lName = ""
        aPost.lng = ""
        aPost.lId = ""           
    
    try:
        #--Comment count
        res = re.search(r"\"comments\":{\"count\":(\w+),",aPostStr)
        aPost.comments = res.group(1)

        #--Created time
        res = re.search(r"\"filter\":.*?,\"created_time\":\"(\w+)\",", aPostStr)
        aPost.time = int(res.group(1))
        aPostStr = aPostStr[res.end():]#cut the post

        #--Likes Count
        res = re.search(r"\"likes\":\{\"count\":(\w+),", aPostStr)
        aPost.likes = int(res.group(1))
        aPostStr = aPostStr[res.end():]#cut the post

        res = re.search(r"\"caption\":.*?,\"user_has_liked\":", aPostStr)
        aPostStr = aPostStr[res.start():]#cut the post
    except:
        print("Error Exception(comments, likes):" + aPostStr)

    #--Text
    try:
        res = re.search(r"\"text\":\"(.*?)\",", aPostStr)
        aPost.text = res.group(1)
    except:
        aPost.text = ""            
    
    try:
        #--Post id , User id, User name
        res = re.search(r"\"id\":\"(\w+)_(\w+)\",\"user\":{", aPostStr)
        aPostStr = aPostStr[res.start():]#cut the post
        aPost.postId = res.group(1)
        aPost.uId = res.group(2)
        res = re.search(r"\"username\":\"(.*?)\",", aPostStr)
        aPost.uName = res.group(1)
    except:
        print("Error Exception(uId, uName, postId):" + aPostStr)

    return aPost

def get_ig_result(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text.encode("utf-8"), "html.parser")
        data = soup.text
    except:
        print("GetIgResult Error, change token.")
        time.sleep(randint(5, 60))# random sleep between 5 to 60 secs
        res = re.search(r"access_token=(.*?)&", url)
        newUrl = url[:res.start()] + "access_token=" + IgAccessToken(True) + url[res.end() - 1:]
        GetIgResult(newUrl)
    return data

def get_user_posts(uId, next_max_id):
    posts = []
    locationPostCount = 0
    allPostCount = 0
    url = \
        "https://api.instagram.com/v1/users/" + uId +\
        "/media/recent/?access_token=" + IgAccessToken() +\
        "&max_id=" + next_max_id +\
        "&count=50" #actually is 20, write 50 to reach maximum
    data = GetIgResult(url)
    
    res = re.search(r"\"next_max_id\":\"(\w+)\"}", data)
    if(res):
        next_max_id = res.group(1)
        print(str(datetime.datetime.now()) + "  , next_max_id: " + str(next_max_id))
    else:
        next_max_id = ""
    
    res = data.split("{\"attribution\":")
    for aPostStr in res[1:]:
        aPost = FitAPost(aPostStr)
        aPost.uId = uId

        if aPost.lId is not "": locationPostCount += 1
        allPostCount += 1
        posts.append(aPost)

    #if next_max_id >= TIMELINE:
    if next_max_id is not "":
        reLPC, reAPC, rePosts = GetUserPosts(uId, str(next_max_id))
        return reLPC + locationPostCount, reAPC + allPostCount, posts.extend(rePosts)
    else:
        return locationPostCount, allPostCount, posts

def get_location_posts(lName, lId, next_max_id = "", outputFile = None):
    posts = []
    curTime = 1451606400 #2016/01/01

    PostPars.OutputPosts(posts, outputFile, "w")

    while curTime > TIMELINE:

        url = \
            "https://api.instagram.com/v1/locations/" + lId +\
            "/media/recent?access_token=" + IgAccessToken() +\
            "&max_id=" + next_max_id +\
            "&count=50" #actually is 20, write 50 to reach maximum
        data = GetIgResult(url)
        
        res = data.split("{\"attribution\":")
        for aPostStr in res[1:]:
            aPost = FitAPost(str(aPostStr))
            aPost.lName = lName
            aPost.lId = lId
            posts.append(aPost)

        res = re.search(r"\"next_max_id\":\"(\w+)\"}", res[0])
        if(res):
            next_max_id = str(res.group(1))
            curTime = posts[len(posts) - 1].time
            print(lName + ":" + next_max_id + " current time:" + str(curTime))
        else:
            curTime = 0

        #if more than 5000 posts, then write file
        if outputFile is not None and len(posts) > 5000:
            PostPars.OutputPosts(posts, outputFile, "a")
            posts = []
    PostPars.OutputPosts(posts, outputFile, "a")

